import argparse
import cv2 as cv
from count import Count

"""
code start the camera capture
sudo modprobe v4l2loopback exclusive_caps=1 card_label="GPhoto2 Webcam"
gphoto2 --stdout --capture-movie  \
| ffmpeg -i - -vcodec rawvideo -pix_fmt yuv420p -threads 0 -f v4l2 /dev/video2
"""


def parse_args():
    parser = argparse.ArgumentParser(
        prog='counter',
        description='counts and annotates parts',
        epilog='author: ian brons')

    parser.add_argument('--camera', required=True)
    parser.add_argument('--weights', required=True)

    args = parser.parse_args()
    return args


def main():
    args = parse_args()

    counter = Count(args.weights, args.camera)
    counter.loop()


if __name__ == '__main__':
    main()
