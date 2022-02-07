import time
import board
import canio
import digitalio

can = canio.CAN(rx=board.IO4, tx=board.IO3, baudrate=500_000, auto_restart=True)
btn = digitalio.DigitalInOut(board.IO21)
btn.switch_to_input()  # external pull-up

old_bus_state = None

while True:
    bus_state = can.state
    if bus_state != old_bus_state:
        print(f"Bus state changed to {bus_state}")
        old_bus_state = bus_state
    
    sbtn = btn.value
    if not sbtn:
        time.sleep(0.02)
        if btn.value == sbtn:
            #d = b'\x12\x34\x56\x78\x9A\xBC\xDE\xF0'
            d = b'\x12\x34\x56'
            msg = canio.Message(id=0x478, data=d)
            can.send(msg)
            ostr = 'to ID [0x{:03X}]: '.format(msg.id)
            for i in range(len(msg.data)):
                ostr += '{:02X} '.format(msg.data[i])
            print(ostr)  # output ID[0xABC]: xx xx .. xx
            while True:
                sbtn = btn.value
                time.sleep(0.02)
                if btn.value==sbtn and sbtn:
                    break
