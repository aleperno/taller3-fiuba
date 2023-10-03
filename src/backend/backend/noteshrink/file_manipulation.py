import sys
import magic
import numpy as np
from PIL import Image
from pdf2image import convert_from_path


def load(input_filename):
    """
    Loads an image from a provided filename
    File can either be an image or a PDF, PDFs will be converted to images

    Returns a list of tuples of the form (image, dpi)
    Each image is an array of pixels of dimensions (height, width, 3)
    """
    ret = []

    try:
        if magic.from_file(input_filename, mime=True) == 'application/pdf':
            pil_imgs = convert_from_path(input_filename)
        else:
            pil_imgs = [Image.open(input_filename)]
    except (IOError, KeyError):
        sys.stderr.write('warning: error opening {}\n'.format(input_filename))
        return ret

    for pil_img in pil_imgs:
        if pil_img.mode != 'RGB':
            pil_img = pil_img.convert('RGB')

        if 'dpi' in pil_img.info:
            dpi = pil_img.info['dpi']
        else:
            dpi = (300, 300)

        img = np.array(pil_img)

        ret.append((img, dpi))

    return ret
