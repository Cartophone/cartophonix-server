import json
import asyncio
import requests
from app.database import register_card, get_card_by_uid, update_playlist, create_alarm, list_alarms, toggle_alarm, edit_alarm
from config.config import MUSIC_HOST, MUSIC_PORT
import time

async def log_and_send(websocket, message, to_websocket=True):
    print(f"Log: {json.dumps(message)}")
    if to_websocket and websocket:
        try:
            await websocket.send(json.dumps(message))
            print(f"Sent to WebSocket: {json.dumps(message)}")
        except Exception as e:
            print(f"Failed to send to WebSocket: {e}")

async def handle_read(websocket, rfid_reader):
    async def read_rfid():
        last_uid = None
        card_present = False

        while True:
            success, uid = rfid_reader.read_uid()
            if success and uid != last_uid:
                last_uid = uid
                card_present = True
                playlist = get_card_by_uid(uid)
                if playlist:
                    response = requests.post(
                        f"http://{MUSIC_HOST}:{MUSIC_PORT}/api/queue/items/add",
                        params={
                            'uris': playlist.playlist,
                            'playback': 'start',
                            'clear': 'true'
                        }
                    )
                    if response.status_code == 200:
                        ws_response = {"status": "success", "uid": uid, "playlist": playlist.playlist}
                    else:
                        ws_response = {"status": "error", "message": "Failed to launch playlist", "uid": uid}
                    await log_and_send(websocket, ws_response)
                else:
                    response = {"status": "error", "message": "Unknown card", "uid": uid}
                    await log_and_send(websocket, response)
                # Wait for the card to be removed before continuing
                card_detected = True
                while rfid_reader.read_uid() == (True, uid):
                    if card_detected:
                        print("Card still detected, waiting for removal...")
                        card_detected = False
                    await asyncio.sleep(0.1)
                # Inform the WebSocket that read mode is active
                read_mode_response = {"status": "info", "message": "Read mode active"}
                await log_and_send(websocket, read_mode_response)
            elif not success:
                last_uid = None
                card_present = False
            await asyncio.sleep(0.1)

    read_task = asyncio.create_task(read_rfid())
    return read_task

async def check_alarms():
    while True:
        current_time = time.strftime("%H:%M")
        alarms = list_alarms()
        for alarm in alarms:
            if alarm['hour'] == current_time and alarm['activated']:
                response = requests.post(
                    f"http://{MUSIC_HOST}:{MUSIC_PORT}/api/queue/items/add",
                    params={
                        'uris': alarm['playlist'],
                        'playback': 'start',
                        'clear': 'true'
                    }
                )
                if response.status_code == 200:
                    print(f"Alarm triggered: {alarm['playlist']}")
        await asyncio.sleep(60)

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
                print(f"Registering with playlist: {playlist}")
                try:
                    start_time = asyncio.get_event_loop().time()
                    uid = None
                    while asyncio.get_event_loop().time() - start_time < 60:
                        success, uid = await asyncio.to_thread(rfid_reader.read_uid)
                        if success:
                            break
                        await asyncio.sleep(0.1)
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
                                        update_playlist(existing_card.id, playlist)
                                        response = {"status": "success", "message": "Card updated", "uid": uid, "playlist": playlist}
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
                        register_card(uid, playlist)
                        response = {"status": "success", "message": "Card registered", "uid": uid, "playlist": playlist}
                        await log_and_send(websocket, response)

                    # Wait for the card to be removed before resuming read task
                    card_detected = True
                    while rfid_reader.read_uid() == (True, uid):
                        if card_detected:
                            print("Card still detected, waiting for removal...")
                            card_detected = False
                        await asyncio.sleep(0.1)

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

            elif action == "stop_read":
                read_task.cancel()
                break

    except asyncio.CancelledError:
        pass
    except Exception as e:
        response = {"status": "error", "message": str(e)}
        await log_and_send(websocket, response)
        print(f"Exception occurred: {e}")