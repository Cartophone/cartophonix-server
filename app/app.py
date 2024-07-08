import asyncio
from quart import Quart, request, jsonify
from app.rfid import RFIDReader
from app.database import (
    register_card,
    get_card_by_uid,
    update_playlist,
    delete_card,
    create_alarm,
    list_alarms,
    toggle_alarm,
    edit_alarm,
    get_activated_alarms
)
from app.handlers.rfid_handler import handle_read
from app.handlers.alarm_handler import check_alarms
from app.handlers.bluetooth_handler import scan_bluetooth, connect_bluetooth
from config.config import MUSIC_HOST, MUSIC_PORT, SERVER_HOST, SERVER_PORT

app = Quart(__name__)
rfid_reader = RFIDReader()

# Initialize read mode
read_mode_active = True


@app.route('/')
async def home():
    return "Cartophonix API is running."


@app.route('/register', methods=['POST'])
async def register():
    global read_mode_active
    read_mode_active = False  # Pause read mode

    data = await request.get_json()
    playlist = data.get('playlist')
    name = data.get('name')
    image = data.get('image')  # This should be base64 encoded
    uid = await rfid_reader.read_uid()  # Wait for card scan

    existing_playlist = get_card_by_uid(uid)
    if existing_playlist:
        response = {
            "status": "exists",
            "message": "This card is already registered, overwrite?",
            "uid": uid,
            "playlist": existing_playlist
        }
    else:
        register_card(uid, playlist, name, image)
        response = {
            "status": "success",
            "message": "Card registered",
            "uid": uid,
            "playlist": playlist,
            "name": name
        }

    read_mode_active = True  # Resume read mode
    return jsonify(response)


@app.route('/register/overwrite', methods=['POST'])
async def register_overwrite():
    global read_mode_active
    read_mode_active = False  # Pause read mode

    data = await request.get_json()
    playlist = data.get('playlist')
    name = data.get('name')
    image = data.get('image')  # This should be base64 encoded
    uid = data.get('uid')

    update_playlist(uid, playlist, name, image)
    response = {
        "status": "success",
        "message": "Card updated",
        "uid": uid,
        "playlist": playlist,
        "name": name
    }

    read_mode_active = True  # Resume read mode
    return jsonify(response)


@app.route('/delete', methods=['POST'])
async def delete():
    global read_mode_active
    read_mode_active = False  # Pause read mode

    data = await request.get_json()
    card_id = data.get('card_id')

    delete_card(card_id)
    response = {
        "status": "success",
        "message": "Card deleted",
        "card_id": card_id
    }

    read_mode_active = True  # Resume read mode
    return jsonify(response)


@app.route('/alarm', methods=['POST'])
async def create_alarm():
    data = await request.get_json()
    hour = data.get('hour')
    playlist = data.get('playlist')

    create_alarm(hour, playlist)
    response = {
        "status": "success",
        "message": "Alarm created",
        "hour": hour,
        "playlist": playlist
    }
    return jsonify(response)


@app.route('/alarms', methods=['GET'])
async def list_alarms():
    alarms = list_alarms()
    response = {
        "status": "success",
        "alarms": alarms
    }
    return jsonify(response)


@app.route('/toggle_alarm', methods=['POST'])
async def toggle_alarm():
    data = await request.get_json()
    alarm_id = data.get('alarm_id')

    toggle_alarm(alarm_id)
    response = {
        "status": "success",
        "message": "Alarm toggled",
        "alarm_id": alarm_id
    }
    return jsonify(response)


@app.route('/edit_alarm', methods=['POST'])
async def edit_alarm():
    data = await request.get_json()
    alarm_id = data.get('alarm_id')
    new_hour = data.get('new_hour')
    new_playlist = data.get('new_playlist')

    edit_alarm(alarm_id, new_hour, new_playlist)
    response = {
        "status": "success",
        "message": "Alarm edited",
        "alarm_id": alarm_id,
        "new_hour": new_hour,
        "new_playlist": new_playlist
    }
    return jsonify(response)


@app.route('/bluetooth/scan', methods=['GET'])
async def bluetooth_scan():
    devices = await scan_bluetooth()
    return jsonify({"status": "success", "devices": devices})


@app.route('/bluetooth/connect', methods=['POST'])
async def bluetooth_connect():
    data = await request.get_json()
    mac_address = data.get('mac_address')
    await connect_bluetooth(mac_address)
    return jsonify({"status": "success", "message": f"Connected to {mac_address}"})


async def run_background_tasks():
    asyncio.create_task(handle_read(rfid_reader))
    asyncio.create_task(check_alarms())


if __name__ == "__main__":
    app.run(host=SERVER_HOST, port=SERVER_PORT)
    asyncio.run(run_background_tasks())