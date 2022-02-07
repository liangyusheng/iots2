import time               # time moudle
import random
import board, busio       # board and busio modules
from hiibot_iots2 import  IoTs2     # use the Button and BlueLED of IoTs2
iots2 = IoTs2()
iots2.blueLED_bright = 1.0          # turn on BlueLED
uart = busio.UART(
        board.IO3, board.IO4,       # two Pins(Tx, RxD)
        baudrate=115200,            # baudrate: 9600 is default
        timeout=0.01,               # waiting time(s) for read(nBytes), and readinto(buf, nBytes)
        receiver_buffer_size=10)    # size of buffer
uart.reset_input_buffer()           # clear input buffer
outBuf = bytearray(1)               # out buffer, uart.write(buf, nBytes)
print("Press the button to send a Cmd")
# send the formated data frame: STX, CMD, Len, Data Field, ECC, ETX
# given CMD, LEN, Data Field, then calculate ECC and append it on the frame
def send(bytes, nBytes):
    global uart
    if nBytes<2:
        return
    if nBytes>5:
        nBytes = 5
    sbuf = bytearray(b'\xA5\x5A')
    ecc = 0x0
    for i in range(nBytes):
        sbuf.append( bytes[i] )  # append a byte on the sbuf
        ecc ^= bytes[i]
    sbuf.append(ecc)
    sbuf.append(0x0A)
    sbuf.append(0x0D)
    uart.write(sbuf, nBytes+5)
# send a response
def sendAck(cmd):
    sb = bytearray(b'\x00\x00')
    sb[0] = cmd
    send(sb, 2)
# send a error response
def sendErrorAck(errorCode):
    sb = bytearray(b'\x45\x01\x00')
    sb[2] += errorCode
    send(sb, 3)
    print('Recv failed{}'.format(errorCode))
# check the readable bytes of received buffer, then read and resolve it
def recv():
    global uart
    rbuf = bytearray(5)
    if uart.in_waiting<1:
        return None
    else:
        tryTimes = 0
        while True:
            time.sleep(0.1)
            if uart.in_waiting>=7:
                break
            tryTimes += 1
            if tryTimes>3:
                uart.reset_input_buffer()
                return None
        time.sleep(0.02)
        rBytes = uart.in_waiting   # check the valid bytes
        rb = uart.read(rBytes)     # read the data frame
        if rb[0]!=0xA5 or rb[1]!=0x5A or rb[-2]!=0x0A or rb[-1]!=0x0D:
            sendErrorAck(0x01)
            return None
        ecc = 0x00
        for i in range(rBytes-5):
            rbuf[i] = rb[2+i]
            ecc ^= rbuf[i]
        if rb[-3]!=ecc:
            sendErrorAck(0x02)
            return None
        if rbuf[0]!=0x41 and rbuf[0]!=0x42 and rbuf[0]!=0x43 and rbuf[0]!=0x45:
            sendErrorAck(0x03)
            return None
        return rbuf
# resolve received data frame, and execute some action
def resolving(rbuf):
    nBytes = len(rbuf)
    if nBytes>=2:
        if rbuf[0]==0x41:
            sendAck(0x41)
            print('Recv Cmd 0x{:02X}, send Ack'.format(rbuf[0]))
        elif rbuf[0]==0x42:
            if rbuf[1]==0x02:
                sendAck(0x42)
                print('Recv Cmd 0x{:02X}, send Ack'.format(rbuf[0]))
            else:
                print('this 0x{:02X} response'.format(rbuf[0]))
        else: # rbuf[0]==0x43
            if rbuf[1]==0x03:
                sendAck(0x43)
                print('Recv Cmd 0x{:02X}, send Ack'.format(rbuf[0]))
            else:
                print('this 0x{:02X} response'.format(rbuf[0]))
    else:
        pass
sFrame = (  bytearray(b'\x41\x00'), 
            bytearray(b'\x42\x02\x02\x45'), 
            bytearray(b'\x43\x03\x12\x34\x56') )
nFrame = (2, 4, 5)
while True:
    iots2.button_update()        # update the Button State
    if iots2.button_wasPressed : # start our game, send a digit
        uart.reset_input_buffer()
        rd = random.randint(0,2) # only {0, 1, 2}
        send(sFrame[rd], nFrame[rd])
        print('send Cmd 0x{:02X} ok'.format(sFrame[rd][0]))
    recbuf = recv()
    if recbuf is not None:
        resolving(recbuf)
    time.sleep(0.01)