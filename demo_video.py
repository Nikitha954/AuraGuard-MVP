"""Demo script showing how to compute and compare video perceptual hashes.

Usage examples:

    python demo_video.py

The script will generate two synthetic videos (solid-color frames), modify one
slightly, and print the frame-hash lists along with the minimum Hamming
distance between them. This mirrors what the Streamlit UI does under the hood.
"""
import tempfile
import os
from pathlib import Path

import numpy as np
from PIL import Image
import cv2

from phash import video_phash, video_hamming_distance


def make_video(path: Path, colors, size=(64, 64), fps=1):
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    writer = cv2.VideoWriter(str(path), fourcc, fps, size)
    for c in colors:
        frame = np.zeros((size[1], size[0], 3), dtype=np.uint8)
        frame[:] = c
        writer.write(frame)
    writer.release()


def main():
    with tempfile.TemporaryDirectory() as td:
        v1 = Path(td) / "orig.avi"
        v2 = Path(td) / "edited.avi"
        # original has three colors
        make_video(v1, [(10, 20, 30), (60, 70, 80), (100, 110, 120)])
        # create edited version by slightly modifying a frame color
        make_video(v2, [(10, 20, 30), (61, 70, 80), (100, 110, 120)])

        h1 = video_phash(str(v1), max_frames=10, frame_step=1)
        h2 = video_phash(str(v2), max_frames=10, frame_step=1)
        print("Hashes video 1:", h1)
        print("Hashes video 2:", h2)
        d = video_hamming_distance(h1, h2)
        print("Minimum Hamming distance between the two videos:", d)
        threshold = 5
        if d <= threshold:
            print(f"Distance {d} <= {threshold} → videos are similar")
        else:
            print(f"Distance {d} > {threshold} → videos are different")


if __name__ == "__main__":
    main()
