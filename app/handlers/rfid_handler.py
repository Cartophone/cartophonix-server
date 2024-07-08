import asyncio
import aiohttp
from app.database import get_card_by_uid
from config.config import MUSIC_HOST, MUSIC_PORT
from app.utils import log_and_send

async def handle_read(rfid_reader):
    last_uid = None
    while True:
        success, uid = await rfid_reader.read_uid()
        if success and uid != last_uid:
            last_uid = uid
            playlist = get_card_by_uid(uid)
            if playlist:
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
                            await log_and_send({"status": "success", "uid": uid, "playlist": playlist.playlist})
                        else:
                            await log_and_send({"status": "error", "message": "Failed to launch playlist", "uid": uid})
            else:
                await log_and_send({"status": "error", "message": "Unknown card", "uid": uid})
            while await rfid_reader.read_uid() == (True, uid):
                await asyncio.sleep(0.2)  # Wait for the card to be removed
        else:
            last_uid = None
        await asyncio.sleep(0.2)