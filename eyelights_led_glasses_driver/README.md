This folder contains experiments related to the "Led Glasses" from ADABox 020.

Hope to combine a number of features:
- bluetooth as control
- used as a scoreboard for volleyball
- control color of each side
- scroll some messages
- use IOS App, Adafruit BlueConnect app
    - uart for general CLI
    - color picker (TODO: how to combine "Packet" with raw serial)
- tap example into a double-tap to turn on/off
- can I use orientation example to turn on


Some features I really don't care about:
- the silk screen (sorry Lady Ada)
- the shape
- used as glasses
- as an introvert, I really don't like the attention


## EyeLights_Bluefruit_Scroller - example from Adafruit

The ADABox 020 comes with a code image that scrolls the text "Adafruit and Digikey ADABox 020" or something like that.
I have not been able to find the exact code, but a close example is this from the Adafruit learning article (in the
references below).  This also allows some control from the IOS app nad has an method to work around the Packet issue
I found in combo.py for the feather_nrf52840_epress.  Unfortunately this not CircuitPython, but Arduino code.

<b>TODO</b> 

- [todo] get code from example
- [todo] understand how scrolling works
- [todo] slow, pause, stop scrolling
- [todo] add bt cli
- [todo] try monkey patch of Packet for combo.py??
- [todo] try port to CP???




## eye_cli.py

<b>TODO</b> 

- [todo] <b>leverage EyeLights_Bluefruit_Scroller????</b>
- [todo] base bt cli for eyelights
- [todo] extended help
- [todo] fonts
- [todo] static message
- [todo] color
- [todo] roll text
- [todo] change letter?
- [todo] patterns
- [todo] rings


## eye_board.py

<b>TODO Ideas</b> 

- [todo] eyelights as simple scoreboard
- [todo] packaging?
- [todo] extended help
- [todo] info
- [todo] new 00 00
- [todo] buttons for score change?


## References

https://learn.adafruit.com/adafruit-eyelights-led-glasses-and-driver/overview

https://learn.adafruit.com/adafruit-eyelights-led-glasses-and-driver/bluetooth-message-scroller
