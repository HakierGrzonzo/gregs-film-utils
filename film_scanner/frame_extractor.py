from itertools import count, pairwise
from pathlib import Path
import subprocess
import tempfile
from statistics import median_low

from film_scanner.crop import crop_film
from film_scanner.frame_detect import detect_frames
from statistics import median_low
from film_scanner.image_with_mask import ImageWithMask


def generate_frame_name(tempdir: str):
    for c in count():
        yield f"{tempdir}/frame_{c:03}.bmp"


class FrameExtractor:
    def __init__(self) -> None:
        self.images = list[tuple[ImageWithMask, list[int]]]()

    def feed(self, path: str):
        image = ImageWithMask(path)

        crop_film(image)
        w, h = image.image.size

        found_maybe_frames = list(detect_frames(image))
        image.trim_mask.save("cut.bmp")

        self.images.append((image, found_maybe_frames))
        print(f"Consumed {path} with {len(found_maybe_frames) * 2} frames")

    def extract_frames(self, framerate: int, output_path: Path):
        frame_heights = []
        frame_widths = []
        for image, frame_toppoints in self.images:
            maybe_frame_heights = [b - a for a, b in pairwise(frame_toppoints)]
            frame_heights.extend(maybe_frame_heights)
            w, _h = image.image.size
            frame_widths.append(w)

        frame_height = median_low(frame_heights)
        frame_width = median_low(frame_widths) // 2

        with tempfile.TemporaryDirectory(
            prefix="film_scanner", delete=False
        ) as tempdir:
            frame_names = generate_frame_name(tempdir)
            for image, frame_tops in self.images:
                w, h = image.image.size
                for frame_top, frame_name in zip(frame_tops, frame_names):
                    print(frame_top)
                    frame = image.image.crop(
                        (w // 2, frame_top, w, frame_top + frame_height)
                    )
                    frame = frame.resize((frame_width, frame_height))
                    frame.save(frame_name)
                    frame.close()

            for image, frame_tops in reversed(self.images):
                w, h = image.image.size
                for frame_top, frame_name in zip(reversed(frame_tops), frame_names):
                    print(frame_top)
                    frame = image.image.crop(
                        (0, frame_top, w // 2, frame_top + frame_height)
                    ).rotate(180)
                    frame = frame.resize((frame_width, frame_height))
                    frame.save(frame_name)
                    frame.close()

            proc = subprocess.run(
                [
                    "ffmpeg",
                    "-framerate",
                    str(framerate),
                    "-y",
                    "-pattern_type",
                    "glob",
                    "-i",
                    f"{tempdir}/*.bmp",
                    "-vf",
                    "crop=in_w-160:x=0,scale=1280:-2",
                    "-pix_fmt",
                    "yuv420p",
                    "-profile:v",
                    "baseline",
                    "-level",
                    "3.0",
                    "-preset",
                    "slower",
                    "-crf",
                    "10",
                    str(output_path),
                ],
                check=True,
            )
