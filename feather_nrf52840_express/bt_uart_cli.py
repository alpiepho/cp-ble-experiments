
import board
import random
import time
from digitalio import DigitalInOut, Direction, Pull
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

ble = BLERadio()
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)

samples = {}

led_battery = 0
led_alarm = 0
led_state = 0
led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT

# switch = DigitalInOut(board.SWITCH)
# switch.direction = Direction.INPUT
# switch.pull = Pull.UP

def Help(uart):
    # help
    # TODO: try to favor letters of numbers, easier from Bluefruit Connect app
    msg1 = f'-1,q - quit config mode\n'
    msg2 = f'0,h,? - help\n'
    msg3 = f'1,i   - info\n'
    msg4 = f'10 - led_battery (current {led_battery})\n'
    msg5 = f'11 - led_alarm (current {led_alarm})\n'
    msg6 = f'20 - dump sample to serial\n'
    uart.write(msg1.encode("utf-8"))
    uart.write(msg2.encode("utf-8"))
    uart.write(msg3.encode("utf-8"))
    uart.write(msg4.encode("utf-8"))
    uart.write(msg5.encode("utf-8"))
    uart.write(msg6.encode("utf-8"))

def getInt(option, oldValue):
    result = oldValue
    try:
        parts = option.split()
        result = int(parts[1])
    except:
        print('bad value')
    return result

# def getFloat(option, oldValue):
#     result = oldValue
#     try:
#         parts = option.split()
#         result = float(parts[1])
#     except:
#         print('bad value')
#     return result

def Info(uart):
    msg1 = f'led_battery: {led_battery}\n'
    msg2 = f'led_alarm:   {led_alarm}\n'
    msg3 = f'led_state:   {led_state}\n'
    uart.write(msg1.encode("utf-8"))
    uart.write(msg2.encode("utf-8"))
    uart.write(msg3.encode("utf-8"))

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

    option = uart.readline()
    option = option.strip()
    # print(f'given: {option}')
    if option == b'1' or option == b'i':
        Info(uart)
    elif option.startswith(b'10 '):
        led_battery = getInt(option, led_battery)
    elif option.startswith(b'11 '):
        led_alarm = getInt(option, led_alarm)
    elif option == b'20':
        Dump(uart)
    elif len(option) > 0:
        Help(uart)

    if len(option) > 0:
        msg = 'option > \n'
        uart.write(msg.encode("utf-8"))

def RunLed():
    global led_last_time
    global led_state

    current_time = time.time()
    if (current_time - led_last_time) > 1:
        led_last_time = current_time

        #print(current_time)
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

# Setup
config_last_time = time.time()
led_last_time = time.time()

while True:

    ble.start_advertising(advertisement)
    print("Waiting to connect")
    while not ble.connected:
        RunLed()
    print("Connected")
    while ble.connected:
        RunLed()
        RunConfigMode(uart)
