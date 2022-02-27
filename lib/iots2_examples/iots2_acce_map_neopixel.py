"""
We will see the NeoPixels light up in colors related to the accelerometer! 
The accelerometer on the BlueFi that returns (x, y, z) acceleration values.
This program uses those values to light up the NeoPixels 
"""
# import IoTs2 class from hiibot_iots2.py
from hiibot_iots2 import IoTs2
# instantiate IoTs2 as iots2
iots2 = IoTs2()
# map acceleration values (-10.24~10.24) into 0~255
def map(v):
    #return  int((v/10.24)*127.0) + 127
    return  abs( int((v/10.24)*255.0) )
# Main loop gets x, y and z axis acceleration, prints the values, and turns on
# red, green and blue, at levels related to the x, y and z values.
while True:
    x, y, z = iots2.Accele_ms2 # unit with ms^2 
    iots2.pixels[0] = ( map(x), map(y), map(z) )
