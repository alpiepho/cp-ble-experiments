
import board
import random
import time
import gc

from digitalio import DigitalInOut, Direction, Pull
from analogio import AnalogIn

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

from adafruit_bluefruit_connect.packet import Packet
from adafruit_bluefruit_connect.color_packet import ColorPacket

import adafruit_dht

# Setup
ble = BLERadio()
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)

dhtDevice = adafruit_dht.DHT11(board.D5)

batt_monitor = AnalogIn(board.BATTERY)

samples = {}

led_battery = 0
led_alarm = 0
led_state = 0
led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT

led_last_time = time.time()
led_time_delta = 500000000 # 1/2 sec

temp_sample_seconds = 5
temp_c_trigger_value = 1000
temp_c_trigger_seconds = 10

# TODO - add options for controlling temp alarm
# TODO - add temp check TODO need pin and pull up
# TODO - add battery check 


def Help(uart):
    # help
    # NOTE: try to favor letters over numbers, 
    #       and extra options instead of parameters,
    #       those are easier from Bluefruit Connect app
    msg1 = f'h - help\n'
    msg2 = f'i - info\n'
    msg3 = f't - set temp_c_trigger_value (current {temp_c_trigger_value})\n'
    msg4 = f'T - set temp_c_trigger_seconds (current {temp_c_trigger_seconds})\n'
    msg5 = f'd - dump sample to serial\n'
    uart.write(msg1.encode("utf-8"))
    uart.write(msg2.encode("utf-8"))
    uart.write(msg3.encode("utf-8"))
    uart.write(msg4.encode("utf-8"))
    uart.write(msg5.encode("utf-8"))

def getInt(option, oldValue):
    result = oldValue
    try:
        parts = option.split()
        if parts[1].startswith(b't') or parts[1].startswith(b'T'):
            result = 1
        elif parts[1].startswith(b'f') or parts[1].startswith(b'F'):
            result = 0
        else:
            result = int(parts[1])
    except:
        print('bad value')
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
    msg1 = f'led_battery:            {led_battery}\n'
    msg2 = f'temp_c_trigger_value:   {temp_c_trigger_value}\n'
    msg3 = f'temp_c_trigger_seconds: {temp_c_trigger_seconds}\n'
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
    # temp = time.time()
    # samples[temp] = state

def RunConfigMode(uart):
    global led_battery
    global led_alarm
    global temp_c_trigger_value
    global temp_c_trigger_seconds

    option = uart.readline()
    option = option.strip()
    if option == b'i':
        Info(uart)
    elif option == b'a':
        led_alarm = not led_alarm
    elif option == b'b':
        led_battery = not led_battery
    elif option.startswith(b't '):
        temp_c_trigger_value = getFloat(option, temp_c_trigger_value)
    elif option.startswith(b'T '):
        temp_c_trigger_seconds = getInt(option, temp_c_trigger_seconds)
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

last_temp_sample_ts = time.monotonic_ns()
last_temp_trigger_ts = time.monotonic_ns()
def RunDHT():
    global temp_c_trigger_value
    global temp_c_trigger_seconds
    global led_alarm
    global last_temp_sample_ts
    global last_temp_trigger_ts
    global samples

    # FROM: https://circuitpython.readthedocs.io/projects/dht/en/latest/
    try:
        ts = time.monotonic_ns()
        led_alarm = 0
        if (ts - last_temp_sample_ts)/1000000000 > temp_sample_seconds:
            last_temp_sample_ts = ts

            temp_c = dhtDevice.temperature
            temp_f = temp_c * (9 / 5) + 32
            humidity = dhtDevice.humidity

            print("Temp: {:.1f} F / {:.1f} C Humidity: {}% ".format(temp_f, temp_c, humidity))
            print(len(samples))
            print(gc.mem_free())
            if len(samples) > 200:
                samples = {}
            samples[ts] = temp_c
        if (ts - last_temp_trigger_ts)/1000000000 > temp_c_trigger_seconds:
            last_temp_trigger_ts = ts
            if temp_c > temp_c_trigger_value: 
                led_alarm = 1
    except Exception as e:
        print("temp read failed")
        print(e)
    


def RunBattery():
    global led_battery
    global batt_monitor

    voltage = (batt_monitor.value / 65535.0) * 3.3 * 2
    #print("Battery: {:.1f} V ".format(voltage))
    led_battery = 0
    if voltage < 3.0:
        led_battery = 1



while True:
    ble.start_advertising(advertisement)
    print("Waiting to connect")
    while not ble.connected:
        RunLed()
        RunDHT()
        RunBattery()
    print("Connected")
    while ble.connected:
        RunLed()
        RunDHT()
        RunBattery()
        RunConfigMode(uart)


