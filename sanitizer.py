from PIL import Image

def strip_metadata(uploaded_image):
    # 1. Open the image the user uploaded
    original_img = Image.open(uploaded_image)
    
    # 2. Create a brand new, blank image with the exact same dimensions and color mode
    clean_img = Image.new(original_img.mode, original_img.size)
    
    # 3. Paste ONLY the visible pixels onto the blank canvas (leaving the hidden GPS data behind)
    clean_img.paste(original_img)
    
    # 4. Return the fully sanitized image
    return clean_img