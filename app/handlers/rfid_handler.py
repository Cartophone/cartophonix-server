import time
import logging
from threading import Event, Thread
from pn532pi import Pn532Spi, Pn532, pn532
from app.database import get_card_by_uid
from app.handlers.alarms_handler import launch_playlist

class RFIDReader:
    def __init__(self):
        self.spi = Pn532Spi(Pn532Spi.SS0_GPIO8)
        self.nfc = Pn532(self.spi)
        self.nfc.begin()
        self.nfc.SAMConfig()
        logging.info("RFID reader initialized")
        self.stop_event = Event()

    def read_uid(self):
        success, uid = self.nfc.readPassiveTargetID(pn532.PN532_MIFARE_ISO14443A_106KBPS)
        if success:
            uid_string = ''.join('{:02x}'.format(i) for i in uid)
            return True, uid_string
        return False, None

rfid_reader = RFIDReader()

def wait_for_card(timeout=60):
    start_time = time.time()
    while (time.time() - start_time) < timeout:
        success, uid = rfid_reader.read_uid()
        if success:
            return uid
        time.sleep(0.2)
    return None

def read_mode():
    while not rfid_reader.stop_event.is_set():
        success, uid = rfid_reader.read_uid()
        if success:
            playlist = get_card_by_uid(uid)
            if playlist:
                launch_playlist(playlist['uri'])
                logging.info(f"UID {uid} detected, launching playlist: {playlist['name']}")
            else:
                logging.info(f"UID {uid} detected, but not registered")
        time.sleep(0.2)

def start_rfid_reading():
    rfid_reader.stop_event.clear()
    Thread(target=read_mode).start()
    logging.info("RFID reading started")

def stop_rfid_reading():
    rfid_reader.stop_event.set()
    logging.info("RFID reading stopped")