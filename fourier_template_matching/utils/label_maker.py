import os
from PIL import Image

def crop_bottom_15_pixels(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            img_path = os.path.join(input_folder, filename)
            img = Image.open(img_path)
            width, height = img.size
            
            # Crop the bottom 15 pixels
            cropped_img = img.crop((0, 0, width, height - 15))
            
            # Save the cropped image
            output_path = os.path.join(output_folder, filename)
            cropped_img.save(output_path)
            print(f"Cropped and saved {filename}")

# Specify the input and output folders
input_folder = 'path/to/your/input/folder'
output_folder = 'path/to/your/output/folder'

crop_bottom_15_pixels(input_folder, output_folder)
