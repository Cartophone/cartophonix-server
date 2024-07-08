import asyncio
import aiohttp
from app.database import get_card_by_uid
from config.config import MUSIC_HOST, MUSIC_PORT

async def handle_read(rfid_reader):
    while True:
        success, uid = rfid_reader.read_uid()
        if success:
            playlist = get_card_by_uid(uid)
            if playlist:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"http://{MUSIC_HOST}:{MUSIC_PORT}/api/queue/items/add",
                        params={
                            'uris': playlist,
                            'playback': 'start',
                            'clear': 'true'
                        }
                    ) as response:
                        if response.status == 200:
                            print(f"Successfully launched playlist for UID: {uid}")
                        else:
                            print(f"Failed to launch playlist for UID: {uid}")
        await asyncio.sleep(0.2)