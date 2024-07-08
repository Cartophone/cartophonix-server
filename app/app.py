import asyncio
import logging
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

logging.basicConfig(level=logging.DEBUG)

app = Quart(__name__)
rfid_reader = RFIDReader()

# Initialize read mode
read_mode_active = True

@app.route('/')
async def home():
    logging.info("Home endpoint hit")
    return "Cartophonix API is running."

@app.route('/register', methods=['POST'])
async def register():
    logging.info("Register endpoint hit")
    global read_mode_active
    read_mode_active = False  # Pause read mode

    try:
        data = await request.get_json()
        logging.info(f"Received data: {data}")
        playlist = data.get('playlist')
        name = data.get('name')
        image = data.get('image')  # This should be base64 encoded
        uid = await rfid_reader.read_uid()  # Wait for card scan
        logging.info(f"Scanned UID: {uid}")

        existing_playlist = get_card_by_uid(uid)
        logging.info(f"Existing playlist: {existing_playlist}")

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

        logging.info(f"Response: {response}")
        read_mode_active = True  # Resume read mode
        return jsonify(response)

    except Exception as e:
        logging.error(f"Error in register endpoint: {e}")
        read_mode_active = True  # Resume read mode in case of error
        return jsonify({"status": "error", "message": str(e)})

@app.route('/register/overwrite', methods=['POST'])
async def register_overwrite():
    logging.info("Register overwrite endpoint hit")
    global read_mode_active
    read_mode_active = False  # Pause read mode

    try:
        data = await request.get_json()
        logging.info(f"Received data for overwrite: {data}")
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

        logging.info(f"Response: {response}")
        read_mode_active = True  # Resume read mode
        return jsonify(response)

    except Exception as e:
        logging.error(f"Error in register overwrite endpoint: {e}")
        read_mode_active = True  # Resume read mode in case of error
        return jsonify({"status": "error", "message": str(e)})

@app.route('/delete', methods=['POST'])
async def delete():
    logging.info("Delete endpoint hit")
    global read_mode_active
    read_mode_active = False  # Pause read mode

    try:
        data = await request.get_json()
        logging.info(f"Received data for delete: {data}")
        card_id = data.get('card_id')

        delete_card(card_id)
        response = {
            "status": "success",
            "message": "Card deleted",
            "card_id": card_id
        }

        logging.info(f"Response: {response}")
        read_mode_active = True  # Resume read mode
        return jsonify(response)

    except Exception as e:
        logging.error(f"Error in delete endpoint: {e}")
        read_mode_active = True  # Resume read mode in case of error
        return jsonify({"status": "error", "message": str(e)})

@app.route('/alarm', methods=['POST'])
async def create_alarm():
    logging.info("Create alarm endpoint hit")
    try:
        data = await request.get_json()
        logging.info(f"Received data for alarm: {data}")
        hour = data.get('hour')
        playlist = data.get('playlist')

        create_alarm(hour, playlist)
        response = {
            "status": "success",
            "message": "Alarm created",
            "hour": hour,
            "playlist": playlist
        }

        logging.info(f"Response: {response}")
        return jsonify(response)

    except Exception as e:
        logging.error(f"Error in create alarm endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/alarms', methods=['GET'])
async def list_alarms():
    logging.info("List alarms endpoint hit")
    try:
        alarms = list_alarms()
        response = {
            "status": "success",
            "alarms": alarms
        }

        logging.info(f"Response: {response}")
        return jsonify(response)

    except Exception as e:
        logging.error(f"Error in list alarms endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/toggle_alarm', methods=['POST'])
async def toggle_alarm():
    logging.info("Toggle alarm endpoint hit")
    try:
        data = await request.get_json()
        logging.info(f"Received data for toggle alarm: {data}")
        alarm_id = data.get('alarm_id')

        toggle_alarm(alarm_id)
        response = {
            "status": "success",
            "message": "Alarm toggled",
            "alarm_id": alarm_id
        }

        logging.info(f"Response: {response}")
        return jsonify(response)

    except Exception as e:
        logging.error(f"Error in toggle alarm endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/edit_alarm', methods=['POST'])
async def edit_alarm():
    logging.info("Edit alarm endpoint hit")
    try:
        data = await request.get_json()
        logging.info(f"Received data for edit alarm: {data}")
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

        logging.info(f"Response: {response}")
        return jsonify(response)

    except Exception as e:
        logging.error(f"Error in edit alarm endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/bluetooth/scan', methods=['GET'])
async def bluetooth_scan():
    logging.info("Bluetooth scan endpoint hit")
    try:
        devices = await scan_bluetooth()
        response = {"status": "success", "devices": devices}
        logging.info(f"Response: {response}")
        return jsonify(response)

    except Exception as e:
        logging.error(f"Error in bluetooth scan endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/bluetooth/connect', methods=['POST'])
async def bluetooth_connect():
    logging.info("Bluetooth connect endpoint hit")
    try:
        data = await request.get_json()
        logging.info(f"Received data for bluetooth connect: {data}")
        mac_address = data.get('mac_address')
        await connect_bluetooth(mac_address)
        response = {"status": "success", "message": f"Connected to {mac_address}"}
        logging.info(f"Response: {response}")
        return jsonify(response)

    except Exception as e:
        logging.error(f"Error in bluetooth connect endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)})

async def run_background_tasks():
    asyncio.create_task(handle_read(rfid_reader))
    asyncio.create_task(check_alarms())

if __name__ == "__main__":
    app.run(host=SERVER_HOST, port=SERVER_PORT)
    asyncio.run(run_background_tasks())