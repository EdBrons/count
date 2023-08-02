import argparse
import cv2 as cv
from count import Count
from drawing import lerp, lerp_color

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

    parser.add_argument('--camera', required=True)
    parser.add_argument('--weights', required=True)

    args = parser.parse_args()
    return args


class Application:
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
        low_confidence = .5
        high_confidence = 1
        bad_color = (0, 0, 204)
        good_color = (0, 204, 0)

        if mode not in valid_modes:
            print('invalid drawing mode')
            return
        count = self.count(labels, cords)

        for label, cord in zip(labels, cords):
            confidence = cord[4]
            if confidence < self.threshold / 100:
                continue
            x = lerp(low_confidence, high_confidence, confidence)
            color = lerp_color(bad_color, good_color, x)
        label_font = cv.FONT_HERSHEY_SIMPLEX  # Font for the label.
        cv.putText(
            frame,
            f'mode: {self.mode} threshold: {self.threshold}% count: {count}',
            (50, 50),
            label_font,
            0.5,
            (0, 0, 0),
            1)
        return frame

    def handle_cap_loop_input(self):
        k = cv.waitKey(1)
        if k == -1:
            return
        elif k == ord('q'):
            self.run = False
        # elif k == 13:  # enter
        #     self.run = False
        elif k == ord('-'):
            self.threshold = max(0, self.threshold - 1)
        elif k == ord('+'):
            self.threshold = min(100, self.threshold + 1)
        elif k == 9:  # tab
            self.cycle_mode()

    def capture_loop(self, camera):
        self.load_capture(camera)
        cv.namedWindow('frame', cv.WINDOW_NORMAL)

        self.run = True
        self.results = None
        self.threshold = 80
        self.mode = 'point'

        while self.run:
            ret, frame = self.capture.read()
            if ret is None or ret is False:
                self.run = False

            self.results = self.inference(frame)
            labels, cords = self.results
            self.label_image(frame, labels, cords, self.mode)

            cv.imshow('frame', frame)
            self.handle_cap_loop_input()

        cv.destroyAllWindows()


def main():
    args = parse_args()

    counter = Count(args.weights, args.camera)
    counter.loop()

    # app = Application(args.weights)
    # app.capture_loop(args.camera)


if __name__ == '__main__':
    main()
