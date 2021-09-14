

This is a collection of example applications using CircuitPython on both a device (specifically the Adafruit nRF52840, and Circuit Playground Exress), 
and on a Raspberry PI running Unbuntu, using the Blinka python libraries.  Also want to try the underlying python library, Bleak.

So what is the purpose of doing this?

- Want to learn more about BLE
- Want to have sample of actually working BLE code for device (peripheral) and host (connect)
- Think I can create interesting host application to inspect, operate BLE device
- Think I can create my own mobile app/UI with Flutter

So, I don't have any real goal here, other than learning and adding to my personal toolbox.  With any luck, something real
will occur to me as I run thru these experiments.


First steps, running thru various demos:
- Adafruit Learning demos for Feather nRF52840 Express
    - ble advertising
    - button_press
    - neopixel
    - mobile_movement
    - location
- Adafruit Learning demos for "BLE Anywhere"
    - uart-board
    - uart-host
- Bleak library
    - send

TODO: clean up example descriptions

Followup Project Ideas:

- run motor
- run proximetry sensor
- run motion sensor
- run temp/humidity
- run I2C display
- run LED matrix


## Files and Directoies

TBD


## Blinka Setup - General

Setting up Blinka with the following:

https://pypi.org/project/Adafruit-Blinka/


From page:

To install in a virtual environment in your current project:

mkdir project-name && cd project-name<br>
python3 -m venv .env<br>
source .env/bin/activate<br>
pip3 install Adafruit-Blinka<br>

Might need:

https://askubuntu.com/questions/1290037/error-while-installing-rpi-gpio-as-error-command-errored-out-with-exit-status


export CFLAGS=-fcommon<br>
pip3 install RPi.GPIO<br>


## Blinka Setup - BLE

pip3 install adafruit-circuitpython-ble



## Other References

- https://pypi.org/project/Adafruit-Blinka/
- https://learn.adafruit.com/circuitpython-nrf52840/bluefruit-le-connect-basics
- https://learn.adafruit.com/introducing-the-adafruit-nrf52840-feather/circuitpython
- https://learn.adafruit.com/circuitpython-nrf52840/overview
- https://learn.adafruit.com/circuitpython-ble-libraries-on-any-computer/install-ble-libraries


- https://learn.adafruit.com/introduction-to-bluetooth-low-energy/gap
- https://github.com/Ladvien/arduino_ble_sense
- https://ladvien.com/python-serial-terminal-with-arduino-and-bleak/
- https://learn.adafruit.com/circuitpython-ble-libraries-on-any-computer/ble-uart-example
- https://www.bluetooth.com/specifications/assigned-numbers/
- https://learn.adafruit.com/introduction-to-bluetooth-low-energy/further-information
- https://bleak.readthedocs.io/en/latest/
- https://github.com/hbldh/bleak


