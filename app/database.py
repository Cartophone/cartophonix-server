from pocketbase import PocketBase
from pocketbase.models.utils import BaseModel
from config.config import POCKETBASE_URL

client = PocketBase(POCKETBASE_URL)

def register_card(uid, playlist, name, image=None):
    data = {
        "uid": uid,
        "playlist": playlist,
        "name": name,
    }
    if image:
        data["image"] = image
    client.collection("cards").create(data)

def get_card_by_uid(uid):
    response = client.collection("cards").get_list(1, 1, {"filter": f'uid="{uid}"'})
    if response.items:
        return response.items[0]
    return None

def update_playlist(card_id, new_playlist):
    data = {
        "playlist": new_playlist
    }
    client.collection("cards").update(card_id, data)

def get_all_cards():
    response = client.collection("cards").get_list(1, 300)  # Adjust as necessary
    return [{"id": item.id, "uid": item.uid, "playlist": item.playlist} for item in response.items]

def delete_card(card_id):
    client.collection("cards").delete(card_id)

# Alarms related functions

def create_alarm(hour, playlist):
    data = {
        "hour": hour,
        "activated": True,
        "playlist": playlist
    }
    client.collection("alarms").create(data)

def list_alarms():
    response = client.collection("alarms").get_list(1, 300)  # Adjust as necessary
    return [{"id": item.id, "hour": item.hour, "activated": item.activated, "playlist": item.playlist} for item in response.items]

def toggle_alarm(alarm_id):
    alarm = client.collection("alarms").get_one(alarm_id)
    new_status = not alarm.activated
    data = {
        "activated": new_status
    }
    client.collection("alarms").update(alarm_id, data)
    return new_status

def edit_alarm(alarm_id, new_hour, new_playlist):
    data = {
        "hour": new_hour,
        "playlist": new_playlist
    }
    client.collection("alarms").update(alarm_id, data)

def delete_alarm(alarm_id):
    client.collection("alarms").delete(alarm_id)