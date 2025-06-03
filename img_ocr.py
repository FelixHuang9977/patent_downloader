from PIL import Image
import pytesseract
import os, glob

image_path = 'rr'
image_pattern = os.path.join(image_path, '*.jpg')
imagelist = sorted(glob.glob(image_pattern))  # Sort to maintain page order

print(f"Found {len(imagelist)} images to add to PDF")

for img_name in imagelist:
    img = Image.open(img_name)
    text = pytesseract.image_to_string(img, lang='eng')
    print(text)