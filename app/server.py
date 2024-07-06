import asyncio
import websockets
from config.config import WEBSOCKET_HOST, WEBSOCKET_PORT
from app.handler import handle_client, handle_read, check_alarms
from app.rfid import RFIDReader

async def client_handler(ws, path, rfid_reader):
    await handle_client(ws, path, rfid_reader)

async def main():
    rfid_reader = RFIDReader()

    # Start the RFID reading task
    read_task = await handle_read(None, rfid_reader)

    # Start the alarm checking task
    alarm_task = asyncio.create_task(check_alarms())

    server = await websockets.serve(
        lambda ws, path: client_handler(ws, path, rfid_reader),
        WEBSOCKET_HOST, WEBSOCKET_PORT
    )
    print(f"WebSocket server started at ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}")

    await asyncio.gather(server.wait_closed(), read_task, alarm_task)

if __name__ == '__main__':
    asyncio.run(main())