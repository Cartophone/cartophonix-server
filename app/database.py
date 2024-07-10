import requests
import logging
import base64
from io import BytesIO
from PIL import Image
from config.config import POCKETBASE_HOST, POCKETBASE_PORT

base_url = f"http://{POCKETBASE_HOST}:{POCKETBASE_PORT}/api/collections/playlists/records"

def create_playlist_record(name, uri, image=None):
    try:
        data = {
            "name": name,
            "uri": uri
        }
        files = None

        if image:
            try:
                image_data = base64.b64decode(image)
                image_file = BytesIO(image_data)
                image_obj = Image.open(image_file)
                image_obj.verify()  # Check that it's a valid image
                image_file.seek(0)  # Reset the stream to the beginning
                files = {'image': ('image.jpg', image_file, 'image/jpeg')}
            except Exception as e:
                logging.error(f"Error processing image: {e}")
                raise

        response = requests.post(base_url, data=data, files=files)
        response.raise_for_status()
        return response.json()["id"]
    except requests.RequestException as e:
        logging.error(f"Error creating playlist record: {e}")
        raise

def get_playlist_by_id(playlist_id):
    try:
        url = f"{base_url}/{playlist_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error retrieving playlist by id: {e}")
        raise

def get_card_by_uid(uid):
    try:
        params = {"filter": f"uid={uid}"}
        response = requests.get(base_url, params=params)
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
        response = requests.get(base_url)
        response.raise_for_status()
        return response.json().get("items", [])
    except requests.RequestException as e:
        logging.error(f"Error retrieving all playlists: {e}")
        raise

def update_playlist_record(playlist_id, updates):
    try:
        url = f"{base_url}/{playlist_id}"
        response = requests.patch(url, json=updates)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error updating playlist record: {e}")
        raise

def delete_playlist_record(playlist_id):
    try:
        url = f"{base_url}/{playlist_id}"
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