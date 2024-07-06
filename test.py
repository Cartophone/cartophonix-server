import time
from pn532pi import Pn532Spi, Pn532, pn532

class RFIDReader:
    def __init__(self):
        self.spi = Pn532Spi(Pn532Spi.SS0_GPIO8)
        self.nfc = Pn532(self.spi)
        self.nfc.begin()
        self.nfc.SAMConfig()
        print("RFID reader initialized")

    def read_uid(self):
        while True:
            print(self.nfc.readPassiveTargetID(pn532.PN532_MIFARE_ISO14443A_106KBPS))
            time.sleep(0.1)

NFC=RFIDReader()
NFC.read_uid()