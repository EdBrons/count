import cv2 as cv
from drawing import show_labels, show_overlay


class Edit:
    def __init__(self, image, rects, width, height):
        self.image = image
        self.width = width
        self.height = height
        self.rects = rects
        self.threshold = 80
        self.point = True
        self.my_rect = None
        cv.setMouseCallback('frame', self.handle_click)

    def get_collisions(self, x, y):
        collisions = []
        for rect in self.rects:
            cords = rect[:-1]
            x1 = int(cords[0] * self.width)
            y1 = int(cords[1] * self.height)
            x2 = int(cords[2] * self.width)
            y2 = int(cords[3] * self.height)
            if x > x1 and x < x2 and y > y1 and y < y2:
                collisions.append(rect)
        collisions.sort(key=lambda rect: abs(
            x - self.width * (rect[0] + rect[2]) / 2) + abs(y - self.height * (rect[1] + rect[3]) / 2))
        return collisions

    def handle_click(self, event, x, y, flags, param):
        rects = self.get_collisions(x, y)
        if event == cv.EVENT_LBUTTONDOWN:
            # draw circle here (etc...)
            # print('x = %d, y = %d' % (x, y))
            for r in rects:
                if r[-1] < self.threshold / 100:
                    r[-1] = 1
                    break
                else:
                    r[-1] = 0
                    break
        else:
            if len(rects) > 0:
                self.my_rect = rects[0]
            else:
                self.my_rect = None

    def handle_input(self):
        k = cv.waitKey(1)
        if k == -1:
            return
        elif k == ord('q'):
            self.run = False
        elif k == ord('-'):
            self.threshold -= 1
        elif k == ord('+'):
            self.threshold += 1
        elif k == 9:
            self.point = not self.point
        else:
            print(k)

    def count(self, threshold):
        n = 0
        for rect in self.rects:
            if rect[-1] > threshold / 100:
                n += 1
        return n

    def loop(self):
        self.run = True
        while self.run:
            labels = show_labels(self.image, self.width,
                                 self.height, self.rects, threshold=(self.threshold / 100), point=self.point)
            if self.my_rect is not None:
                labels = show_labels(labels, self.width, self.height, [
                                     self.my_rect], color=(200, 0, 0), threshold=0, point=False)

            show_overlay(
                f'EDITING\nthreshold: {self.threshold / 100}%\ncount: {self.count(self.threshold)}', labels)

            cv.imshow('frame', labels)
            self.handle_input()
