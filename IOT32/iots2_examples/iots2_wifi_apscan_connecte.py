import time
import wifi
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
iots2.screen.rotation = 270  # rotate IoTs2 screen 
iots2.pixels[0] = (255,0,0)  # show RED color
avaliableAP_list = []  # to save the avaliable APs
print('start to scan APs')
for network in wifi.radio.start_scanning_networks():
    time.sleep(0.05)
    print("\t'%s'\t\tRSSI: %d\tChannel: %d" % (network.ssid, network.rssi, network.channel))
    avaliableAP_list.append( network.ssid ) # append the AP to the list
wifi.radio.stop_scanning_networks()  # stop scan
iots2.pixels[0] = (127,127,0) # show YELLOW color
print('AP scanning Done')
try:
    from secrets import secrets # import secrets.py module
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise
theAP = None
for ap in avaliableAP_list:  # check avaliable APs
    if ap==secrets["ssid"]:
        theAP = ap
        break
if theAP==None:
    print("Not this AP, please to modify the secrects.py")
    iots2.pixels[0] = (255,0,0)  # show RED color
    while True:
        pass
elif not wifi.radio.ipv4_address:
    macaddr = 'My MAC Address: 0x'
    for addr in wifi.radio.mac_address:
        macaddr += '{:02X}'.format(addr) 
    print( macaddr )
    print("Connecting to WiFi AP (SSID: %s) ..." % secrets["ssid"])
    print("Connecting to %s" % secrets["ssid"])
    wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected to %s!" % secrets["ssid"]) 
iots2.pixels[0] = (0,0,255) 
print("My IP address is {}".format(wifi.radio.ipv4_address))
while True:
    time.sleep(10)