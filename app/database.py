import requests
import logging
from config.config import POCKETBASE_HOST, POCKETBASE_PORT
from PIL import Image
import base64
import io

def create_playlist_record(name, uri, image=None):
    try:
        url = f"http://{POCKETBASE_HOST}:{POCKETBASE_PORT}/api/collections/playlists/records"
        data = {
            "name": name,
            "uri": uri
        }
        
        files = None
        if image:
            image_data = base64.b64decode(image)
            image_file = io.BytesIO(image_data)
            img = Image.open(image_file)
            img_format = img.format

            if img_format not in ['JPEG', 'PNG']:
                raise ValueError("Unsupported image format")

            files = {
                "image": ("image." + img_format.lower(), image_data, f"image/{img_format.lower()}")
            }

        response = requests.post(url, data=data, files=files)
        response.raise_for_status()
        return response.json()["id"]
    except requests.RequestException as e:
        logging.error(f"Error creating playlist record: {e}")
        raise
    except Exception as e:
        logging.error(f"General error creating playlist record: {e}")
        raise

def get_playlist_by_id(playlist_id):
    try:
        url = f"http://{POCKETBASE_HOST}:{POCKETBASE_PORT}/api/collections/playlists/records/{playlist_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error retrieving playlist by id: {e}")
        raise

def get_card_by_uid(uid):
    try:
        url = f"http://{POCKETBASE_HOST}:{POCKETBASE_PORT}/api/collections/playlists/records"
        params = {"filter": f"uid={uid}"}
        response = requests.get(url, params=params)
        response.raise_for_status()
        records = response.json().get("items", [])
        if records:
            return records[0]
        return None
    except requests.RequestException as e:
        logging.error(f"Error retrieving card by uid: {e}")
        raise

def get_all_playlists():
    try:
        url = f"http://{POCKETBASE_HOST}:{POCKETBASE_PORT}/api/collections/playlists/records"
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get("items", [])
    except requests.RequestException as e:
        logging.error(f"Error retrieving all playlists: {e}")
        raise

def update_playlist_record(playlist_id, updates):
    try:
        url = f"http://{POCKETBASE_HOST}:{POCKETBASE_PORT}/api/collections/playlists/records/{playlist_id}"
        response = requests.patch(url, json=updates)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error updating playlist record: {e}")
        raise

def delete_playlist_record(playlist_id):
    try:
        url = f"http://{POCKETBASE_HOST}:{POCKETBASE_PORT}/api/collections/playlists/records/{playlist_id}"
        response = requests.delete(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error deleting playlist record: {e}")
        raise

def dissociate_card_from_playlist(playlist_id):
    try:
        updates = {"uid": None}
        return update_playlist_record(playlist_id, updates)
    except Exception as e:
        logging.error(f"Error dissociating card from playlist: {e}")
        raise