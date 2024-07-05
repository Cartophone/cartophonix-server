import json
import asyncio
import requests

response = requests.post(
    f"http://0.0.0.0:80/api/queue/items/add",
        params={
            'uris': "spotify:track:6BOgN046AFobs2sZV7YlRy",
            'playback': 'start',
            'clear': 'true'
            }
        )
