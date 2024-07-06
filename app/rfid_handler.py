import asyncio
import aiohttp
from app.database import get_card_by_uid
from config.config import MUSIC_HOST, MUSIC_PORT
from app.utils import log_and_send

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
                    print(playlist.playlist)
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            f"http://{MUSIC_HOST}:{MUSIC_PORT}/api/queue/items/add",
                            params={
                                'uris': playlist.playlist,
                                'playback': 'start',
                                'clear': 'true'
                            }
                        ) as response:
                            if response.status == 200:
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
                        card_detected_response = {"status": "info", "message": "Card still detected, waiting for removal..."}
                        await log_and_send(websocket, card_detected_response)
                        print("Card still detected, waiting for removal...")
                        card_detected = False
                    await asyncio.sleep(0.2)
                # Inform the WebSocket that read mode is active
                read_mode_response = {"status": "info", "message": "Read mode active"}
                await log_and_send(websocket, read_mode_response)
            elif not success:
                last_uid = None
                card_present = False
            await asyncio.sleep(0.2)

    read_task = asyncio.create_task(read_rfid())
    return read_task