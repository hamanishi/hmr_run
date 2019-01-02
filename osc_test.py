
import time

from pathlib import Path
import cv2

#from pythonosc import udp_client
#from pythonosc.osc_message_builder import OscMessageBuilder

import liblo, sys

def osc():
    #IP = '127.0.0.1'
    IP = '192.170.11.4'
    PORT = 12345

    target = liblo.Address(IP, PORT)

    liblo.send(target, "/foo/hoge", 123.456,789,"test", -0.456879)
    
    #client = udp_client.UDPClient(IP, PORT)

    print("start building")
    #msg = OscMessageBuilder(address='/color')
    #msg.add_arg('0')
    #    msg.add_arg("a")
    #    m = msg.build()
    #client.send(m)
    print("send done")
    
    
if __name__ == '__main__':
    print("begin")
    osc()
    #cam()
    #get_path()
    
