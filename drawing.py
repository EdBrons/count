import cv2 as cv


def show_overlay(text, image):
    font = cv.FONT_HERSHEY_SIMPLEX
    cv.rectangle(image, (0, 0), (200, 100), (255, 255, 255), -1)
    cv.rectangle(image, (0, 0), (200, 100), (0, 0, 0), 2)
    offset = 0
    for line in text.split('\n'):
        cv.putText(
            image, line, (20, 20 + offset), font, 0.6, (0, 0, 0), 2)
        offset += 20


def show_rect(image, cw, ch, rect,
              point=True, color=(0, 200, 0),
              show_conf=False):
    cords = rect[:-1]
    p = rect[-1]
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
        cv.rectangle(image, (x1, y1), (x2, y2), color, 2)
    if show_conf:
        text = f'{p:.2}%'
        font = cv.FONT_HERSHEY_SIMPLEX
        cv.rectangle(image, (x1, y1 - 25), (x1 + 60, y1), color, -1)
        cv.putText(image, text, (x1, y1 - 5),
                   font, 0.6, (0, 0, 0), 2)


def show_labels(image, cw, ch, rects,
                point=True, color=(0, 200, 0),
                threshold=0.8):
    for row in rects:
        p = row[-1]
        if p > threshold:
            show_rect(image, cw, ch, row, point=point, color=color)


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
