import time
import wifi
import socketpool 
from secrets import secrets     # hold your AP name and password
MAXBUF = 255
buf_tcp  = bytearray(MAXBUF)    # the received buffer for TCP server 
tcpServerName = '192.168.1.107' # modify this ipv4 address
tcpServerPort = 1988            # modify this port
# make a Wi-Fi connect firstly!
print("Connecting to a AP ..")  # connect to wifi
try:
    wifi.radio.connect(secrets["ssid"], secrets["password"])
except ConnectionError:
    print("Please check /CIRCUITPY/secrets.py")
    raise ConnectionError("No network with that ssid or error password")
print("Connected! my IP: {}".format(wifi.radio.ipv4_address))
# create a socketpool (Socket池!) with the Wi-Fi connect
pool = socketpool.SocketPool(wifi.radio)
# make a native socket to connect a TCP Server (ipv4 be used)
sock_tcp = pool.socket(pool.AF_INET, pool.SOCK_STREAM)  # SOCK_DGRAM, SOCK_STREAM, SOCK_RAW
sock_tcp.settimeout( 5 )  # timeout must be set into 5 seconds 
tcpServer = pool.getaddrinfo(tcpServerName, tcpServerPort)[0][4]
print("Connecting a TCP Server:", tcpServer)
sock_tcp.connect( tcpServer )
print('Connected to ', tcpServer)
while True:
    # using TCP has a problem: the TCP disconnected from Server!
    try:
        sock_tcp.settimeout( 0.1 )
        numsRecv = sock_tcp.recv_into(buf_tcp, MAXBUF)
        print("Received", buf_tcp[:numsRecv], numsRecv, "bytes from", tcpServer)
        numsSend = sock_tcp.send(buf_tcp[:numsRecv])
        print("Send", buf_tcp[:numsSend], numsSend, "bytes to", tcpServer)
    except:
        time.sleep(0.1)  # timeout then wait some time
        pass
