from flask import Flask, request, jsonify
import logging
import threading
from config.config import SERVER_HOST, SERVER_PORT
from app.handlers.bluetooth_handler import scan_bluetooth_devices, trust_and_connect_device
from app.handlers.alarms_handler import check_alarms, launch_playlist
from app.handlers.rfid_handler import rfid_reader, stop_rfid_reading, start_rfid_reading, wait_for_card
from app.database import create_playlist_record, get_playlist_by_id, update_playlist_record, delete_playlist_record, dissociate_card_from_playlist, get_all_playlists

app = Flask(__name__)

@app.route("/")
def home():
    logging.info("Home endpoint hit")
    return jsonify({"status": "success", "message": "Cartophonix API"})

@app.route("/create_playlist", methods=["POST"])
def create_playlist():
    data = request.json
    name = data.get("name")
    uri = data.get("uri")
    image = data.get("image")
    
    try:
        playlist_id = create_playlist_record(name, uri, image)
        logging.info(f"Playlist {name} created with ID: {playlist_id}")
        return jsonify({"status": "success", "id": playlist_id})
    except Exception as e:
        logging.error(f"Error creating playlist: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/associate_card", methods=["POST"])
def associate_card():
    data = request.json
    playlist_id = data.get("id")
    
    try:
        playlist = get_playlist_by_id(playlist_id)
        stop_rfid_reading()
        uid = wait_for_card(timeout=60)
        
        if not uid:
            start_rfid_reading()
            return jsonify({"status": "error", "message": "No card detected within timeout"}), 408
        
        if playlist.get("uid") and playlist["uid"] != uid:
            start_rfid_reading()
            return jsonify({"status": "error", "message": "This card is already registered. Overwrite?"}), 409
        
        playlist_with_same_uid = [p for p in get_all_playlists() if p.get("uid") == uid]
        if playlist_with_same_uid and playlist_with_same_uid[0]["id"] != playlist_id:
            start_rfid_reading()
            return jsonify({"status": "error", "message": "A card cannot be associated with two playlists"}), 409
        
        update_playlist_record(playlist_id, {"uid": uid})
        logging.info(f"Card with UID {uid} associated with playlist ID: {playlist_id}")
        start_rfid_reading()
        return jsonify({"status": "success", "message": "Card associated", "uid": uid})
    except Exception as e:
        logging.error(f"Error associating card: {e}")
        start_rfid_reading()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/edit_playlist", methods=["POST"])
def edit_playlist():
    data = request.json
    playlist_id = data.get("id")
    updates = {k: v for k, v in data.items() if k in ["name", "uri", "image"]}

    try:
        update_playlist_record(playlist_id, updates)
        logging.info(f"Playlist {playlist_id} updated with {updates}")
        return jsonify({"status": "success", "message": "Playlist updated"})
    except Exception as e:
        logging.error(f"Error updating playlist: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/delete_playlist", methods=["POST"])
def delete_playlist():
    data = request.json
    playlist_id = data.get("id")

    try:
        delete_playlist_record(playlist_id)
        logging.info(f"Playlist {playlist_id} deleted")
        return jsonify({"status": "success", "message": "Playlist deleted"})
    except Exception as e:
        logging.error(f"Error deleting playlist: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/dissociate_card", methods=["POST"])
def dissociate_card():
    data = request.json
    playlist_id = data.get("id")

    try:
        dissociate_card_from_playlist(playlist_id)
        logging.info(f"Card dissociated from playlist {playlist_id}")
        return jsonify({"status": "success", "message": "Card dissociated"})
    except Exception as e:
        logging.error(f"Error dissociating card: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/associate_alarm", methods=["POST"])
def associate_alarm():
    data = request.json
    playlist_id = data.get("id")
    hour = data.get("hour")

    try:
        update_playlist_record(playlist_id, {"hour": hour, "activated": True})
        logging.info(f"Alarm associated with playlist {playlist_id} at {hour}")
        return jsonify({"status": "success", "message": "Alarm associated"})
    except Exception as e:
        logging.error(f"Error associating alarm: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/toggle_alarm", methods=["POST"])
def toggle_alarm():
    data = request.json
    playlist_id = data.get("id")

    try:
        playlist = get_playlist_by_id(playlist_id)
        if "hour" not in playlist:
            return jsonify({"status": "error", "message": "No alarm set yet for this playlist"}), 400

        activated = not playlist.get("activated", False)
        update_playlist_record(playlist_id, {"activated": activated})
        logging.info(f"Alarm toggled for playlist {playlist_id} to {activated}")
        return jsonify({"status": "success", "message": "Alarm toggled", "activated": activated})
    except Exception as e:
        logging.error(f"Error toggling alarm: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/edit_hour", methods=["POST"])
def edit_hour():
    data = request.json
    playlist_id = data.get("id")
    hour = data.get("hour")

    try:
        update_playlist_record(playlist_id, {"hour": hour})
        logging.info(f"Hour updated for playlist {playlist_id} to {hour}")
        return jsonify({"status": "success", "message": "Hour updated"})
    except Exception as e:
        logging.error(f"Error updating hour: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/dissociate_alarm", methods=["POST"])
def dissociate_alarm():
    data = request.json
    playlist_id = data.get("id")

    try:
        update_playlist_record(playlist_id, {"hour": None, "activated": None})
        logging.info(f"Alarm dissociated from playlist {playlist_id}")
        return jsonify({"status": "success", "message": "Alarm dissociated"})
    except Exception as e:
        logging.error(f"Error dissociating alarm: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from waitress import serve
    serve(app, host=SERVER_HOST, port=SERVER_PORT)