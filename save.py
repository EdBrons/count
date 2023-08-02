import os
import uuid
import cv2 as cv


def save_labels(self, frame, labels):
    it = os.path.join(self.outdir, 'images/train')
    lt = os.path.join(self.outdir, 'labels/train')
    base_fn = str(uuid.uuid4()) + '.jpg'
    filename = os.path.join(it, base_fn)
    cv.imwrite(filename, frame)
    text_fn = os.path.join(lt, os.path.basename(
        os.path.splitext(filename)[0]) + '.txt')
    lines = []
    for label, cord in labels:
        x1 = float(cord[0])
        y1 = float(cord[1])
        x2 = float(cord[2])
        y2 = float(cord[3])
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        w = x2 - x1
        h = y2 - y1
        lines.append(f'{int(label)} {cx} {cy} {w} {h}\n')
    with open(text_fn, 'w') as f:
        f.writelines(lines)
