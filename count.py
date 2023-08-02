import torch
import cv2 as cv
from edit import Edit
from drawing import show_labels, show_overlay


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
        self.threshold = .8
        cv.namedWindow('frame', cv.WINDOW_NORMAL)

    def load_capture(self, camera):
        self.capture = cv.VideoCapture(camera)
        self.capture.set(3, 640)
        self.capture.set(4, 480)
        if not self.capture.read()[0]:
            print('Cannot open camera. Exiting')
            exit(1)
        self.capture_width = int(self.capture.get(cv.CAP_PROP_FRAME_WIDTH))
        self.capture_height = int(self.capture.get(cv.CAP_PROP_FRAME_HEIGHT))

    def mask_image(self, image, rects):
        new_img = image.copy()
        for row in rects:
            overlay = new_img.copy()
            cords = row[:-1]
            x1 = int(cords[0] * self.capture_width)
            y1 = int(cords[1] * self.capture_height)
            x2 = int(cords[2] * self.capture_width)
            y2 = int(cords[3] * self.capture_height)
            p = row[-1] / 2
            cv.rectangle(overlay, (x1, y1), (x2, y2), (0, 200, 0), -1)
            new_img = cv.addWeighted(overlay, p, new_img, 1 - p, 0)
        return new_img

    def edit_image(self):
        ret, image = self.capture.read()
        if ret is None or ret is False:
            self.run = False
            return
        results = self.model(image)
        rects = results.xyxyn[0][:, :-1].numpy()
        edit = Edit(image, rects, self.capture_width, self.capture_height)
        edit.loop()

    def handle_input(self):
        k = cv.waitKey(1)
        if k == -1:
            return
        elif k == ord('q'):
            self.run = False
        elif k == 13:  # tab
            self.edit_image()

    def loop(self):
        self.run = True
        while self.run:
            ret, image = self.capture.read()
            if ret is None or ret is False:
                self.run = False
                break
            results = self.model(image)
            rects = results.xyxyn[0][:, :-1].numpy()
            image = show_labels(
                image, self.capture_width, self.capture_height, rects, threshold=self.threshold)
            show_overlay(f'threshold: {self.threshold}', image)
            cv.imshow('frame', image)
            self.handle_input()
