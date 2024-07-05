import asyncio
import websockets
import json
from config.config import WEBSOCKET_HOST, WEBSOCKET_PORT
from app.handlers import handle_client

async def main():
    server = await websockets.serve(handle_client, WEBSOCKET_HOST, WEBSOCKET_PORT)
    print("WebSocket server started")
    await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())
