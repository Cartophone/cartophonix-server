import logging
from pocketbase import PocketBase
from config.config import POCKETBASE_URL, POCKETBASE_PORT

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Ensure the URL includes the protocol
client = PocketBase(f"http://{POCKETBASE_URL}:{POCKETBASE_PORT}")

def register_card(uid, playlist, name, image):
    data = {
        "uid": uid,
        "playlist": playlist,
        "name": name,
        "image": image
    }
    logging.debug(f"Registering card with data: {data}")
    try:
        response = client.collection("cards").create(data)
        logging.debug(f"Response from PocketBase: {response}")
    except Exception as e:
        logging.error(f"Error registering card: {e}")
        raise

def get_card_by_uid(uid):
    response = client.collection("cards").get_list(1, 1, {"filter": f'uid="{uid}"'})
    if response.items:
        return response.items[0].playlist
    return None

def update_playlist(card_id, new_playlist, new_name, new_image):
    data = {
        "playlist": new_playlist,
        "name": new_name,
        "image": new_image
    }
    logging.debug(f"Updating card with data: {data}")
    try:
        response = client.collection("cards").update(card_id, data)
        logging.debug(f"Response from PocketBase: {response}")
    except Exception as e:
        logging.error(f"Error updating card: {e}")
        raise

def delete_card(card_id):
    try:
        client.collection("cards").delete(card_id)
        logging.debug(f"Deleted card with id: {card_id}")
    except Exception as e:
        logging.error(f"Error deleting card: {e}")
        raise

def create_alarm(hour, playlist):
    data = {
        "hour": hour,
        "playlist": playlist,
        "activated": True
    }
    logging.debug(f"Creating alarm with data: {data}")
    try:
        response = client.collection("alarms").create(data)
        logging.debug(f"Response from PocketBase: {response}")
    except Exception as e:
        logging.error(f"Error creating alarm: {e}")
        raise

def list_alarms():
    response = client.collection("alarms").get_list(1, 300)  # Adjust as necessary
    return [{"id": item.id, "hour": item.hour, "playlist": item.playlist, "activated": item.activated} for item in response.items]

def toggle_alarm(alarm_id):
    alarm = client.collection("alarms").get_one(alarm_id)
    new_state = not alarm.activated
    try:
        response = client.collection("alarms").update(alarm_id, {"activated": new_state})
        logging.debug(f"Toggled alarm with id: {alarm_id} to state: {new_state}")
    except Exception as e:
        logging.error(f"Error toggling alarm: {e}")
        raise

def edit_alarm(alarm_id, new_hour, new_playlist):
    data = {
        "hour": new_hour,
        "playlist": new_playlist
    }
    logging.debug(f"Editing alarm with data: {data}")
    try:
        response = client.collection("alarms").update(alarm_id, data)
        logging.debug(f"Response from PocketBase: {response}")
    except Exception as e:
        logging.error(f"Error editing alarm: {e}")
        raise

def get_activated_alarms():
    response = client.collection("alarms").get_list(1, 300, {"filter": "activated=True"})  # Adjust as necessary
    return [{"id": item.id, "hour": item.hour, "playlist": item.playlist} for item in response.items]