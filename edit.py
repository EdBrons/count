import cv2 as cv
from drawing import show_labels, show_overlay, show_rect


class Edit:
    def __init__(self, image, rects, width, height):
        self.image = image
        self.width = width
        self.height = height
        self.rects = rects

        self.threshold = 80
        self.point = True
        self.hover_rect = None

        self.input_mode = 'select'

        cv.setMouseCallback('frame', self.handle_mouse)

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
        collisions.sort(key=lambda rect:
                        # method 1: sort by rect size
                        (rect[2] - rect[0]) * (rect[3] - rect[1])
                        # method 2: sort by distance to rect center
                        # abs(x - self.width * (rect[0] + rect[2]) / 2) +
                        # abs(y - self.height * (rect[1] + rect[3]) / 2)
                        )
        return collisions

    def handle_mouse(self, event, x, y, flags, param):
        rects = self.get_collisions(x, y)
        if event == cv.EVENT_LBUTTONDOWN:
            if self.hover_rect is not None:
                print('clicked my rect')
            else:
                print('new rect?')
        else:
            if len(rects) > 0:
                self.hover_rect = rects[0]
            else:
                self.hover_rect = None
        # if event == cv.EVENT_LBUTTONDOWN:
        #     # draw circle here (etc...)
        #     # print('x = %d, y = %d' % (x, y))
        #     for r in rects:
        #         if r[-1] < self.threshold / 100:
        #             r[-1] = 1
        #             break
        #         else:
        #             r[-1] = 0
        #             break
        # else:

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
            labels = self.image.copy()
            show_labels(labels, self.width,
                        self.height, self.rects,
                        threshold=(self.threshold / 100),
                        point=self.point
                        )

            if self.hover_rect is not None:
                show_rect(labels, self.width, self.height,
                          self.hover_rect,
                          color=(200, 0, 0),
                          show_conf=True,
                          point=False)

            overlay_str = f'input mode: {self.input_mode}\n' \
                f'threshold: {self.threshold / 100}%\n' \
                f'count: {self.count(self.threshold)}'

            show_overlay(
                overlay_str,
                labels
            )

            cv.imshow('frame', labels)
            self.handle_input()
        self.quit()

    def quit(self):
        cv.setMouseCallback('frame', lambda *args: None)
