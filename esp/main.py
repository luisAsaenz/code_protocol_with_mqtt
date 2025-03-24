# import modules
from machine import UART
from machine import Pin
import time
import uasyncio as asyncio


MAX_MESSAGE_LEN=64
team = [b'a',b'b',b'c',b'd']
id = b'a'
broadcast = 'X'

# initialize a new UART class
uart = UART(2, 9600,tx=17,rx=16)
# run the init method with more details including baudrate and parity
uart.init(9600, bits=8, parity=None, stop=1) 
# define pin 2 as an output with name led. (Pin 2 is connected to the ESP32-WROOM dev board's onboard blue LED)
led = Pin(2,Pin.OUT)


def send_message(message):
    print('ESP: send message')
    # send_queue.append(message)

def handle_message(message):
    my_string = message.decode('utf-8')
    print('ESP: handling my message',message)
    


async def process_rx():

    # stream = []
    stream = b''
    message = b''
    send_queue = []
    receiving_message=False

    while True:
        # read one byte
        c = uart.read(1)
        # if c is not empty:
        if c is not None:

            stream+=c
            try:
                if stream[-2:]==b'AZ':
                    # print('ESP: message start:')
                    message=stream[-2:-1]
                    receiving_message=True
            except IndexError:
                pass
            try:
                if stream[-2:]==b'YB':
                    message+=stream[-1:]
                    stream=b''
                    receiving_message = False
                    # print('ESP: message received:',message)
                    handle_message(message)
                    led.value(led.value()^1)
            
            except IndexError:
                pass
            
            if receiving_message:
                
                message+=c


                if len(message)==3:
                    if not (message[2:3] in team):
                        print('ESP: sender not in team')
                    else:
                        print('ESP: sender in team')

                if len(message)==4:
                    if not (message[3:4] in team):
                        print('ESP: receiver not in team')
                    else:
                        print('ESP: receiver in team')

                if len(message)>MAX_MESSAGE_LEN:
                    receiving_message = False
                    print('ESP: Message too long, aborting')
                    message=b''


        await asyncio.sleep_ms(10)    

async def heartbeat():

    while True:
        print('ESP: sending')
        uart.write(b'AZabHello!YB')
        await asyncio.sleep(10)    



async def main():
    while True:
        await asyncio.sleep(1)

asyncio.create_task(process_rx())
asyncio.create_task(heartbeat())

try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()
