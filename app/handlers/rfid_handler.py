import threading
import time
from pn532pi import Pn532Spi, Pn532, pn532
from app.database import get_card_by_uid
from config.config import MUSIC_HOST, MUSIC_PORT
import requests
import logging

class RFIDReader:
    def __init__(self):
        self.spi = Pn532Spi(Pn532Spi.SS0_GPIO8)
        self.nfc = Pn532(self.spi)
        self.nfc.begin()
        self.nfc.SAMConfig()
        print("RFID reader initialized")

    def read_uid(self):
        success, uid = self.nfc.readPassiveTargetID(pn532.PN532_MIFARE_ISO14443A_106KBPS)
        if success:
            uid_string = ''.join('{:02x}'.format(i) for i in uid)
            return True, uid_string
        return False, None

rfid_reader = RFIDReader()
reading_active = True

def read_rfid():
    global reading_active
    last_uid = None
    while reading_active:
        success, uid = rfid_reader.read_uid()
        if success and uid != last_uid:
            last_uid = uid
            playlist = get_card_by_uid(uid)
            if playlist:
                response = requests.post(
                    f"http://{MUSIC_HOST}:{MUSIC_PORT}/api/queue/items/add",
                    params={
                        'uris': playlist['uri'],
                        'playback': 'start',
                        'clear': 'true'
                    }
                )
                if response.status_code == 200:
                    logging.info(f"Playlist {playlist['name']} launched for card {uid}")
                else:
                    logging.error(f"Failed to launch playlist for card {uid}")
        elif not success:
            last_uid = None
        time.sleep(0.5)

def start_rfid_reading():
    global reading_active
    reading_active = True
    threading.Thread(target=read_rfid, daemon=True).start()

def stop_rfid_reading():
    global reading_active
    reading_active = False

def wait_for_card(timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        success, uid = rfid_reader.read_uid()
        if success:
            return True, uid
        time.sleep(0.2)
    return False, None

# Start RFID reading in the background by default
start_rfid_reading()