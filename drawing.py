import cv2 as cv
import numpy as np


# converts yolo format, where dimensions are fractions of total dimension
# to a pixel format, where dimensions are the number of pixels:w
# i.e. the converion of the yolo output (0.1, 0.1, 0.2, 0.2)
# when the width=200 and heigh=100 would be
#   (0.1 * width, 0.1 * height, 0.2 * width, 0.2 * height)
# = (20, 10, 40, 20)
def yolo_to_pixel(preds, w, h):
    return [ (int(p[0] * w), int(p[1] * h), 
              int(p[2] * w), int(p[3] * h ), 
              p[4])
            for p in preds 
        ]



def r_to_p(r, w=None, h=None):
    if w is not None and h is not None:
        x1 = int(r[0] * w)
        y1 = int(r[1] * h)
        x2 = int(r[2] * w)
        y2 = int(r[3] * h)
    return ((x1 + x2) / 2, (y1 + y2) / 2)


def rect_center(rect, convert_int=True):
    if convert_int:
        return (int((rect[0] + rect[1]) / 2), int((rect[1] + rect[2]) / 2))
    else:
        return ((rect[0] + rect[1]) / 2, (rect[1] + rect[2]) / 2)

# shows a text box in the upper right corner
# lines of text should be seperated by \n
def show_overlay(text, image):
    font = cv.FONT_HERSHEY_SIMPLEX
    # cv.rectangle(image, (0, 0), (200, 100), (255, 255, 255), -1)
    # cv.rectangle(image, (0, 0), (200, 100), (0, 0, 0), 2)
    offset = 0
    for line in text.split('\n'):
        cv.putText(
            image, line, (20, 20 + offset), font, 0.6, (0, 0, 0), 2)
        offset += 20


def show_labels(image, rows,
                point=True, color=(0, 200, 0),
                threshold=0.8, fill=None, mask=True, lerp=False, show_conf=False):
    for row in rows:
        if row[-1] < threshold:
            continue
        show_label(image, row, color1=color, point=point, fill=fill, lerp=lerp, show_conf=show_conf)


def show_label(image, rect,
               show_conf=False, 
               point=True, 
               lerp=False,
               color1=(0, 200, 0),
               color2=(0, 0, 200),
               low_conf=.4,
               high_conf=.8,
               fill=None):
    cords = rect[:-1]
    p = rect[-1]
    x1 = cords[0]
    y1 = cords[1]
    x2 = cords[2]
    y2 = cords[3]
    if lerp:
        d = 1 - min(1, (p - low_conf) / (high_conf - low_conf))
        color = (
                int(color1[0] + d * (color2[0] - color1[0])),
                int(color1[1] + d * (color2[1] - color1[1])),
                int(color1[2] + d * (color2[2] - color1[2])),
            )
    else:
        color = color1
    if point:
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)
        cv.circle(image, (cx, cy), radius=5,
                  color=color, thickness=-1)
    else:
        if fill is not None:
            cv.rectangle(image, (x1, y1), (x2, y2), fill, -1)
        else:
            cv.rectangle(image, (x1, y1), (x2, y2), color, 2)
    if show_conf:
        text = f'{p:1.2}%'
        font = cv.FONT_HERSHEY_SIMPLEX
        cv.rectangle(image, (x1, y1 - 25), (x1 + 60, y1), color, -1)
        cv.putText(image, text, (x1, y1 - 5),
                   font, 0.6, (0, 0, 0), 2)


def dist_squared(p1, p2):
    return pow(p1[0] - p2[0], 2) + pow(p1[1] - p2[1], 2)


def circle_collides(p1, p2, r, w=None, h=None):
    if w is not None and h is not None:
        p1_ = r_to_p(p1, w, h)
        p2_ = r_to_p(p2, w, h)
    return dist_squared(p1_, p2_) <= (pow(r, 2))


def find_overlaps(image, cw, ch, rows, threshold, new_rects=None, highlight=False):
    im1 = np.zeros(image.shape, dtype=np.uint8)
    im2 = np.zeros(image.shape, dtype=np.uint8)
    im3 = np.zeros(image.shape, dtype=np.uint8)
    for i, row in enumerate(rows):
        if row[-1] < threshold:
            continue
        for j, r2 in enumerate(rows):
            if (new_rects is not None and i not in new_rects) or i == j or (r2[-1] < threshold):
                continue
            if circle_collides(row[:4], r2[:4], 10, w=cw, h=ch):
                # show_label(image, cw, ch, r2, color=(200, 200, 0))
                im3.fill(0)
                if not highlight:
                    show_label(im3, cw, ch, row, point=True,
                               color=(255, 255, 255))
                    im2 = cv.bitwise_or(im2, cv.bitwise_and(im1, im3))
                else:
                    show_label(im2, cw, ch, row, point=True,
                               color=(255, 255, 255))
                    show_label(im2, cw, ch, r2, point=True,
                               color=(255, 255, 255))
                continue
        show_label(im1, cw, ch, row, point=True,
                   color=(255, 255, 255))
    # if highlight:
    #     return im2
    # else:
    return cv.bitwise_not(im2)
