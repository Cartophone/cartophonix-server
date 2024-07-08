import logging
from pocketbase import PocketBase
from config.config import POCKETBASE_URL, POCKETBASE_PORT

client = PocketBase(f"http://{POCKETBASE_URL}:{POCKETBASE_PORT}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def register_card(uid, playlist, name, image):
    try:
        data = {
            "uid": uid,
            "playlist": playlist,
            "name": name,
            "image": image
        }
        client.collection("cards").create(data)
        logger.info(f"Card registered with UID: {uid}")
    except Exception as e:
        logger.error(f"Error registering card with UID {uid}: {e}")

def get_card_by_uid(uid):
    try:
        response = client.collection("cards").get_list(1, 1, {"filter": f'uid="{uid}"'})
        if response.items:
            return response.items[0]
        return None
    except Exception as e:
        logger.error(f"Error fetching card by UID {uid}: {e}")
        return None

def update_playlist(card_id, new_playlist):
    try:
        data = {
            "playlist": new_playlist
        }
        client.collection("cards").update(card_id, data)
        logger.info(f"Playlist updated for card ID: {card_id}")
    except Exception as e:
        logger.error(f"Error updating playlist for card ID {card_id}: {e}")

def get_all_alarms():
    try:
        response = client.collection("alarms").get_list(1, 300)  # Adjust as necessary
        return [{"id": item.id, "hour": item.hour, "playlist": item.playlist, "activated": item.activated} for item in response.items]
    except Exception as e:
        logger.error(f"Error fetching all alarms: {e}")
        return []

def create_alarm(hour, playlist):
    try:
        data = {
            "hour": hour,
            "playlist": playlist,
            "activated": True
        }
        client.collection("alarms").create(data)
        logger.info(f"Alarm created for hour: {hour} with playlist: {playlist}")
    except Exception as e:
        logger.error(f"Error creating alarm for hour {hour}: {e}")

def delete_alarm(alarm_id):
    try:
        client.collection("alarms").delete(alarm_id)
        logger.info(f"Alarm deleted with ID: {alarm_id}")
    except Exception as e:
        logger.error(f"Error deleting alarm with ID {alarm_id}: {e}")