
import board
import neopixel
import time

from digitalio import DigitalInOut, Direction, Pull

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

from adafruit_bluefruit_connect.packet import Packet
from adafruit_bluefruit_connect.color_packet import ColorPacket

# Setup
ble = BLERadio()
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)

neo_color = 0xff111111
neo_bright = 0.2
pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=0.1)
pixels.fill(neo_color)

switch = DigitalInOut(board.SWITCH)
switch.direction = Direction.INPUT
switch.pull = Pull.UP

samples = {}

led_battery = 0
led_alarm = 0
led_state = 0
led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT

led_last_time = time.time()
led_time_delta = 500000000 # 1/2 sec



def Help(uart):
    # help
    # NOTE: try to favor letters over numbers, 
    #       and extra options instead of parameters,
    #       those are easier from Bluefruit Connect app
    msg1 = f'h - help\n'
    msg2 = f'i - info\n'
    msg3 = f'a - toggle led_alarm (current {led_alarm})\n'
    msg4 = f'b - toggle led_battery (current {led_battery})\n'
    msg5 = f'n - set neopixel color <hex> (current #{neo_color:08x})\n'
    msg6 = f'N - set neopixel  brightness (current {neo_bright})\n'
    msg7 = f'd - dump sample to serial\n'
    uart.write(msg1.encode("utf-8"))
    uart.write(msg2.encode("utf-8"))
    uart.write(msg3.encode("utf-8"))
    uart.write(msg4.encode("utf-8"))
    uart.write(msg5.encode("utf-8"))
    uart.write(msg6.encode("utf-8"))
    uart.write(msg7.encode("utf-8"))

def getHex(option, oldValue):
    result = oldValue
    try:
        parts = option.split()
        temp = parts[1].decode("utf-8")
        result = int(temp, 16)
    except Exception as e:
        print('bad value')
        print(e)
    return result

def getFloat(option, oldValue):
    result = oldValue
    try:
        parts = option.split()
        result = float(parts[1])
    except:
        print('bad value')
    return result

def Info(uart):
    msg1 = f'led_battery: {led_battery}\n'
    msg2 = f'led_alarm:   {led_alarm}\n'
    msg3 = f'led_state:   {led_state}\n'
    msg4 = f'neo_color:   #{neo_color:08x}\n'
    msg5 = f'neo_bright:  {neo_bright}\n'
    uart.write(msg1.encode("utf-8"))
    uart.write(msg2.encode("utf-8"))
    uart.write(msg3.encode("utf-8"))
    uart.write(msg4.encode("utf-8"))
    uart.write(msg5.encode("utf-8"))

def Dump(uart):
    global samples
    keys = samples.keys()
    for key in keys:
        value =samples[key]
        print(f'{key}, {value}')
    length = len(samples)
    msg1 = f'samples size, sent to serial: {length}\n'
    uart.write(msg1.encode("utf-8"))

def SetLed(state):
    led.value = state
    temp = time.time()
    samples[temp] = state

def RunConfigMode(uart):
    global led_battery
    global led_alarm
    global neo_color
    global neo_bright

    option = uart.readline()
    option = option.strip()
    if option == b'i':
        Info(uart)
    elif option == b'a':
        led_alarm = not led_alarm
    elif option == b'b':
        led_battery = not led_battery
    elif option.startswith(b'n '):
        neo_color = getHex(option, neo_color)
    elif option.startswith(b'N '):
        neo_bright = getFloat(option, neo_bright)
	pixels.fill(neo_color)
    elif option == b'd':
        Dump(uart)
    elif len(option) > 0:
        if option.startswith(b'!'):
            print("is this a Packet?\n")
            print(option)
        else:
            Help(uart)

    if len(option) > 0:
        msg = 'option > \n'
        uart.write(msg.encode("utf-8"))

def RunLed():
    global led_last_time
    global led_time_delta
    global led_state

    current_time = time.monotonic_ns()
    if (current_time - led_last_time) > led_time_delta:
        led_last_time = current_time

        if led_alarm: # 1,0,1,0... overrides battery
            if led_state == 0:
                led_state = 1
                SetLed(1)
            elif led_state == 1:
                led_state = 0
                SetLed(0)
            elif led_state == 2: # override possible battery sequence
                led_state = 0
                SetLed(0)
        elif led_battery: # 1,0,0,1,0,0...
            if led_state == 0:
                led_state = 1
                SetLed(1)
            elif led_state == 1:
                led_state = 2
                SetLed(0)
            elif led_state == 2:
                led_state = 0
                SetLed(0)
        else:
            led_state = 0
            SetLed(0)

def RunNeo():
    global neo_bright
    if switch.value == 0:
        pixels.brightness = 1.0
    else:
        pixels.brightness = neo_bright

while True:
    ble.start_advertising(advertisement)
    print("Waiting to connect")
    while not ble.connected:
        RunLed()
        RunNeo()
    print("Connected")
    while ble.connected:
        RunLed()
        RunNeo()
        RunConfigMode(uart)


