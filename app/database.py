from pocketbase import PocketBase
from pocketbase.models.utils import BaseModel
from config.config import POCKETBASE_URL

client = PocketBase(POCKETBASE_URL)

def register_card(uid, playlist):
    data = {
        "uid": uid,
        "playlist": playlist
    }
    client.collection("cards").create(data)

def get_card_by_uid(uid):
    response = client.collection("cards").get_list(1, 1, {"filter": f'uid="{uid}"'})
    if response.items:
        return response.items[0].playlist
    return None

def update_playlist(card_id, new_playlist):
    data = {
        "playlist": new_playlist
    }
    client.collection("cards").update(card_id, data)

def get_all_cards():
    response = client.collection("cards").get_list(1, 300)  # Adjust as necessary
    return [{"id": item.id, "uid": item.uid, "playlist": item.playlist} for item in response.items]
