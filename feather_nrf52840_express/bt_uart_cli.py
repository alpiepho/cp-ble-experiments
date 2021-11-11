
import random
import threading
import time
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

ble = BLERadio()
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)

led_battery = False
led_alarm = False
led_state = 0

def Help():
    # help
    print(f'-1,q - quit config mode')
    print(f'0,h,? - help')
    print(f'1,i   - info ')
    # led
    print(f'10 - led_battery (current {led_battery})')
    print(f'11 - led_alarm (current {led_alarm})')
    # dump
    print(f'20 - dump sample to serial')

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

def Info():
    print(f'led_battery: {led_battery}')
    print(f'led_alarm:   {led_alarm}')
    print(f'led_state:   {led_state}')

def Dump():
    global samples
    keys = samples.keys()
    for key in range(10):
        value = random.uniform(0, 100)
        print(f'{key}, {value}') # TODO: change to serial

def SetLed(state):
    # TODO: turn on/off led
    print(f'led: {state}')
    ...


def RunConfigMode(uart):
    global led_battery
    global led_alarm

    # TODO: add button press test here
    global config_last_time
    current_time = time.time()
    if (current_time - config_last_time) > 10:
        config_last_time = current_time

        option = ''
        while option != '-1' and option != 'q':
            # print('option > ')
            msg = 'option > '
            uart.write(msg.encode("utf-8"))
            option = input()
            # s = uart.readline()
            # if s:
            #     try:
            #         result = str(eval(s))
            #     except Exception as e:
            #         result = repr(e)
            #     uart.write(result.encode("utf-8"))

            if option == '0' or option == 'h' or option == '?':
                Help()
            elif option == '1' or option == 'i':
                Info()
            elif option.startswith('10 '):
                led_battery = getInt(option, led_battery)
            elif option.startswith('11 '):
                led_alarm = getInt(option, led_alarm)
            elif option == '20':
                Dump()


def RunLed():
    global led_last_time
    global led_state

    current_time = time.time()
    if (current_time - led_last_time) > 1:
        led_last_time = current_time

        #print(current_time)
        if not led_battery and not led_alarm:
            led_state = 0
            SetLed(0)
        if led_battery: # 1,0,0,1,0,0...
            if led_state == 0:
                led_state = 1
                SetLed(1)
            elif led_state == 1:
                led_state = 2
                SetLed(0)
            elif led_state == 2:
                led_state = 0
                SetLed(0)
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
        # s = uart.readline()
        # if s:
        #     try:
        #         result = str(eval(s))
        #     except Exception as e:
        #         result = repr(e)
        #     uart.write(result.encode("utf-8"))
