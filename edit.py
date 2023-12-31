import cv2 as cv
from drawing import show_labels, show_overlay, show_label, find_overlaps
import numpy as np

# TODO:
# better way to handle mouse drags [X]
# show preview of new rect [X]
# ability to adjust squares: complicated
#   select rect then click line and drag it to move it
# move keybinds to a settings area
# add auto toggle mode [X]
# when two circles overlap, invert the overlapping region [x]
# add mode to hide rectangles that have been selected [x]


class Edit:
    def __init__(self, image, rects, width, height):
        self.image = image
        self.width = width
        self.height = height
        self.rects = rects

        self.mask = False
        self.threshold = 80
        self.show_point = True
        self.hover_rect = None
        self.selected_rect = None
        self.start_point = None
        self.hightlight = True

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
        if rect is None:
            return
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
            # add rect
            new_overlap = find_overlaps(
                self.image, self.width, self.height, self.rects, self.threshold / 100, new_rects=[len(self.rects) - 1], highlight=self.hightlight)
            self.overlap = cv.bitwise_and(self.overlap, new_overlap)
            self.start_point = None

    def collides_circ(self, p, r, x, y):
        return abs(p[0] - x) ** 2 + abs(p[1] - y) ** 2 < r ** 2

    def get_points(self, rect):
        return [
            (rect[0], rect[1]),
            (rect[2], rect[1]),
            (rect[0], rect[3]),
            (rect[2], rect[3])
        ]

    def get_corner(self, rect, x, y, eps=1):
        for index, p in enumerate(self.get_points(rect)):
            p2 = (p[0] * self.width, p[1] * self.height)
            if self.collides_circ(p2, eps, x, y):
                return index
        else:
            return -1

    def handle_mouse(self, event, x, y, flags, param):
        rects = self.get_collisions(x, y)
        self.mouse_pos = (x, y)
        # if self.selected_rect is not None and event == cv.EVENT_LBUTTONDOWN:
        # corner = self.get_corner(self.selected_rect, x, y, eps=5)
        # if corner != -1:
        #     print('clicked corner')
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

    def toggle_mask(self):
        self.mask = not self.mask

    def handle_input(self):
        k = cv.waitKey(1)
        if k == -1:
            return
        elif k == ord('q'):
            self.run = False
        elif k == ord('-'):
            self.threshold -= 1
            self.overlap = find_overlaps(
                self.image, self.width, self.height, self.rects, self.threshold / 100, highlight=self.hightlight)
        elif k == ord('+'):
            self.threshold += 1
            self.overlap = find_overlaps(
                self.image, self.width, self.height, self.rects, self.threshold / 100, highlight=self.hightlight)
        elif k == 27:  # Escape
            self.select_rect(None)
            self.start_point = None
        elif k == 9:
            self.show_point = not self.show_point
        elif k == ord('m'):
            self.toggle_mode()
        elif k == ord('p'):
            self.toggle_mask()
        else:
            # print(k)
            pass

    def count(self, threshold):
        n = 0
        for rect in self.rects:
            if rect[-1] > threshold / 100:
                n += 1
        return n

    def loop(self):
        self.run = True

        self.labels = self.image.copy()
        self.overlap = find_overlaps(
            self.labels, self.width, self.height, self.rects, self.threshold / 100, highlight=self.hightlight)
        while self.run:
            self.labels = self.image.copy()

            if self.mask:
                show_labels(self.labels, self.width,
                            self.height, self.rects,
                            threshold=(self.threshold / 100),
                            point=False,
                            fill=(0, 128, 255)
                            )
            else:
                show_labels(self.labels, self.width,
                            self.height, self.rects,
                            threshold=(self.threshold / 100),
                            point=self.show_point
                            )

            # show rect under mouse
            if self.hover_rect is not None and self.input_mode == 'select':
                show_label(self.labels, self.width, self.height,
                           self.hover_rect,
                           color=(200, 0, 0),
                           show_conf=True,
                           point=False)

            # show selected rect
            if self.selected_rect is not None:
                show_label(self.labels, self.width, self.height,
                           self.selected_rect,
                           color=(200, 0, 200),
                           show_conf=True,
                           point=False)

            # draw starter point and new rect
            if self.start_point is not None:
                cv.circle(self.labels, self.start_point, 2, (200, 0, 0), -1)
                x1 = min(self.start_point[0], self.mouse_pos[0]) / self.width
                y1 = min(self.start_point[1], self.mouse_pos[1]) / self.height
                x2 = max(self.start_point[0], self.mouse_pos[0]) / self.width
                y2 = max(self.start_point[1], self.mouse_pos[1]) / self.height
                show_label(self.labels, self.width, self.height,
                           [x1, y1, x2, y2, 1],
                           color=(0, 0, 200),
                           point=False)

            overlay_str = f'input mode: {self.input_mode}\n' \
                f'threshold: {self.threshold / 100:1.2}%\n' \
                f'count: {self.count(self.threshold)}'

            show_overlay(
                overlay_str,
                self.labels
            )

            labels = cv.bitwise_and(self.labels, self.overlap)

            cv.imshow('frame', labels)
            self.handle_input()
        self.quit()

    def quit(self):
        cv.setMouseCallback('frame', lambda *args: None)
