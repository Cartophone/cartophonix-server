import logging
from pocketbase import PocketBase
from config.config import POCKETBASE_URL, POCKETBASE_PORT

client = PocketBase(f"http://{POCKETBASE_URL}:{POCKETBASE_PORT}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def register_playlist(name, uri, image=None):
    try:
        data = {
            "name": name,
            "uri": uri,
            "image": image,
            "hour": None,
            "activated": False,
            "uid": None
        }
        record = client.collection("playlists").create(data)
        logger.info(f"Playlist registered: {record.id}")
        return record
    except Exception as e:
        logger.error(f"Error registering playlist: {e}")
        return None

def get_playlist_by_id(playlist_id):
    try:
        record = client.collection("playlists").get_one(playlist_id)
        return record
    except Exception as e:
        logger.error(f"Error fetching playlist: {e}")
        return None

def update_playlist(playlist_id, name=None, uri=None, image=None):
    try:
        data = {}
        if name:
            data["name"] = name
        if uri:
            data["uri"] = uri
        if image:
            data["image"] = image
        record = client.collection("playlists").update(playlist_id, data)
        logger.info(f"Playlist updated: {record.id}")
        return record
    except Exception as e:
        logger.error(f"Error updating playlist: {e}")
        return None

def delete_playlist(playlist_id):
    try:
        client.collection("playlists").delete(playlist_id)
        logger.info(f"Playlist deleted: {playlist_id}")
    except Exception as e:
        logger.error(f"Error deleting playlist: {e}")

def associate_card(playlist_id, uid):
    try:
        playlist = get_playlist_by_id(playlist_id)
        if not playlist:
            return {"error": "Playlist not found"}

        if playlist.uid:
            return {"error": "This playlist already has a card associated"}

        # Check if the UID is already associated with another playlist
        response = client.collection("playlists").get_list(1, 1, {"filter": f'uid="{uid}"'})
        if response.items:
            return {"error": "This card is already associated with another playlist"}

        # Associate card
        playlist.uid = uid
        updated_playlist = client.collection("playlists").update(playlist_id, {"uid": uid})
        logger.info(f"Card {uid} associated with playlist {playlist_id}")
        return updated_playlist
    except Exception as e:
        logger.error(f"Error associating card: {e}")
        return {"error": str(e)}

def dissociate_card(playlist_id):
    try:
        playlist = get_playlist_by_id(playlist_id)
        if not playlist:
            return {"error": "Playlist not found"}
        
        playlist.uid = None
        updated_playlist = client.collection("playlists").update(playlist_id, {"uid": None})
        logger.info(f"Card dissociated from playlist {playlist_id}")
        return updated_playlist
    except Exception as e:
        logger.error(f"Error dissociating card: {e}")
        return {"error": str(e)}

def associate_alarm(playlist_id, hour):
    try:
        data = {
            "hour": hour,
            "activated": True
        }
        record = client.collection("playlists").update(playlist_id, data)
        logger.info(f"Alarm associated with playlist: {record.id}")
        return record
    except Exception as e:
        logger.error(f"Error associating alarm: {e}")
        return None

def toggle_alarm(playlist_id):
    try:
        playlist = get_playlist_by_id(playlist_id)
        if not playlist:
            return {"error": "Playlist not found"}
        
        if not playlist.hour:
            return {"error": "No alarm set for this playlist"}

        playlist.activated = not playlist.activated
        updated_playlist = client.collection("playlists").update(playlist_id, {"activated": playlist.activated})
        logger.info(f"Alarm toggled for playlist {playlist_id}")
        return updated_playlist
    except Exception as e:
        logger.error(f"Error toggling alarm: {e}")
        return {"error": str(e)}

def edit_hour(playlist_id, hour):
    try:
        record = client.collection("playlists").update(playlist_id, {"hour": hour})
        logger.info(f"Hour updated for playlist: {record.id}")
        return record
    except Exception as e:
        logger.error(f"Error updating hour: {e}")
        return None

def dissociate_alarm(playlist_id):
    try:
        data = {
            "hour": None,
            "activated": False
        }
        record = client.collection("playlists").update(playlist_id, data)
        logger.info(f"Alarm dissociated from playlist: {record.id}")
        return record
    except Exception as e:
        logger.error(f"Error dissociating alarm: {e}")
        return None