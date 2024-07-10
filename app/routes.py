from flask import Flask, request, jsonify
from app.database import *
from app.rfid import RFIDReader
import requests
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

rfid_reader = RFIDReader()

@app.route('/')
def home():
    return jsonify({"status": "server running"}), 200

@app.route('/create_playlist', methods=['POST'])
def create_playlist_route():
    data = request.json
    name = data.get('name')
    uri = data.get('uri')
    image = data.get('image')
    if not name or not uri:
        return jsonify({"error": "Name and URI are required"}), 400
    playlist = create_playlist(name, uri, image)
    if playlist:
        return jsonify({"status": "success", "id": playlist.id}), 200
    return jsonify({"error": "Failed to register playlist"}), 500

@app.route('/associate_card', methods=['POST'])
def associate_card_route():
    data = request.json
    playlist_id = data.get('playlist_id')
    if not playlist_id:
        return jsonify({"error": "Playlist ID is required"}), 400
    existing_playlist = get_playlist_by_id(playlist_id)
    if not existing_playlist:
        return jsonify({"error": "Playlist not found"}), 404
    if existing_playlist.uid:
        return jsonify({"error": "Card already associated. Use overwrite endpoint"}), 400
    
    logger.info("Waiting for card scan...")
    success, uid = rfid_reader.read_uid()
    if success:
        return jsonify({"status": "success", "message": "Card read successfully", "uid": uid}), 200
    return jsonify({"error": "Timeout waiting for card scan"}), 408

@app.route('/overwrite_card', methods=['POST'])
def overwrite_card_route():
    data = request.json
    playlist_id = data.get('playlist_id')
    uid = data.get('uid')
    if not playlist_id or not uid:
        return jsonify({"error": "Playlist ID and UID are required"}), 400
    record = associate_card(playlist_id, uid)
    if "error" in record:
        return jsonify(record), 400
    return jsonify({"status": "success", "id": record.id}), 200

@app.route('/edit_playlist', methods=['POST'])
def edit_playlist_route():
    data = request.json
    playlist_id = data.get('playlist_id')
    name = data.get('name')
    uri = data.get('uri')
    image = data.get('image')
    if not playlist_id:
        return jsonify({"error": "Playlist ID is required"}), 400
    updated_playlist = update_playlist(playlist_id, name, uri, image)
    if updated_playlist:
        return jsonify({"status": "success", "id": updated_playlist.id}), 200
    return jsonify({"error": "Failed to update playlist"}), 500

@app.route('/delete_playlist', methods=['DELETE'])
def delete_playlist_route():
    data = request.json
    playlist_id = data.get('playlist_id')
    if not playlist_id:
        return jsonify({"error": "Playlist ID is required"}), 400
    delete_playlist(playlist_id)
    return jsonify({"status": "success"}), 200

@app.route('/dissociate_card', methods=['POST'])
def dissociate_card_route():
    data = request.json
    playlist_id = data.get('playlist_id')
    if not playlist_id:
        return jsonify({"error": "Playlist ID is required"}), 400
    response = dissociate_card(playlist_id)
    if "error" in response:
        return jsonify(response), 400
    return jsonify({"status": "success"}), 200

@app.route('/associate_alarm', methods=['POST'])
def associate_alarm_route():
    data = request.json
    playlist_id = data.get('playlist_id')
    hour = data.get('hour')
    if not playlist_id or not hour:
        return jsonify({"error": "Playlist ID and hour are required"}), 400
    record = associate_alarm(playlist_id, hour)
    if record:
        return jsonify({"status": "success", "id": record.id}), 200
    return jsonify({"error": "Failed to associate alarm"}), 500

@app.route('/toggle_alarm', methods=['POST'])
def toggle_alarm_route():
    data = request.json
    playlist_id = data.get('playlist_id')
    if not playlist_id:
        return jsonify({"error": "Playlist ID is required"}), 400
    response = toggle_alarm(playlist_id)
    if "error" in response:
        return jsonify(response), 400
    return jsonify({"status": "success"}), 200

@app.route('/edit_hour', methods=['POST'])
def edit_hour_route():
    data = request.json
    playlist_id = data.get('playlist_id')
    hour = data.get('hour')
    if not playlist_id or not hour:
        return jsonify({"error": "Playlist ID and hour are required"}), 400
    updated_playlist = edit_hour(playlist_id, hour)
    if updated_playlist:
        return jsonify({"status": "success", "id": updated_playlist.id}), 200
    return jsonify({"error": "Failed to edit hour"}), 500

@app.route('/dissociate_alarm', methods=['POST'])
def dissociate_alarm_route():
    data = request.json
    playlist_id = data.get('playlist_id')
    if not playlist_id:
        return jsonify({"error": "Playlist ID is required"}), 400
    updated_playlist = dissociate_alarm(playlist_id)
    if updated_playlist:
        return jsonify({"status": "success", "id": updated_playlist.id}), 200
    return jsonify({"error": "Failed to dissociate alarm"}), 500

@app.route('/scan_bluetooth', methods=['GET'])
def scan_bluetooth_route():
    devices = scan_bluetooth_devices()
    if devices:
        return jsonify({"status": "success", "devices": devices}), 200
    return jsonify({"error": "Failed to scan for Bluetooth devices"}), 500

@app.route('/connect_bluetooth', methods=['POST'])
def connect_bluetooth_route():
    data = request.json
    mac_address = data.get('mac_address')
    if not mac_address:
        return jsonify({"error": "MAC address is required"}), 400
    result = trust_and_connect_device(mac_address)
    if result:
        return jsonify({"status": "success"}), 200
    return jsonify({"error": "Failed to connect to Bluetooth device"}), 500

if __name__ == "__main__":
    app.run(host=SERVER_HOST, port=SERVER_PORT)