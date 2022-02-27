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
iots2.screen.rotation = 270

ssid = ""
passwd = ""
tcp_port = 7788
MAXBUF = 255
refresh = 1

text_group = displayio.Group()
def text_info():
    host_txt            = label.Label(terminalio.FONT, x=10, y=10,  text="", scale=2, color=(255, 0, 0))
    uptime_txt          = label.Label(terminalio.FONT, x=10, y=30,  text="", scale=1, color=(100, 100, 50))
    ip_txt              = label.Label(terminalio.FONT, x=10, y=45,  text="", scale=1, color=(0, 255, 0))
    cpu_model_txt       = label.Label(terminalio.FONT, x=10, y=60,  text="", scale=1, color=(230, 252, 0))
    cpu_temp_txt        = label.Label(terminalio.FONT, x=10, y=75,  text="", scale=1, color=(0, 252, 243))
    cpu_freq_txt        = label.Label(terminalio.FONT, x=10, y=90,  text="", scale=1, color=(252, 0, 229))
    mem_available_txt   = label.Label(terminalio.FONT, x=10, y=105, text="", scale=1, color=(59, 255, 0))
    mem_max_txt         = label.Label(terminalio.FONT, x=10, y=120, text="", scale=1, color=(251, 251, 251))
    
    text_group.append(host_txt)
    text_group.append(uptime_txt)
    text_group.append(ip_txt)
    text_group.append(cpu_model_txt)
    text_group.append(cpu_temp_txt)
    text_group.append(cpu_freq_txt)
    text_group.append(mem_available_txt)
    text_group.append(mem_max_txt)
    
    return host_txt, uptime_txt, ip_txt, cpu_model_txt, cpu_temp_txt, cpu_freq_txt, mem_available_txt, mem_max_txt

def parse_msg(msg):
    info            = msg.split("#")
    hostname        = info[0]
    uptime          = info[1]
    ip              = info[2]
    cpu_model       = info[3]
    cpu_temp        = info[4]
    cpu_freq        = info[5]
    mem_available   = info[6]
    mem_max         = info[7]
    return hostname, uptime, ip, cpu_model, cpu_temp, cpu_freq, mem_available, mem_max

def tcp_server():
    # make a Wi-Fi connect firstly!
    print("Connecting to a AP ..")  # connect to wifi
    try:
        wifi.radio.connect(ssid, passwd)
    except ConnectionError:
        print("Please check ssid and passwd!")
        return
    print("Connected!\nmy IP: {}".format(wifi.radio.ipv4_address))
    print("port: ", tcp_port)
    # create a socketpool (Socket池!) with the Wi-Fi connect
    pool = socketpool.SocketPool(wifi.radio)
    # make a native socket to creat a TCP Server (ipv4 be used)
    sock_tcp = pool.socket(
        pool.AF_INET, pool.SOCK_STREAM
    )  # SOCK_DGRAM, SOCK_STREAM, SOCK_RAW
    # TCP Server (Host): name, and port
    print("Creat a TCP Server")
    tcpServerName = str(wifi.radio.ipv4_address)
    tcpServerPort = tcp_port
    sock_tcp.settimeout(None)  # timeout must be set into None!
    sock_tcp.bind((tcpServerName, tcpServerPort))
    print("Waiting for a TCP Client")
    # sock_tcp.setblocking(False)
    sock_tcp.listen(1)  # waiting for a connect
    connectSocket, clientAddr = sock_tcp.accept()
    print("a TCP client be acceptted (IP): ", clientAddr)
    buf_tcp = bytearray(MAXBUF)  # the received buffer for TCP server

    iots2.screen.show(text_group)
    host_txt, uptime_txt, ip_txt, cpu_model_txt, cpu_temp_txt, cpu_freq_txt, mem_available_txt, mem_max_txt = text_info()

    send_buf  = bytearray(MAXBUF)
    send_buf = 'OK'
    while True:
        try:
            sock_tcp.settimeout(0.5)
            numsReceived = connectSocket.recv_into(buf_tcp)
            hostname, uptime, ip, cpu_model, cpu_temp, cpu_freq, mem_available, mem_max = parse_msg(bytearray.decode(buf_tcp[:numsReceived]))
            # print(bytearray.decode(buf_tcp[:numsReceived]))
            
            host_txt.text           = "host: "      + hostname
            uptime_txt.text         = "uptime: "    + str(float(uptime.split(' ')[0]) / 60 / 60 / 24) + " day(s)"
            ip_txt.text             = "IP: "        + ip
            cpu_model_txt.text      = "CPU Model: " + cpu_model
            cpu_temp_txt.text       = "CPU Temp:  " + str(int(cpu_temp) / 1000) + " C"
            cpu_freq_txt.text       = "CPU freq:  " + str(int(cpu_freq) / 1000) + " MHz"
            mem_available_txt.text  = "Memory available: " + str(int(mem_available) / 1024) + " MiB"
            mem_max_txt.text        = "Total memory:     " + str(int(mem_max) / 1024) + " MiB"

            # 向客户端返回 OK，客户端收到后进行下一次发送。
            connectSocket.send(send_buf)
            time.sleep(refresh)
        except:
            time.sleep(refresh)

def main():
    tcp_server()

########################################

if __name__ == "__main__":
    main()
