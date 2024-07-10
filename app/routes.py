from flask import request, jsonify
from app import app
from app.handlers.rfid_handler import stop_rfid_reading, start_rfid_reading, wait_for_card
from app.database import create_playlist_record, get_playlist_by_id, update_playlist_record, delete_playlist_record, dissociate_card_from_playlist
import logging

@app.route('/')
def home():
    return "Cartophonix API"

@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    data = request.get_json()
    name = data.get('name')
    uri = data.get('uri')
    image = data.get('image')
    
    try:
        playlist_id = create_playlist_record(name, uri, image)
        return jsonify({"status": "success", "id": playlist_id}), 201
    except Exception as e:
        logging.error(f"Error creating playlist: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/associate_card', methods=['POST'])
def associate_card():
    data = request.get_json()
    playlist_id = data.get('id')

    try:
        stop_rfid_reading()
        existing_playlist = get_playlist_by_id(playlist_id)
        if existing_playlist.get('uid'):
            return jsonify({"status": "error", "message": "This card is already registered, overwrite?"}), 409
        
        success, uid = wait_for_card()
        if success:
            updates = {"uid": uid}
            update_playlist_record(playlist_id, updates)
            return jsonify({"status": "success", "message": "Card associated", "uid": uid}), 200
        else:
            return jsonify({"status": "error", "message": "Timeout waiting for card"}), 408
    except Exception as e:
        logging.error(f"Error associating card: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        start_rfid_reading()

@app.route('/edit_playlist', methods=['PATCH'])
def edit_playlist():
    data = request.get_json()
    playlist_id = data.get('id')
    updates = {k: v for k, v in data.items() if k in ['name', 'uri', 'image']}

    try:
        update_playlist_record(playlist_id, updates)
        return jsonify({"status": "success", "message": "Playlist updated"}), 200
    except Exception as e:
        logging.error(f"Error editing playlist: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/delete_playlist', methods=['DELETE'])
def delete_playlist():
    playlist_id = request.get_json().get('id')

    try:
        delete_playlist_record(playlist_id)
        return jsonify({"status": "success", "message": "Playlist deleted"}), 200
    except Exception as e:
        logging.error(f"Error deleting playlist: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/dissociate_card', methods=['POST'])
def dissociate_card():
    playlist_id = request.get_json().get('id')

    try:
        dissociate_card_from_playlist(playlist_id)
        return jsonify({"status": "success", "message": "Card dissociated"}), 200
    except Exception as e:
        logging.error(f"Error dissociating card: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/associate_alarm', methods=['POST'])
def associate_alarm():
    data = request.get_json()
    playlist_id = data.get('id')
    hour = data.get('hour')

    try:
        updates = {"hour": hour, "activated": True}
        update_playlist_record(playlist_id, updates)
        return jsonify({"status": "success", "message": "Alarm associated"}), 200
    except Exception as e:
        logging.error(f"Error associating alarm: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/toggle_alarm', methods=['POST'])
def toggle_alarm():
    playlist_id = request.get_json().get('id')

    try:
        playlist = get_playlist_by_id(playlist_id)
        if not playlist.get('hour'):
            return jsonify({"status": "error", "message": "No alarm set yet for this playlist"}), 400

        updates = {"activated": not playlist.get('activated', False)}
        update_playlist_record(playlist_id, updates)
        return jsonify({"status": "success", "message": "Alarm toggled"}), 200
    except Exception as e:
        logging.error(f"Error toggling alarm: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/edit_hour', methods=['PATCH'])
def edit_hour():
    data = request.get_json()
    playlist_id = data.get('id')
    hour = data.get('hour')

    try:
        updates = {"hour": hour}
        update_playlist_record(playlist_id, updates)
        return jsonify({"status": "success", "message": "Hour updated"}), 200
    except Exception as e:
        logging.error(f"Error editing hour: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/dissociate_alarm', methods=['POST'])
def dissociate_alarm():
    playlist_id = request.get_json().get('id')

    try:
        updates = {"hour": None, "activated": False}
        update_playlist_record(playlist_id, updates)
        return jsonify({"status": "success", "message": "Alarm dissociated"}), 200
    except Exception as e:
        logging.error(f"Error dissociating alarm: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500