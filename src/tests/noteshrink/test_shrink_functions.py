from backend.noteshrink import sample_pixels
from backend.noteshrink.file_manipulation import load


def test_load():
     img, _ = load("./tests/utils/imgs/template-0.png")[0]
     assert img.shape == (3508, 2480, 3)


def test_sample_pixels(sample_image_1):
    img, _ = load("./tests/utils/imgs/template-0.png")[0]
    sample_pixels(img, 0.05)
