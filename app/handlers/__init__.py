# This file can be left empty or used to initialize the handlers package.
# For example, you can use it to import all handlers at once.
from .rfid_handler import handle_read
from .alarm_handler import check_alarms
from .bluetooth_handler import scan_bluetooth, connect_bluetooth