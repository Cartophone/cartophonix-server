import time
from pn532pi import Pn532Spi, Pn532, pn532
from config.config import SPI_GPIO

class RFIDReader:
    def __init__(self):
        self.spi = Pn532Spi(Pn532Spi.SPI_GPIO)
        self.nfc = Pn532(self.spi)
        self.nfc.begin()
        self.nfc.SAMConfig()
        print("RFID reader initialized")

    def read_uid(self):
        while True:
            print(self.nfc.readPassiveTargetID(pn532.PN532_MIFARE_ISO14443A_106KBPS))
            time.sleep(0.2)

NFC=RFIDReader()
NFC.read_uid()