import time
import wifi
import socketpool 
from secrets import secrets  # hold your AP name and password
MAXBUF = 256
print("Connecting to a AP ..")  # connect to wifi
wifi.radio.connect(secrets["ssid"], secrets["password"])
pool = socketpool.SocketPool(wifi.radio)
print("Connected! my IP: {}".format(wifi.radio.ipv4_address))
# make a native socket to creat a UDP Server
sock_udp = pool.socket(pool.AF_INET, pool.SOCK_DGRAM)  # SOCK_STREAM, SOCK_RAW
# UDP Server (Host): name, and port 
udpHostName = str(wifi.radio.ipv4_address)
udpHostPort = 1688
print("Creat a UDP Server")
sock_udp.settimeout( None )  # timeout must be set into None! 
sock_udp.bind( (udpHostName, udpHostPort) )
buf = bytearray(MAXBUF)
while True:
    # listen, and receive a datagram from a UDP Client
    size, udpClient = sock_udp.recvfrom_into(buf)
    print("Received", buf[:size], size, "bytes from", udpClient)
    # it is very important: change the byte-order of UDP Client port
    cp = udpClient[1]  # udp client port 
    nbo_cp = ((cp>>8)&0x00FF) + ((cp<<8)&0xFF00)  # change the byte-order
    # give a ACK (Reply)
    size = sock_udp.sendto(buf[:size], (udpClient[0], nbo_cp) )
    print("Sent", buf[:size], size, "bytes to", udpClient)
    time.sleep(0.1)
