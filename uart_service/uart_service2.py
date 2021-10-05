"""
UART Service
-------------

An example showing how to write a simple program using the Nordic Semiconductor
(nRF) UART service.

"""

import asyncio
import sys

from bleak import BleakScanner, BleakClient
from bleak.backends.scanner import AdvertisementData
from bleak.backends.device import BLEDevice

# from adafruit_bluefruit_connect.button_packet import ButtonPacket
# from adafruit_bluefruit_connect.accelerometer_packet import AccelerometerPacket
# from adafruit_bluefruit_connect.gyro_packet import GyroPacket
# from adafruit_bluefruit_connect.location_packet import LocationPacket
# from adafruit_bluefruit_connect.magnetometer_packet import MagnetometerPacket
# from adafruit_bluefruit_connect.quaternion_packet import QuaternionPacket

UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

# All BLE devices have MTU of at least 23. Subtracting 3 bytes overhead, we can
# safely send 20 bytes at a time to any device supporting this service.
UART_SAFE_SIZE = 20


def checksum(partial_packet):
    """Compute checksum for bytes, not including the checksum byte itself."""
    return ~sum(partial_packet) & 0xFF


async def uart_terminal():
    """This is a simple "terminal" program that uses the Nordic Semiconductor
    (nRF) UART service. It reads from stdin and sends each line of data to the
    remote device. Any data received from the device is printed to stdout.
    """

    def match_nus_uuid(device: BLEDevice, adv: AdvertisementData):
        # This assumes that the device includes the UART service UUID in the
        # advertising data. This test may need to be adjusted depending on the
        # actual advertising data supplied by the device.
        if UART_SERVICE_UUID.lower() in adv.service_uuids:
            return True

        return False

    device = await BleakScanner.find_device_by_filter(match_nus_uuid)

    def handle_disconnect(_: BleakClient):
        print("Device was disconnected, goodbye.")
        # cancelling all tasks effectively ends the program
        for task in asyncio.all_tasks():
            task.cancel()

    def handle_rx(_: int, data: bytearray):
        print("received:", data)

    async with BleakClient(device, disconnected_callback=handle_disconnect) as client:
        await client.start_notify(UART_TX_CHAR_UUID, handle_rx)

        print("Connected, start typing and press ENTER...")

        loop = asyncio.get_event_loop()

        while True:
            # This waits until you type a line and press ENTER.
            # A real terminal program might put stdin in raw mode so that things
            # like CTRL+C get passed to the remote device.
            data = await loop.run_in_executor(None, sys.stdin.buffer.readline)

            # data will be empty on EOF (e.g. CTRL+D on *nix)
            if not data:
                break

            # some devices, like devices running MicroPython, expect Windows
            # line endings (uncomment line below if needed)
            # data = data.replace(b"\n", b"\r\n")

            # look for packet format
            try:
                sdata = data.decode("utf-8") 
                if sdata[0] == '!':
                    letter = sdata[1]
                    print(letter)
                    if letter == 'H' or letter == 'h' or letter == '?':
                        print("Supported operations:")
                        print("!A x y z                         - send AccelerometerPacket, x, y, z float values")
                        print("!B button press                  - send ButtonPacket, integer, 0/1")
                        print("!G x y z                         - send GyroPacket, x, y, z float values")
                        print("!L latitude, longitude, altitude - send LocationPacket, x, y, z float values")
                        print("!M x y z,                        - send LocationPacket, x, y, z float values")
                        print("!Q x y z w                       - send LocationPacket,  x, y, z, w float values")
                    elif letter == 'A':
                        parts = sdata.split()
                        x = float(parts[1])
                        y = float(parts[2])
                        z = float(parts[3])
                        partial_packet = struct.pack(
                            "<2sfff", b"!A", x, y, z
                        )
                        data = partial_packet + checksum(partial_packet)
                    elif letter == 'B':
                        parts = sdata.split()
                        partial_packet = struct.pack(
                            "<2sss", b"!B", parts[1], parts[2]
                        )
                        data = partial_packet + checksum(partial_packet)
                    elif letter == 'G':
                        parts = sdata.split()
                        x = float(parts[1])
                        y = float(parts[2])
                        z = float(parts[3])
                        partial_packet = struct.pack(
                            "<2sfff", b"!G", x, y, z
                        )
                        data = partial_packet + checksum(partial_packet)
                    elif letter == 'L':
                        parts = sdata.split()
                        x = float(parts[1])
                        y = float(parts[2])
                        z = float(parts[3])
                        partial_packet = struct.pack(
                            "<2sfff", b"!L", x, y, z
                        )
                        data = partial_packet + checksum(partial_packet)
                    elif letter == 'M':
                        parts = sdata.split()
                        x = float(parts[1])
                        y = float(parts[2])
                        z = float(parts[3])
                        partial_packet = struct.pack(
                            "<2sfff", b"!M", x, y, z
                        )
                        data = partial_packet + checksum(partial_packet)
                    elif letter == 'Q':
                        parts = sdata.split()
                        x = float(parts[1])
                        y = float(parts[2])
                        z = float(parts[3])
                        w = float(parts[4])
                        partial_packet = struct.pack(
                            "<2sfff", b"!Q", x, y, z, w
                        )
                        data = partial_packet + checksum(partial_packet)

                await client.write_gatt_char(UART_RX_CHAR_UUID, data)
                print("sent:", data)
            except Exception as error:
                print(error)


# It is important to use asyncio.run() to get proper cleanup on KeyboardInterrupt.
# This was introduced in Python 3.7. If you need it in Python 3.6, you can copy
# it from https://github.com/python/cpython/blob/3.7/Lib/asyncio/runners.py
try:
    asyncio.run(uart_terminal())
except asyncio.CancelledError:
    # task is cancelled on disconnect, so we ignore this error
    pass
