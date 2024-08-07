from concurrent.futures import ThreadPoolExecutor, as_completed
import tqdm
import json
import os
import numpy as np
import logging
import fourier_transform_match
from utils.plot_jsons import plot_jsons
from time import time
from distort_image import apply_random_distortion
import cv2
import shutil

max_runs = 1000
distortion_levels = [3, 5, 7]
scales = list(range(2, 11, 1))
images_folder = '/home/undadmin/Documents/GitHub/map_maker/cropped_screenshots/color_maps/'

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Get a list of all images in the folder
all_images = [f for f in os.listdir(images_folder) if os.path.isfile(os.path.join(images_folder, f))]
results = {}
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
os.makedirs(output_dir, exist_ok=True)


def run_match(blur_level, run_idx, source_path, template_path, scale):
    correct_location_found, correct_location_idx = fourier_transform_match.fourier_transform_match(
        source_path,
        template_path,
        3,
        0,
        scale,
        False,
        blur_level
    )
    return (correct_location_found, correct_location_idx)

with tqdm.tqdm(distortion_levels, desc='Running each distortion level', unit='distortion levels') as sbar:
    for level in sbar:
        scale_start_time = time()
        os.makedirs(os.path.join(output_dir, 'temp'), exist_ok=True)
        random_image = all_images[np.random.randint(0, len(all_images))]
        selected_image_path = os.path.join(images_folder, random_image)
        distortion_1 = apply_random_distortion(selected_image_path, level)
        distortion_1_output_path = f'{output_dir}/temp/1_{random_image}'
        cv2.imwrite(distortion_1_output_path, distortion_1)
        distortion_2 = apply_random_distortion(selected_image_path, level)
        distortion_2_output_path = f'{output_dir}/temp/2_{random_image}'
        cv2.imwrite(distortion_2_output_path, distortion_2)

        for scale in tqdm.tqdm(scales, desc='Running each scale level', unit='scale levels', leave=False):
            blur_start_time = time()
            found_correct_location = 0
            found_correct_at_1 = 0
            found_correct_at_2 = 0
            found_correct_at_3 = 0

            with ThreadPoolExecutor() as executor:
               
                futures = [executor.submit(run_match, 0, i, distortion_1_output_path, distortion_2_output_path, scale) for i in range(max_runs)]
                for future in as_completed(futures):
                    try:
                        correct_location_found, correct_location_idx = future.result()
                        if correct_location_found:
                            if correct_location_idx == 1:
                                found_correct_at_1 += 1
                            elif correct_location_idx == 2:
                                found_correct_at_2 += 1
                            elif correct_location_idx == 3:
                                found_correct_at_3 += 1
                            found_correct_location += 1
                    except Exception as e:
                        logger.error(f"Error during execution: {e}")

            results[scale] = (found_correct_location, found_correct_at_1, found_correct_at_2, found_correct_at_3)
            logger.info(f"Completed distortion level {scale} in {time() - blur_start_time:.2f} seconds")

        # Ensure output directory exists
        os.makedirs(f'{output_dir}/jsons', exist_ok=True)
        os.makedirs(f'{output_dir}/txts', exist_ok=True)
        
        # Save results as JSON
        output_file = os.path.join(output_dir, f'jsons/{level}_results.json')
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f)
        except Exception as e:
            logger.error(f"Error saving JSON results: {e}")

        # Save results as TXT
        output_file = os.path.join(output_dir, f'txts/{level}_results.txt')
        try:
            with open(output_file, 'w') as f:
                for key, result in results.items():
                    f.write(f"Results for blur level {key}:\n")
                    f.write(f"Found correct location: {result[0]}/{max_runs} or {result[0]/max_runs*100:.2f}%\n")
                    if result[0] > 0:
                        f.write(f"Found correct location at index 1: {result[1]}/{result[0]} or {result[1]/result[0]*100:.2f}%\n")
                        f.write(f"Found correct location at index 2: {result[2]}/{result[0]} or {result[2]/result[0]*100:.2f}%\n")
                        f.write(f"Found correct location at index 3: {result[3]}/{result[0]} or {result[3]/result[0]*100:.2f}%\n")
                    f.write('\n')
        except Exception as e:
            logger.error(f"Error saving TXT results: {e}")

        # Remove temp directory
        if os.path.exists(os.path.join(output_dir, 'temp')):
            shutil.rmtree(os.path.join(output_dir, 'temp'))

plot_jsons()


