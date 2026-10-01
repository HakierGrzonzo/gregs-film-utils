from sys import argv
import time
from statistics import median, median_low
import tempfile
from itertools import count, pairwise
from PIL import Image, ImageOps, ImageDraw
import numpy
import subprocess

file = argv[1]

image = Image.open(file)

trim_mask = ImageOps.grayscale(image)
trim_mask = ImageOps.posterize(trim_mask, 1)

data = numpy.asarray(trim_mask)

w, h = image.size

for x in range(0, w):
    column = data[:, x]
    avr = numpy.average(column)
    if avr > 100:
        image = image.crop((x, 0, w, h))
        trim_mask = trim_mask.crop((x, 0, w, h))
        break

for x in range(w - 1, 0, -1):
    row = data[:, x]
    avr = numpy.average(row)
    if avr > 100:
        w2, h2 = image.size
        image = image.crop((0, 0, w2 - (w - x), h2))
        trim_mask = trim_mask.crop((0, 0, w2 - (w - x), h2))
        break

# chop in half

w, h = image.size

image = image.crop((0, 0, w // 2, h))

w, h = image.size

# Chop into frames
NUM_OF_FRAMES = 9

naive_height = h // NUM_OF_FRAMES

y = 0
data = numpy.asarray(trim_mask)

found_maybe_frames = []
while y < h:
    row = data[y]
    avr = numpy.average(row)
    if avr < 100:
        found_maybe_frames.append(y)
        y += naive_height // 4
        continue
    y += 1


maybe_frame_heights = [b - a for a, b in pairwise(found_maybe_frames)]
frame_height = median_low(maybe_frame_heights)

with tempfile.TemporaryDirectory() as tempdir:
    frame_tops = found_maybe_frames[:-1]
    for i, frame_top in enumerate(frame_tops):
        frame = image.crop((0, frame_top, w, frame_top + frame_height))
        frame.save(f"{tempdir}/frame_{i:03}.bmp")
        frame.close()

    proc = subprocess.run(
            ["ffmpeg", "-framerate", "12",  "-y", "-pattern_type", "glob", "-i", f"{tempdir}/*.bmp", "concatenated_output.mp4"],
            check=True
    )
