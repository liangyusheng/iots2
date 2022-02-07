import time
import touchio, board
from hiibot_iots2 import IoTs2
from hiibot_iots2_mqtt import MQTTClient
iots2 = IoTs2()
tp3 = touchio.TouchIn(board.IO3)
tp9 = touchio.TouchIn(board.IO9)

mqttClient = MQTTClient()
msgTopic0 = '/test/topic1'
msgTopic1 = '/iot/un_8661c51c/iots2-module/buttonevent'
msgTopic2 = "/iot/un_8661c51c/group1/node2" #  published msg
msgTopic3 = "/iot/un_8661c51c/iots2-module/screenbrightness" # screen.brightness
msgTopic4 = '/iot/un_8661c51c/iots2-module/rgbled' # neopixels[0]
msgTopic5 = '/iot/un_8661c51c/iots2-module/blueled'
msgTopic6 = '/iot/un_8661c51c/iots2-module/touchpad3'
msgTopic7 = '/iot/un_8661c51c/iots2-module/touchpad9'

def Chars2Int(chars):
    h = ord(chars[0])-48 if ord(chars[0])<=57 else ord(chars[0])-65+10
    l = ord(chars[1])-48 if ord(chars[1])<=57 else ord(chars[1])-65+10
    return (h*16)+l

def cbf_msgTopic3(message):
    bt = 0.0
    try:
        bt = float(message)
    except:
        pass
    bt = min(bt, 1.0)
    bt = max(0.1, bt)
    iots2.screen.brightness = bt
    #mqttClient.publishMessage(msgTopic2, '{}'.format(bt*1000))

def cbf_msgTopic4(message):
    #print('New message (topic="{}", message="{}")'.format(msgTopic2, message))
    message=message.upper()
    if message[0]=='#':
        r = Chars2Int(message[1:3])
        g = Chars2Int(message[3:5])
        b = Chars2Int(message[5:7])
    iots2.pixels[0] = (r,g,b)
    iots2.pixels.show()
    mqttClient.publishMessage(msgTopic2, 'R:{},G:{},B:{}'.format(r,g,b))

def cbf_msgTopic5(message):
    if len(message)==1 and message=='1':
        iots2.blueLED_bright=1.0
    elif len(message)==1 and message=='0':
        iots2.blueLED_bright=0.0

mqttClient.subscribeTopic(msgTopic3, cbf_msgTopic3)
mqttClient.subscribeTopic(msgTopic4, cbf_msgTopic4)
mqttClient.subscribeTopic(msgTopic5, cbf_msgTopic5)

mqttClient.connect()

mqttClient.publishMessage(msgTopic0, 'Hello broker')
counter = 0
tp3Vp = 0
tp9Vp = 0

while True:
    iots2.button_update()
    if counter>= 200:
        mqttClient.loop()
        counter = 0
    counter+=1
    time.sleep(0.005)
    if iots2.button_wasPressed:
        print('wasPressed')
        mqttClient.publishMessage(msgTopic1, 'wasPressed')
        time.sleep(0.1)
    elif iots2.button_wasReleased:
        print('wasReleased')
        mqttClient.publishMessage(msgTopic1, 'wasReleased')
        time.sleep(0.1)
    if not tp3Vp==tp3.value:
        if tp3.value:
            mqttClient.publishMessage(msgTopic6, '1')
        else:
            mqttClient.publishMessage(msgTopic6, '0')
        tp3Vp = tp3.value
        time.sleep(0.1)
    if not tp9Vp==tp9.value:
        if tp9.value:
            mqttClient.publishMessage(msgTopic7, '1')
        else:
            mqttClient.publishMessage(msgTopic7, '0')
        tp9Vp = tp9.value
        time.sleep(0.1)
