
import random
import threading
import time
# from adafruit_ble import BLERadio
# from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
# from adafruit_ble.services.nordic import UARTService

# ble = BLERadio()
# uart = UARTService()
# advertisement = ProvideServicesAdvertisement(uart)

last_temperature = 0
last_distance = 100000


samples = {}
count = 0
count_max = 100
count_rollover = 0
count_rate = 1
pause = False

trigger_high_value = 3.3
trigger_high_seconds = 3600

trigger_low_value = 1.0
trigger_low_seconds = 300

led_battery = False # TODO: battery led slow blink
led_alarm = False   # TODO: threshold alarm led fast blink
led_state = 0

def led_thread():
    global led_battery
    global led_alarm
    global led_state

    while True:
        time.sleep(0.5)
        if led_battery:
            print(f'LED: {led_state}')

def sample_thread():
    global samples
    global count
      
    while True:
        time.sleep(count_rate)
        if not pause:
            seconds = time.time()
            if count >= count_max:
                count_rollover = count_rollover + 1
                count = 0
                samples = {} # TODO: create rollover instead of reset

            last_distance = random.uniform(0, 100) # TODO: add sensor read here

            last_temperature = random.uniform(0, 3.3) # TODO: add sensor read here
            samples[seconds] = last_temperature
            count = count + 1

            # TODO check for low battery

            # TODO check for trigger high

            # TODO check for trigger low

def Help():
    # help
    print(f'0,h,? - help')
    print(f'1,i   - info ')
    # measure
    print(f'10 - last raw/C/F')
    print(f'11 - last distance')
    # sampling
    print(f'20 - max samples (current {count_max})')
    print(f'21 - sample rate (current {count_rate})')
    print(f'22,s - start')
    print(f'23,t - stop')
    print(f'24,p - pause')
    print(f'25,r - reset')
    # dump
    print(f'31 - dump to serial - C')
    print(f'32 - dump to serial - F')
    # triggers
    print(f'51 - temp high threshold - C   (current {trigger_high_value})')
    temp = convertCtoF(trigger_high_value)
    print(f'52 - temp high threshold - F   (current {temp})')
    print(f'53 - temp high seconds         (current {trigger_high_seconds})')
    print(f'61 - temp low  threshold - C   (current {trigger_low_value})')
    temp = convertCtoF(trigger_low_value)
    print(f'62 - temp low  threshold - F   (current {temp})')
    print(f'63 - temp low  seconds         (current {trigger_low_seconds})')

def getInt(option, oldValue):
    result = oldValue
    try:
        parts = option.split()
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

def Info():
    print(f'count: {count}')
    print(f'count_max: {count_max}')
    print(f'count_rate: {count_rate}')
    print(f'count_rate: {count_rollover}')
    print(f'pause: {pause}')

def LastTemp():
    print(f'temperature: {last_temperature}')

def LastDistance():
    print(f'distance: {last_distance}')

def Start():
    global pause
    pause = False
    
def Stop():
    global pause
    pause = True

def Pause():
    global pause
    pause = not pause

def Reset():
    global count
    global samples
    global pause

    saved = pause
    pause = True
    count = 0
    samples = {}
    pause = saved

def convertCtoF(value):
    return value * (9 / 5) + 32

def convertFtoC(value):
    return ((value - 32) * 5) / 9

def DumpC():
    global samples
    keys = samples.keys()
    for key in keys:
        value = samples[key]
        print(f'{key}, {value}') # TODO: change to serial

def DumpF():
    global samples
    keys = samples.keys()
    for key in keys:
        value = samples[key]
        value = convertCtoF(value)
        print(f'{key}, {value}') # TODO: change to serial

# Setup
# TODO: is this going to work with CircuitPython???
t1 = threading.Thread(target=led_thread)
t1.start()

t2 = threading.Thread(target=sample_thread)
t2.start()

while True:
    print('option > ')
    option = input()
    if option == '0' or option == 'h' or option == '?':
        Help()
    elif option == '1' or option == 'i':
        Info()
    elif option == '10':
        LastTemp()
    elif option == '11':
        LastDistance()
    elif option.startswith('20 '):
        count_max = getInt(option, count_max)
    elif option.startswith('21 '):
        count_rate = getInt(option, count_rate)
    elif option == '22' or option == 's':
        Start()
    elif option == '23' or option == 't':
        Stop()
    elif option == '24' or option == 'p':
        Pause()
    elif option == '25' or option == 'r':
        Reset()
    elif option == '31':
        DumpC()
    elif option == '32':
        DumpF()
    elif option.startswith('51 '):
        trigger_high_value = getFloat(option, trigger_high_value)
    elif option.startswith('52 '):
        trigger_high_value = getFloat(option, trigger_high_value)
        trigger_high_value = convertFtoC(trigger_high_value)
    elif option.startswith('53 '):
        trigger_high_seconds = getInt(option, trigger_high_seconds)
    elif option.startswith('61 '):
        trigger_low_value = getFloat(option, trigger_low_value)
    elif option.startswith('62 '):
        trigger_low_value = getFloat(option, trigger_low_value)
        trigger_low_value = convertFtoC(trigger_low_value)
    elif option.startswith('63 '):
        trigger_low_seconds = getInt(option, trigger_low_seconds)

#     ble.start_advertising(advertisement)
#     print("Waiting to connect")
#     while not ble.connected:
#         pass
#     print("Connected")
#     while ble.connected:
#         s = uart.readline()
#         if s:
#             try:
#                 result = str(eval(s))
#             except Exception as e:
#                 result = repr(e)
#             uart.write(result.encode("utf-8"))
