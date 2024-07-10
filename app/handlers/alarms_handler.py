import datetime
import logging
from app.database import get_all_playlists, update_playlist_record

def check_alarms():
    try:
        now = datetime.datetime.now().strftime("%H:%M")
        playlists = get_all_playlists()
        for playlist in playlists:
            if playlist.get('hour') == now and playlist.get('activated'):
                launch_playlist(playlist['uri'])
                logging.info(f"Alarm triggered for playlist {playlist['name']} at {now}")
    except Exception as e:
        logging.error(f"Error checking alarms: {e}")

def launch_playlist(uri):
    import requests
    from config.config import MUSIC_HOST, MUSIC_PORT

    try:
        response = requests.post(
            f"http://{MUSIC_HOST}:{MUSIC_PORT}/api/queue/items/add",
            params={
                'uris': uri,
                'playback': 'start',
                'clear': 'true'
            }
        )
        response.raise_for_status()
        return {"status": "success", "message": "Playlist launched successfully"}
    except requests.RequestException as e:
        logging.error(f"Error launching playlist: {e}")
        return {"status": "error", "message": "Failed to launch playlist"}