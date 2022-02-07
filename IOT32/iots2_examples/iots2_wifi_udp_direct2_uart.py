import time
import board, busio          # board and busio modules
import wifi
import socketpool 
from secrets import secrets  # hold your AP name and password
MAXBUF = 255
buf_udp  = bytearray(MAXBUF) # the received buffer for UDP server 
buf_uart = bytearray(MAXBUF) # the received buffer for UART
udpRemote = ["", 1024]       # ["IPv4", port]
# creat a UART (serial bus)
uart = busio.UART(
        board.IO3, board.IO4,         # two Pins(Tx, RxD)
        baudrate=115200,              # baudrate: 9600 is default
        timeout=0.01,                 # waiting time(s) for read(nBytes), and readinto(buf, nBytes)
        receiver_buffer_size=MAXBUF)  # size of buffer
uart.reset_input_buffer()             # clear input buffer
# make a Wi-Fi connect firstly!
print("Connecting to a AP ..")  # connect to wifi
try:
    wifi.radio.connect(secrets["ssid"], secrets["password"])
except ConnectionError:
    print("Please check /CIRCUITPY/secrets.py")
    raise ConnectionError("No network with that ssid or error password")
# create a socketpool (Socket池!) with the Wi-Fi connect
pool = socketpool.SocketPool(wifi.radio)
print("Connected! my IP: {}".format(wifi.radio.ipv4_address))
# make a native socket to creat a UDP Server (ipv4 be used)
sock_udp = pool.socket(pool.AF_INET, pool.SOCK_DGRAM)  # SOCK_DGRAM, SOCK_STREAM, SOCK_RAW
# UDP Server (Host): name, and port 
print("Creat a UDP Server")
udpHostName = str(wifi.radio.ipv4_address)
udpHostPort = 1688
sock_udp.settimeout( None )  # timeout must be set into None! 
sock_udp.bind( (udpHostName, udpHostPort) )
# Pass-Through transaction: UDP datagram <----> UART data frame
while True:
    # check UDP datagram and relay to UART
    try:
        # listen, and receive a datagram from a UDP Client
        sock_udp.settimeout( 0.05 )
        size, udpClient = sock_udp.recvfrom_into(buf_udp)
        udpRemote[0] = udpClient[0]
        # send the buf(bytearray) into UART
        uart.write(buf_udp[:size], size)
        #  --- for debug ---
        # it is very important: change the byte-order of UDP Client port
        cp = udpClient[1]  # udp client port 
        udpRemote[1] = ((cp>>8)&0x00FF) + ((cp<<8)&0xFF00)  # change the byte-order
        print("Received", buf_udp[:size], size, "bytes from", udpRemote)
        # give a ACK (Reply)
        size = sock_udp.sendto(buf_udp[:size], udpRemote)
        print("Sent", buf_udp[:size], size, "bytes to", udpRemote)
        #  --- for debug ---
    except:
        pass  # ignore some abnormal
    # check UART dataframe and relay to UDP
    if uart.in_waiting>=1:
        # found the data buffer has at least one byte readable data 
        nbytes = 0
        # waiting for complete data frame to arrive, and read from the buffer
        while True:
            time.sleep(0.05)
            n_rb = uart.in_waiting
            if n_rb<=0:
                break   # got a complete data frames, break the while loop
            rbs = uart.read(n_rb)
            buf_uart[nbytes:n_rb]=rbs
            nbytes += n_rb
        print("Received", buf_uart[:nbytes], nbytes, "bytes from UART")
        # replay the data frame to UDP
        if udpRemote[0]=='':  # udp remote ipv4_address be empty
            print("UDP Remote IP and port has not been configured")
            # give a ACK (Reply) to debug
            uart.write(buf_uart[:nbytes], nbytes)
            print("Send", buf_uart[:nbytes], nbytes, "bytes to UART")
        else:
            size = sock_udp.sendto(buf_uart[:nbytes], udpRemote)
            print("Send", buf_uart[:nbytes], nbytes, "bytes to", udpRemote)
    else:
        pass
