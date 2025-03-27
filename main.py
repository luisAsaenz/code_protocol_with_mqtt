# import modules
from machine import UART
from machine import Pin
import time
import uasyncio as asyncio


MAX_MESSAGE_LEN=64
team = [b'a',b'b',b'c',b'd']
id = b'b' #tyler - c , alex - a, frank - d
broadcast = b'X'

# initialize a new UART class
uart = UART(2, 9600,tx=17,rx=16)
# run the init method with more details including baudrate and parity
uart.init(9600, bits=8, parity=None, stop=1) 
# define pin 2 as an output with name led. (Pin 2 is connected to the ESP32-WROOM dev board's onboard blue LED)
led = Pin(2,Pin.OUT)


def send_message(message):
    print('ESP: send message')
    if len(message)>MAX_MESSAGE_LEN:
        print('ESP: message too long')
        return
    if message[0:2] != b'AZ':
        print('ESP: message does not start with AZ')
        return
    if message[-2:] != b'YB':
        print('ESP: message does not end with YB')
        return
    if message[2:3] not in team:
        print('ESP: sender not in team')
        return
    if message[3:4] not in team:
        if message[3:4] == broadcast:
            pass
            
        else: print('ESP: receiver not in team')
        return
    if message[2:3] == id:
        uart.write(message)
        print('ESP: sending MY message')
    else:
        uart.write(message)
        print('ESP: sending team message')



    # send_queue.append(message)

def handle_message(message):
    my_string = message.decode('utf-8')
    if message[3:4] != id:
        if message[3:4] == broadcast:
            print('ESP: handling broadcast ', message)
        else:
            print('ESP: handling team message ')
            print(message)
            send_message(message)
    else:
        message_type = message[4]
        print('ESP: handling my message ',message)
        if message_type == 2:
            # Handle message type 2
            sensor_id = my_string[5]
            sensor_value = my_string[6]
            print('ESP: message contains sensor id and value')
            # Send to Wi-Fi publisher
            pass

        elif message_type == 5:
            # Handle message type 5
            subsystem_id = my_string[5]
            print('ESP: message contains subsystem that is experiencing error')
            pass

        elif message_type == 6:
            # Handle message type 6
            motor_status = message[5]
            print('ESP: message contains the status of motor')
            pass

        elif message_type == 7:
            # Handle message type 7
            sensor_status = message[5]
            print('ESP: message contains the status of sensor')
            pass

        else:
            print('ESP: unknown message type')

    
        


    

    


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
            if type(c) != bytes:
                c = bytes(c, 'utf-8')
            stream+=c
            try:
                if stream[-2:]==b'AZ':
                    # print('ESP: message start:')
                    message=stream[-2:-1] #add a to message
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
                
                message+=c #immediately after receiving_message == true, Z is added to message 


                if len(message)==3:
                    if not (message[2:3] in team):
                        print('ESP: sender not in team')
                        # get rid of message if sender not on team
                        stream=b''
                        receiving_message = False
                    else:
                        if message[2:3] == id:
                            print('ESP: receiving message from self. DELETING...')
                            stream=b''
                            receiving_message = False
                        else:
                            print('ESP: sender in team')

                if len(message)==4:
                    if not (message[3:4] in team):
                        print('ESP: receiver not in team')
                        # get rid of message if sender not on team
                        stream=b''
                        receiving_message = False
                    elif message[3:4] == broadcast:
                        print('ESP: receiving broadcast')
                    else:
                        print('ESP: receiver in team')

                if len(message)>MAX_MESSAGE_LEN:
                    receiving_message = False
                    print('ESP: Message too long, aborting')
                    message=b''


        await asyncio.sleep_ms(10)    

async def heartbeat():

    while True:
        print('ESP: sending heartbeat')
        uart.write(b'AZbaHello!YB')
        await asyncio.sleep(10)    



async def main():
    counter = 0
    while True:
        token = counter%10
        if token == 9: # MESSAGE TYPE1
            message = b'AZcd\x0130YB'
            send_message(message)
        if token == 10: # MESSAGE TYPE3
            message = b'AZbd\x03wifi is not communicatingYB'
        if token == 11: # MESSAGE TYPE4
            message = b'AZcd\x040YB'
        if token == 12: # MESSAGE TYPe5
            message = b'AZcd\x05bYB'
        if token == 13: # MESSAGE TYPe8
            message = b'AZcd\x08this is the broadcastYB'
        counter += 1
        await asyncio.sleep(1)

asyncio.create_task(process_rx())
asyncio.create_task(heartbeat())

try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()
