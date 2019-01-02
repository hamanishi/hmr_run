from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
from absl import flags
import numpy as np

import skimage.io as io
import tensorflow as tf

from src.util import renderer as vis_util
from src.util import image as img_util
from src.util import openpose as op_util
import src.config
from src.RunModel import RunModel

import time

from pathlib import Path
import cv2

from pythonosc import udp_client
from pythonosc.osc_message_builder import OscMessageBuilder


def osc():
    #IP = '127.0.0.1'
    IP = '192.170.11.4'
    PORT = 12345
    client = udp_client.UDPClient(IP, PORT)

    print("start building")
    msg = OscMessageBuilder(address='/color')
    #msg.add_arg('0')
    msg.add_arg("a")
    m = msg.build()
    client.send(m)
    print("send done")
    


def get_path():
    dir = Path("/home/dev/openpose_output/tmp")
    #img_pathes = dir.iterdir()
    img_path = sorted(dir.iterdir())
    #img = cv2.imread(str(img_path))
    for i in img_path:
        #print(i)
        filepath = str(i).replace(".png", "_keypoints.json")
        filepath = str(i).replace("tmp/", "")
        print(filepath)
#    print("path:" + img_path + ", "+len(img_pathes))


def cam():
    vc = cv2.VideoCapture(0)
    if vc.isOpened():
        is_capturing, _ = vc.read()
    else:
        is_capturing = False

    cnt = 0
    while is_capturing:
        is_capturing, img = vc.read()
        cv2.imwrite("./images/img_" + str(cnt).zfill(8) + ".png", img)
        #cv2.imshow("./images/img_{cnt:04d}.png", img)
        #g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cv2.imshow('video', img)
        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break
        cnt += 1
    vc.release()
    cv2.destroyAllWindows()

    
if __name__ == '__main__':
    print("begin")
    osc()
    #cam()
    #get_path()
    
