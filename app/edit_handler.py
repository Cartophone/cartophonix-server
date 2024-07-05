import json
from app.database import get_all_cards

async def handle_edit(websocket):
    try:
        async for message in websocket:
            data = json.loads(message)
            action = data.get("action")
            if action == "edit":
                cards = get_all_cards()
                response = {"status": "success", "cards": cards}
                await websocket.send(json.dumps(response))
                break
    except asyncio.CancelledError:
        pass