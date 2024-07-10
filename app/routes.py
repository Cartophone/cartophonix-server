import os
import base64
import io
import time
from PIL import Image
from flask import Flask, request, jsonify
from config.config import POCKETBASE_HOST, POCKETBASE_PORT, SERVER_HOST, SERVER_PORT, MUSIC_HOST, MUSIC_PORT
from app.rfid import RFIDReader
from app.database import create_playlist_record, get_playlist_by_id, update_playlist_record, delete_playlist_record, dissociate_card_from_playlist
import logging

app = Flask(__name__)
rfid_reader = RFIDReader()

logging.basicConfig(level=logging.INFO)

@app.route('/')
def home():
    logging.info("Home endpoint hit")
    return "Welcome to the Cartophonix Server"

@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    try:
        data = request.json
        name = data['name']
        uri = data['uri']
        image_base64 = data.get('image')

        if image_base64:
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data))
            image_filename = f"{name}.png"
            image_path = os.path.join('/tmp', image_filename)
            image.save(image_path)
        else:
            image_path = None

        playlist_id = create_playlist_record(name, uri, image_path)
        
        if image_path:
            os.remove(image_path)

        response = {"status": "success", "id": playlist_id}
        logging.info(f"Created playlist: {response}")
        return jsonify(response)
    except Exception as e:
        logging.error(f"Error in create_playlist endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/associate_card', methods=['POST'])
def associate_card():
    try:
        data = request.json
        playlist_id = data['id']
        timeout = 60  # seconds

        logging.info(f"Associating card with playlist ID: {playlist_id}")
        start_time = time.time()
        while time.time() - start_time < timeout:
            success, uid = rfid_reader.read_uid()
            if success:
                playlist = get_playlist_by_id(playlist_id)
                if playlist and playlist.get('uid') and playlist['uid'] != uid:
                    response = {"status": "error", "message": "Card already associated with another playlist"}
                elif playlist and playlist.get('uid') == uid:
                    response = {"status": "error", "message": "This card is already registered, overwrite?"}
                else:
                    update_playlist_record(playlist_id, {"uid": uid})
                    response = {"status": "success", "message": "Card associated", "uid": uid}
                logging.info(f"Associate card response: {response}")
                return jsonify(response)
            time.sleep(0.2)
        
        response = {"status": "error", "message": "Timeout waiting for card"}
        logging.error(response)
        return jsonify(response)
    except Exception as e:
        logging.error(f"Error in associate_card endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/edit_playlist', methods=['POST'])
def edit_playlist():
    try:
        data = request.json
        playlist_id = data['id']
        name = data.get('name')
        uri = data.get('uri')
        image_base64 = data.get('image')

        updates = {}
        if name:
            updates['name'] = name
        if uri:
            updates['uri'] = uri
        if image_base64:
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data))
            image_filename = f"{playlist_id}.png"
            image_path = os.path.join('/tmp', image_filename)
            image.save(image_path)
            updates['image'] = image_path

        update_playlist_record(playlist_id, updates)

        if image_base64:
            os.remove(image_path)

        response = {"status": "success", "id": playlist_id}
        logging.info(f"Edited playlist: {response}")
        return jsonify(response)
    except Exception as e:
        logging.error(f"Error in edit_playlist endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/delete_playlist', methods=['POST'])
def delete_playlist():
    try:
        data = request.json
        playlist_id = data['id']
        delete_playlist_record(playlist_id)
        response = {"status": "success", "message": "Playlist deleted"}
        logging.info(response)
        return jsonify(response)
    except Exception as e:
        logging.error(f"Error in delete_playlist endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/dissociate_card', methods=['POST'])
def dissociate_card():
    try:
        data = request.json
        playlist_id = data['id']
        dissociate_card_from_playlist(playlist_id)
        response = {"status": "success", "message": "Card dissociated"}
        logging.info(response)
        return jsonify(response)
    except Exception as e:
        logging.error(f"Error in dissociate_card endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/associate_alarm', methods=['POST'])
def associate_alarm():
    try:
        data = request.json
        playlist_id = data['id']
        hour = data['hour']
        update_playlist_record(playlist_id, {"hour": hour, "activated": True})
        response = {"status": "success", "message": "Alarm associated"}
        logging.info(response)
        return jsonify(response)
    except Exception as e:
        logging.error(f"Error in associate_alarm endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/toggle_alarm', methods=['POST'])
def toggle_alarm():
    try:
        data = request.json
        playlist_id = data['id']
        playlist = get_playlist_by_id(playlist_id)
        if 'hour' in playlist and 'activated' in playlist:
            new_status = not playlist['activated']
            update_playlist_record(playlist_id, {"activated": new_status})
            response = {"status": "success", "message": f"Alarm {'activated' if new_status else 'deactivated'}"}
        else:
            response = {"status": "error", "message": "No alarm set for this playlist"}
        logging.info(response)
        return jsonify(response)
    except Exception as e:
        logging.error(f"Error in toggle_alarm endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/edit_hour', methods=['POST'])
def edit_hour():
    try:
        data = request.json
        playlist_id = data['id']
        hour = data['hour']
        update_playlist_record(playlist_id, {"hour": hour})
        response = {"status": "success", "message": "Alarm hour updated"}
        logging.info(response)
        return jsonify(response)
    except Exception as e:
        logging.error(f"Error in edit_hour endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/dissociate_alarm', methods=['POST'])
def dissociate_alarm():
    try:
        data = request.json
        playlist_id = data['id']
        update_playlist_record(playlist_id, {"hour": None, "activated": False})
        response = {"status": "success", "message": "Alarm dissociated"}
        logging.info(response)
        return jsonify(response)
    except Exception as e:
        logging.error(f"Error in dissociate_alarm endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(host=SERVER_HOST, port=SERVER_PORT)