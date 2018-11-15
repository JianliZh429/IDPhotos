import click
import cv2
import numpy as np


@click.group()
def main():
    pass


def avg_color(roi):
    b, g, r, _ = np.array(cv2.mean(roi), dtype=np.uint8)
    return b, g, r


def swap_color(image, color_2_change, target_color):
    image[np.where((image == color_2_change).all(axis=2))] = target_color
    return image


@main.command()
@click.option('--image_file', type=str, help='Image file of the photo you want to process')
def change_color(image_file):
    im = cv2.imread(image_file)
    height, width = im.shape[:2]
    offset = 20
    x1 = 0
    y1 = 0
    x2 = width - 1
    y2 = height - 1
    drawing = False
    raw_image = im.copy()
    image = im.copy()

    def _draw_rectangles(x1, y1, x2, y2):
        nonlocal raw_image
        cloned = raw_image.copy()
        cv2.rectangle(cloned, (x1, y1), (x2, y2), (5, 191, 30), 1)
        return cloned

    def select_bg_color(event, x, y, flags, param):
        nonlocal x1, y1, x2, y2, drawing, image, raw_image
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            x1, y1 = x, y

        elif event == cv2.EVENT_MOUSEMOVE and drawing:
            image = _draw_rectangles(x1, y1, x, y)

        elif event == cv2.EVENT_LBUTTONUP and drawing:
            x2, y2 = x, y
            image = _draw_rectangles(x1, y1, x2, y2)
            roi = raw_image[x1:x2, y1:y2]
            mean_color = avg_color(roi)
            print('mean_color: {}'.format(mean_color))
            raw_image = swap_color(raw_image, mean_color,  (255, 0, 0))

            drawing = False

    cv2.namedWindow(image_file)
    cv2.setMouseCallback(image_file, select_bg_color)

    while 1:
        try:
            cv2.imshow(image_file, image)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                break
        except Exception:
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
