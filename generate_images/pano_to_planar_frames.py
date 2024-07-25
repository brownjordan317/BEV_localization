import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates
from tqdm import tqdm
import os
import argparse
import time

def map_to_sphere(x, y, z, f, yaw_radian, pitch_radian):
    """
    Calculates the mapping of 3D coordinates (x, y, z) to spherical coordinates (theta, phi) on a sphere.
    
    Parameters:
    x (float): x-coordinate in 3D space.
    y (float): y-coordinate in 3D space.
    z (float): z-coordinate in 3D space.
    f (float): focal length of the camera.
    yaw_radian (float): yaw angle in radians.
    pitch_radian (float): pitch angle in radians.
    
    Returns:
    tuple: A tuple containing the flattened theta and phi values after the mapping.
    """
    theta = np.arccos(z / np.sqrt(x ** 2 + y ** 2 + z ** 2))
    phi = np.arctan2(y, x)

    theta_prime = np.arccos(np.sin(theta) * np.sin(phi) * np.sin(pitch_radian) +
                            np.cos(theta) * np.cos(pitch_radian))

    phi_prime = np.arctan2(np.sin(theta) * np.sin(phi) * np.cos(pitch_radian) -
                           np.cos(theta) * np.sin(pitch_radian),
                           np.sin(theta) * np.cos(phi))
    phi_prime += yaw_radian
    phi_prime = phi_prime % (2 * np.pi)

    return theta_prime.flatten(), phi_prime.flatten()

def interpolate_color(coords, img, method='bilinear'):
    """
    Interpolates the color of an image at given coordinates using the specified interpolation method.

    Parameters:
        coords (ndarray): The coordinates at which to interpolate the color. Shape: (N, 2).
        img (ndarray): The input image. Shape: (H, W, 3).
        method (str, optional): The interpolation method to use. Defaults to 'bilinear'.
            Must be one of 'nearest', 'bilinear', or 'bicubic'.

    Returns:
        ndarray: The interpolated color at the given coordinates. Shape: (N, 3).
    """
    order = {'nearest': 0, 'bilinear': 1, 'bicubic': 3}.get(method, 1)
    red = map_coordinates(img[:, :, 0], coords, order=order, mode='reflect')
    green = map_coordinates(img[:, :, 1], coords, order=order, mode='reflect')
    blue = map_coordinates(img[:, :, 2], coords, order=order, mode='reflect')
    return np.stack((red, green, blue), axis=-1)

def mask_bottom_quarter(image_path):
    """
    Masks the bottom quarter of an image with a black background.

    Parameters:
        image_path (str): The path to the image file to be processed.

    Returns:
        PIL.Image: The masked image with the bottom quarter replaced by a black background.
    """
    # Open the image using Pillow
    img = Image.open(image_path)

    # Get the dimensions of the image
    width, height = img.size

    # Calculate the height of the bottom quarter
    bottom_quarter_height = height // 9

    # Create a new image with black background
    masked_img = Image.new('RGB', (width, height), (0, 0, 0))

    # Paste the top 3/4 of the original image onto the black image
    masked_img.paste(img.crop((0, 0, width, height - bottom_quarter_height)), (0, 0))

    return masked_img

def panorama_to_plane(panorama_path, FOV, output_size, yaw, pitch):
    """
    Processes a panoramic image to a planar representation.

    Parameters:
        panorama_path (str): The path to the panoramic image file.
        FOV (int): The field of view of the panorama.
        output_size (tuple): The size of the output image (width, height).
        yaw (int): The yaw angle.
        pitch (int): The pitch angle.

    Returns:
        Image: The planar representation of the panoramic image.
    """
    masked_panorama = mask_bottom_quarter(panorama_path)
    panorama = masked_panorama
    pano_width, pano_height = panorama.size
    pano_array = np.array(panorama)
    yaw_radian = np.radians(yaw)
    pitch_radian = np.radians(pitch)

    W, H = output_size
    f = (0.5 * W) / np.tan(np.radians(FOV) / 2)

    u, v = np.meshgrid(np.arange(W), np.arange(H), indexing='xy')

    x = u - W / 2
    y = H / 2 - v
    z = f

    theta, phi = map_to_sphere(x, y, z, f, yaw_radian, pitch_radian)

    U = phi * pano_width / (2 * np.pi)
    V = theta * pano_height / np.pi

    U, V = U.flatten(), V.flatten()
    coords = np.vstack((V, U))

    colors = interpolate_color(coords, pano_array)
    output_image = Image.fromarray(colors.reshape((H, W, 3)).astype('uint8'), 'RGB')

    return output_image

def extract_frames(panorama_path, output_folder, intended_result_frames, FOV, output_size, pitch):
    """
    Extracts frames from a panoramic image and saves them to the specified output folder.

    Parameters:
        panorama_path (str): The path to the panoramic image file.
        output_folder (str): The path to the folder where extracted frames will be saved.
        intended_result_frames (int): The number of frames to extract.
        FOV (int): The field of view of the panorama.
        output_size (tuple): The size of the output image (width, height).
        pitch (int): The pitch of the panorama.

    Returns:
        None
    """

    start_time = time.time()
    # Create a folder to save frames
    os.makedirs(output_folder, exist_ok=True)

    degrees_to_rotate = 360
    step_size = 0.25

    total_frames = int(degrees_to_rotate / step_size)

    every_xth_frame = total_frames // intended_result_frames

    # Generate frames and save every 10th frame
    for index, deg in enumerate(tqdm(np.arange(0, degrees_to_rotate, step_size))):
        if index % every_xth_frame == 0:
            output_image = panorama_to_plane(panorama_path, FOV, output_size, deg, pitch)
            output_image.save(os.path.join(output_folder, f"frame_{index:04d}.png"))

    end_time = time.time()

    total_time = end_time - start_time
    print("Frames saved successfully.")
    print(f"Total time taken: {total_time:.2f} seconds")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract frames from a video file and save them to a folder.")
    parser.add_argument("--pano_path", type=str, help="Path to the input panorama file.", default='/home/undadmin/Documents/GitHub/BEV_localization/Google_Earth_vids/balboa_park/balboa_9/stitched_panorama.png')
    parser.add_argument("--output_folder", type=str, help="Path to the output folder where frames will be saved.", default='/home/undadmin/Documents/GitHub/BEV_localization/Google_Earth_vids/balboa_park/balboa_9/')
    parser.add_argument("--intended_result_frames", type=int, help="Number of frames to extract (max 1440).", default=1)
    parser.add_argument("--FOV", type=int, help="Field of view of the panorama.", default=130)
    parser.add_argument("--output_size", type=int, help="Size of the output image.", default=(608, 608))
    parser.add_argument("--pitch", type=int, help="Pitch of the panorama.", default=180)

    args = parser.parse_args()

    extract_frames(args.pano_path, args.output_folder, args.intended_result_frames, args.FOV, args.output_size, args.pitch)
