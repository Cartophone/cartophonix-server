import asyncio
import time
import requests
from app.database import list_alarms
from config.config import MUSIC_HOST, MUSIC_PORT
from app.utils import log_and_send

async def check_alarms(websocket):
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
                    triggered_response = {"status": "info", "message": f"Alarm triggered: {alarm['playlist']}"}
                    await log_and_send(websocket, triggered_response)
        await asyncio.sleep(60)