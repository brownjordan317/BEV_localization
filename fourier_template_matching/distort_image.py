import cv2
import numpy as np
from scipy.ndimage import gaussian_filter, map_coordinates
import os

def elastic_transform(image, alpha, sigma):
    random_state = np.random.RandomState(None)
    shape = image.shape[:2]
    
    dx = gaussian_filter((random_state.rand(*shape) * 2 - 1), sigma, mode="constant", cval=0) * alpha
    dy = gaussian_filter((random_state.rand(*shape) * 2 - 1), sigma, mode="constant", cval=0) * alpha
    
    x, y = np.arange(shape[1]), np.arange(shape[0])
    x, y = np.meshgrid(x, y)
    
    indices = np.reshape(np.stack([y + dy, x + dx], axis=-1), (-1, 2)).T
    distorted_image = np.zeros_like(image)
    
    for i in range(image.shape[2]):
        channel = image[:, :, i]
        dist_channel = map_coordinates(channel, indices, order=1, mode='reflect')
        distorted_image[:, :, i] = dist_channel.reshape(shape[0], shape[1])
    
    return distorted_image

def wavy_distortion(image, freq, amp):
    rows, cols, _ = image.shape
    x = np.arange(cols)
    y = np.arange(rows)
    x, y = np.meshgrid(x, y)
    wave_x = amp * np.sin(2 * np.pi * freq * y / rows)
    wave_y = amp * np.sin(2 * np.pi * freq * x / cols)
    map_x = (x + wave_x).astype(np.float32)
    map_y = (y + wave_y).astype(np.float32)
    return cv2.remap(image, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def apply_distortion_to_region(image, x_start, x_end, y_start, y_end, level):
    region = image[y_start:y_end, x_start:x_end]
    
    if level > 0:
        distortion_type = np.random.choice(['elastic', 'wavy'])
        if distortion_type == 'elastic':
            alpha = level * 10
            sigma = level * 2
            region = elastic_transform(region, alpha, sigma)
        elif distortion_type == 'wavy':
            freq = level
            amp = level * 0.5
            region = wavy_distortion(region, freq, amp)
    
    image[y_start:y_end, x_start:x_end] = region
    return image

def apply_random_distortion(image, level, num_regions = 30):
    image = cv2.imread(image)
    rows, cols, _ = image.shape
    
    for _ in range(num_regions):
        x_start = np.random.randint(0, cols // 2)
        x_end = np.random.randint(x_start + 10, cols)
        y_start = np.random.randint(0, rows // 2)
        y_end = np.random.randint(y_start + 10, rows)
        
        image = apply_distortion_to_region(image, x_start, x_end, y_start, y_end, level)
    
    return image

if __name__ == '__main__':

    # Read the image
    image = '/home/undadmin/Documents/GitHub/BEV_localization/fourier_template_matching/source_sat.png'

    # Input the level of distortion
    level = 5

    # Apply random distortion
    distorted_image = apply_random_distortion(image, level)

    # Save or display the result
    file_path = os.path.abspath(__file__)
    output_dir = os.path.dirname(file_path)
    cv2.imwrite(os.path.join(output_dir, 'distorted_image_2.png'), distorted_image)
