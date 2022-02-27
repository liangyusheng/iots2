import time               # time moudle
import board, busio       # board and busio modules
from hiibot_iots2 import  IoTs2     # use the Button and BlueLED of IoTs2
iots2 = IoTs2()
iots2.blueLED_bright = 1.0          # turn on BlueLED
uart = busio.UART(
        board.IO17, board.IO18,     # two Pins(Tx, RxD)
        baudrate=115200,            # baudrate: 9600 is default
        timeout=0.01,               # waiting time(s) for read(nBytes), and readinto(buf, nBytes)
        receiver_buffer_size=1)     # size of buffer
uart.reset_input_buffer()           # clear input buffer
outBuf = bytearray(1)               # out buffer, uart.write(buf, nBytes)
print("Press the button to start game")
while True:
    iots2.button_update()        # update the Button State
    if iots2.button_wasPressed : # start our game, send a digit
        outBuf[0] = 0            # any digit: 0~255
        uart.write(outBuf, 1)    # send the first digit
        print("Go it! the first was sent")
    if uart.in_waiting>0:        # check input buffer isn't empty
        inBuf = uart.read(1)     # return a bytearray type
        if inBuf is not None :   # inBuf isn't None
            iots2.blueLED_toggle()      # toggle BlueLED (turn off)
            time.sleep(0.1)
            print( 'Rec: {}'.format(inBuf[0]) )
            if int(inBuf[0]) < 255:
                outBuf[0] = inBuf[0]+1  # increment and send this digit
            else:
                outBuf[0] = 0           # rollback: .., 254, 255, next 0
            uart.write(outBuf, 1)
            iots2.blueLED_toggle()      # toggle BlueLED (turn on)
            time.sleep(0.1)