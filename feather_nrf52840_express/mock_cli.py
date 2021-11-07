
import random
from threading import Thread
from time import sleep
# from adafruit_ble import BLERadio
# from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
# from adafruit_ble.services.nordic import UARTService

# ble = BLERadio()
# uart = UARTService()
# advertisement = ProvideServicesAdvertisement(uart)

samples = {}
count = 0
rate = 1
pause = False

result = None

def sample_thread():
    global count
      
    while True:
        sleep(rate)
        if not pause:
            samples[count] = random.uniform(0, 3.3)
            count = count + 1

# possible options
#     0  help
#     1  info
#     2  sample rate (seconds)
#     3  start
#     4  pause
#     5  stop
#     6  dump
#     7  reset
#     8  alarm enable
#     9  alarm high enable
#     10 alarm high threshold
#     11 alarm low enable
#     12 alarm high threshold
#     13 alarm led enable
#     14 alarm beacon enable
#     15 last as C
#     16 last as F
#     17 last as raw

def Help():
    print('0, h, ? - help')
    print('1, i - info')
    print('7, r - reset')

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
t = Thread(target=sample_thread)
t.start()

while True:
    print('> ')
    option = input()
    if option == '0' or option == 'h' or option == '?':
        Help()
    elif option == '1' or option == 'i':
        Info()
    elif option == '7' or option == 'r':
        Reset()

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
