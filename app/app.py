import logging
from quart import Quart, request, jsonify
from app.handlers.rfid_handler import rfid_reader
from app.database import register_card, get_card_by_uid, update_playlist, delete_card, create_alarm, list_alarms, toggle_alarm, edit_alarm, get_activated_alarms
from app.bluetooth_handler import scan_bluetooth_devices, trust_and_connect_device

app = Quart(__name__)
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
async def home():
    logging.info("Home endpoint hit")
    return jsonify({"status": "success", "message": "Cartophonix API is running."})

@app.route('/register', methods=['POST'])
async def register():
    logging.info("Register endpoint hit")
    data = await request.get_json()
    logging.info(f"Received data: {data}")
    try:
        uid = await rfid_reader.read_uid()  # Wait for card scan
        logging.info(f"Scanned UID: {uid}")
        existing_playlist = get_card_by_uid(uid)
        if existing_playlist:
            logging.info(f"Card with UID {uid} already exists")
            return jsonify({"status": "error", "message": "Card already exists. Overwrite?", "uid": uid}), 409
        register_card(uid, data['playlist'], data['name'], data.get('image', None))
        return jsonify({"status": "success", "message": "Card registered", "uid": uid}), 201
    except Exception as e:
        logging.error(f"Error in register endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/register/overwrite', methods=['POST'])
async def register_overwrite():
    logging.info("Register overwrite endpoint hit")
    data = await request.get_json()
    logging.info(f"Received data: {data}")
    try:
        uid = await rfid_reader.read_uid()  # Wait for card scan
        logging.info(f"Scanned UID: {uid}")
        existing_card = get_card_by_uid(uid)
        if existing_card:
            update_playlist(existing_card['id'], data['playlist'], data['name'], data.get('image', None))
            return jsonify({"status": "success", "message": "Card updated", "uid": uid}), 200
        return jsonify({"status": "error", "message": "Card not found"}), 404
    except Exception as e:
        logging.error(f"Error in register overwrite endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/delete', methods=['POST'])
async def delete():
    logging.info("Delete endpoint hit")
    data = await request.get_json()
    logging.info(f"Received data: {data}")
    try:
        delete_card(data['id'])
        return jsonify({"status": "success", "message": "Card deleted"}), 200
    except Exception as e:
        logging.error(f"Error in delete endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/alarm', methods=['POST'])
async def create_alarm_endpoint():
    logging.info("Create alarm endpoint hit")
    data = await request.get_json()
    logging.info(f"Received data: {data}")
    try:
        create_alarm(data['hour'], data['playlist'])
        return jsonify({"status": "success", "message": "Alarm created"}), 201
    except Exception as e:
        logging.error(f"Error in create alarm endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/alarms', methods=['GET'])
async def list_alarms_endpoint():
    logging.info("List alarms endpoint hit")
    try:
        alarms = list_alarms()
        return jsonify({"status": "success", "alarms": alarms}), 200
    except Exception as e:
        logging.error(f"Error in list alarms endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/toggle_alarm', methods=['POST'])
async def toggle_alarm_endpoint():
    logging.info("Toggle alarm endpoint hit")
    data = await request.get_json()
    logging.info(f"Received data: {data}")
    try:
        toggle_alarm(data['id'])
        return jsonify({"status": "success", "message": "Alarm toggled"}), 200
    except Exception as e:
        logging.error(f"Error in toggle alarm endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/edit_alarm', methods=['POST'])
async def edit_alarm_endpoint():
    logging.info("Edit alarm endpoint hit")
    data = await request.get_json()
    logging.info(f"Received data: {data}")
    try:
        edit_alarm(data['id'], data['hour'], data['playlist'])
        return jsonify({"status": "success", "message": "Alarm edited"}), 200
    except Exception as e:
        logging.error(f"Error in edit alarm endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/bluetooth/scan', methods=['GET'])
async def bluetooth_scan():
    logging.info("Bluetooth scan endpoint hit")
    try:
        devices = await scan_bluetooth_devices()
        return jsonify({"status": "success", "devices": devices}), 200
    except Exception as e:
        logging.error(f"Error in bluetooth scan endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/bluetooth/connect', methods=['POST'])
async def bluetooth_connect():
    logging.info("Bluetooth connect endpoint hit")
    data = await request.get_json()
    logging.info(f"Received data: {data}")
    try:
        await trust_and_connect_device(data['mac_address'])
        return jsonify({"status": "success", "message": f"Connected to {data['mac_address']}"}), 200
    except Exception as e:
        logging.error(f"Error in bluetooth connect endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.before_serving
async def start_read_mode():
    logging.info("Starting read mode")
    await read_rfid_loop()

async def read_rfid_loop():
    logging.info("Read mode active")
    while True:
        uid = await rfid_reader.read_uid()
        if uid:
            logging.info(f"UID read: {uid}")
            playlist = get_card_by_uid(uid)
            if playlist:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"http://{MUSIC_HOST}:{MUSIC_PORT}/api/queue/items/add",
                        params={
                            'uris': playlist,
                            'playback': 'start',
                            'clear': 'true'
                        }
                    ) as response:
                        if response.status == 200:
                            logging.info(f"Playlist launched for UID: {uid}")
                        else:
                            logging.error(f"Failed to launch playlist for UID: {uid}")
        await asyncio.sleep(0.2)  # Adjust the sleep time as needed to avoid excessive polling

if __name__ == "__main__":
    app.run(host=SERVER_HOST, port=SERVER_PORT)