import time
import rtc
import wifi
import ipaddress
from hiibot_iots2 import IoTs2
import ssl
import wifi
import socketpool
import adafruit_requests

iots2 = IoTs2()
iots2.pixels[0] = (255,0,0)
iots2.pixels.show()

the_rtc = rtc.RTC()
response = None
weekDayAbbr = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

print('start scan APs')
for network in wifi.radio.start_scanning_networks():
    time.sleep(0.05)
    print("\t'%s'\t\tRSSI: %d\tChannel: %d" % (network.ssid, network.rssi, network.channel))
wifi.radio.stop_scanning_networks()
iots2.pixels[0] = (127,127,0)
iots2.pixels.show()
print('AP scanning Done')

try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

print("Connecting to %s" % secrets["ssid"])
wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected to %s!" % secrets["ssid"])

iots2.pixels[0] = (0,0,255)
iots2.pixels.show()
print("My IP address is {}".format(wifi.radio.ipv4_address))

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

response = requests.get("http://worldtimeapi.org/api/timezone/Asia/Shanghai", timeout=60.0)
iots2.pixels[0] = (0,255,255)
iots2.pixels.show()

rgb_gright = 0.1
def fadeRGB() :
    global rgb_gright
    rgb_gright += 0.005
    if rgb_gright>0.1:
        rgb_gright = 0.0
    iots2.pixels.brightness = rgb_gright
    iots2.pixels.show()
    time.sleep(0.1)

######### 4. Parse Date&Time from JSON #########
if response.status_code == 200:
    print("We got a NTP server")
    iots2.pixels[0] = (0,255,0)
    iots2.pixels.show()
    json = response.json()
    print(json)  # print all message
    current_time = json["datetime"]
    the_date, the_time = current_time.split("T")
    print(the_date)
    year, month, mday = [int(x) for x in the_date.split("-")]
    the_time = the_time.split(".")[0]
    print(the_time)
    hours, minutes, seconds = [int(x) for x in the_time.split(":")]
    # We can also fill in these extra nice things
    year_day = json["day_of_year"]
    week_day = json["day_of_week"]
    # Daylight Saving Time (夏令时)?
    is_dst = json["dst"] 
    now = time.struct_time(
        (year, month, mday, hours, minutes, seconds+1, week_day, year_day, is_dst) )
    the_rtc.datetime = now

    while True:
        print("  {}-{}-{}".format(
            the_rtc.datetime.tm_year,  
            the_rtc.datetime.tm_mon,  
            the_rtc.datetime.tm_mday, ) 
            )
        print("  " + weekDayAbbr[the_rtc.datetime.tm_wday])
        print("  {}:{}:{}".format(
            the_rtc.datetime.tm_hour, 
            the_rtc.datetime.tm_min, 
            the_rtc.datetime.tm_sec, ) 
            )
        ipv4 = ipaddress.ip_address('182.61.200.6')
        print('  ping', wifi.radio.ping(ipv4))
        for _ in range(520):
            fadeRGB()
else:
    print("Getting time failed")