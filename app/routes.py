from flask import Blueprint, request, jsonify
from app.database import (
    register_playlist, get_playlist_by_id, update_playlist, delete_playlist,
    associate_card, dissociate_card, associate_alarm, toggle_alarm,
    edit_hour, dissociate_alarm
)
from app.rfid import RFIDReader
from app.utils import launch_playlist, check_alarms
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

main = Blueprint('main', __name__)
rfid_reader = RFIDReader()

@main.route('/')
def home():
    return "Cartophonix Backend is running!"

@main.route('/register_playlist', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    uri = data.get('uri')
    image = data.get('image')
    if not name or not uri:
        return jsonify({"error": "Name and URI are required"}), 400
    record = register_playlist(name, uri, image)
    if record:
        return jsonify({"status": "success", "id": record.id}), 201
    return jsonify({"error": "Failed to register playlist"}), 500

@main.route('/associate_card', methods=['POST'])
def associate():
    data = request.json
    playlist_id = data.get('playlist_id')
    if not playlist_id:
        return jsonify({"error": "Playlist ID is required"}), 400

    playlist = get_playlist_by_id(playlist_id)
    if not playlist:
        return jsonify({"error": "Playlist not found"}), 404

    if playlist.uid:
        return jsonify({"error": "This playlist already has a card associated. Use /dissociate_card first."}), 400

    logger.info("Waiting for RFID scan...")
    for _ in range(60):
        success, uid = rfid_reader.read_uid()
        if success:
            response = associate_card(playlist_id, uid)
            if "error" in response:
                return jsonify(response), 400
            return jsonify({"status": "success", "uid": uid}), 201
        time.sleep(1)
    return jsonify({"error": "Timeout waiting for card"}), 408

@main.route('/edit_playlist', methods=['POST'])
def edit():
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

@main.route('/delete_playlist', methods=['DELETE'])
def delete():
    data = request.json
    playlist_id = data.get('playlist_id')
    if not playlist_id:
        return jsonify({"error": "Playlist ID is required"}), 400
    delete_playlist(playlist_id)
    return jsonify({"status": "success"}), 200

@main.route('/dissociate_card', methods=['POST'])
def dissociate_card_route():
    data = request.json
    playlist_id = data.get('playlist_id')
    if not playlist_id:
        return jsonify({"error": "Playlist ID is required"}), 400
    response = dissociate_card(playlist_id)
    if "error" in response:
        return jsonify(response), 400
    return jsonify({"status": "success"}), 200

@main.route('/associate_alarm', methods=['POST'])
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

@main.route('/toggle_alarm', methods=['POST'])
def toggle_alarm_route():
    data = request.json
    playlist_id = data.get('playlist_id')
    if not playlist_id:
        return jsonify({"error": "Playlist ID is required"}), 400
    response = toggle_alarm(playlist_id)
    if "error" in response:
        return jsonify(response), 400
    return jsonify({"status": "success", "activated": response.activated}), 200

@main.route('/edit_hour', methods=['POST'])
def edit_hour_route():
    data = request.json
    playlist_id = data.get('playlist_id')
    hour = data.get('hour')
    if not playlist_id or not hour:
        return jsonify({"error": "Playlist ID and hour are required"}), 400
    record = edit_hour(playlist_id, hour)
    if record:
        return jsonify({"status": "success", "id": record.id}), 200
    return jsonify({"error": "Failed to edit hour"}), 500

@main.route('/dissociate_alarm', methods=['POST'])
def dissociate_alarm_route():
    data = request.json
    playlist_id = data.get('playlist_id')
    if not playlist_id:
        return jsonify({"error": "Playlist ID is required"}), 400
    record = dissociate_alarm(playlist_id)
    if record:
        return jsonify({"status": "success", "id": record.id}), 200
    return jsonify({"error": "Failed to dissociate alarm"}), 500