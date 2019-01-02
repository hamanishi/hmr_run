"""
Demo of HMR.

Note that HMR requires the bounding box of the person in the image. The best performance is obtained when max length of the person in the image is roughly 150px. 

When only the image path is supplied, it assumes that the image is centered on a person whose length is roughly 150px.
Alternatively, you can supply output of the openpose to figure out the bbox and the right scale factor.

Sample usage:

# On images on a tightly cropped image around the person
python -m demo --img_path data/im1963.jpg
python -m demo --img_path data/coco1.png

# On images, with openpose output
python -m demo --img_path data/random.jpg --json_path data/random_keypoints.json
"""
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

import liblo, sys

flags.DEFINE_string('img_path', 'data/im1963.jpg', 'Image to run')
flags.DEFINE_string(
    'json_path', None,
    'If specified, uses the openpose output to crop the image.')

import datetime

def visualize(img, proc_param, joints, verts, cam, img_path):
    """
    Renders the result in original image coordinate frame.
    """
    cam_for_render, vert_shifted, joints_orig = vis_util.get_original(
        proc_param, verts, cam, joints, img_size=img.shape[:2])

    # Render results
    skel_img = vis_util.draw_skeleton(img, joints_orig)
    rend_img_overlay = renderer(
        vert_shifted, cam=cam_for_render, img=img, do_alpha=True)
    rend_img = renderer(
        vert_shifted, cam=cam_for_render, img_size=img.shape[:2])
    rend_img_vp1 = renderer.rotated(
        vert_shifted, 60, cam=cam_for_render, img_size=img.shape[:2])
    rend_img_vp2 = renderer.rotated(
        vert_shifted, -60, cam=cam_for_render, img_size=img.shape[:2])

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    # plt.ion()
    plt.figure(1)
    plt.clf()
    plt.subplot(231)
    plt.imshow(img)
    plt.title('input')
    plt.axis('off')
    plt.subplot(232)
    plt.imshow(skel_img)
    plt.title('joint projection')
    plt.axis('off')
    plt.subplot(233)
    plt.imshow(rend_img_overlay)
    plt.title('3D Mesh overlay')
    plt.axis('off')
    plt.subplot(234)
    plt.imshow(rend_img)
    plt.title('3D mesh')
    plt.axis('off')
    plt.subplot(235)
    plt.imshow(rend_img_vp1)
    plt.title('diff vp')
    plt.axis('off')
    plt.subplot(236)
    plt.imshow(rend_img_vp2)
    plt.title('diff vp')
    plt.axis('off')
    plt.draw()
    now=datetime.datetime.now()
    pp = str(now.hour) + str(now.minute)+str(now.second) + '_'# + img_path
    #pp = pp.replace('/tmp', '/hmr')
    #pp = pp.replace('.png', '_hmr.png')
    print(pp)
    plt.savefig('/home/dev/openpose_output/cams/' + pp)
    #plt.show()
    # import ipdb
    # ipdb.set_trace()


def joints3d2csv(joints, img_path):
    ## save joint3d as csv
    import csv
    pp = '' + img_path
    pp = pp.replace('/frames', '/basic')
    pp = pp.replace('.png', '_hmr.csv')

    with open(pp, 'w') as f:
        writer = csv.writer(f, lineterminator='\n')
        for joint in joints:
            writer.writerows(joint)

    print("end of saving as .csv:" + str(pp))
            

def preprocess_image(img_path, json_path=None):
    img = io.imread(img_path)
    if img.shape[2] == 4:
        img = img[:, :, :3]

    if json_path is None:
        if np.max(img.shape[:2]) != config.img_size:
            print('Resizing so the max image size is %d..' % config.img_size)
            scale = (float(config.img_size) / np.max(img.shape[:2]))
        else:
            scale = 1.
        center = np.round(np.array(img.shape[:2]) / 2).astype(int)
        # image center in (x,y)
        center = center[::-1]
    else:
        scale, center = op_util.get_bbox(json_path)

    crop, proc_param = img_util.scale_and_crop(img, scale, center,
                                               config.img_size)

    # Normalize image to [-1, 1]
    crop = 2 * ((crop / 255.) - 0.5)

    return crop, proc_param, img

def preprocess_image_cam(img_path, json_path=None, image=None):
    img = image
    if img.shape[2] == 4:
        img = img[:, :, :3]

    if json_path is None:
        if np.max(img.shape[:2]) != config.img_size:
            print('Resizing so the max image size is %d..' % config.img_size)
            scale = (float(config.img_size) / np.max(img.shape[:2]))
        else:
            scale = 1.
        center = np.round(np.array(img.shape[:2]) / 2).astype(int)
        # image center in (x,y)
        center = center[::-1]
    else:
        scale, center = op_util.get_bbox(json_path)

    crop, proc_param = img_util.scale_and_crop(img, scale, center,
                                               config.img_size)

    # Normalize image to [-1, 1]
    crop = 2 * ((crop / 255.) - 0.5)

    return crop, proc_param, img



from pathlib import Path
import cv2

def main(img_path, json_path=None):
    sess = tf.Session()
    model = RunModel(config, sess=sess)

    start = time.time()

    # Add batch dimension: 1 x D x D x 3

    dir = Path("/home/dev/openpose_output/frames")
    img_pathes = sorted(dir.iterdir())    
    for i in img_pathes:
        img_path = i
        json_path = str(i).replace(".png", "_keypoints.json")
        json_path = str(json_path).replace("frames/", "keypoints/")
        
        input_img, proc_param, img = preprocess_image(img_path, json_path)
        input_img = np.expand_dims(input_img, 0)
        
        a = time.time() - start
        #print(a)
        joints, verts, cams, joints3d, theta = model.predict(input_img, get_theta=True)

        b = time.time() - start
        print(b - a)
        #print(type(joints3d))
    
        joints3d2csv(joints3d, str(img_path))
    
        #visualize(img, proc_param, joints[0], verts[0], cams[0], img_path)

def main_cam(img_path, json_path=None):
    vc = cv2.VideoCapture(0)
    if vc.isOpened():
        is_capturing, _ = vc.read()
    else:
        is_capturing = False

    cnt = 0

    sess = tf.Session()
    model = RunModel(config, sess=sess)

    start = time.time()
    while is_capturing:
        is_capturing, img = vc.read()
        #cv2.imwrite("./images/img_" + str(cnt).zfill(8) + ".png", img)
        cv2.imshow('video', img)

        a = time.time() - start
        #print(a)
        input_img, proc_param, img = preprocess_image_cam(img_path, json_path, img)
        input_img = np.expand_dims(input_img, 0)

        joints, verts, cams, joints3d, theta = model.predict(input_img, get_theta=True)
        #b = time.time() - start
        #print(b - a)

        idx = 0
        for j in joints3d[0]:
            liblo.send(target, "/xyz", float(j[0]), float(j[1]), float(j[2]), str(cnt), idx)
            idx += 1

        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break
        cnt += 1
        print(cnt)

    vc.release()
    cv2.destroyAllWindows()
            

IP = '192.170.11.6'
PORT = 12345
target = liblo.Address(IP, PORT)

if __name__ == '__main__':
    
    config = flags.FLAGS
    config(sys.argv)
    # Using pre-trained model, change this to use your own.
    config.load_path = src.config.PRETRAINED_MODEL

    config.batch_size = 1

    renderer = vis_util.SMPLRenderer(face_path=config.smpl_face_path)

    main(config.img_path, config.json_path)
    #main_cam(config.img_path, config.json_path)
