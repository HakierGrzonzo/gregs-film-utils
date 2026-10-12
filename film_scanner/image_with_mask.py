import numpy
from PIL import Image


class ImageWithMask:
    def __init__(self, path: str) -> None:
        self.image = Image.open(path).rotate(90)
        self.trim_mask = self.image.convert("L").point(lambda p: 255 if p > 5 else 0)
        self.data = numpy.asarray(self.trim_mask)

    def crop(self, params: tuple[float, float, float, float]):
        self.image = self.image.crop(params)
        self.trim_mask = self.trim_mask.crop(params)
        self.data = numpy.asarray(self.trim_mask)
