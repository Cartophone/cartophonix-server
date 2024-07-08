# This file can be left empty or used to initialize the package.
# For example, you can use it to import all handlers at once.
from .handlers.rfid_handler import handle_read
from .handlers.alarm_handler import check_alarms
from .handlers.bluetooth_handler import scan_bluetooth, connect_bluetooth