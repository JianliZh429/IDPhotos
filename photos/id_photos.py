import os

import click
import cv2
import numpy as np
import sys

CURRENT_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.append(ROOT_DIR)

from photos.contants import BACKGROUND_COLORS, BACKGROUND_COLORS_NAMES, TARGET_SIZES


@click.group()
def cli():
    pass


def grab_cut(image_file, out_dir, tz, verbose=1):
    im = cv2.imread(image_file)
    height, width = im.shape[:2]
    mask = np.zeros(im.shape[:2], np.uint8)
    bgd = np.zeros((1, 65), np.float64)
    fgd = np.zeros((1, 65), np.float64)
    rect = (0, 0, width - 1, height - 1)

    cv2.grabCut(im, mask, rect, bgd, fgd, 5, cv2.GC_INIT_WITH_RECT)
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype(np.uint8)
    img = im*mask2[:, :, np.newaxis]

    for name, tz_color in zip(BACKGROUND_COLORS_NAMES, BACKGROUND_COLORS):
        _img = img.copy()
        _img[np.where((_img == (0, 0, 0)).all(axis=2))] = tz_color
        _img = cv2.resize(_img, TARGET_SIZES[tz], interpolation=cv2.INTER_AREA)

        cv2.imwrite(os.path.join(out_dir, '{}_{}.jpg'.format(tz, name)), _img)

    if verbose:
        while 1:
            cv2.imshow('im', img)
            k = cv2.waitKey(1) & 0xFF
            if k == 27:
                break

    cv2.destroyAllWindows()


@cli.command()
@click.option('--image_file', type=str, help='Image file of the photo you want to process')
@click.option('--out_dir', default='./output', type=str, help='Output directory to save results')
@click.option('--tz', default=1, type=int, help='Output image size: 1 is for 1 inch, 2 is for 2 inches')
@click.option('--verbose', default=0, type=int, help='Whether to show processing images, press ESC to close window')
def change_color(image_file, out_dir, tz, verbose):
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    grab_cut(image_file, out_dir, tz, verbose=verbose)


if __name__ == "__main__":
    cli()
