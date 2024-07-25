import os
import cv2
import argparse
from tqdm import tqdm

RESIZE_FACTOR = 0.4
VALID_IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")

def get_image_paths(input_folder):
    """
    Retrieves a list of image paths from the specified input folder.

    Parameters:
        input_folder (str): The path to the input folder.

    Returns:
        list: A list of image paths sorted in alphabetical order.
    """
    all_files = os.listdir(input_folder)
    image_files = [os.path.join(input_folder, f) for f in all_files if f.lower().endswith(VALID_IMAGE_EXTENSIONS)]
    image_files.sort()
    every_xth_image = image_files[::1]
    return every_xth_image

def load_and_resize_images(image_paths):
    """
    Loads images from the specified paths, resizes them, and returns a list of resized images.

    Parameters:
        image_paths (list): A list of file paths to the images to be loaded and resized.

    Returns:
        list: A list of resized images.
    """
    imgs = []
    print("Loading and resizing images:")

    for path in tqdm(image_paths):
        img = cv2.imread(path)
        if img is None:
            print(f"Corrupted or unsupported image format: {path}")
            continue
        img = cv2.resize(img, (0, 0), fx=RESIZE_FACTOR, fy=RESIZE_FACTOR)
        imgs.append(img)
    return imgs

def stitch_images(imgs, stitcher_type):
    """
    Stitches multiple images together using the specified stitcher type.

    Parameters:
        imgs (List[numpy.ndarray]): A list of images to be stitched.
        stitcher_type (str): The type of stitcher to use. Valid options are "SCANS" and "PANORAMA".

    Returns:
        Tuple[int, Optional[numpy.ndarray]]: A tuple containing the status of the stitching procedure and the stitched image.
            - If the stitching procedure is successful, the status is cv2.Stitcher_OK and the stitched image is returned.
            - If the stitcher type is invalid, the status is None and the stitched image is None.
            - If the stitching procedure fails, the status is one of cv2.Stitcher_ERR_NEED_MORE_IMGS, cv2.Stitcher_ERR_HOMOGRAPHY_EST_FAIL, or cv2.Stitcher_ERR_CAMERA_PARAMS_ADJUST_FAIL, and the stitched image is None.

    """
    # Create a Stitcher object
    if stitcher_type == "SCANS":
        stitcher = cv2.Stitcher.create(cv2.Stitcher_SCANS)
    elif stitcher_type == "PANORAMA":
        stitcher = cv2.Stitcher.create(cv2.Stitcher_PANORAMA)
    else:
        print(f"Invalid stitcher type: {stitcher_type}")
        return None
    
    print("Stitching images:")
    # Perform the stitching process
    (status, stitched_image) = stitcher.stitch(imgs) 
    
    # Check if the stitching procedure is successful
    if status != cv2.Stitcher_OK:
        # Error messages for different statuses
        error_messages = {
            cv2.Stitcher_ERR_NEED_MORE_IMGS: "Need more images to stitch",
            cv2.Stitcher_ERR_HOMOGRAPHY_EST_FAIL: "Homography estimation failed",
            cv2.Stitcher_ERR_CAMERA_PARAMS_ADJUST_FAIL: "Camera parameters adjustment failed"
        }
        print(f"Stitching failed with status {status}: {error_messages.get(status, 'Unknown error')}")
        return status, None
    else:  
        print('Your Panorama is ready!!!') 
        return status, stitched_image
    
def main(input_folder, output_path, stitcher_type):
    """
    Main function that stitches multiple images together using the specified stitcher type.

    Parameters:
        input_folder (str): The path to the folder containing the input images.
        output_path (str): The path to save the stitched image.
        stitcher_type (str): The type of stitching algorithm to use.

    Returns:
        None

    This function retrieves the image paths from the input folder, loads and resizes the images, checks for inconsistent image sizes, and stitches the images using the specified stitcher type. If any errors occur during the process, appropriate error messages are printed. Finally, the stitched image is saved to the specified output path and a success message is printed.

    """
    image_paths = get_image_paths(input_folder)
    if not image_paths:
        print("No images found in the input folder.")
        return

    imgs = load_and_resize_images(image_paths)
    if not imgs:
        print("No valid images found or failed to load any images.")
        return

    first_img_shape = imgs[0].shape
    for img in imgs:
        if img.shape != first_img_shape:
            print(f"Inconsistent image size detected: {img.shape}. Expected: {first_img_shape}")
            return

    status, stitched_image = stitch_images(imgs, stitcher_type)
    if status != cv2.Stitcher_OK:
        print("Error during stitching.")
        return

    cv2.imwrite(output_path, stitched_image)
    print("Your image is ready!")

if __name__ == "__main__":
    # Create ArgumentParser object
    parser = argparse.ArgumentParser(description="Stitch images into a panorama.")
    
    # Add arguments to the parser
    # parser.add_argument("-i", "--input_folder", type=str, default="/home/undadmin/Documents/GitHub/BEV_localization/Google_Earth_vids/ppl_v2_6/ppl_video6_frames/", help="Path to folder containing input images.")
    # parser.add_argument("-o", "--output_path", type=str, default="/home/undadmin/Documents/GitHub/BEV_localization/Google_Earth_vids/ppl_v2_6/stitched_panorama.png", help="Path to save the stitched panorama.")
    # parser.add_argument("-s", "--stitch_type", type=str, default="PANORAMA", help="Type of stitching algorithm to use.")

    parser.add_argument("-i", "--input_folder", type=str, default="/home/undadmin/Documents/GitHub/BEV_localization/Google_Earth_vids/ppl_v2/all_bevs/", help="Path to folder containing input images.")
    parser.add_argument("-o", "--output_path", type=str, default="/home/undadmin/Documents/GitHub/BEV_localization/Google_Earth_vids/ppl_all_bevs/best_bev.png", help="Path to save the stitched panorama.")
    parser.add_argument("-s", "--stitch_type", type=str, default="PANORAMA", help="Type of stitching algorithm to use.", options=["SCANS", "PANORAMA"])

    # Parse the command-line arguments
    args = parser.parse_args()
    
    # Call the main function with parsed arguments
    main(args.input_folder, args.output_path, args.stitch_type)