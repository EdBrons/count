import argparse
import cv2 as cv
import torch

from drawing import draw_box, draw_point
# from save import save_labels

"""
code start the camera capture
sudo modprobe v4l2loopback exclusive_caps=1 card_label="GPhoto2 Webcam"
gphoto2 --stdout --capture-movie  \
| ffmpeg -i - -vcodec rawvideo -pix_fmt yuv420p -threads 0 -f v4l2 /dev/video2
"""


def parse_args():
    parser = argparse.ArgumentParser(
        prog='counter',
        description='counts and annotates parts',
        epilog='author: ian brons')

    parser.add_argument('--camera')

    # parser.add_argument('--threshold', default=0.8)
    # parser.add_argument('--annotate', action='store_true')

    parser.add_argument('--format', choices=['yolo'], default='yolo')

    parser.add_argument('--weights', required=True)

    args = parser.parse_args()
    return args


class Application:
    def __init__(self, path_to_weights):
        self.model = torch.hub.load(
            'ultralytics/yolov5',
            'custom',
            path=path_to_weights,
            force_reload=True)

        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model.to(device)

    def load_capture(self, camera):
        self.capture = cv.VideoCapture(camera)
        self.capture.set(3, 640)
        self.capture.set(4, 480)
        if not self.capture.read()[0]:
            print('Cannot open camera. Exiting')
            exit(1)
        self.capture_width = int(self.capture.get(cv.CAP_PROP_FRAME_WIDTH))
        self.capture_height = int(self.capture.get(cv.CAP_PROP_FRAME_HEIGHT))

    def inference(self, frame):
        results = self.model(frame)
        labels = results.xyxyn[0][:, -1].numpy()
        cords = results.xyxyn[0][:, :-1].numpy()
        return labels, cords

    def cycle_mode(self):
        valid_modes = ['box', 'point']
        self.mode = valid_modes[(valid_modes.index(
            self.mode) + 1) % len(valid_modes)]

    def label_image(self, frame, labels, cords, mode):
        valid_modes = ['box', 'point']
        if mode not in valid_modes:
            print('invalid drawing mode')
            return
        count = 0
        for label, cord in zip(labels, cords):
            confidence = cord[4]
            if confidence < self.threshold:
                continue
            count += 1
            color = (0, int(255 * confidence), int(255 * (1 - confidence)))
            # if confidence < .8:
            #     continue
            if mode == 'box':
                draw_box(frame, label, cord, bg=color)
            elif mode == 'point':
                draw_point(frame, label, cord, bg=color)
        label_font = cv.FONT_HERSHEY_SIMPLEX  # Font for the label.
        cv.putText(
            frame,
            f'{count}',
            (50, 50),
            label_font,
            0.5,
            (0, 0, 0),
            1)
        return frame

    def handle_edit_input(self):
        k = cv.waitKey(1)
        if k == ord('q'):
            self.run = False
        if k == ord('h'):
            pass
        elif k == ord('j'):
            pass
        elif k == ord('k'):
            pass
        elif k == ord('l'):
            pass
        elif k == ord('H'):
            pass
        elif k == ord('J'):
            pass
        elif k == ord('K'):
            pass
        elif k == ord('L'):
            pass

    def edit_frame(self):
        ret, frame = self.capture.read()
        if not ret:
            return
        labels, cords = self.inference(frame)
        self.run = True
        while self.run:
            f = frame.copy()
            self.label_image(f, labels, cords, self.mode)
            cv.imshow('frame', f)
            self.handle_edit_input()

    def draw_edit(self, frame):
        pass

    def image_inference(self):
        image = cv.imread(self.image_path)
        cv.namedWindow('frame', cv.WINDOW_NORMAL)
        labels, cord = self.inference(image)
        self.label_image(image, labels, cord)
        cv.imshow('frame', image)
        cv.waitKey()

    def handle_cap_loop_input(self):
        k = cv.waitKey(1)
        if k == -1:
            return
        elif k == ord('i'):
            self.do_inference = not self.do_inference
        elif k == ord('q'):
            self.run = False
        elif k == 13:  # Enter
            self.run = False
            self.edit_frame()
        elif k == ord('-'):
            self.threshold = max(0, self.threshold - .05)
        elif k == ord('+'):
            self.threshold = min(1, self.threshold + .05)
        elif k == 9:
            self.cycle_mode()

    def capture_loop(self, camera):
        self.load_capture(camera)
        cv.namedWindow('frame', cv.WINDOW_NORMAL)

        self.run = True
        self.do_inference = True
        self.inference_rate = 2
        self.last_inference = 0
        self.results = None
        self.selection = (0, 0, 0, 0)
        self.threshold = .8
        self.mode = 'point'

        while self.run:
            ret, frame = self.capture.read()
            if ret is None or ret is False:
                self.run = False

            if self.do_inference:
                if self.last_inference == 0:
                    self.results = self.inference(frame)
                    self.last_inference = self.inference_rate
                else:
                    self.last_inference -= 1
                labels, cords = self.results
                self.label_image(frame, labels, cords, self.mode)

            cv.imshow('frame', frame)
            self.handle_cap_loop_input()

        cv.destroyAllWindows()


def main():
    args = parse_args()

    if args.camera is not None and args.image is not None:
        print('Input cannot be camera and image.')
        exit(1)
    elif args.camera is None and args.image is None:
        print('Camera or image must be specified.')
        exit(1)

    app = Application(args.weights)
    app.capture_loop(args.camera)


if __name__ == '__main__':
    main()
