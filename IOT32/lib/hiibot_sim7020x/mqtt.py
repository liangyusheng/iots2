# The MIT License (MIT)
#
# Copyright Wang Zhongfei (ZJUT-ME)
# Copyright (c) 2020 
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
`mqtt`
================================================================================

CircuitPython library for the SIM7020X NB-IoT module

* Author(s): Wang Zhongfei

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""
import time
import binascii, random
from micropython import const
from .sim7020x import SIM7020X

__version__ = "1.0.0"

MQTT_DEFAULT_TIMEOUT_MS = 2000  # TODO: Check this against arduino...
MAX_NUMBER_SUBSCRIBED_TOPICS = 5

# pylint: disable=too-many-instance-attributes, too-many-public-methods
class MQTT:
    """CircuitPython SIM7020X module interface.
    :param  sim7020x: MQTT network interface
    :param bool debug: Enable debugging output. """

    # pylint: disable=too-many-arguments
    def __init__(self, sim7020x, debug=False):
        self._netif = sim7020x
        self._netif_status = False
        self._broker_connected = False
        self._debug = debug
        self._mqtt_id = 0
        self._mqtt_broker = None         # "www.hiibotiot.com"
        self._broker_port = None         # "1883"
        self._broker_client_id = None    # "myclientid"
        self._listSubscribedTopics = []  # the list of subscripted topics (list)
        self._listCallbackFunTopics = [] # the list of callback function of subscripted topics (list)
        self._listSubTopics_qos = []     # the list of qos of subscripted topics (list)
        self._numSubscribedTopics = 0    # the number of subscripted topics

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.disconnect()

    @property
    def is_connected(self):
        # Returns if attached to network and an IP Addresss was obtained
        if self._netif.send_check_ack(b'AT+CMQCON?\r\n'):
            if self._netif._numLines >= 3 :
                if self._debug:
                    print("ACK Lines: ")
                    for i in range(self._netif._numLines):
                        print(self._netif._listLines[i])
                _ni = self._netif._resolve_item(self._netif._listLines[1][9:])
                if _ni>=3 :
                    if self._debug:
                        print("Paras: ")
                        for i in range(_ni):
                            print(self._netif._listItems[i])
                    self._mqtt_id = self._netif._listItems[0]
                    self._mqtt_broker = self._netif._listItems[2]
                    if self._netif._listItems[1] == b'1':  # used = b'1' (connected), = b'0' (disconnected)
                        self._broker_connected = True
                        return True
                    else:
                        print("Disconnected to MQTT Broker")
                        self._broker_connected = False
                        return False
                else:
                    print("Failed to resolve parameters")
                    self._broker_connected = False
                    return False
            else:
                print("ACK Error!")
                self._broker_connected = False
                return False
        else:
            print("Failed to execute")
            self._broker_connected = False
            return False

    def connect(self, broker=b'', port=b'', clientid=None):
        # Connect to MQTT Broker
        if self.is_connected :
            print("Disconnect older connection firstly, then reconnect")
            self.disconnect() # disconnect older connection
        print("Connecting to MQTT Broker ..")
        _newc_str = b'AT+CMQNEW="' + broker + b'","' + port + b'",12000,100\r\n'
        _br1 = self._netif.send_check_ack(_newc_str, timeout=3000)
        time.sleep(1.2)
        if clientid==None:
            cId = "hiibot_iots2_cpy_exb_nbc_{}".format(random.randint(0, int(time.monotonic() * 100) % 1000))
            for i in range(5):
                cId += random.choice('aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ')
            cId += '{}'.format(random.randint(0, 999))
            print("IoT ClientID: {}".format(cId))
            clientid = cId
        _send_str = b'AT+CMQCON=0,4,"' + clientid + b'",600,1,0\r\n'
        _br2 = self._netif.send_check_ack(_send_str, timeout=3000)
        if _br2:
            print("Connected to MQTT Broker")
            # save new parameters for reconnecting
            self._mqtt_broker = broker
            self._broker_port = port
            self._broker_client_id = clientid
            self._broker_connected = True
            return True
        else:
            print("Failed to execute")
            self._broker_connected = False
            return False

    def reconnect_resubTopics(self):
        if self._mqtt_broker is None or self._broker_port is None or self._broker_client_id is None:
            print("MQTT Broker, and Port must both be defined")
            return False
        if self.connect(self._mqtt_broker, self._broker_port, self._broker_client_id):
            self._subscribe_topics()
            return True
        else:
            print("Failed to Reconnect MQTT Broker")
            return False

    def disconnect(self):
        # Disconnect from MQTT Broker
        self._netif.send_check_ack(b'AT+CMQDISCON=0\r\n', timeout=1000)
        self._broker_connected = False

    def _subscribe_topics(self):
        # this command, for example: b'AT+CMQSUB=0,"/iot/un_8661c51c/group1/node2",1\r\n'
        # AT+CMQSUB = <mqtt_id>, <"topic">, <qos>
        _ok_num = 0
        for i in range(self._numSubscribedTopics):
            _send_str = b'AT+CMQSUB=0,"' + self._listSubscribedTopics[i] + b'",1\r\n'
            tryCnt = 3
            while tryCnt > 0:
                if self._netif.send_check_ack(_send_str, timeout=3000):
                    _ok_num += 1
                    break
                time.sleep(1.2)
                tryCnt -= 1
                if tryCnt>0:
                    print("Try again the {}-th".format(4-tryCnt))
            time.sleep(0.5)

    def subTopic_regCallback(self, sub_topic=b'', reg_callback=None, qos=b'1'):
    	# subscribe one topic and register one callback function
        if sub_topic == b'' or reg_callback is None:
            #raise ValueError("MQTT topic and callback function must both be defined.")
            print("MQTT topic and callback function must both be defined.")
            return False
        if self._numSubscribedTopics >= MAX_NUMBER_SUBSCRIBED_TOPICS:
            #raise ValueError("Subscribed Topics Number is too big!")
            print("Subscribed Topics Number is too big! <=5 ")
            return False
        self._listSubscribedTopics.append(sub_topic)
        self._listCallbackFunTopics.append(reg_callback)
        self._numSubscribedTopics += 1
        if self._debug:
            print("Topic(debug): ")
            print(self._listSubscribedTopics)
        if self.is_connected:
            # AT+CMQSUB = <mqtt_id>, <"topic">, <qos>
            _send_str = b'AT+CMQSUB=0,"' + sub_topic + b'",1\r\n'
            _tryCnt = 3
            while _tryCnt > 0:
                if self._netif.send_check_ack(_send_str, timeout=3000):
                    print("Successfully Subscribe Topic: '{}' ".format(sub_topic.decode("utf-8")))
                    break
                time.sleep(1.2)
                _tryCnt -= 1
                if _tryCnt>0:
                    print("Try again the {}-th".format(4-_tryCnt))
            pass
        return True

    def unsubTopic(self, unsub_topic=b''):
        # subscribe one topic and register one callback function
        if unsub_topic == b'':
            raise ValueError("MQTT topic must be specified.")
        if self._numSubscribedTopics == 0:
            raise ValueError("No specified topic!")
        if self._debug:
            print("Topic(debug): ")
            print(self._listSubscribedTopics)
        _idx = self._listSubscribedTopics.index(unsub_topic)
        if _idx == -1:
            print("No matched Topic")
            if self._debug:
                print(self._listSubscribedTopics)
            return False
        else:
            self._listSubscribedTopics.pop(_idx)
            self._listCallbackFunTopics.pop(_idx)
            self._numSubscribedTopics -= 1
            if self._debug:
                print("Topic(debug): ")
                print(self._listSubscribedTopics)
            if self.is_connected:
                # AT+CMQUNSUB = <mqtt_id>, <"topic">
                _send_str = b'AT+CMQUNSUB=0,"' + unsub_topic + b'"\r\n'
                tryCnt = 3
                while tryCnt > 0:
                    if self._netif.send_check_ack(_send_str, timeout=3000):
                        print("Successfully Unsubscribe Topic: '{}' ".format(unsub_topic.decode("utf-8")))
                        break
                    time.sleep(1.2)
                    tryCnt -= 1
                    if tryCnt>0:
                        print("Try again the {}-th".format(4-tryCnt))
            return True

    def publish(self, pub_topic=b'', pub_msg=None, retain=b'0', qos=b'1'):
        # this command, forexample: b'AT+CMQPUB=0,"/iot/un_8661c51c/group1/node2",1,0,0, 10,"3031323334"\r\n'
        # AT+CMQPUB=<mqtt_id>,<"topic">,<QoS>,<retained>,<dup>,<message_len>,<message>
        if pub_topic == b'' or pub_msg is None:
            #raise ValueError("MQTT topic and message must both be specified")
            print("MQTT topic and message must both be specified")
            return False
        if self.is_connected:
            if isinstance(pub_msg, bytes):
                pass
            elif isinstance(pub_msg, (int, float)):
                pub_msg = str(pub_msg).encode("ascii")
            elif isinstance(pub_msg, str):
                pub_msg = str(pub_msg).encode("utf-8")
            else:
                print("Invalid message data type")
                return False
            _pub_msg = binascii.hexlify(pub_msg) # converte a bytearray into hex bytearray
            _pub_msg = _pub_msg.upper()          # converte upper
            _len = len(pub_msg)*2
            _len = str(_len).encode("ascii")
            _send_str = b'AT+CMQPUB=0,"' + pub_topic + b'",' + qos + b',' + retain + b',0,' + _len + b',"' + _pub_msg + b'"\r\n'
            print("SEND: {}".format(_send_str))
            _tryCnt = 3
            while _tryCnt > 0:
                if self._netif.send_check_ack(_send_str, timeout=3000):
                    print("Successfully Publish Topic: '{}' ".format(pub_topic.decode("utf-8")))
                    return True
                time.sleep(1.2)
                _tryCnt -= 1
                if _tryCnt>0:
                    print("Try again the {}-th".format(4-_tryCnt))
            return False
        else:
            print("Failed to publish this message, off-line status!")

    def mqtt_loop(self):
        _rl_numbytes, _rl_content = self._netif.read_line()
        if _rl_numbytes>0:
            # for example: +CMQPUB: 0,"mytopic",1,0,0,6,"303132"\n
            _first8b = _rl_content[:8]
            if _first8b == b'+CMQPUB:':
                # this is a MQTT message
                print("New message")
                _rl_content = _rl_content[9:_rl_numbytes-1]
                _ni, _li = self._netif.resolve_item(len(_rl_content), _rl_content)
                if _ni == 7:
                    __n = len(_li[1])
                    _the_topic = _li[1][1:__n-1]   # remove ""
                    #print(_the_topic)
                    __n = len(_li[6])
                    __payload= _li[6][1:__n-1] # remove ""
                    _the_payload = binascii.unhexlify(__payload)
                    #_the_payload = _the_payload.decode("utf-8")
                    #print(_the_payload)
                    if self._debug:
                        print("MSG TOPIC: {}".format(_the_topic.decode("utf-8")))
                        print("MSG PAYLOAD: {}".format(_the_payload.decode("utf-8")))
                    _idx = self._listSubscribedTopics.index(_the_topic)
                    if _idx == -1:
                        print("Unsubscribed Topic message")
                    else:
                        if self._listCallbackFunTopics[_idx] is not None:
                            print("execute the callback funtion")
                            self._listCallbackFunTopics[_idx](_the_topic, _the_payload, len(_the_payload))
                else:
                    print("Bad/Unknown message")
