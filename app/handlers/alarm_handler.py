import asyncio
from datetime import datetime
import aiohttp
from app.database import get_activated_alarms
from config.config import MUSIC_HOST, MUSIC_PORT

async def check_alarms():
    while True:
        current_time = datetime.now().strftime('%H:%M')
        activated_alarms = get_activated_alarms(current_time)
        for alarm in activated_alarms:
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
                        print(f"Successfully launched playlist for alarm at {current_time}")
                    else:
                        print(f"Failed to launch playlist for alarm at {current_time}")
        await asyncio.sleep(60)  # Check every minute