# The MIT License (MIT)
#
# Copyright (c) 2020 HiiBot for Hangzhou Leban Tech. Ltd
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`hiibotiot_iots2`
================================================================================

the board-supported-package to connecte www.hiibotiot.com(MQTT Broker) with HiiBot IoTs2 board, include

1) connect, 
2) subscribeTopic,
3) publishMessage,
4) reconnect, 
5) loop, 

those interface are used as following:



* Author(s): HiiBot

Implementation Notes
--------------------

**Hardware:**
.. "* `HiiBot IoTs2 - a funny production with WiFi`_"

**Software and Dependencies:**
* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases
 * Adafruit's Minimqtt library: 
 * 
"""
import time
import random
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import ssl
import socketpool
import wifi
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

__version__ = "0.1.0-auto.0"
__repo__ = "https://github.com/HiiBot/Hiibot_CircuitPython_IoTs2.git"


class MQTTClient:
    def __init__(self, server=None, clientId=None, user='anonymity', password='12345678', port=1883):
        if not server:
            server = "www.hiibotiot.com"
        self.__server = server
        self.__user = user
        self.__password = password
        self.__port = port
        if not clientId:
            clientId = "hiibot_iots2_cpy_{}".format(random.randint(0, int(time.monotonic() * 100) % 1000))
            for i in range(5):
                clientId += random.choice('aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ')
            clientId += '{}'.format(random.randint(0, 999))
        print("IoT ClientID: {}".format(clientId))
        self.__clientId = clientId
        self.__topics = []
        self.__topicFuncs = []

        # Set up a MiniMQTT Client
        self.__client = MQTT.MQTT(
            broker=self.__server,
            port=self.__port,
            username=self.__user,
            password=self.__password,
            client_id=self.__clientId,
            is_ssl=False,
            socket_pool=socketpool.SocketPool(wifi.radio),
            ssl_context=ssl.create_default_context(),
        )

        self.__client.on_connect = self.__mqttConnectedCallback
        self.__client.on_disconnect = self.__mqttDisconnectCallback
        self.__client.on_publish = self.__mqttPublishCallback
        self.__client.on_message = self.__mqttMessageCallback
        self.__client.on_subscribe = self.__mqttSubscribeCallback
        self.__client.on_unsubscribe = self.__mqttUnsubscribeCallback


    def __mqttConnectedCallback(self, client, userdata, flags, rc):
        print("Connected to {}:{} !".format(self.__server, self.__port))
        print("Flags: {0}\n RC: {1}".format(flags, rc))
        if len(self.__topics) > 0:
            for i in range(len(self.__topics)):
                self.__client.subscribe(self.__topics[i])

    def __mqttSubscribeCallback(self, client, userdata, topic, granted_qos):
        print("Subscribed to {0} with QOS level {1}".format(topic, granted_qos))

    def __mqttDisconnectCallback(self, client, userdata, rc):
        print("Disconnected from MQTT Broker!")

    def __mqttPublishCallback(self, client, userdata, topic, pid):
        print("Published to {0} with PID {1}".format(topic, pid))

    def __mqttMessageCallback(self, client, topic, message):
        print("New message on topic {0}: {1}".format(topic, message))
        recvTopic = str(topic)
        recvMsg = str(message)
        for i in range(len(self.__topics)):
            if self.__topics[i] == recvTopic:
                self.__topicFuncs[i](recvMsg)
                break
    def __mqttUnsubscribeCallback(self, client, topic):
        pass

    def publishMessage(self, topic, message):
        try:
            if self.__client.is_connected():
                self.__client.publish(topic,message)
        except:
            pass

    def subscribeTopic(self, topic, func):
        self.__topics.append(topic)
        self.__topicFuncs.append(func)

    def connect(self):
        # Connecte to AP (ignore this step if connected)
        if not wifi.radio.ipv4_address:
            print("My MAC addr:", [hex(i) for i in wifi.radio.mac_address])
            print("Connecting to WiFi AP (SSID: %s) ..." % secrets["ssid"])
            wifi.radio.connect(secrets["ssid"], secrets["password"])
            print("Connected to %s!" % secrets["ssid"])
            print("My IP address: ", wifi.radio.ipv4_address)
        # Connecte to IoT Broker
        print("Connecting to MQTT Broker ({0}:{1}) ...".format(self.__server, self.__port))
        self.__client.connect() 

    def loop(self):
        if not self.__client.is_connected():
            self.connect()
        tryCount = 0
        while tryCount < 10:
            try:
                self.__client.loop()
                time.sleep(0.005)
                break
            except (ValueError,RuntimeError) as e:
                print("Failed to get data, retrying\n", e)
                self.__client.reconnect()
                tryCount += 1
                continue
            time.sleep(0.005)
