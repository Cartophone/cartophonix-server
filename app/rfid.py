import time
from pn532pi import Pn532Spi, Pn532, pn532

class RFIDReader:
    def __init__(self):
        self.spi = Pn532Spi(Pn532Spi.SS0_GPIO8)
        self.nfc = Pn532(self.spi)
        self.nfc.begin()
        self.nfc.SAMConfig()
        print("RFID reader initialized")

    async def read_uid(self):
        while True:
            success, uid = self.nfc.readPassiveTargetID(pn532.PN532_MIFARE_ISO14443A_106KBPS)
            if success:
                uid_string = ''.join('{:02x}'.format(i) for i in uid)
                return True, uid_string
            await asyncio.sleep(0.2)  # Make the function async