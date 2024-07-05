import json
import asyncio
import requests
from app.database import register_card, get_card_by_uid, update_playlist, get_all_cards
from config.config import MUSIC_HOST, MUSIC_PORT

async def handle_read(websocket, rfid_reader):
    async def read_rfid():
        while True:
            uid = rfid_reader.read_uid()
            if uid:
                playlist = get_card_by_uid(uid)
                if playlist:
                    response = requests.post(
                        f"http://{MUSIC_HOST}:{MUSIC_PORT}/api/queue/items/add",
                        params={
                            'uris': playlist,
                            'playback': 'start',
                            'clear': 'true'
                        }
                    )
                    if response.status_code == 200:
                        ws_response = {"status": "success", "uid": uid, "playlist": playlist}
                    else:
                        ws_response = {"status": "error", "message": "Failed to launch playlist", "uid": uid}
                    await websocket.send(json.dumps(ws_response))
                else:
                    response = {"status": "error", "message": "Unknown card", "uid": uid}
                    await websocket.send(json.dumps(response))
            await asyncio.sleep(1)

    read_task = asyncio.create_task(read_rfid())
    return read_task

async def handle_client(websocket, path, rfid_reader):
    read_task = await handle_read(websocket, rfid_reader)
    try:
        async for message in websocket:
            print(f"Received message: {message}")
            data = json.loads(message)
            action = data.get("action")

            if action == "register":
                read_task.cancel()  # Pause the read task
                playlist = data.get("playlist")
                print(f"Registering with playlist: {playlist}")
                uid = await asyncio.wait_for(rfid_reader.read_uid(), timeout=60)
                print(f"Scanned UID: {uid}")
                existing_card = get_card_by_uid(uid)

                if existing_card:
                    print(f"Updating existing card with UID: {uid}")
                    update_playlist(existing_card.id, playlist)
                    response = {"status": "success", "message": "Card updated", "uid": uid, "playlist": playlist}
                else:
                    print(f"Registering new card with UID: {uid}")
                    register_card(uid, playlist)
                    response = {"status": "success", "message": "Card registered", "uid": uid, "playlist": playlist}

                await websocket.send(json.dumps(response))
                print("Response sent to client")
                read_task = await handle_read(websocket, rfid_reader)  # Resume the read task
            elif action == "edit":
                cards = get_all_cards()
                response = {"status": "success", "cards": cards}
                await websocket.send(json.dumps(response))
            elif action == "stop_read":
                read_task.cancel()
                break
    except asyncio.TimeoutError:
        response = {"status": "error", "message": "No card detected within timeout"}
        await websocket.send(json.dumps(response))
        print("Timeout: No card detected")
    except asyncio.CancelledError:
        pass
    except Exception as e:
        response = {"status": "error", "message": str(e)}
        await websocket.send(json.dumps(response))
        print(f"Exception occurred: {e}")