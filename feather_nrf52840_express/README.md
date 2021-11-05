# Experiments with Adafruit Feather Nrf52840 Express

## General Experiments

Files:

<b>TBD</b>
- minimum.py - advertise only
- button_press.py - print to serial when button is pressed
- neopixel.py - - control neopixel thru IOS applicaiton
- mobile_movement.py - print to serial when IOS movement sent
- location.py- print to serial when IOS location sent
- lib - copy of CP 6.x libraries (need new for CP 7.x)


## Temperature Logger

Eventually, I would like a full long-term "sensor" logger platform runing ZephyrOS with many sensors running in real time.  However, the simplicity of CP (Circuit Python) is hard to pass up inorder to get a prototype working.


- CP
- Nrf52840
- DHT11
- 10k resister
- BT UI
- Command Line like and/or re-use BlueFruitConnect IOS (Android?) application
- use MAGTAG sleep idea for longer battery?


## Looking for way to 'revive' board falshed with Zephyr to CircuitPython

Need to review these:

https://learn.adafruit.com/introducing-the-adafruit-nrf52840-feather/update-bootloader

https://learn.adafruit.com/bluefruit-nrf52-feather-learning-guide/flashing-the-bootloader

https://learn.adafruit.com/circuitpython-on-the-nrf52/nrf52840-bootloader

https://github.com/adafruit/Adafruit_nRF52_Bootloader

## References

https://learn.adafruit.com/dht/dht-circuitpython-code

https://www.digikey.com/htmldatasheets/production/2071184/0/0/1/dht11-humidity-temp-sensor.html?utm_adgroup=xGeneral&utm_source=google&utm_medium=cpc&utm_campaign=Dynamic%20Search_EN_Product&utm_term=&utm_content=xGeneral&gclid=Cj0KCQjwrJOMBhCZARIsAGEd4VE-y2GArTc0jV7AzMAocpMigdgkhviQDjdtSYQr0yUu6q5MWDBm0hMaAptpEALw_wcB