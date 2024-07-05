import asyncio
import websockets
from config.config import WEBSOCKET_HOST, WEBSOCKET_PORT
from app.handler import handle_client, handle_read
from app.rfid import RFIDReader

async def client_handler(ws, path, rfid_reader):
    await handle_client(ws, path, rfid_reader)

async def main():
    rfid_reader = RFIDReader()

    # Start the RFID reading task
    read_task = await handle_read(None, rfid_reader)

    server = await websockets.serve(
        lambda ws, path: client_handler(ws, path, rfid_reader),
        WEBSOCKET_HOST, WEBSOCKET_PORT
    )
    print(f"WebSocket server started at ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}")

    while True:
        await asyncio.sleep(1)  # Keep the server running

if __name__ == '__main__':
    asyncio.run(main())