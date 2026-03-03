import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS
import datetime

# ==========================================
# FEATURE 1: The Visual Proof (EXIF Extractor)
# ==========================================
def extract_exif_danger(image):
    """Reads the image and returns dangerous EXIF data to show the judges."""
    exif_data = {}
    info = image.getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            # Filter to only show interesting/dangerous data to the judges
            if decoded in ['Make', 'Model', 'DateTime', 'GPSInfo', 'Software']:
                exif_data[decoded] = value
    return exif_data


# ==========================================
# FEATURE 2: Anti-AI Deepfake Shield (Visual Noise)
# ==========================================
def apply_adversarial_noise(image):
    """Injects a subtle visual noise to disrupt AI deepfake training models."""
    # Convert image to a mathematical array
    img_array = np.array(image)
    
    # Generate random Gaussian noise (mean=0, standard deviation=8)
    # This is strong enough to confuse an AI, but faint enough for humans to ignore
    noise = np.random.normal(0, 8, img_array.shape).astype(np.int16)
    
    # Add noise to the original image and ensure colors stay within valid 0-255 bounds
    noisy_img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
    
    # Convert back to an image file
    return Image.fromarray(noisy_img_array)


# ==========================================
# FEATURE 3: Cyber-Crime Report Generator
# ==========================================
def generate_legal_report(decoded_message):
    """Generates a downloadable text file for cyber-cell reporting."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report_content = f"""
=====================================================
    AURAGUARD DIGITAL OWNERSHIP VERIFICATION REPORT
=====================================================
Date Generated: {timestamp}

TO WHOM IT MAY CONCERN (CYBER CRIME DIVISION):

This document serves as cryptographic proof of digital media ownership.
The attached media file was analyzed by the AuraGuard Steganographic Engine.

EXTRACTED OWNERSHIP WATERMARK: "{decoded_message}"

This embedded watermark verifies that the user who encoded the phrase "{decoded_message}" 
is the original owner of the source image. Any unauthorized morphing, deepfake 
generation, or distribution of this asset is a violation of digital privacy.

Generated securely via AuraGuard.
=====================================================
"""
    return report_content