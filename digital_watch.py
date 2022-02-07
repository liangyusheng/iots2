import ssl
import rtc
import wifi
import time
import random
import displayio
import ipaddress
import terminalio
import socketpool
import adafruit_requests
from hiibot_iots2 import IoTs2
from adafruit_display_text import label

iots2 = IoTs2()

class MyIoTs2():
    __ssid = ""
    __ip_address = ""
    __pool = socketpool.SocketPool(wifi.radio)
    __temperature = ""
    __run_time = 0
    __boot_time = ""

    def __init__(self):
        wifi.radio.enabled = True
        self.__requests = adafruit_requests.Session(self.__pool, ssl.create_default_context())
    
    def set_rotation(rotation):
        iots2.screen.rotation = rotation
    
    @staticmethod
    def lcd(on):
        if on:
            iots2.blueLED_bright = 1.0
        elif not on:
            iots2.blueLED_bright = 0.05
                    
    @staticmethod
    def set_rgb_color(color):
        iots2.pixels.auto_write = True
        iots2.pixels.brightness = 0.03
        colorsList = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))]
        iots2.pixels[0] = colorsList[color]
        
    def connect2Wifi(self, ssid, passwd):
        while not wifi.radio.ipv4_address:
            wifi.radio.connect(ssid, passwd)
        self.__ssid = str(wifi.radio.ap_info.ssid, 'utf-8')
        print("SSID: \t\t", self.__ssid)
        self.__ip_address = wifi.radio.ipv4_address
        print("IP: \t\t", self.__ip_address)
    
    def get_ip_addr(self):
        return str(self.__ip_address)
    
    def get_timestamp(self):
        url = r'http://worldtimeapi.org/api/timezone/Asia/Shanghai'
        response = self.__requests.get(url, timeout=60.0)
        print("status code: \t\t", response.status_code)
        if response.status_code != 200:
            print("getting time failed!")
        json = response.json()
        # print(json)
        timestamp = json['datetime']
        # print(timestamp)
        return timestamp


    def get_tempmperature(self):
        url = r'http://worldtimeapi.org/api/timezone/Asia/Shanghai'
        response = self.__requests.get(url, timeout=60.0)
        print("status code: \t\t", response.status_code)
        if response.status_code != 200:
            print("getting tempmperature failed!")
        json = response.json()
        # print(json)
        timestamp = json['datetime']
        # print(timestamp)
        return timestamp
    
    def timestamp2local(self, timestamp):
        date, time = timestamp.split("T")
        time = time.split('.')[0]
        self.__boot_time = date + " " + time
        return date, time
    
    @staticmethod
    def clock(date_str, time_str):
        y, m, d = str(date_str).split("-")
        h, mi, s = str(time_str).split(":")
        
        time.sleep(1)
        s = int(s, 10) + 1
        
        nmi = int(mi, 10)
        nh  = int(h,  10)
        nd  = int(d,  10)
        if (s == 60):
            nmi = nmi + 1
            s = 0
            if (nmi == 60):
                h = nh + 1
                nmi = 0
                if (nh != 24):
                    nh += 1
                if (nh == 24):
                    nh = 0
                    nd += 1
        if (s <= 9):
            s = str("0") + str(s)
        
        mi = str(nmi)
        if (nmi <= 9):
            mi = str("0") + mi

        h = str(nh)
        if (nh <= 9):
            h = str("0") + h

        d = str(nd)
        if (nd <= 9):
            d = str("0") + d
            
        date_str = y + "-" + m  + "-" + d
        time_str = h + ":" + mi + ":" + str(s)
        return date_str, time_str            
    
    def show_info(self, date_str, time_str):
        text_group = displayio.Group()
        tempmperature = label.Label(terminalio.FONT, x=2, y=8,  text="", scale = 1, color=(255, 0, 127))
        ssid = label.Label(terminalio.FONT, x=120,  y=8,  text="", scale = 1, color=(170, 85, 127))
        ip   = label.Label(terminalio.FONT, x=120,  y=20,  text="", scale = 1, color=(0,255,0))
        date = label.Label(terminalio.FONT, x=58, y=45, text="", scale = 2, color=(255, 85, 0))
        time = label.Label(terminalio.FONT, x=45, y=80, text="", scale = 3, color=(200,50,180))
        boot_time = label.Label(terminalio.FONT, x=2, y=120, text="", scale = 1, color=(170,255,0))
        work_time = label.Label(terminalio.FONT, x=2, y=130, text="", scale = 1, color=(100,150,220))

        text_group.append(tempmperature)
        text_group.append(ssid)
        text_group.append(ip)
        text_group.append(date)
        text_group.append(time)
        text_group.append(boot_time)
        text_group.append(work_time)
        iots2.screen.show(text_group)
        color = 0
        while True:
            d, t = MyIoTs2.clock(date_str, time_str)
            MyIoTs2.set_rgb_color(color)
            MyIoTs2.lcd(int(t.split(":")[2]) % 2)
            #ip.text   = "IP: " + str(self.__ip_address)
            tempmperature.text = "tempmperature: " + self.__temperature
            ssid.text = "SSID: " + self.__ssid
            ip.text = "IP: " + str(self.__ip_address)
            date.text = d
            time.text = t
            boot_time.text = "boot time: " + self.__boot_time
            work_time.text = "has been running for " + str(self.__run_time) + " seconds"
            date_str  = d
            time_str  = t
            self.__run_time += 1
            color += 1
            if (color == 6):
                color = 0
            
def main():
    MyIoTs2.set_rotation(270)

    my_iots2 = MyIoTs2()
    my_iots2.connect2Wifi('your-wifi-ssid', 'your-wifi-password')
    timestamp = my_iots2.get_timestamp()
    date_str, time_str = my_iots2.timestamp2local(timestamp)
    my_iots2.show_info(date_str, time_str)
    #my_iots2.show_info("2020-12-12", "23:59:57")

if __name__ == '__main__':
    main()
