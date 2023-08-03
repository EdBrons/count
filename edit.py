import cv2 as cv
from drawing import show_labels, show_overlay, show_rect
import numpy as np

# TODO:
# better way to handle mouse drags [X]
# show preview of new rect [X]
# ability to adjust squares
#   select rect then click line and drag it to move it
# move keybinds to a settings area
# add auto toggle mode [X]


class Edit:
    def __init__(self, image, rects, width, height):
        self.image = image
        self.width = width
        self.height = height
        self.rects = rects

        self.threshold = 80
        self.show_point = True
        self.hover_rect = None
        self.selected_rect = None
        self.start_point = None

        self.click_start = None
        self.mouse_pos = None

        self.input_mode = 'select'

        cv.setMouseCallback('frame', self.handle_mouse)

    def toggle_mode(self):
        modes = ['select', 'place']
        index = (modes.index(self.input_mode) + 1) % len(modes)
        if self.input_mode == 'select':
            self.select_rect(None)
        elif self.input_mode == 'place':
            self.start_point = None
        self.input_mode = modes[index]

    def collides(self, rect, x, y):
        x1 = int(rect[0] * self.width)
        y1 = int(rect[1] * self.height)
        x2 = int(rect[2] * self.width)
        y2 = int(rect[3] * self.height)
        if x > x1 and x < x2 and y > y1 and y < y2:
            return True
        return False

    def get_collisions(self, x, y):
        collisions = []
        for rect in self.rects:
            if self.collides(rect, x, y):
                collisions.append(rect)
        collisions.sort(key=lambda rect:
                        # method 1: sort by rect size
                        (rect[2] - rect[0]) * (rect[3] - rect[1])
                        # method 2: sort by distance to rect center
                        # abs(x - self.width * (rect[0] + rect[2]) / 2) +
                        # abs(y - self.height * (rect[1] + rect[3]) / 2)
                        )
        return collisions

    def select_rect(self, rect):
        self.selected_rect = rect

    def toggle_prob(self, rect):
        if rect[-1] < self.threshold / 100:
            rect[-1] = 1
        else:
            rect[-1] = 0

    # TODO: fix this
    # minor bug if a rect is inside another it can get toggled
    # if the big rect is select and small clicked
    def handle_selection_click(self, event, x, y, flags, param):
        if self.selected_rect is not None:
            if self.collides(self.selected_rect, x, y):
                self.toggle_prob(self.hover_rect)
            else:
                self.select_rect(self.hover_rect)
                self.toggle_prob(self.hover_rect)
        else:
            self.select_rect(self.hover_rect)

    def handle_place_click(self, event, x, y, flags, param):
        if self.start_point is None:
            self.start_point = (x, y)
        else:
            x1 = min(self.start_point[0], x) / self.width
            y1 = min(self.start_point[1], y) / self.height
            x2 = max(self.start_point[0], x) / self.width
            y2 = max(self.start_point[1], y) / self.height
            self.rects = np.vstack([self.rects, [x1, y1, x2, y2, 1]])
            self.start_point = None

    def handle_mouse(self, event, x, y, flags, param):
        rects = self.get_collisions(x, y)
        self.mouse_pos = (x, y)
        if event == cv.EVENT_LBUTTONDBLCLK:
            if self.input_mode == 'select':
                self.handle_selection_click(event, x, y, flags, param)
            else:
                self.handle_place_click(event, x, y, flags, param)
        else:
            if len(rects) > 0:
                self.hover_rect = rects[0]
            else:
                self.hover_rect = None

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
        elif k == 27:  # Escape
            self.select_rect(None)
            self.start_point = None
        elif k == 9:
            self.show_point = not self.show_point
        elif k == ord('m'):
            self.toggle_mode()
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
                        point=self.show_point
                        )

            if self.hover_rect is not None:
                show_rect(labels, self.width, self.height,
                          self.hover_rect,
                          color=(200, 0, 0),
                          show_conf=True,
                          point=False)

            if self.selected_rect is not None:
                show_rect(labels, self.width, self.height,
                          self.selected_rect,
                          color=(200, 0, 200),
                          show_conf=True,
                          point=False)

            if self.start_point is not None:
                cv.circle(labels, self.start_point, 2, (200, 0, 0), -1)
                x1 = min(self.start_point[0], self.mouse_pos[0]) / self.width
                y1 = min(self.start_point[1], self.mouse_pos[1]) / self.height
                x2 = max(self.start_point[0], self.mouse_pos[0]) / self.width
                y2 = max(self.start_point[1], self.mouse_pos[1]) / self.height
                show_rect(labels, self.width, self.height,
                          [x1, y1, x2, y2, 1],
                          color=(0, 0, 200),
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
