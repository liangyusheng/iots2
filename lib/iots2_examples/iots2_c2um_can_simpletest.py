import time
import struct
from hiibot_iots2_can2uart import C2UM
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
c2um = C2UM(canid=0x10, en_debug=False)

def show_msg_data(_sender_id, _msg_id, _data):
    out_str = "[{:02X}, {:02X}] : ".format(_sender_id, _msg_id)
    for d in _data:
        out_str += "{:02X} ".format(d)
    print(out_str)

old_bus_state = None
count = 0

while True:
    now_bus_state = c2um.canif_state
    if  now_bus_state != old_bus_state:
        print(f"CAN-Bus state changed to {now_bus_state}")
        old_bus_state = now_bus_state

    iots2.button_update()
    if iots2.button_wasPressed:
        now_ms = (time.monotonic_ns() // 1_000_000) & 0xffffffff
        print(f"Send message: count={count} now_ms={now_ms}")
        msg_id, msg_data = 0x09, struct.pack("<II", count, now_ms)
        rs = c2um.canif_send(msg_id, msg_data)
        if rs==True:
            count += 1
        else:
            print("failed to send")

    rec = c2um.canif_receive()
    if rec is None:
        pass
    else:
        _sender_id, _msg_id, _data = rec[0], rec[1], rec[2]
        show_msg_data(_sender_id, _msg_id, _data)
        
