from fpdf import FPDF
import os
import glob
from PIL import Image

pdf = FPDF()

# Get all jpg images from the rr folder
image_path = 'rr'
image_pattern = os.path.join(image_path, '*.jpg')
imagelist = sorted(glob.glob(image_pattern))  # Sort to maintain page order

print(f"Found {len(imagelist)} images to add to PDF")

for image in imagelist:
    try:
        # Get image dimensions
        with Image.open(image) as img:
            width, height = img.size
            # Calculate aspect ratio
            aspect = width / height
            
        print(f"Adding image: {image} (dimensions: {width}x{height})")
        
        pdf.add_page()
        
        # Use A4 page size (210x297 mm)
        page_width = 210
        page_height = 297
        
        # Calculate dimensions to fit the image properly on the page
        if aspect > (page_width / page_height):  # wider than tall
            img_width = page_width
            img_height = page_width / aspect
            x = 0
            y = (page_height - img_height) / 2
        else:  # taller than wide
            img_height = page_height
            img_width = page_height * aspect
            y = 0
            x = (page_width - img_width) / 2
        
        # Add image with proper dimensions and positioning
        pdf.image(image, x=x, y=y, w=img_width, h=img_height)
        
    except Exception as e:
        print(f"Error processing image {image}: {e}")

try:
    pdf.output("no_watermark.pdf")
    print(f"PDF created with {len(imagelist)} pages")
except Exception as e:
    print(f"Error creating PDF: {e}")