import time
import terminalio
import displayio
from adafruit_display_text.label import Label
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
iots2.screen.rotation = 180
# create a text label
textlabel_group = displayio.Group(scale=2)
textLabel_title = Label(terminalio.FONT, x=9, y=10, text="Acce", scale=2, color=(255,0,0))
textLabel_x = Label(terminalio.FONT, x=1, y=32, text="", color=(255,0,0))
textLabel_y = Label(terminalio.FONT, x=1, y=48, text="", color=(0,255,0))
textLabel_z = Label(terminalio.FONT, x=1, y=64, text="", color=(0,0,255))
textLabel_roll = Label(terminalio.FONT, x=1, y=80, text="", color=(255,0,255))
textLabel_pitch = Label(terminalio.FONT, x=1, y=96, text="", color=(0,255,255))
textlabel_group.append(textLabel_title)
textlabel_group.append(textLabel_x)
textlabel_group.append(textLabel_y)
textlabel_group.append(textLabel_z)
textlabel_group.append(textLabel_roll)
textlabel_group.append(textLabel_pitch)
# show those content on the IoTs2 screen angle_RollPitch
iots2.screen.show(textlabel_group)
while True:
    x, y, z = iots2.Accele_ms2 # Accele_Gs
    roll, pitch = iots2.angle_RollPitch # angle of roll and pitch
    textLabel_x.text = "x: {:.2f}".format(x)
    textLabel_y.text = "y: {:.2f}".format(y)
    textLabel_z.text = "z: {:.2f}".format(z)
    textLabel_roll.text = "roll: {}".format(roll)
    textLabel_pitch.text = "pitch: {}".format(pitch)
    time.sleep(0.1)
