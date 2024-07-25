import numpy as np
from PIL import Image, ImageDraw
import cv2
import os
import csv

def calc_pixel_lat_long(pixel_coords, tl_coords, br_coords, image_size):
    tl_lat, tl_lon = tl_coords
    br_lat, br_lon = br_coords

    w, h = image_size

    lat_multiplier = (br_lat - tl_lat) / h
    lon_multiplier = (br_lon - tl_lon) / w

    lat = tl_lat + lat_multiplier * pixel_coords[1]
    lon = tl_lon + lon_multiplier * pixel_coords[0]

    return lat, lon

def crop_out_segments(image_path, tl_coords, br_coords):
    image = Image.open(image_path)
    image_np = np.array(image)

    # Define the red color range in RGB format
    lower_red = np.array([120, 0, 0])  # Adjust these values based on your specific red shade
    upper_red = np.array([255, 50, 50])  # Adjust these values based on your specific red shade

    # Mask of red areas in the image
    red_mask = cv2.inRange(image_np, lower_red, upper_red)

    # Find contours of the red areas
    contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find the largest contour (assuming it's your red square)
    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)

    # Crop the original image based on the bounding box
    cropped_image = image.crop((x, y, x + w, y + h))
    # Resize the cropped
    cropped_image = cropped_image.resize((6000, 6000))
    cropped_image.save('cropped.png')

    # Split the image into 4 equal-sized segments
    segment_width = cropped_image.width // 3
    segment_height = cropped_image.height // 3
    segments = []
    segment_coords = []
    for i in range(3):
        for j in range(3):
            left = i * segment_width
            upper = j * segment_height
            right = left + segment_width
            lower = upper + segment_height
            segment = cropped_image.crop((left, upper, right, lower))
            segments.append(segment)
            segment_coords.append((left, upper, right, lower))

    # Save each segment
    output_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crops')
    os.makedirs(output_directory, exist_ok=True)

    for i, segment in enumerate(segments):
        # print(segment_coords[i])
        segment_tl_lat, segment_tl_lon = calc_pixel_lat_long((segment_coords[i][0], segment_coords[i][1]), tl_coords, br_coords, cropped_image.size)
        # print(segment_tl_lat, segment_tl_lon)
        segment_br_lat, segment_br_lon = calc_pixel_lat_long((segment_coords[i][2], segment_coords[i][3]), tl_coords, br_coords, cropped_image.size)
        # print(segment_br_lat, segment_br_lon)
        image_filename_without_extension = os.path.basename(image_path).split('.')[0]
        filename = f'{image_filename_without_extension}_segment_{i}.jpg'
        segment.save(os.path.join(output_directory, filename))

        print(f"Segment {i} saved as {filename}")

        # Append metadata to CSV file
        csvFile = os.path.join(output_directory, "map.csv")
        with open(csvFile, "a", newline='') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow([filename, segment_tl_lat, segment_tl_lon, segment_br_lat, segment_br_lon])


if __name__ == '__main__':
    input_image = '/home/undadmin/Documents/GitHub/BEV_localization/sat_images_with_coords/randolphVT_sat_1.jpg'
    tl_coords = (32.740347504504506, -117.1462345045045)
    br_coords = (32.7313384954955, -117.13722549549549)
    crop_out_segments(input_image, tl_coords, br_coords)
