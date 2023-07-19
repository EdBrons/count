import argparse
import cv2 as cv
import torch
import os
import uuid


def parse_args():
    parser = argparse.ArgumentParser(
        prog='Counter',
        description='What the program does',
        epilog='Text at the bottom of help')

    parser.add_argument('--capture', default=0)
    parser.add_argument('--realtime', action='store_true')
    parser.add_argument('--threshold', default=0.8)
    parser.add_argument('--annotate', action='store_true')
    parser.add_argument('--outdir', required=True)
    parser.add_argument('--format', choices=['yolo'], default='yolo')
    parser.add_argument('--weights', required=True)

    args = parser.parse_args()
    return args


class Application:
    def __init__(self, path_to_weights, outdir,
                 annotate=False, threshold=.8, fmt='yolo'):
        self.outdir = outdir
        self.annotate = annotate
        self.threshold = threshold
        self.format = fmt

        self.model = torch.hub.load(
            'ultralytics/yolov5',
            'custom',
            path=path_to_weights,
            force_reload=True)
        self.capture = self.load_capture()
        self.capture_width = int(self.capture.get(cv.CAP_PROP_FRAME_WIDTH))
        self.capture_height = int(self.capture.get(cv.CAP_PROP_FRAME_HEIGHT))

    def load_capture(self):
        cap = cv.VideoCapture(0)
        if not cap.read()[0]:
            print('Cannot open camera. Exiting')
            exit(1)
        return cap

    def inference(self, frame):
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model.to(device)
        results = self.model(frame)
        labels = results.xyxyn[0][:, -1].numpy()
        cord = results.xyxyn[0][:, :-1].numpy()
        return labels, cord

    def draw_box(self, frame, label, row, bg=(0, 255, 0)):
        x_shape, y_shape = frame.shape[1], frame.shape[0]
        x1 = int(row[0]*x_shape)
        y1 = int(row[1]*y_shape)
        x2 = int(row[2]*x_shape)
        y2 = int(row[3]*y_shape)
        classes = self.model.names  # Get the name of label index
        label_font = cv.FONT_HERSHEY_SIMPLEX  # Font for the label.
        # Plot the boxes
        cv.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            bg,
            2)
        # Put a label over box.
        cv.putText(
            frame,
            classes[label],
            (x1, y1),
            label_font,
            0.9,
            bg,
            2)

    def save_labels(self, frame, labels):
        it = os.path.join(self.outdir, 'images/train')
        lt = os.path.join(self.outdir, 'labels/train')
        base_fn = str(uuid.uuid4()) + '.jpg'
        filename = os.path.join(it, base_fn)
        cv.imwrite(filename, frame)
        text_fn = os.path.join(lt, os.path.basename(
            os.path.splitext(filename)[0]) + '.txt')
        # shutil.copy2(filename, it)
        lines = [f'{int(label)} {cord[0]:.6f} {cord[1]:.6f} '
                 f'{cord[2]:.6f} {cord[3]:.6f}\n'
                 for (label, cord) in labels]
        # print(text_fn, lines)
        with open(text_fn, 'w') as f:
            f.writelines(lines)

    def label_image(self, frame, labels, cords):
        for label, cord in zip(labels, cords):
            self.draw_box(frame, label, cord)
        return frame

    def edit_frame(self, frame):
        labels, cords = self.inference(frame)
        clean_frame = frame.copy()

        if not self.annotate:
            self.save_labels(frame, zip(labels, cords))
            return

        show_labels = frame.copy()
        self.label_image(show_labels, labels, cords)
        cv.imshow('frame', show_labels)
        print('preview, press any key to continue')
        cv.waitKey()

        valid = []
        print('valid rectangle - y, invalid rect - n')
        for label, cord in zip(labels, cords):
            confidence = cord[4]
            if confidence < self.threshold:
                new_frame = frame.copy()
                self.draw_box(new_frame, label, cord)
                cv.imshow('frame', new_frame)
                k = cv.waitKey()
                if k == ord('y'):
                    valid.append((label, cord))
        print('preview of selection')
        for (label, cord) in valid:
            self.draw_box(frame, label, cord)
        cv.imshow('frame', frame)
        cv.waitKey()

        print('save labels? y - yes')
        k = None
        while (k not in [ord('y'), ord('n')]):
            k = cv.waitKey()
            if k == ord('y'):
                self.save_labels(clean_frame, valid)

    def capture_loop(self, realtime):
        ret = True
        while ret:
            ret, frame = self.capture.read()
            if realtime:
                labels, cord = self.inference(frame)
                self.label_image(frame, labels, cord)
            cv.imshow('frame', frame)
            k = cv.waitKey(1)
            if k == ord('q'):
                break
            elif k == 13:
                ret, frame = self.capture.read()
                self.edit_frame(frame)
                break
        cv.destroyAllWindows()


def main():
    args = parse_args()
    app = Application(args.weights, args.outdir, annotate=args.annotate,
                      threshold=args.threshold, fmt=args.format)
    app.capture_loop(args.realtime)


if __name__ == '__main__':
    main()
