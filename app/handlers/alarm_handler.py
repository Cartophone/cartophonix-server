import asyncio
from datetime import datetime
from app.database import get_all_alarms
from config.config import MUSIC_HOST, MUSIC_PORT
import aiohttp

async def check_alarms():
    while True:
        now = datetime.now().strftime("%H:%M")
        alarms = get_all_alarms()
        for alarm in alarms:
            if alarm['hour'] == now and alarm['activated']:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"http://{MUSIC_HOST}:{MUSIC_PORT}/api/queue/items/add",
                        params={
                            'uris': alarm['playlist'],
                            'playback': 'start',
                            'clear': 'true'
                        }
                    ) as response:
                        if response.status == 200:
                            print(f"Alarm triggered and playlist {alarm['playlist']} launched.")
                        else:
                            print(f"Failed to launch playlist for alarm at {alarm['hour']}.")
        await asyncio.sleep(60)  # Check every minute