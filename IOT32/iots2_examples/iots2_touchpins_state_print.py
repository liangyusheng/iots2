import time
import board
from touchio import TouchIn
#from hiibot_iots2 import IoTs2
#iots2 = IoTs2()
# list of the Touched Pins
touchPins = [TouchIn(board.IO3),  TouchIn(board.IO4), 
             TouchIn(board.IO7),  TouchIn(board.IO8),
             TouchIn(board.IO9), TouchIn(board.IO10),
             TouchIn(board.IO11), TouchIn(board.IO12)]
# set their threshold (default threshold be equal to 300 + "initial raw_value")
for i in range(8):
    threshold = touchPins[i].raw_value
    touchPins[i].threshold = threshold+300
while True:
    for i in range(8):  # scan all touchPins
        if touchPins[i].value:
            print("touchPin-{} be touched".format(i))
            time.sleep(0.2)
