from PIL import Image
import numpy as np
import json
from typing import List
from scipy.fftpack import dct as scipy_dct

# Try to import cv2 for video support, but don't require it
try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False


def image_phash(image: Image.Image, hash_size: int = 8, highfreq_factor: int = 4) -> str:
    """Compute perceptual hash (pHash) for an image and return as hex string.

    Steps:
    - convert to grayscale
    - resize to (hash_size * highfreq_factor)
    - compute 2D DCT via scipy
    - keep top-left hash_size x hash_size low-frequency DCT coeffs
    - compute median (excluding DC term) and build bits
    - return hex string representation of the bits
    """
    img_size = hash_size * highfreq_factor
    try:
        resample = Image.Resampling.LANCZOS
    except AttributeError:
        resample = Image.ANTIALIAS

    img = image.convert("L").resize((img_size, img_size), resample)
    pixels = np.asarray(img, dtype=np.float32)

    # compute 2D DCT using scipy (more reliable than cv2)
    dct = scipy_dct(scipy_dct(pixels, axis=0, norm='ortho'), axis=1, norm='ortho')

    # take top-left low-frequency components
    dct_low = dct[:hash_size, :hash_size]

    # use median of the coefficients excluding the DC term at [0,0]
    flattened = dct_low.flatten()
    if flattened.size <= 1:
        median = 0
    else:
        median = np.median(flattened[1:])

    bits = (dct_low > median).astype(int).flatten()
    bitstring = ''.join(str(b) for b in bits)
    hexlen = (len(bitstring) + 3) // 4
    intval = int(bitstring, 2)
    return f"{intval:0{hexlen}x}"


def hamming_distance(hex1: str, hex2: str, hash_size: int = 8) -> int:
    """Return Hamming distance between two pHash hex strings."""
    nbits = hash_size * hash_size
    a = int(hex1, 16)
    b = int(hex2, 16)
    x = a ^ b
    mask = (1 << nbits) - 1
    x = x & mask
    return x.bit_count()


def is_similar(hex1: str, hex2: str, max_distance: int = 10, hash_size: int = 8) -> bool:
    return hamming_distance(hex1, hex2, hash_size) <= max_distance


def load_known_hashes(path: str) -> List[str]:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except FileNotFoundError:
        return []
    except Exception:
        return []


def save_known_hashes(path: str, hashes: List[str]):
    """Store a list of hashes to a JSON file (overwrites)."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(hashes, f, indent=2)


def load_known_video_hashes(path: str) -> List[List[str]]:
    """Load video hash lists; each entry is a list of frame hashes."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                # naive check; assume nested lists
                return data  # type: ignore
    except FileNotFoundError:
        return []
    except Exception:
        return []


def save_known_video_hashes(path: str, hashes: List[List[str]]):
    """Save a list of frame-hash lists to JSON."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(hashes, f, indent=2)


# ---- video support -------------------------------------------------------

def video_phash(
    video_path: str,
    max_frames: int = 20,
    frame_step: int = 30,
    hash_size: int = 8,
    highfreq_factor: int = 4,
) -> List[str]:
    """Compute perceptual hashes for a video by sampling frames.

    Uses OpenCV if available, otherwise falls back to basic image file reading.
    Every ``frame_step`` frames a snapshot is taken until ``max_frames`` hashes 
    have been produced or the video ends.

    Each sampled frame is converted to ``PIL.Image`` and passed to
    :func:`image_phash` using the provided ``hash_size``/``highfreq_factor``.

    Returns a list of hex-string hashes corresponding to the sampled frames.
    """
    if not HAS_CV2:
        raise ImportError(
            "Video processing requires opencv-python-headless. "
            "Please ensure it's installed in your environment."
        )
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"cannot open video {video_path}")

    hashes: List[str] = []
    frame_idx = 0
    produced = 0
    while produced < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % frame_step == 0:
            # OpenCV reads as BGR numpy array
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            hashes.append(image_phash(img, hash_size=hash_size, highfreq_factor=highfreq_factor))
            produced += 1
        frame_idx += 1
    cap.release()
    return hashes


def video_hamming_distance(
    hashes1: List[str], hashes2: List[str], max_distance: int = 10
) -> int:
    """Return the smallest hamming distance between any frame hash pairs."""
    best = None
    for h1 in hashes1:
        for h2 in hashes2:
            d = hamming_distance(h1, h2)
            if best is None or d < best:
                best = d
    return best if best is not None else -1


def video_is_similar(
    hashes1: List[str], hashes2: List[str], max_distance: int = 10
) -> bool:
    """Bool indicating whether any pair of frame hashes are within threshold."""
    return video_hamming_distance(hashes1, hashes2, max_distance) <= max_distance
