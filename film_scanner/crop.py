import numpy

from .image_with_mask import ImageWithMask


def crop_film(image: ImageWithMask):
    w, h = image.image.size

    for x in range(w):
        column = image.data[:, x]
        avr = numpy.average(column)
        if avr > 100:
            image.crop((x, 0, w, h))
            break

    w, h = image.image.size
    for x in range(w - 1, 0, -1):
        row = image.data[:, x]
        avr = numpy.average(row)
        if avr > 100:
            image.crop((0, 0, x, h))
            break
