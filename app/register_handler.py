import json
import asyncio
from app.database import register_card, get_card_by_uid, update_playlist

async def handle_register(websocket, rfid_reader):
    async def wait_for_uid():
        while True:
            print("Waiting for RFID scan...")
            uid = rfid_reader.read_uid()
            print(f"Read UID: {uid}")  # Debugging statement
            if uid:
                print(f"UID detected: {uid}")
                return uid
            await asyncio.sleep(1)

    playlist = None
    try:
        async for message in websocket:
            print(f"Register handler received message: {message}")
            data = json.loads(message)
            action = data.get("action")
            if action == "register":
                playlist = data.get("playlist")
                print(f"Registering with playlist: {playlist}")
                break

        if playlist:
            print("Starting to wait for UID...")
            try:
                uid = await asyncio.wait_for(wait_for_uid(), timeout=60)
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
            except asyncio.TimeoutError:
                response = {"status": "error", "message": "No card detected within timeout"}
                await websocket.send(json.dumps(response))
                print("Timeout: No card detected")
    except Exception as e:
        response = {"status": "error", "message": str(e)}
        await websocket.send(json.dumps(response))
        print(f"Exception occurred: {e}")
    except asyncio.CancelledError:
        pass