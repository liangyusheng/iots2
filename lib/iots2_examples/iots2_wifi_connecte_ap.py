from hiibot_iots2 import IoTs2
import wifi
import time
iots2 = IoTs2()
iots2.pixels[0] = (255,0,0) # red
iots2.pixels.show()

### connecte to a WiFi AP (AP name and password in secrets.py) ###
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

iots2.pixels[0] = (128,128,0) # yellow
iots2.pixels.show()

print("Connecting to %s" % secrets["ssid"])
wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected to %s!" % secrets["ssid"])

iots2.pixels[0] = (0,0,255) # blue
iots2.pixels.show()
time.sleep(2.0)

print("program done")