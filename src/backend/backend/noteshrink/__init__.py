import random
from typing import List, Tuple
import numpy as np
from PIL import Image


def sample_pixels(img: Image, sample_fraction: float) -> List[Tuple[int, int]]:
    """Returns a random sample of pixels from an image.
    The sample is a fraction of the total pixels in the image.
    """
    # Lo convierto a un vector de pixeles (alto x largo) x 3
    pixels = img.reshape((-1, 3))
    # Extraigo la cantidad de pixeles
    num_pixels = pixels.shape[0]
    # Calculo la cantidad de pixeles a samplear
    num_samples = int(num_pixels*sample_fraction)

    # Create a index vector of all pixels, shuffle it, and slice off the
    # required number of pixels for the sample
    idx = np.arange(num_pixels)
    np.random.shuffle(idx)

    # Return the sample
    return pixels[idx[:num_samples]]

