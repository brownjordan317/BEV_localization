from PIL import Image
import os
import re

# Path to the folder containing the images
folder_path = '/home/undadmin/Documents/GitHub/BEV_localization/fourier_template_matching/output/plots/plots_png'
output_path = '/home/undadmin/Documents/GitHub/BEV_localization/fourier_template_matching/output/plots/plots_png/combined.png'

# Define the cropping box (left, top, right, bottom)
crop_box = (10, 90, 1700, 950)  # Adjust these values as needed

# Function to extract numerical part from filename
def extract_number(filename):
    match = re.search(r'(\d+)', filename)
    return int(match.group(0)) if match else float('inf')

# List and sort png files in numerical order
image_files = [f for f in os.listdir(folder_path) if f.endswith('.png')]
image_files.sort(key=extract_number)

# Load images and crop them
cropped_images = []
for img_file in image_files:
    img_path = os.path.join(folder_path, img_file)
    img = Image.open(img_path)
    cropped_img = img.crop(crop_box)
    cropped_images.append(cropped_img)

# Assuming all images are of the same size after cropping
img_width, img_height = cropped_images[0].size

# Create a new blank image with size large enough to hold the 3x3 grid
new_image = Image.new('RGBA', (img_width * 3, img_height * 3))

# Paste each image into the new image
for index, img in enumerate(cropped_images):
    x = (index % 3) * img_width
    y = (index // 3) * img_height
    new_image.paste(img, (x, y))

# Save the final image
new_image.save(output_path)