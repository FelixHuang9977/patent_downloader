from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

def images_to_pdf(image_paths, output_pdf):
    """
    Converts a list of image paths to a single PDF file.

    Args:
        image_paths: A list of strings, where each string is the path to an image.
        output_pdf: The path where the output PDF should be saved.
    """
    c = canvas.Canvas(output_pdf, pagesize=letter)
    for image_path in image_paths:
        try:
            img = Image.open(image_path)
            img_width, img_height = img.size
            c.drawImage(image_path, 0, 0, width=img_width, height=img_height)
            c.showPage()
        except Exception as e:
            print(f"Could not process image {image_path}: {e}")
    c.save()

if __name__ == '__main__':
    image_dir = "rr/"
    output_pdf = "output.pdf"
    
    image_files = [os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
    
    images_to_pdf(image_files, output_pdf)
    print(f"PDF created at: {output_pdf}")