import json
import asyncio
from app.database import register_card, get_card_by_uid, update_card, create_alarm, list_alarms, toggle_alarm, edit_alarm, delete_alarm, delete_card
from app.rfid_handler import handle_read
from app.utils import log_and_send

async def handle_client(websocket, path, rfid_reader):
    print("Client connected")
    read_task = await handle_read(websocket, rfid_reader)

    # Inform the client about the current mode
    initial_mode_response = {"status": "info", "message": "Read mode active"}
    await log_and_send(websocket, initial_mode_response)

    try:
        async for message in websocket:
            print(f"Received message: {message}")
            data = json.loads(message)
            action = data.get("action")

            if action == "register":
                read_task.cancel()  # Pause the read task
                playlist = data.get("playlist")
                name = data.get("name")
                image = data.get("image")  # Optional
                print(f"Registering with playlist: {playlist}, name: {name}, image: {image}")
                try:
                    start_time = asyncio.get_event_loop().time()
                    uid = None
                    while asyncio.get_event_loop().time() - start_time < 60:
                        success, uid = await asyncio.to_thread(rfid_reader.read_uid)
                        if success:
                            break
                        await asyncio.sleep(0.2)
                    if not success:
                        raise asyncio.TimeoutError

                    print(f"Scanned UID: {uid}")
                    existing_card = get_card_by_uid(uid)

                    if existing_card:
                        print(f"UID {uid} already registered. Asking for overwrite confirmation.")
                        response = {"status": "info", "message": "This card is already registered, overwrite?"}
                        await log_and_send(websocket, response)

                        try:
                            confirm_start_time = asyncio.get_event_loop().time()
                            confirmation_received = False
                            while asyncio.get_event_loop().time() - confirm_start_time < 60:
                                try:
                                    confirm_message = await asyncio.wait_for(websocket.recv(), timeout=1)
                                    confirm_data = json.loads(confirm_message)
                                    if confirm_data.get("action") == "overwrite" and confirm_data.get("confirm") == "yes":
                                        print(f"Overwriting card with UID: {uid}")
                                        update_card(existing_card.id, playlist, name, image)
                                        response = {"status": "success", "message": "Card updated", "uid": uid, "playlist": playlist, "name": name, "image": image}
                                        await log_and_send(websocket, response)
                                        confirmation_received = True
                                        break
                                    elif confirm_data.get("action") == "overwrite" and confirm_data.get("confirm") == "no":
                                        print(f"Card with UID: {uid} not overwritten")
                                        response = {"status": "info", "message": "Card not overwritten"}
                                        await log_and_send(websocket, response)
                                        confirmation_received = True
                                        break
                                except asyncio.TimeoutError:
                                    continue

                            if not confirmation_received:
                                raise asyncio.TimeoutError
                        except asyncio.TimeoutError:
                            response = {"status": "error", "message": "No reply within timeout. Card not overwritten."}
                            await log_and_send(websocket, response)
                            print("Timeout: No reply received for overwrite confirmation")

                    else:
                        print(f"Registering new card with UID: {uid}")
                        register_card(uid, playlist, name, image)
                        response = {"status": "success", "message": "Card registered", "uid": uid, "playlist": playlist, "name": name, "image": image}
                        await log_and_send(websocket, response)

                    # Wait for the card to be removed before resuming read task
                    card_detected = True
                    while rfid_reader.read_uid() == (True, uid):
                        if card_detected:
                            card_detected_response = {"status": "info", "message": "Card still detected, waiting for removal..."}
                            await log_and_send(websocket, card_detected_response)
                            print("Card still detected, waiting for removal...")
                            card_detected = False
                        await asyncio.sleep(0.2)

                    print("Card removed, resuming read task")
                    read_mode_response = {"status": "info", "message": "Read mode active"}
                    await log_and_send(websocket, read_mode_response)

                except asyncio.TimeoutError:
                    response = {"status": "error", "message": "No card detected within timeout"}
                    await log_and_send(websocket, response)
                    print("Timeout: No card detected")

            elif action == "create_alarm":
                hour = data.get("hour")
                playlist = data.get("playlist")
                create_alarm(hour, playlist)
                response = {"status": "success", "message": "Alarm created", "hour": hour, "playlist": playlist}
                await log_and_send(websocket, response)

            elif action == "list_alarms":
                alarms = list_alarms()
                response = {"status": "success", "alarms": alarms}
                await log_and_send(websocket, response)

            elif action == "toggle_alarm":
                alarm_id = data.get("alarm_id")
                new_status = toggle_alarm(alarm_id)
                response = {"status": "success", "message": "Alarm toggled", "new_status": new_status}
                await log_and_send(websocket, response)

            elif action == "edit_alarm":
                alarm_id = data.get("alarm_id")
                new_hour = data.get("new_hour")
                new_playlist = data.get("new_playlist")
                edit_alarm(alarm_id, new_hour, new_playlist)
                response = {"status": "success", "message": "Alarm updated", "alarm_id": alarm_id, "new_hour": new_hour, "new_playlist": new_playlist}
                await log_and_send(websocket, response)

            elif action == "delete_alarm":
                alarm_id = data.get("alarm_id")
                delete_alarm(alarm_id)
                response = {"status": "success", "message": "Alarm deleted", "alarm_id": alarm_id}
                await log_and_send(websocket, response)

            elif action == "delete_card":
                card_id = data.get("card_id")
                delete_card(card_id)
                response = {"status": "success", "message": "Card deleted", "card_id": card_id}
                await log_and_send(websocket, response)

            elif action == "stop_read":
                read_task.cancel()
                break

    except asyncio.CancelledError:
        pass
    except Exception as e:
        response = {"status": "error", "message": str(e)}
        await log_and_send(websocket, response)
        print(f"Exception occurred: {e}")