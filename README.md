

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
    - [done] ble advertising
    - [done] button_press
    - [done] neopixel
    - [done] mobile_movement
    - [done] location
- Adafruit Learning demos for "BLE Anywhere"
    - [done] uart-board
    - [done] uart-host
- Bleak library
    - send
- [done] create combo of nRF52840 apps
- [done] find playground express demo code (https://github.com/adafruit/Adafruit_CircuitPlayground/tree/master/examples/demo)

<br>
<br>

# A Tale of Too Many Tutorials and Expanded Scope

As I was digging into BLE, specifically with Circuit Python, I kept running into more and more tutorials/references...thus the really long list of references at the bottom of this page.  As you will see, I am probably trying to connect too many dots.  (Good thing my boss on this project is ok with it...oh, that's me!)

Each new reference tailed into another.  At some point I was going in circles...and that is why I am documenting the various cases.

I have a couple wants with Bluetooth and BLE: 
1. I want to "control both ends".  
1. Also want to "scan my environment and understand what is out there".
1. Want to gain experience with ZephryOS
1. Want to incorporate Flutter web-on-Flask
1. Roll Flutter to IOS?
1. Roll Flutter to Android? (excuse to by Pixel 6 with support for ML)

<br>
The following is a table of cases I derived from the varous tutorials, and cases I want to complete toward meeting "Want" number 1.

<br>
<br>

| Case | BLE "Connect" or Host Side  | BLE Protocol | BLE "Peripheral" or Board Side |
| :--- | :---  | :--- | :--- |
| 1 [done] | IPhone / IOS / "BluefruitConnect" App  | No GATT* / Custom "Packet" class  | nRF52840 / CircuitPython / combo.py (from ref apps) |
| 2 [done] | Ubuntu / Blinka(Bleak) / uart_host.py  | No GATT* / simple UART**  | CircuitPlaygroundExpress / uart_board.py  |
| 3 [fail] | Ubuntu / Bleak / uart_service.py  | No GATT* / Custom "Packet" class  | nRF52840 / CircuitPython / combo.py  |
| 4 [tbd] | Ubuntu / Bleak / uart_service.py  | No GATT* / Custom "Packet" class  | nRF52840 / CircuitPython / combo.py |
| 5 [tbd] | Ubuntu / Bleak / python, Flask, Flutter?  | No GATT* / Custom "Packet" class  | nRF52840 / CircuitPython / combo.py |
| 10 [tbd] | Ubuntu / Bleak / ??.py  | No GATT* / Custom "Packet" class  | nRF52840 / ZephyrOS / ?? code |


Notes:
- "Connect" is Bluetooth term for Host vs. Peripheral, or Client vs. Server.  It drives the discover.
- "Peripheral" is a Bluetooth term for Peripheral vs. Host, or Server vs. Client.  Typically the device that offers a Beacon to be discovered
- "No GATT*" - It doesn't appear that the Circuit Python library is providing a Beacon with supporte GATT descriptors, but the library could be abstracting that...<b>TODO</b> need to check.
- "simple UART**" - Not to confused with the Nordic Semiconductor Proprietory UART protocol.
- "Case 3 [fail] - doesn't full work, Board side gets text, but need host side generation of packets with checksum
- "Case 4 [tbd] - implement host side generation of packets with checksum if "!" given, maybe add "help" or "?"
- "Case 10 [tbd]" - Want experience with ZephryOS, tutorials happen to use same Adafruit board, nRF52840

So with this <b>NEW</b> goal, the following sections will try to reference back to these cases where possible.  

<br>
<br>

## CASE 1: CircuitPython / combo.py

Following the tutorial at: https://learn.adafruit.com/circuitpython-nrf52840/bluefruit-le-connect-basics

The source for this is scattered thru the tutorial.  I pulled these into files in the directory `feather_nrf52840_express`, and then merged then into `combo.py`.

The IOS App has more functions than are discussed in this demo.  I suspect that the IOS was built to test several BLE boards, but I have not found those on the
AdaFruit site.


<br>
<br>

## CASE 2: Blinka Setup

Setting up Blinka with the following: https://pypi.org/project/Adafruit-Blinka/.  Uses files in `uart-board` and `uart-host`.

To install in a virtual environment in your current project:
```
mkdir project-name && cd project-name
python3 -m venv .env
source .env/bin/activate
pip3 install Adafruit-Blinka
```

Might need: 
https://askubuntu.com/questions/1290037/error-while-installing-rpi-gpio-as-error-command-errored-out-with-exit-status

```
export CFLAGS=-fcommon
pip3 install RPi.GPIO
```

Blinka Setup - BLE
```
pip3 install adafruit-circuitpython-ble
```

<br>
<br>

## CASE 3: Bleak / uart_service.py

Followed installation from https://bleak.readthedocs.io/en/latest/.

Using `uart_service.py` from https://github.com/hbldh/bleak/tree/develop/examples.

This partially works with CircuitPython/combo.py as the Board side.  The Board side can see characters, but since it is trying to form Packets from the characters along with a checksum, each Packet is failing.
The plan for Case 4 is to create a modified `uart_service.py` that recodnizes when user input as packets and form the Packet stream properly.

<br>
<br>

## CASE 4: Bleak / uart_service2.py

<b>TBD</b>

<br>
<br>

## CASE 5: Bleak / python, Flask, Flutter?

Excuse to keep up with Flask on the backend and Flutter on the frontend???

<b>TBD</b>

<br>
<br>

## CASE 10: nRF52840 / ZephyrOS / ?? code

Excuse to learn ZephyrOS on same hardware used by Circuit Python???

<b>TBD</b>

<br>
<br>

## Files and Directories

- feather_nrf52840_express
    - minimum.py
    - button_press.py
    - neopixel.py
    - mobile_movement.py
    - location.py
    - lib
- uart-board
    - code.py
    - lib
- uart-host
    - python env
    - code.py
- uart_service.py


<br>
<br>

## Followup Project Ideas:

- extend combo to handle all pages of IOS phone app
    - info
        - rxd
        - client charteristic configuration
        - txd
    - uart
        - text area
    - plotter
        - TBD
    - pin I/O
        - pin 1, input, Low
        - ...
        - scrolling
    - controller
        - quaternion
        - accelerometer
        - gyro
        - magnetometer
        - location
        - control pad
            - up, down, left, right
            - 1 ,2, 3, 4
        - color picker
            - send hex (#00FFFF), alpha
    - AHRS/Calibration
        - TBD
    - thermal camera
        - TBD
    - image transfer
        - TBD
- check ino demo for board exeamples supporting these IOS app pages
- test these on playground express
- review other cp examples for playground express

- Run various components I have in-hand:
    - run motor
    - run proximetry sensor
    - run motion sensor
    - run temp/humidity
    - run I2C display
    - run LED matrix

- think next AdaBox will be the led glasses
    - Use IPhone / IOS / "BluefruitConnect" App to control for scrolling text
    - Use IPhone / IOS / "BluefruitConnect" App to control Scoreboard
        - "1" use next color for home team
        - "2" use next color for away team
        - uart for score text??
    - <b>TODO</b> Fill out details

<br>
<br>

## References

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


- https://readthedocs.org/projects/adafruit-circuitpython-ble/downloads/pdf/latest/


- https://github.com/adafruit/Adafruit_CircuitPython_CircuitPlayground
- https://learn.adafruit.com/adafruit-circuit-playground-express?view=all#overview


Zephyr on nrf52840:<br>
- https://docs.zephyrproject.org/latest/samples/basic/blinky/README.html#blinky-sample
- https://github.com/zephyrproject-rtos/zephyr/tree/main/samples
- https://www.novelbits.io/zephyr-getting-started-bluetooth-low-energy-development/
