# app/bluetooth_handler.py

import asyncio
import subprocess

async def scan_bluetooth_devices(timeout):
    process = await asyncio.create_subprocess_shell(
        "bluetoothctl scan on",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    try:
        await asyncio.sleep(timeout)
        process.kill()
        process = await asyncio.create_subprocess_shell(
            "bluetoothctl devices",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            raise Exception(f"Error scanning Bluetooth devices: {stderr.decode()}")
        output = stdout.decode()
        devices = []
        for line in output.split('\n'):
            if line.startswith("Device"):
                parts = line.split(' ', 2)
                mac_address = parts[1]
                name = parts[2]
                devices.append({"name": name, "mac_address": mac_address})
        return devices
    except asyncio.TimeoutError:
        process.kill()
        raise Exception("Timeout while scanning for Bluetooth devices")

async def connect_bluetooth_device(mac_address):
    try:
        # Trust the device
        trust_command = f"echo -e 'trust {mac_address}\nconnect {mac_address}' | bluetoothctl"
        subprocess.run(trust_command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to connect to Bluetooth device {mac_address}: {str(e)}")