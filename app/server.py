import asyncio
import websockets
from config.config import WEBSOCKET_HOST, WEBSOCKET_PORT
from app.handler import handle_client
from app.rfid import RFIDReader

async def main():
    rfid_reader = RFIDReader()
    
    async def client_handler(ws, path):
        await handle_client(ws, path, rfid_reader)

    server = await websockets.serve(client_handler, WEBSOCKET_HOST, WEBSOCKET_PORT)
    print(f"WebSocket server started at ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}")

    while True:
        await asyncio.sleep(1)  # Keep the server running

if __name__ == '__main__':
    asyncio.run(main())