import subprocess
import logging

def scan_bluetooth_devices():
    try:
        result = subprocess.run(['bluetoothctl', 'scan', 'on'], capture_output=True, text=True, timeout=10)
        devices = []
        for line in result.stdout.split('\n'):
            if "Device" in line:
                parts = line.split()
                mac_address = parts[1]
                name = ' '.join(parts[2:])
                devices.append({"name": name, "mac_address": mac_address})
        return devices
    except subprocess.TimeoutExpired:
        logging.error("Bluetooth scan timed out")
        return []
    except Exception as e:
        logging.error(f"Error scanning Bluetooth devices: {e}")
        return []

def trust_and_connect_device(mac_address):
    try:
        subprocess.run(['bluetoothctl', 'trust', mac_address], check=True)
        subprocess.run(['bluetoothctl', 'connect', mac_address], check=True)
        return {"status": "success", "message": f"Connected to {mac_address}"}
    except subprocess.CalledProcessError as e:
        logging.error(f"Error connecting to Bluetooth device {mac_address}: {e}")
        return {"status": "error", "message": f"Failed to connect to {mac_address}"}