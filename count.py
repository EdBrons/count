import torch
import cv2 as cv
from edit import Edit
from drawing import yolo_to_pixel, show_labels, show_overlay


class Count:
    def __init__(self, path_to_weights, camera):
        self.model = torch.hub.load(
            'ultralytics/yolov5',
            'custom',
            path=path_to_weights,
            force_reload=True)
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model.to(device)
        self.load_capture(camera)

        self.labeled_image = None
        cv.namedWindow('frame', cv.WINDOW_NORMAL)

        # display options

        self._threshold = 80
        self.thresh_step = 1
        self.lerp_conf = False
        self.show_point = True
        self.show_highlight = False
        self.mask_rect = False

        # keymap

        self.key_quit = ord('q')
        self.key_inc_thresh = ord('+')
        self.key_dec_thresh = ord('-')
        self.key_toggle_lerp = ord('l')
        self.key_edit = 13 # enter

    def load_capture(self, camera):
        self.capture = cv.VideoCapture(camera)
        self.capture.set(3, 640)
        self.capture.set(4, 480)
        if not self.capture.read()[0]:
            print('Cannot open camera. Exiting')
            exit(1)
        self.capture_width = int(self.capture.get(cv.CAP_PROP_FRAME_WIDTH))
        self.capture_height = int(self.capture.get(cv.CAP_PROP_FRAME_HEIGHT))

    def inc_threshold(self, val):
        MIN = 0
        MAX = 100
        new_threshold = self._threshold + val
        if new_threshold < MIN:
            self._threshold = MIN
        elif new_threshold > MAX:
            self._threshold = MAX
        else:
            self._threshold = new_threshold

    def threshold(self):
        return self._threshold / 100

    def toggle_lerp(self):
        self.lerp_conf = not self.lerp_conf

    def label_image(self, image, labels, saved=False):
        if not saved:
            self.labeled_image = image.copy()
            show_labels(
                self.labeled_image,
                labels, 
                threshold=self.threshold(),
                lerp=self.lerp_conf)
            show_overlay(self.overlay_string(), self.labeled_image)
        else:
            pass
            # just draw mouse stuff


    def handle_input(self, t=1):
        k = cv.waitKey(t)
        changed = False
        if k == -1:
            return
        elif k == self.key_quit:
            self.run = False
        elif k == self.key_inc_thresh:
            self.inc_threshold(self.thresh_step)
            changed = True
        elif k == self.key_dec_thresh:
            self.inc_threshold(-self.thresh_step)
            changed = True
        elif k == self.key_toggle_lerp:
            self.toggle_lerp()
            changed = True
        elif k == self.key_edit:
            self.edit_image()
        return changed


    def overlay_string(self):
        return f'threshold: {self.threshold()} (+/- to change)\n' \
               f'lerping: {self.lerp_conf}'

    def loop(self):
        self.run = True
        while self.run:
            ret, image = self.capture.read()
            if ret is None or ret is False:
                self.run = False
                break
            results = self.model(image)
            rects = yolo_to_pixel(results.xyxyn[0][:, :-1].numpy(), 
                            self.capture_width, self.capture_height)
            self.label_image(image, rects)
            cv.imshow('frame', self.labeled_image)
            self.handle_input()
    
    def edit_image(self, image=None):
        if image is None:
            ret, image = self.capture.read()

        results = self.model(image)
        rects = yolo_to_pixel(results.xyxyn[0][:, :-1].numpy(), 
                        self.capture_width, self.capture_height)

        while self.run:
            cv.imshow('frame', self.labeled_image)
            if self.handle_input(t=-1):
                self.label_image(image, rects)
                cv.imshow('frame', self.labeled_image)
        self.run = True

