import PyPDF2
import io


from PIL import Image
import numpy as np
import noteshrink
from ..utils import file_manipulation as fm


HEADERS = {"Content-Type": "application/json"}


DEFAULT_OPTS = {
    'filenames': ['/tmp/template.pdf'],
    'quiet': False,
    'basename': 'page',
    'pdfname': '/tmp/shrinked3.pdf',
    'value_threshold': 0.25,
    'sat_threshold': 0.2,
    'num_colors': 80,
    'sample_fraction': 0.05,
    'white_bg': True,
    'global_palette': False,
    'saturate': True,
    'sort_numerically': True,
    'postprocess_cmd': None,
    'postprocess_ext': '_post.png',
    'pdf_cmd': 'convert %i %o',
    'clean': True
}


create_task_request = {
    "global_palette_opt": True,
    "white_background": True,
    "colours": 5,
    "total_pages": 2,
    "selected_pages": [0, 1]
}


class CustomOptions(object):
    def __init__(self, data):
        self._data = data

    def __getattr__(self, item):
        return self._data[item]

    def __setattr__(self, key, value):
        if key == '_data':
            return super(CustomOptions, self).__setattr__(key, value)
        self._data[key] = value


def load_from_img(img):
    return np.array(img), (300, 300)


def save_changes(labels, palette, dpi, options):
    if options.saturate:
        palette = palette.astype(np.float32)
        pmin = palette.min()
        pmax = palette.max()
        palette = 255 * (palette - pmin)/(pmax-pmin)
        palette = palette.astype(np.uint8)

    if options.white_bg:
        palette = palette.copy()
        palette[0] = (255, 255, 255)

    output_img = Image.fromarray(labels, 'P')
    output_img.putpalette(palette.flatten())

    return output_img


def shrink_img(img, options):
    img_pixels, dpi = load_from_img(img)
    samples = noteshrink.sample_pixels(img_pixels, options)
    palette = noteshrink.get_palette(samples, options)
    labels = noteshrink.apply_palette(img_pixels, palette, options)
    out_img = save_changes(labels, palette, dpi, options)
    out_img = out_img.convert('RGB')
    bytes_output = io.BytesIO()
    out_img.save(bytes_output, format='pdf', dpi=dpi)
    pdf_obj = PyPDF2.PdfReader(stream=bytes_output)
    return pdf_obj


def shrink_pdf_bytes(pdf_bytes, white_background, colour_count):
    pdf_obj = fm.encoded_bytes_to_pdf_obj(pdf_bytes)
    aux = fm.pdf_obj_to_images(pdf_obj)
    options = CustomOptions(DEFAULT_OPTS)
    options.white_bg = white_background
    options.num_colors = colour_count

    shrinked_pdf_obj = shrink_img(aux[0], options)
    return fm.pdf_obj_to_encoded_bytes(shrinked_pdf_obj)
