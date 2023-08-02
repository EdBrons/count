import cv2 as cv


def draw_point(frame, label, row, bg=(0, 255, 0)):
    x_shape, y_shape = frame.shape[1], frame.shape[0]
    x1 = int(row[0]*x_shape)
    y1 = int(row[1]*y_shape)
    x2 = int(row[2]*x_shape)
    y2 = int(row[3]*y_shape)
    # classes = self.model.names  # Get the name of label index
    # label_font = cv.FONT_HERSHEY_SIMPLEX  # Font for the label.
    # Plot the boxes
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    cv.circle(frame, (cx, cy), radius=4, color=bg, thickness=-1)


def draw_box(frame, label, row, bg=(0, 255, 0)):
    x_shape, y_shape = frame.shape[1], frame.shape[0]
    x1 = int(row[0]*x_shape)
    y1 = int(row[1]*y_shape)
    x2 = int(row[2]*x_shape)
    y2 = int(row[3]*y_shape)
    confidence = row[4]
    # classes = self.model.names  # Get the name of label index
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
        f'{confidence:.2f}',
        (x1, y1),
        label_font,
        0.5,
        bg,
        1)
