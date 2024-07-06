import asyncio
import subprocess

async def scan_bluetooth_devices(timeout):
    process = await asyncio.create_subprocess_shell(
        "pactl list short sources",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
        if process.returncode != 0:
            raise Exception(f"Error scanning Bluetooth devices: {stderr.decode()}")
        output = stdout.decode()
        devices = []
        for line in output.split('\n'):
            if 'bluez' in line:
                parts = line.split('\t')
                name = parts[1]
                mac_address = parts[0].split('.')[1]
                devices.append({"name": name, "mac_address": mac_address})
        return devices
    except asyncio.TimeoutError:
        process.kill()
        raise Exception("Timeout while scanning for Bluetooth devices")

async def connect_bluetooth_device(mac_address):
    try:
        # Trust the device
        trust_command = f"echo 'trust {mac_address}' | bluetoothctl"
        subprocess.run(trust_command, shell=True, check=True)
        
        # Connect to the device
        connect_command = f"echo 'connect {mac_address}' | bluetoothctl"
        subprocess.run(connect_command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to connect to Bluetooth device {mac_address}: {str(e)}")