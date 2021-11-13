# SPDX-FileCopyrightText: 2020 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# CircuitPython NeoPixel Color Picker Example

import board
import neopixel
import time

from adafruit_bluefruit_connect.packet import Packet
from adafruit_bluefruit_connect.color_packet import ColorPacket

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

ble = BLERadio()
uart_service = UARTService()
advertisement = ProvideServicesAdvertisement(uart_service)

pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=0.1)

while True:
    # pixels.fill(0x11111111)
    # time.sleep(0.5)
    pixels.fill(0x00000000)
    time.sleep(0.5)
    pixels.fill(0x00ff0000)
    time.sleep(0.5)
    pixels.fill(0x0000ff00)
    time.sleep(0.5)
    pixels.fill(0x000000ff)
    time.sleep(0.5)
    
    # # Advertise when not connected.
    # ble.start_advertising(advertisement)
    # while not ble.connected:
    #     pass
    # ble.stop_advertising()

    # while ble.connected:
    #     if uart_service.in_waiting:
    #         packet = Packet.from_stream(uart_service)
    #         if isinstance(packet, ColorPacket):
    #             print(packet.color)
    #             pixels.fill(packet.color)
