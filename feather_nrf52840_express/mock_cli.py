
import random
import threading
import time


# from adafruit_ble import BLERadio
# from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
# from adafruit_ble.services.nordic import UARTService

# ble = BLERadio()
# uart = UARTService()
# advertisement = ProvideServicesAdvertisement(uart)

samples = {}
count = 0
count_max = 100
count_rollover = 0
count_rate = 1
pause = False

result = None

def sample_thread():
    global count
      
    while True:
        time.sleep(count_rate)
        if not pause:
            seconds = time.time()
            if count >= count_max:
                count_rollover = count_rollover + 1
                count = 0
                samples = {} # TODO: create rollover instead of reset

            samples[seconds] = random.uniform(0, 3.3)
            count = count + 1

def Help():
    # help
    print('0,h,? - help')
    print('1,i   - info ')
    # measure
    print('10 - last raw/C/F')
    print('11 - last distance raw/cm/inches')
    # sampling
    print(f'20 - max samples (default {count_max})')
    print(f'21 - sample rate (default {count_rate})')
    print('22,s - start')
    print('23,t - stop')
    print('24,p - pause')
    print('25,r - reset')
    # dump
    print('30 - dump to serial - raw')
    print('31 - dump to serial - C')
    print('32 - dump to serial - F (default)')
    # alarms
    print('40 - battery led slow blink (default 1)')
    print('41 - threshold alarm led fast blink (default 1)')
    # triggers
    print('50 - temp high threshold - raw (default TBD)')
    print('51 - temp high threshold - C   (default TBD)')
    print('52 - temp high threshold - F   (default TBD)')
    print('53 - temp high seconds         (default TBD)')
    print('60 - temp low  threshold - raw (default TBD)')
    print('61 - temp low  threshold - C   (default TBD)')
    print('62 - temp low  threshold - F   (default TBD)')
    print('63 - temp low  seconds         (default TBD)')

def Info():
    print(f'rate: {rate}')
    print(f'samples: {count}')

def Reset():
    global count
    global samples
    global pause

    saved = pause
    pause = True
    count = 0
    samples = {}
    pause = saved


# Setup
t = threading.Thread(target=sample_thread)
t.start()

while True:
    print('> ')
    option = input()
    if option == '0' or option == 'h' or option == '?':
        Help()
    elif option == '1' or option == 'i':
        Info()
    elif option == '10':
        LastTemp()
    elif option == '11':
        LastDistance()
    elif option.starts_with('20 '): # max samples <count>
        try:
            parts = options.split()
            count_max = parts[1]
        except:
            print('bad value')
    elif option.starts_with('20 '): # sample rate <seconds>
        try:
            parts = options.split()
            count_rate = parts[1]
        except:
            print('bad value')
    elif option == '22' or option == 's':
        Start()
    elif option == '23' or option == 't':
        Stop()
    elif option == '24' or option == 'p':
        Pause()
    elif option == '25' or option == 'r':
        Reset()

    # # dump
    # print('30 - dump to serial - raw')
    # print('31 - dump to serial - C')
    # print('32 - dump to serial - F (default)')
    # # alarms
    # print('40 - battery led slow blink (default 1)')
    # print('41 - threshold alarm led fast blink (default 1)')
    # # triggers
    # print('50 - temp high threshold - raw (default TBD)')
    # print('51 - temp high threshold - C   (default TBD)')
    # print('52 - temp high threshold - F   (default TBD)')
    # print('53 - temp high seconds         (default TBD)')
    # print('60 - temp low  threshold - raw (default TBD)')
    # print('61 - temp low  threshold - C   (default TBD)')
    # print('62 - temp low  threshold - F   (default TBD)')
    # print('63 - temp low  seconds         (default TBD)')



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
