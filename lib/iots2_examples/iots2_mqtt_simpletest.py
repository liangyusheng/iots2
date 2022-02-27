import time
from hiibot_iots2 import IoTs2
from hiibot_iots2_mqtt import MQTTClient
iots2 = IoTs2()
mqttClient = MQTTClient()

msgTopic1 = "/test/topic1"
msgTopic2 = "/test/topic2"
msgTopic3 = "/test/topic3"

def testTopic1(message):
    print('New message (topic="{}", message="{}")'.format(msgTopic1, message))
    mqttClient.publishMessage(msgTopic2, message)

def testTopic2(message):
    print('New message (topic="{}", message="{}")'.format(msgTopic2, message))
    mqttClient.publishMessage(msgTopic3, message)

mqttClient.subscribeTopic(msgTopic1, testTopic1)
mqttClient.subscribeTopic(msgTopic2, testTopic2)

mqttClient.connect()
while True:
    mqttClient.loop()
    time.sleep(0.005)
