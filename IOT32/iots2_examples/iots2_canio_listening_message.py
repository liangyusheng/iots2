import board
import canio

can = canio.CAN(rx=board.IO4, tx=board.IO3, baudrate=500_000, auto_restart=True)

#listener = can.listen(matches=[canio.Match(0x488)], timeout=0.9) # only receive id=0x488
listener = can.listen(timeout=0.1)  # all id

old_bus_state = None
print("Listening to the new message")

while True:
    bus_state = can.state
    if bus_state != old_bus_state:
        print(f"Bus state changed to {bus_state}")
        old_bus_state = bus_state
 
    message = listener.receive()
    if message is None:
        #print("No messsage received within timeout")
        continue
    else:
        id, data = message.id, message.data
        ostr = 'from ID [0x{:03X}]: '.format(id)
        for i in range(len(data)):
            ostr += '{:02X} '.format(data[i])
        print(ostr)  # output ID[0xABC]: xx xx .. xx
