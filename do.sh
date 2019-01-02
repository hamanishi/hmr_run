#!/bin/bash

for f in `ls /home/dev/openpose_output/tmp/*.png`; do
    echo $f|sed -e "s/tmp\///g" | sed -e "s/\(.png\)/_keypoints.json/"
    python -m demo --img_path $f --json_path `echo $f | sed -e "s/tmp\///g" | sed -e "s/\(.png\)/_keypoints.json/"`
done;
