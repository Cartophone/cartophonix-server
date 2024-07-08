# app/handlers/bluetooth_handler.py

import asyncio
import subprocess

async def scan_bluetooth_devices():
    process = await asyncio.create_subprocess_exec(
        'bluetoothctl', 'scan', 'on',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await asyncio.sleep(10)  # Adjust the sleep time as needed
    process.terminate()
    stdout, _ = await process.communicate()

    devices = []
    for line in stdout.decode().split('\n'):
        if 'Device' in line:
            parts = line.split(' ')
            devices.append({'mac_address': parts[1], 'name': ' '.join(parts[2:])})
    
    return devices

async def trust_and_connect_device(mac_address):
    await asyncio.create_subprocess_exec(
        'bluetoothctl', 'trust', mac_address
    )
    await asyncio.create_subprocess_exec(
        'bluetoothctl', 'connect', mac_address
    )