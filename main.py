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
    # if len(message)>MAX_MESSAGE_LEN:
    #     print('ESP: message too long')
    #     return
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
            print(f'ESP: sending broadcast message ---> {message}')
            uart.write(message)

            pass
            
        else:
            print('ESP: receiver not in team')
        return
    # if len(message)>MAX_MESSAGE_LEN:
    #     print(f'ESP: message is too long: {message}')
    #     print(f'ESP: not sending message. Deleting message.')
    #     return
    if message[2:3] == id:
        uart.write(message)
        print('ESP: sending MY message ', message)
    else:
        uart.write(message)
        print('ESP: sending team message ', message)



    # send_queue.append(message)

def handle_message(message):
    my_string = message.decode('utf-8')
    if message[3:4] != id and message[3:4] != broadcast: ## checks if receiver is not my id or the broadcast
       
        print(f'ESP: handling team message {message}')
        send_message(message)
    else:
        # if broadcast message and message type is 8 then pass message if not handle message normally then pass broadcast
        message_type = message[4]
        if message[3:4] == broadcast and message_type == 8:
            print('ESP: passing broadcast ', message)
            send_message(message)
        else: 
            if message[3:4] == broadcast:
                print('ESP: handling broadcast ', message)
            else:
                print(f'ESP: handling my message {message}')
            if message_type == 2:
                # Handle message type 2
                sensor_id = my_string[5]
                sensor_value = message[6]
                if sensor_value > 100:
                    print('ESP: sensor value is too out of range')
                    return
                else:
                    print(f'ESP: message contains sensor {sensor_id} value: {sensor_value}')
                # Send to Wi-Fi publisher
                pass

            elif message_type == 5:
                # Handle message type 5
                subsystem_id = my_string[5]
                print(f'ESP: subsystem {subsystem_id} that is experiencing error')
                pass

            elif message_type == 6:
                # Handle message type 6
                motor_status = message[5]
                if motor_status == 0:
                    print('ESP: Motor is not down.')
                elif motor_status == 1:
                    print('ESP: Motor is up.')
                else: 
                    print('ESP: Motor status is unknown.')

            elif message_type == 7:
                # Handle message type 7
                sensor_status = message[5]
                if sensor_status == 0:
                    print('ESP: Sensor is not down.')
                elif sensor_status == 1:
                    print('ESP: Sensor is up.')
                else: 
                    print('ESP: Sensor status is unknown.')
                pass

            else:
                print('ESP: unknown message type.')
            if message[3:4] == broadcast:
                print('ESP: broadcast messaged handled, passing broadcast.')
                send_message(message)
            else:
                print(f'ESP: Message, {message} ,  handled. Deleting message..')

    
        


    

    


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
                    message=stream[-2:-1] #add a to message
                    receiving_message=True
            except IndexError:
                pass
            try:
                if stream[-2:]==b'YB':
                    if receiving_message == False:
                        message=b''
                        pass
                    else:
                        message+=stream[-1:]
                        receiving_message = False
                        print('ESP: message received:',message)
                        handle_message(message)
                    stream=b''

                    led.value(led.value()^1)
            
            except IndexError:
                pass
            
            if receiving_message:
                
                message+=c #immediately after receiving_message == true, Z is added to message
                #print(message) 
                #print(c)


                if len(message)==3:
                    if  (message[2:3] not in team):
                        print('ESP: sender not in team ------>  ')
                        print(c)

                        # get rid of message if sender not on team
                       # message=b''
                        receiving_message = False
                    else:
                        if message[2:3] == id:
                            print('ESP: receiving message from self. DELETING...')
                          #  message=b''
                            receiving_message = False
                        else:
                            print('ESP: sender in team')

                if len(message)==4:
                    if  (message[3:4] not in team):
                        
                        # get rid of message if sender not on team
                        #message=b''
                        if message[3:4] == broadcast:
                            print('ESP: receiving broadcast')
                        else:
                            print('ESP: receiver not in team')
                            receiving_message = False
                    else:
                        print('ESP: receiver in team')

                if len(message)>MAX_MESSAGE_LEN:
                    receiving_message = False
                    print('ESP: Message too long, aborting')
                    message=b''


        await asyncio.sleep_ms(10)    

async def heartbeat():

    token= 0

    while token == 0:
        token = 1
        print('ESP: sending heartbeat')
        uart.write(b'AZba\x08Hello!YB')
        print('ESP: heartbeat sent')

        await asyncio.sleep(10)    



async def main():
    counter = 0
    while True:
        token = counter%100
        
        if token == 9: # MESSAGE TYPE1
            message = b'AZcd\x0130dfdsgrejhv dfjhgdlkfjhvldkfj fjklhguieoeh dfhuigb dfjfdgfdgsdfgdfgdffYB'
            send_message(message)
    
        if token == 11: # MESSAGE TYPE3
            message = b'AZbX\x03wifi is not communicatingYB'       
            send_message(message)

        if token == 15: # MESSAGE TYPE2
            message = b'AZcb\x021\x10YB'
            send_message(message)

        if token == 22: # MESSAGE TYPE6
            message = b'AZcX\x08this is broadcastYB'
            send_message(message)

        # if token == 40: # MESSAGE TYPE4
        #     message = b'AZcb\x040YB'
        #     send_message(message)

        # if token ==  45: # MESSAGE TYPe5
        #     message = b'AZbd\x05bYB'
        #     send_message(message)

        # if token == 50: # MESSAGE TYPe8
        #     message = b'AZcX\x08this is the broadcastYB'
        #     send_message(message)
        

        counter += 1
        await asyncio.sleep(1)

asyncio.create_task(process_rx())
#asyncio.create_task(heartbeat())

try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()
