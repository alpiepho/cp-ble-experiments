
# Combining the following:
# minimum.py
# button_press.py
# neopixel.py
# mobile_movement.py
# location.py

import board
import neopixel

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

from adafruit_bluefruit_connect.packet import Packet
from adafruit_bluefruit_connect.button_packet import ButtonPacket
from adafruit_bluefruit_connect.color_packet import ColorPacket
from adafruit_bluefruit_connect.accelerometer_packet import AccelerometerPacket
from adafruit_bluefruit_connect.magnetometer_packet import MagnetometerPacket
from adafruit_bluefruit_connect.gyro_packet import GyroPacket
from adafruit_bluefruit_connect.quaternion_packet import QuaternionPacket
from adafruit_bluefruit_connect.location_packet import LocationPacket


ble = BLERadio()
uart_service = UARTService()
advertisement = ProvideServicesAdvertisement(uart_service)

pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=0.1)

while True:
    ble.start_advertising(advertisement)
    while not ble.connected:
        pass
    ble.stop_advertising()

    # Now we're connected

    while ble.connected:
        if uart_service.in_waiting:
            try:
                packet = Packet.from_stream(uart_service)
                if isinstance(packet, ButtonPacket):
                    if packet.pressed:
                        if packet.button == ButtonPacket.BUTTON_1:
                            # The 1 button was pressed.
                            print("1 button pressed!")
                        if packet.button == ButtonPacket.BUTTON_2:
                            # The 2 button was pressed.
                            print("2 button pressed!")
                        if packet.button == ButtonPacket.BUTTON_3:
                            # The 3 button was pressed.
                            print("3 button pressed!")
                        if packet.button == ButtonPacket.BUTTON_4:
                            # The 4 button was pressed.
                            print("4 button pressed!")
                        elif packet.button == ButtonPacket.UP:
                            # The UP button was pressed.
                            print("UP button pressed!")
                        elif packet.button == ButtonPacket.DOWN:
                            # The DOWN button was pressed.
                            print("DOWN button pressed!")
                        elif packet.button == ButtonPacket.LEFT:
                            # The LEFT button was pressed.
                            print("LEFT button pressed!")
                        elif packet.button == ButtonPacket.RIGHT:
                            # The RIGHT button was pressed.
                            print("RIGHT button pressed!")
                elif isinstance(packet, ColorPacket):
                    print(packet.color)
                    pixels.fill(packet.color)
                elif isinstance(packet, AccelerometerPacket):
                    print("Acceleration:", packet.x, packet.y, packet.z)
                elif isinstance(packet, MagnetometerPacket):
                    print("Magnetometer:", packet.x, packet.y, packet.z)
                elif isinstance(packet, GyroPacket):
                    print("Gyro:", packet.x, packet.y, packet.z)
                elif isinstance(packet, QuaternionPacket):
                    print("Quaternion:", packet.x, packet.y, packet.z)
                elif isinstance(packet, LocationPacket):
                    print("Latitude:", packet.latitude)
                    print("Longitude", packet.longitude)
                    print("Altitude:", packet.altitude)
            except ValueError:
                # assume just a string, try to get all bytes after !<letter>
                if uart_service.in_waiting:
                    raw_bytes = uart_service.read(uart_service.in_waiting)
                    text = raw_bytes.decode().strip()
                    # print("raw bytes =", raw_bytes)
                    print(text)

            except Exception as err:
                print(err)


    # If we got here, we lost the connection. Go up to the top and start
    # advertising again and waiting for a connection.

