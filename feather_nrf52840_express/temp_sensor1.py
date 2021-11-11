

# FROM: https://readthedocs.org/projects/adafruit-circuitpython-dht/downloads/pdf/latest/


# # SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# 2 # SPDX-License-Identifier: MIT
# 3
# 4 import time
# 5 import board
# 6 import adafruit_dht
# 7
# 8 # Initial the dht device, with data pin connected to:
# 9 dhtDevice = adafruit_dht.DHT22(board.D18)
# 10
# 11 # you can pass DHT22 use_pulseio=False if you wouldn't like to use pulseio.
# 12 # This may be necessary on a Linux single board computer like the Raspberry Pi,
# 13 # but it will not work in CircuitPython.
# 14 # dhtDevice = adafruit_dht.DHT22(board.D18, use_pulseio=False)
# 15
# 16 while True:
# 17 try:
# 18 # Print the values to the serial port
# 19 temperature_c = dhtDevice.temperature
# 20 temperature_f = temperature_c * (9 / 5) + 32
# 21 humidity = dhtDevice.humidity
# 22 print(
# 23 "Temp: {:.1f} F / {:.1f} C Humidity: {}% ".format(
# 24 temperature_f, temperature_c, humidity
# 25 )
# 26 )
# 27
# 28 except RuntimeError as error:
# 29 # Errors happen fairly often, DHT's are hard to read, just keep going
# 30 print(error.args[0])
# 31 time.sleep(2.0)
# 32 continue
# 33 except Exception as error:
# 34 dhtDevice.exit()
# raise error
# 36
# 37 time.sleep(2.0)