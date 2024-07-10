from pocketbase import PocketBase
from pocketbase.models.utils import BaseModel
from config.config import POCKETBASE_URL, POCKETBASE_PORT
import logging

client = PocketBase(f"http://{POCKETBASE_URL}:{POCKETBASE_PORT}")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_playlist(name, uri, image=None):
    data = {
        "name": name,
        "uri": uri,
        "image": image,
        "uid": None,
        "hour": None,
        "activated": False
    }
    try:
        record = client.collection("playlists").create(data)
        return record
    except Exception as e:
        logger.error(f"Error creating playlist: {e}")
        return None

def update_playlist(id, name=None, uri=None, image=None):
    data = {}
    if name:
        data["name"] = name
    if uri:
        data["uri"] = uri
    if image:
        data["image"] = image
    try:
        record = client.collection("playlists").update(id, data)
        return record
    except Exception as e:
        logger.error(f"Error updating playlist: {e}")
        return None

def delete_playlist(id):
    try:
        client.collection("playlists").delete(id)
    except Exception as e:
        logger.error(f"Error deleting playlist: {e}")

def get_playlist_by_id(id):
    try:
        record = client.collection("playlists").get_one(id)
        return record
    except Exception as e:
        logger.error(f"Error fetching playlist: {e}")
        return None

def associate_card(id, uid):
    try:
        record = get_playlist_by_uid(uid)
        if record:
            return {"error": "Card already associated with another playlist"}
        record = client.collection("playlists").update(id, {"uid": uid})
        return record
    except Exception as e:
        logger.error(f"Error associating card: {e}")
        return None

def dissociate_card(id):
    try:
        record = client.collection("playlists").update(id, {"uid": None})
        return record
    except Exception as e:
        logger.error(f"Error dissociating card: {e}")
        return None

def get_playlist_by_uid(uid):
    try:
        response = client.collection("playlists").get_list(1, 1, {"filter": f'uid="{uid}"'})
        if response.items:
            return response.items[0]
        return None
    except Exception as e:
        logger.error(f"Error fetching playlist by UID: {e}")
        return None

def associate_alarm(id, hour):
    try:
        record = client.collection("playlists").update(id, {"hour": hour, "activated": True})
        return record
    except Exception as e:
        logger.error(f"Error associating alarm: {e}")
        return None

def toggle_alarm(id):
    try:
        record = get_playlist_by_id(id)
        if not record or not record.hour:
            return {"error": "No alarm set for this playlist"}
        new_status = not record.activated
        record = client.collection("playlists").update(id, {"activated": new_status})
        return record
    except Exception as e:
        logger.error(f"Error toggling alarm: {e}")
        return None

def edit_hour(id, hour):
    try:
        record = client.collection("playlists").update(id, {"hour": hour})
        return record
    except Exception as e:
        logger.error(f"Error editing hour: {e}")
        return None

def dissociate_alarm(id):
    try:
        record = client.collection("playlists").update(id, {"hour": None, "activated": False})
        return record
    except Exception as e:
        logger.error(f"Error dissociating alarm: {e}")
        return None

def get_all_playlists():
    try:
        response = client.collection("playlists").get_list(1, 100)  # Adjust as necessary
        return response.items
    except Exception as e:
        logger.error(f"Error fetching all playlists: {e}")
        return []