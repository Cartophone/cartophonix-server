import json
import asyncio
import requests
from app.database import register_card, get_card_by_uid, update_playlist
from config.config import MUSIC_HOST, MUSIC_PORT

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
                    await websocket.send(json.dumps(ws_response))
                    print(f"Sent to WebSocket: {json.dumps(ws_response)}")
                else:
                    response = {"status": "error", "message": "Unknown card", "uid": uid}
                    await websocket.send(json.dumps(response))
                    print(f"Sent to WebSocket: {json.dumps(response)}")
                # Wait for the card to be removed before continuing
                card_detected = True
                while rfid_reader.read_uid() == (True, uid):
                    if card_detected:
                        print("Card still detected, waiting for removal...")
                        card_detected = False
                    await asyncio.sleep(0.1)
                # Inform the WebSocket that read mode is active
                read_mode_response = {"status": "info", "message": "Read mode active"}
                await websocket.send(json.dumps(read_mode_response))
                print(f"Sent to WebSocket: {json.dumps(read_mode_response)}")
            elif not success:
                last_uid = None
                card_present = False
            await asyncio.sleep(0.1)

    read_task = asyncio.create_task(read_rfid())
    return read_task

async def handle_client(websocket, path, rfid_reader):
    print("Client connected")
    read_task = await handle_read(websocket, rfid_reader)

    # Inform the client about the current mode
    initial_mode_response = {"status": "info", "message": "Read mode active"}
    await websocket.send(json.dumps(initial_mode_response))
    print(f"Sent to WebSocket: {json.dumps(initial_mode_response)}")

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
                        await websocket.send(json.dumps(response))
                        print(f"Sent to WebSocket: {json.dumps(response)}")

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
                                        await websocket.send(json.dumps(response))
                                        print(f"Sent to WebSocket: {json.dumps(response)}")
                                        confirmation_received = True
                                        break
                                    elif confirm_data.get("action") == "overwrite" and confirm_data.get("confirm") == "no":
                                        print(f"Card with UID: {uid} not overwritten")
                                        response = {"status": "info", "message": "Card not overwritten"}
                                        await websocket.send(json.dumps(response))
                                        print(f"Sent to WebSocket: {json.dumps(response)}")
                                        confirmation_received = True
                                        break
                                except asyncio.TimeoutError:
                                    continue

                            if not confirmation_received:
                                raise asyncio.TimeoutError
                        except asyncio.TimeoutError:
                            response = {"status": "error", "message": "No reply within timeout. Card not overwritten."}
                            await websocket.send(json.dumps(response))
                            print(f"Sent to WebSocket: {json.dumps(response)}")
                            print("Timeout: No reply received for overwrite confirmation")

                    else:
                        print(f"Registering new card with UID: {uid}")
                        register_card(uid, playlist)
                        response = {"status": "success", "message": "Card registered", "uid": uid, "playlist": playlist}
                        await websocket.send(json.dumps(response))
                        print(f"Sent to WebSocket: {json.dumps(response)}")

                    # Wait for the card to be removed before resuming read task
                    card_detected = True
                    while rfid_reader.read_uid() == (True, uid):
                        if card_detected:
                            print("Card still detected, waiting for removal...")
                            card_detected = False
                        await asyncio.sleep(0.1)

                    print("Card removed, resuming read task")
                    read_mode_response = {"status": "info", "message": "Read mode active"}
                    await websocket.send(json.dumps(read_mode_response))
                    print(f"Sent to WebSocket: {json.dumps(read_mode_response)}")

                except asyncio.TimeoutError:
                    response = {"status": "error", "message": "No card detected within timeout"}
                    await websocket.send(json.dumps(response))
                    print(f"Sent to WebSocket: {json.dumps(response)}")
                    print("Timeout: No card detected")

            elif action == "stop_read":
                read_task.cancel()
                break
    except asyncio.CancelledError:
        pass
    except Exception as e:
        response = {"status": "error", "message": str(e)}
        await websocket.send(json.dumps(response))
        print(f"Sent to WebSocket: {json.dumps(response)}")
        print(f"Exception occurred: {e}")