import time
import board
import canio
import digitalio

can = canio.CAN(rx=board.IO4, tx=board.IO3, baudrate=500_000, auto_restart=True)
listener = can.listen(matches=[canio.Match(0x478)], timeout=0.1) # only id=0x478
myid = 0x479

old_bus_state = None

while True:
    bus_state = can.state
    if bus_state != old_bus_state:
        print(f"Bus state changed to {bus_state}")
        old_bus_state = bus_state
    
    rMsg = listener.receive()
    if rMsg is None:
        #print("No messsage received within timeout")
        continue
    else:
        ostr = 'from ID [0x{:03X}]: '.format(rMsg.id)
        for i in range(len(rMsg.data)):
            ostr += '{:02X} '.format(rMsg.data[i])
        print(ostr)  # output ID[0xABC]: xx xx .. xx
        sMsg = canio.Message(id=myid, data=rMsg.data)
        can.send(sMsg)
        print('echo ok')