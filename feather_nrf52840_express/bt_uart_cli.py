
import board
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

def Help(uart):
    # help
    msg1 = f'-1,q - quit config mode'
    msg2 = f'0,h,? - help'
    msg3 = f'1,i   - info '
    # led
    msg4 = f'10 - led_battery (current {led_battery})'
    msg5 = f'11 - led_alarm (current {led_alarm})'
    # dump
    msg6 = f'20 - dump sample to serial'
    print(msg1)
    print(msg2)
    print(msg3)
    print(msg4)
    print(msg5)
    print(msg6)
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
    msg1 = f'led_battery: {led_battery}'
    msg2 = f'led_alarm:   {led_alarm}'
    msg3 = f'led_state:   {led_state}'
    print(msg1)
    print(msg2)
    print(msg3)
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
    msg1 = f'samples size, sent to serial: {length}'
    uart.write(msg1.encode("utf-8"))

def SetLed(state):
    #print(f'led: {state}')
    board.LED = state


def RunConfigMode(uart):
    global led_battery
    global led_alarm

    if board.SWITCH: # D7, debouncer?
        # global config_last_time
        # current_time = time.time()
        # if (current_time - config_last_time) > 10:
        #     config_last_time = current_time

        option = ''
        while option != '-1' and option != 'q':
            # print('option > ')
            msg = 'option > '
            uart.write(msg.encode("utf-8"))
            #option = input()
            option = uart.readline()
            if option:
                try:
                    if option == '0' or option == 'h' or option == '?':
                        Help(uart)
                    elif option == '1' or option == 'i':
                        Info(uart)
                    elif option.startswith('10 '):
                        led_battery = getInt(option, led_battery)
                    elif option.startswith('11 '):
                        led_alarm = getInt(option, led_alarm)
                    elif option == '20':
                        Dump(uart)
                except Exception as e:
                    result = repr(e)
                    uart.write(result.encode("utf-8"))

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
