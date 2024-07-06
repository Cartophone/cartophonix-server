import time
from pn532pi import Pn532I2c, Pn532, pn532
from config.config import I2C_BUS

class RFIDReader:
    def __init__(self):
        self.i2c = Pn532I2c(I2C_BUS)
        self.nfc = Pn532(self.i2c)
        self.initialize()

    def initialize(self):
        for attempt in range(5):  # Retry up to 5 times
            try:
                self.nfc.begin()
                self.nfc.SAMConfig()
                print("RFID reader initialized")
                return
            except OSError as e:
                print(f"Initialization attempt {attempt + 1} failed: {e}")
                time.sleep(1)
        raise RuntimeError("Failed to initialize RFID reader after several attempts")

    def read_uid(self):
        while True:
            try:
                success, uid = self.nfc.readPassiveTargetID(pn532.PN532_MIFARE_ISO14443A_106KBPS)
                if success:
                    uid_string = ''.join('{:02x}'.format(i) for i in uid)
                    if uid_string:
                        return success, uid.hex()
                time.sleep(0.2)
            except Exception as e:
                print(f"Error reading UID: {e}")
                time.sleep(0.2)
                continue