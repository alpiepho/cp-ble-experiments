# Experiments with Adafruit Feather Nrf52840 Express

Really don't know where to put details of specfic projects for the board, so stuffing it here.  


## General Experiments

As part of the overall CP-BLE-Experiments, I tried a number of examples related to BLE.  These all use a custom BT Uart Packet to work with the "BluefruitConnect" IOS application. (think there is an Android one as well). 

<b>TODO</b>  Find combo version that supports general BT Uart AND the custom Packet form, include here.

Files:
- minimum.py - advertise only
- button_press.py - print to serial when button is pressed
- combo.py - a mash up of the various custom BT Uart Packet demos
- neopixel.py - - control neopixel thru IOS applicaiton
- mobile_movement.py - print to serial when IOS movement sent
- location.py- print to serial when IOS location sent
- lib - copy of CP 6.x libraries (need new for CP 7.x)


## Temperature Logger

This is a simple temperature sensor setup.  Some of the design requirements:

- Adafruit Feather Nrf52840 Express
- Circuit Python
- a DHT11 3 pin sensor
- a 10K resister
- built on breadboard
- Custom "CLI" interface over BT Uart
- UI to configure
- Keep samples of temp at given rate
- no persistent storage
- BT CLI command to dump data to Serial port
- UI to configure state for "alarm"
- alarm thru LED
- alarm thru BT Beacon?

Eventually, I would like a full long-term "sensor" logger platform runing ZephyrOS with many sensors running in real time.  However, the simplicity of CP (Circuit Python) is hard to pass up inorder to get a prototype working.

Files:
- <b>TODO</b> mock_cli.py - example implemetation of CLI running on desktop
- <b>TODO</b> bt_uart_cli.py - example implemetation of CLI over BT UART working with BluefruitConnect IOS application
- <b>TODO</b> temp_sensor1.py - example circuitpython.org?

## TEMP SENSOR SAMPLE

From the example in the REFFERENCES below:

![Diagran](./dht22.png)

This digram shows a DHT22 part while we will use a DHT11 part.  The DHT11 has 3 pins and is a blue part.  Also shown is using a Adafruit Tricket board instead of a Adafruit Feather NRF52840, where we should be able to use one of the A0-A5 imput pins (and the 10k resistor is needed with the DHT11 part).

The first circuit will use a breadboard and later be converted to perfboard.


## Mock CLI

<b>TODO</b> 


<b>TODO</b> 


## Mock CLI

<b>TODO</b> 

- idea
- mock on desktop

## BT UART CLI

<b>TODO</b> 

- idea
- mock on desktop
- example on CP
- how to expand for temp sensor

## BT UART CLI WITH TEMP SENSOR

<b>TODO</b> 




## Looking for way to 'revive' board falshed with Zephyr to CircuitPython

Need to review these:

https://learn.adafruit.com/introducing-the-adafruit-nrf52840-feather/update-bootloader

https://learn.adafruit.com/bluefruit-nrf52-feather-learning-guide/flashing-the-bootloader

https://learn.adafruit.com/circuitpython-on-the-nrf52/nrf52840-bootloader

https://github.com/adafruit/Adafruit_nRF52_Bootloader

## References

[DHT CircuitPython Code](https://learn.adafruit.com/dht/dht-circuitpython-code)

[Adafruit Feather NRF52840 Pinout](https://learn.adafruit.com/introducing-the-adafruit-nrf52840-feather/pinouts)

[DHT11 Data Sheet](https://www.digikey.com/htmldatasheets/production/2071184/0/0/1/dht11-humidity-temp-sensor.html?utm_adgroup=xGeneral&utm_source=google&utm_medium=cpc&utm_campaign=Dynamic%20Search_EN_Product&utm_term=&utm_content=xGeneral&gclid=Cj0KCQjwrJOMBhCZARIsAGEd4VE-y2GArTc0jV7AzMAocpMigdgkhviQDjdtSYQr0yUu6q5MWDBm0hMaAptpEALw_wcB)