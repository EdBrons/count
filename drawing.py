import cv2 as cv
import numpy as np


def show_overlay(text, image):
    font = cv.FONT_HERSHEY_SIMPLEX
    cv.rectangle(image, (0, 0), (200, 100), (255, 255, 255), -1)
    cv.rectangle(image, (0, 0), (200, 100), (0, 0, 0), 2)
    offset = 0
    for line in text.split('\n'):
        cv.putText(
            image, line, (20, 20 + offset), font, 0.6, (0, 0, 0), 2)
        offset += 20


def show_label(image, cw, ch, row,
               point=True, color=(0, 200, 0),
               show_conf=False, fill=None):
    cords = row[:-1]
    p = row[-1]
    x1 = int(cords[0] * cw)
    y1 = int(cords[1] * ch)
    x2 = int(cords[2] * cw)
    y2 = int(cords[3] * ch)
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


def r_to_p(r, w=None, h=None):
    if w is not None and h is not None:
        x1 = int(r[0] * w)
        y1 = int(r[1] * h)
        x2 = int(r[2] * w)
        y2 = int(r[3] * h)
    return ((x1 + x2) / 2, (y1 + y2) / 2)


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


def show_labels(image, cw, ch, rows,
                point=True, color=(0, 200, 0),
                threshold=0.8, fill=None, mask=True):
    # im1 = np.zeros(image.shape, dtype=np.uint8)
    # im2 = np.zeros(image.shape, dtype=np.uint8)
    # im3 = np.zeros(image.shape, dtype=np.uint8)
    for row in rows:
        p = row[-1]
        if p > threshold:
            # im2.fill(0)
            show_label(image, cw, ch, row, point=point,
                       color=color, fill=fill)
            # im3 = cv.bitwise_or(im3, cv.bitwise_and(im1, im2))
            # im1 = cv.bitwise_or(im1, im2)
    # cv.fillPoly(im1, color=(0, 255, 0))
    # image[(im1 == (255, 255, 255)).all(-1)] = [0, 255, 0]
    # image[(im3 == (255, 255, 255)).all(-1)] = [0, 0, 255]


def lerp(low, high, n):
    if n < low:
        return 0
    elif n > high:
        return 1
    else:
        return (n - low) / (high - low)


def lerp_color(c1, c2, x):
    diff = (c2[0] - c1[0], c2[1] - c1[1], c2[2] - c1[2])
    return (c1[0] + x * diff[0], c1[1] + x * diff[1], c1[2] + x * diff[2])
