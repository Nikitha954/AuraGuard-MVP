from PIL import Image
from io import BytesIO


def _ensure_rgb(image: Image.Image) -> Image.Image:
    if image.mode != "RGB":
        return image.convert("RGB")
    return image


def encode_image_with_message(image: Image.Image, message: str) -> Image.Image:
    """Encode `message` into a copy of `image` using LSB steganography on the red channel.

    Appends a single-character delimiter '$' to mark the end of the message.
    Returns a new PIL Image.
    """
    img = _ensure_rgb(image).copy()
    width, height = img.size
    pixels = list(img.getdata())

    data = message + "$"
    bits = ''.join(format(ord(c), '08b') for c in data)
    if len(bits) > len(pixels):
        raise ValueError("Message too long to encode in image")

    out_pixels = []
    bit_idx = 0
    for pix in pixels:
        if bit_idx < len(bits):
            r, g, b = pix
            new_r = (r & 0xFE) | int(bits[bit_idx])
            out_pixels.append((new_r, g, b))
            bit_idx += 1
        else:
            out_pixels.append(pix)

    img.putdata(out_pixels)
    return img


def decode_message_from_image(image: Image.Image) -> str:
    """Decode and return the hidden message from `image` using LSB of red channel.

    Returns empty string if no delimiter is found.
    """
    img = _ensure_rgb(image)
    pixels = list(img.getdata())

    bits = []
    for pix in pixels:
        bits.append(str(pix[0] & 1))

    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) < 8:
            break
        ch = chr(int(''.join(byte), 2))
        chars.append(ch)
        if ch == '$':
            break

    if not chars or chars[-1] != '$':
        return ""

    return ''.join(chars)[:-1]


def image_to_bytes(image: Image.Image, fmt: str = "PNG") -> bytes:
    buf = BytesIO()
    img = _ensure_rgb(image)
    img.save(buf, format=fmt)
    return buf.getvalue()
from PIL import Image
from io import BytesIO
from typing import Tuple


def encode_image_with_message(image: Image.Image, message: str) -> Image.Image:
    """Return a copy of `image` with `message` encoded into LSB of red channel.

    The returned image is an RGB PNG-capable Image object. Message is
    terminated with a single `$` delimiter.
    """
    if image.mode != "RGB":
        img = image.convert("RGB")
    else:
        img = image.copy()

    data = message + "$"
    data_bin = ''.join(format(ord(c), '08b') for c in data)

    pixels = list(img.getdata())
    out_pixels = []
    idx = 0
    for p in pixels:
        r, g, b = p
        if idx < len(data_bin):
            r = (r & 0xFE) | int(data_bin[idx])
            idx += 1
        out_pixels.append((r, g, b))

    img.putdata(out_pixels)
    return img


def decode_message_from_image(image: Image.Image) -> str:
    """Extract the hidden message from `image` encoded in red-channel LSBs.

    Returns the decoded string. If no delimiter is found, returns an empty
    string.
    """
    if image.mode != "RGB":
        img = image.convert("RGB")
    else:
        img = image

    pixels = list(img.getdata())
    bits = []
    for p in pixels:
        bits.append(str(p[0] & 1))

    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) < 8:
            break
        val = int(''.join(byte), 2)
        ch = chr(val)
        chars.append(ch)
        if ch == '$':
            break

    # If no delimiter was present, treat as no message
    if not chars or '$' not in chars:
        return ""
    s = ''.join(chars)
    return s.rstrip('$')


def image_to_bytes(img: Image.Image, fmt: str = "PNG") -> bytes:
    buf = BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()
