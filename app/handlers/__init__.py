# app/handlers/__init__.py

from .rfid_handler import rfid_reader
from .bluetooth_handler import scan_bluetooth_devices, trust_and_connect_device
from .alarm_handler import check_alarms