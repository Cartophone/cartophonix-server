import logging
import requests
from config.config import MUSIC_HOST, MUSIC_PORT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def launch_playlist(uri):
    try:
        response = requests.post(
            f"http://{MUSIC_HOST}:{MUSIC_PORT}/api/queue/items/add",
            params={
                'uris': uri,
                'playback': 'start',
                'clear': 'true'
            }
        )
        if response.status_code == 200:
            logger.info(f"Playlist launched: {uri}")
            return True
        else:
            logger.error(f"Failed to launch playlist: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Error launching playlist: {e}")
        return False

def check_alarms():
    # This function should be scheduled to run every minute
    from app.database import get_all_playlists
    playlists = get_all_playlists()
    for playlist in playlists:
        if playlist.activated and playlist.hour == get_current_hour():
            launch_playlist(playlist.uri)

def get_current_hour():
    from datetime import datetime
    return datetime.now().strftime("%H:%M")