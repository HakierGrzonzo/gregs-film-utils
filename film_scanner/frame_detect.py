from film_scanner.image_with_mask import ImageWithMask
import numpy


naive_height = 235
sprocket_height = 78
threshold = 0.95 * 255


def detect_frames(image: ImageWithMask):
    w, h = image.image.size
    y = 0

    while y < h:
        row = image.data[y]
        avr = numpy.average(row)
        if avr < threshold and avr > 200:
            rows = image.data[y : y + sprocket_height]
            sprocket_average = numpy.average(rows)

            if avr < 200:
                y += naive_height // 4
                continue

            if sprocket_average < threshold:
                frame_start = y + sprocket_height // 2
                if frame_start + naive_height > h:
                    break
                yield frame_start
                y += naive_height // 2
                continue
        y += 1
