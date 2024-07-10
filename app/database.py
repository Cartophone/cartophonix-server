import httpx
import logging
from config.config import POCKETBASE_HOST, POCKETBASE_PORT

BASE_URL = f"http://{POCKETBASE_HOST}:{POCKETBASE_PORT}/api/collections/playlists/records"

def create_playlist_record(name, uri, image_path=None):
    try:
        data = {
            "name": name,
            "uri": uri
        }
        files = {}
        if image_path:
            files = {"image": open(image_path, "rb")}

        response = httpx.post(BASE_URL, data=data, files=files)
        response.raise_for_status()
        return response.json()['id']
    except Exception as e:
        logging.error(f"Error creating playlist record: {e}")
        raise

def get_playlist_by_id(playlist_id):
    try:
        response = httpx.get(f"{BASE_URL}/{playlist_id}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Error getting playlist by ID: {e}")
        raise

def update_playlist_record(playlist_id, updates):
    try:
        response = httpx.patch(f"{BASE_URL}/{playlist_id}", json=updates)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Error updating playlist record: {e}")
        raise

def delete_playlist_record(playlist_id):
    try:
        response = httpx.delete(f"{BASE_URL}/{playlist_id}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Error deleting playlist record: {e}")
        raise

def dissociate_card_from_playlist(playlist_id):
    try:
        updates = {"uid": None}
        response = update_playlist_record(playlist_id, updates)
        return response
    except Exception as e:
        logging.error(f"Error dissociating card from playlist: {e}")
        raise

def get_all_playlists():
    try:
        response = httpx.get(BASE_URL)
        response.raise_for_status()
        return response.json()['items']
    except Exception as e:
        logging.error(f"Error getting all playlists: {e}")
        raise

def main():
    pass

if __name__ == "__main__":
    main()