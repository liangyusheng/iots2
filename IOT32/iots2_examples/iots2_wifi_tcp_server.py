import time
import wifi
import socketpool 
from secrets import secrets     # hold your AP name and password
MAXBUF = 255
buf_tcp  = bytearray(MAXBUF)    # the received buffer for TCP server 
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
# make a native socket to creat a TCP Server (ipv4 be used)
sock_tcp = pool.socket(pool.AF_INET, pool.SOCK_STREAM)  # SOCK_DGRAM, SOCK_STREAM, SOCK_RAW
# TCP Server (Host): name, and port 
print("Creat a TCP Server")
tcpServerName = str(wifi.radio.ipv4_address)
tcpServerPort = 1888
sock_tcp.settimeout( None )  # timeout must be set into None! 
sock_tcp.bind( (tcpServerName, tcpServerPort) )
print("Waiting for a TCP Client")
#sock_tcp.setblocking(False)
sock_tcp.listen(1)  # waiting for a connect
connectSocket, clientAddr = sock_tcp.accept()
print("a TCP client be acceptted (IP): ", clientAddr)
while True:
    try:
        sock_tcp.settimeout( 0.1 )
        numsReceived = connectSocket.recv_into(buf_tcp)
        print("Received", buf_tcp[:numsReceived], numsReceived, "bytes from", clientAddr)
        numsSent = connectSocket.send(buf_tcp[:numsReceived])
        print("Send", buf_tcp[:numsSent], numsSent, "bytes to", clientAddr)
    except:
        time.sleep(0.1)
    #connectSocket.close()
