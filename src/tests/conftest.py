import pytest
from PIL import Image


@pytest.fixture
def sample_image_1():
    return Image.open("./tests/utils/imgs/template-0.png")
