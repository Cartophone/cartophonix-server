import subprocess
import asyncio

async def scan_bluetooth():
    process = await asyncio.create_subprocess_exec(
        'bluetoothctl', 'scan', 'on',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    devices = []
    for line in stdout.decode().split('\n'):
        if 'Device' in line:
            parts = line.split()
            mac = parts[1]
            name = ' '.join(parts[2:])
            devices.append({'mac': mac, 'name': name})
    return devices

async def connect_bluetooth(mac_address):
    process = await asyncio.create_subprocess_exec(
        'bluetoothctl', 'trust', mac_address,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await process.communicate()

    process = await asyncio.create_subprocess_exec(
        'bluetoothctl', 'connect', mac_address,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await process.communicate()