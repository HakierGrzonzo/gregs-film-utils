from sys import argv
from film_scanner.frame_extractor import FrameExtractor
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from pathlib import Path


how_the_film_should_look = """
The raw files to be scanned should have this orientation:

frame->frame->frame
frame<-frame<-frame

The top row will be scanned first.
""".strip()


def main():
    parser = ArgumentParser(
        prog="film-scanner",
        description="Extracts frames from standard 8mm scans",
        epilog=how_the_film_should_look,
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "filename",
        type=Path,
        action="extend",
        nargs="+",
        help="Path to file or files to extract the frames from, the files should contain the scans, with frames going left to right, then back from right to left",
    )
    parser.add_argument(
        "--framerate",
        type=int,
        default=12,
        help="Frame rate to output, defaults to %(default)s",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Path to output the video, defaults to %(default)s",
        default="./concatenated_output.mp4",
    )
    parsed = parser.parse_args()

    frame_extractor = FrameExtractor()
    for file in parsed.filename:
        frame_extractor.feed(file)

    frame_extractor.extract_frames(parsed.framerate, parsed.output)
