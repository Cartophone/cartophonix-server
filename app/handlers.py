import json
import asyncio
import requests
from app.rfid import RFIDReader
from app.database import register_card, get_card_by_uid, get_all_cards
from config.config import MUSIC_HOST, MUSIC_PORT

async def handle_client(websocket, path):
    rfid_reader = RFIDReader()

    async def read_rfid():
        while True:
            uid = rfid_reader.read_uid()
            if uid:
                playlist = get_card_by_uid(uid)
                if playlist:
                    # Call the Owntone music server API
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
                        ws_response = {"status": "error", "message": "Failed to launch playlist", "uid": uid, "playlist": playlist}

                    await websocket.send(json.dumps(ws_response))
                else:
                    response = {"status": "error", "message": "Unknown card", "uid": uid}
                    await websocket.send(json.dumps(response))
            await asyncio.sleep(1)  # Adjust the sleep time as needed to avoid excessive polling

    read_task = asyncio.create_task(read_rfid())

    try:
        async for message in websocket:
            data = json.loads(message)
            action = data.get("action")
            if action == "register":
                playlist = data.get("playlist")
                uid = rfid_reader.read_uid()
                register_card(uid, playlist)
                response = {"status": "success", "message": "Card registered", "uid": uid, "playlist": playlist}
                await websocket.send(json.dumps(response))
            elif action == "edit":
                cards = get_all_cards()
                response = {"status": "success", "cards": cards}
                await websocket.send(json.dumps(response))
            elif action == "stop_read":
                read_task.cancel()
    except asyncio.CancelledError:
        pass
    finally:
        read_task.cancel()
