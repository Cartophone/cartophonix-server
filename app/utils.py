import json

async def log_and_send(websocket, message, to_websocket=True):
    print(f"Log: {json.dumps(message)}")
    if to_websocket and websocket:
        try:
            await websocket.send(json.dumps(message))
            print(f"Sent to WebSocket: {json.dumps(message)}")
        except Exception as e:
            print(f"Failed to send to WebSocket: {e}")