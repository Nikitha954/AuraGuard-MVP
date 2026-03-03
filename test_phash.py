import os
import tempfile

import numpy as np
from PIL import Image
import cv2

from phash import (
    image_phash,
    hamming_distance,
    video_phash,
    video_hamming_distance,
    load_known_hashes,
    save_known_hashes,
    load_known_video_hashes,
    save_known_video_hashes,
)


def test_image_phash_same():
    img = Image.new("RGB", (64, 64), color=(100, 150, 200))
    h1 = image_phash(img)
    h2 = image_phash(img.copy())
    assert h1 == h2


def test_hamming_distance():
    assert hamming_distance("ff", "ff") == 0
    assert hamming_distance("0f", "f0") > 0


def test_video_phash_and_similarity(tmp_path):
    # create a short video with 3 frames of solid colors
    video_file = tmp_path / "test.avi"
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(str(video_file), fourcc, 1.0, (64, 64))
    colors = [(10, 20, 30), (10, 21, 30), (200, 200, 200)]
    for c in colors:
        frame = np.zeros((64, 64, 3), dtype=np.uint8)
        frame[:] = c
        out.write(frame)
    out.release()

    hashes = video_phash(str(video_file), max_frames=5, frame_step=1)
    assert len(hashes) >= 3

    # identical video should have zero distance
    hashes2 = video_phash(str(video_file), max_frames=5, frame_step=1)
    assert video_hamming_distance(hashes, hashes2) == 0


def test_load_save(tmp_path):
    path = tmp_path / "h.json"
    save_known_hashes(str(path), ["abc", "def"])
    assert load_known_hashes(str(path)) == ["abc", "def"]
    vpath = tmp_path / "vh.json"
    save_known_video_hashes(str(vpath), [["a"], ["b"]])
    assert load_known_video_hashes(str(vpath)) == [["a"], ["b"]]
