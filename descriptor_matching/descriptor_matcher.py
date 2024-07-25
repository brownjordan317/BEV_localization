import sqlite3
import numpy as np
import cv2
from tqdm import tqdm
import argparse

import cv2
import numpy as np

def extract_non_black_pixels(image_path):
    """
    Extracts non-black pixels from an image and returns their (x, y) coordinates.

    Args:
        image_path (str): The path to the input image.

    Returns:
        list: A list of (x, y) coordinates of non-black pixels in the image.
    """
    # Load the image
    image = cv2.imread(image_path)
    
    # Convert the image to RGB (cv2 loads images in BGR by default)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Create a mask where non-black pixels are False
    non_black_mask = np.all(image_rgb == [0, 0, 0], axis=-1)
    
    # Find non-zero (True) indices
    non_black_indices = np.argwhere(non_black_mask)
    
    # Convert indices to (x, y) coordinates
    non_black_pixels = [(idx[1], idx[0]) for idx in non_black_indices]
    
    return non_black_pixels

def extract_keypoints_and_descriptors(image_path, mask_path):
    """
    Extracts keypoints and descriptors from an image using the SIFT algorithm.

    Args:
        image_path (str): The path to the input image.
        mask_path (str, optional): The path to a mask image. If provided, keypoints inside the mask will be ignored.

    Returns:
        tuple: A tuple containing two lists. The first list contains the keypoints detected in the image, and the second list contains the corresponding descriptors.
    """
    # Load the single subregion image
    query = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    # query = cv2.GaussianBlur(query, (3, 3), 0)
    
    # Initialize SIFT detector
    sift = cv2.SIFT_create()
    
    # Detect keypoints and compute descriptors
    keypoints, descriptors = sift.detectAndCompute(query, None)

    if mask_path is not None:
        # Convert extract_non_black_pixels(mask_path) to a set for faster lookup
        non_black_pixels = set(extract_non_black_pixels(mask_path))

        # Use set comprehension for faster tuple creation
        keep_indices = [i for i, kp in enumerate(keypoints) if (kp.pt[0], kp.pt[1]) not in non_black_pixels]

    else:
        center_x = query.shape[1] / 2
        center_y = query.shape[0] / 2
        
        # Ignore keypoints within a 150 pixel radius of the center of the image
        keep_indices = []
        for i, kp in enumerate(keypoints):
            if np.linalg.norm(np.array([kp.pt[0], kp.pt[1]]) - np.array([center_x, center_y])) > 150:
                keep_indices.append(i)

    keypoints = np.array(keypoints)
    descriptors = np.array(descriptors)
    
    # Use numpy advanced indexing
    keypoints = keypoints[keep_indices]
    descriptors = descriptors[keep_indices]
    
    return keypoints, descriptors

def find_closest_matches(db_name, keypoints, descriptors, n_best_matches):
    """
    Connects to the database, queries descriptors, converts them to a NumPy array, uses FLANN for nearest neighbor search,
    finds the closest matches, sorts matches by distance, and selects the top 3 best matches.

    Args:
        db_name (str): The name of the database to connect to.
        keypoints (list): List of keypoints.
        descriptors (numpy.ndarray): Array of descriptors.

    Returns:
        list: List of the top x best matches, each containing a tuple with distance and coordinates.
    """
    # Connect to the database
    conn = sqlite3.connect(db_name)
    c = conn.cursor()


    closest_matches = []

    # Query descriptors from the database
    c.execute('SELECT descriptor, center_y, center_x, top_left_y, top_left_x, bottom_right_y, bottom_right_x FROM descriptors')
    rows = c.fetchall()
    
    # Convert the descriptors from the database to a NumPy array
    db_descriptors = []
    db_coords = []
    for row in tqdm(rows, desc="Reading Database Descriptors"):
        stored_descriptor = np.frombuffer(row[0], dtype=np.float32)
        stored_descriptor = stored_descriptor.reshape(-1, 128)  # Assuming SIFT descriptors are 128-dimensional
        db_descriptors.append(stored_descriptor)
        db_coords.append(row[1:])

    db_descriptors = np.vstack(db_descriptors)
    db_coords = np.array(db_coords)
    
    # Use FLANN for efficient nearest neighbor search
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)

    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(descriptors, db_descriptors, k=2)

    
    for match in tqdm(matches, desc="Finding Closest Matches"):
        distance = match[0].distance
        coords = db_coords[match[0].trainIdx]
        closest_matches.append((distance, coords))

    conn.close()

    # Sort matches by distance
    closest_matches.sort(key=lambda x: x[0])

    # Select the top x best matches
    best_matches = closest_matches[:n_best_matches]
    
    return best_matches

def draw_matches(image_path, matches, output_path):
    """
    Draws matches on an image and optionally saves the image with the drawn rectangles.

    Args:
        image_path (str): The path to the image on which to draw the matches.
        matches (List[Tuple[float, Tuple[int, int, int, int, int, int]]]): A list of matches, where each match is a tuple containing the distance and the coordinates of the rectangle to be drawn.
        output_path (str, optional): The path to save the image with the drawn rectangles. If not provided, the image will not be saved.

    Returns:
        None
    """
    # Load the image on which to draw the shapes
    image = cv2.imread(image_path)
    
    # Iterate through the matches and draw rectangles
    for i, match in enumerate(matches):
        distance, coords = match
        center_y, center_x, top_left_y, top_left_x, bottom_right_y, bottom_right_x = coords
        
        # Draw a rectangle on the image
        top_left = (top_left_x, top_left_y)
        bottom_right = (bottom_right_x, bottom_right_y)
        try:
            intensity = 255 - i * 255 / (len(matches) - 1)
        except ZeroDivisionError:
            intensity = 255
        color = (255, intensity, intensity)
        thickness = 5
        
        cv2.rectangle(image, top_left, bottom_right, color, thickness)
        
        # # Add label with the match index
        # label = f"{i+1}"
        # label_position = (center_x, center_y)  # Position label 
        # cv2.putText(image, label, label_position, cv2.FONT_ITALIC, 0.25, color, 2)
    
    # # Show the image with drawn rectangles and labels
    # cv2.imshow('Matches', image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # Optionally save the image with drawn rectangles and labels
    cv2.imwrite(output_path, image)

# Function to extract the subregion
def extract_subregion(image_path, coords):
    """
    Extracts a subregion from an image using the given coordinates.

    Args:
        image_path (str): The path to the image file.
        coords (tuple): A tuple containing the center coordinates (center_y, center_x) and the top-left 
            and bottom-right coordinates (top_left_y, top_left_x, bottom_right_y, bottom_right_x) of the subregion.

    Returns:
        numpy.ndarray: The extracted subregion from the image.

    """
    # Load the image
    image = cv2.imread(image_path)

    center_y, center_x, top_left_y, top_left_x, bottom_right_y, bottom_right_x = coords

    # Define the coordinates
    # (Ensure the coordinates are within the image dimensions)
    center_y = max(0, min(center_y, image.shape[0] - 1))
    center_x = max(0, min(center_x, image.shape[1] - 1))
    top_left_y = max(0, min(top_left_y, image.shape[0] - 1))
    top_left_x = max(0, min(top_left_x, image.shape[1] - 1))
    bottom_right_y = max(0, min(bottom_right_y, image.shape[0] - 1))
    bottom_right_x = max(0, min(bottom_right_x, image.shape[1] - 1))

    # Extract the subregion
    subregion = image[top_left_y:bottom_right_y, top_left_x:bottom_right_x]

    return subregion

def display_sift_matches(query_path, query_keypoints, query_descriptors, img2, count):
    """
    Display SIFT matches between two images.

    Args:
        query_path (str): The path to the query image.
        query_keypoints (list): The keypoints detected in the query image.
        query_descriptors (numpy.ndarray): The descriptors extracted from the query image.
        img2 (numpy.ndarray): The second image for matching.
        count (int): The count of the image.

    Returns:
        None
    """
    # Initiate SIFT detector
    sift = cv2.SIFT_create()

    img1 = cv2.imread(query_path, cv2.IMREAD_GRAYSCALE)
    img1_color = cv2.imread(query_path)

    kp2, des2 = sift.detectAndCompute(img2, None)

    # FLANN parameters
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)

    # Create FLANN matcher
    flann = cv2.FlannBasedMatcher(index_params, search_params)

    # Match descriptors
    matches = flann.knnMatch(query_descriptors, des2, k=2)

    # Apply ratio test
    good_matches = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good_matches.append(m)

    # Compute scale factors
    scale_x = img1.shape[1] / img2.shape[1]
    scale_y = img1.shape[0] / img2.shape[0]

    # Resize subregion
    resized_subregion = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

    # Adjust keypoints
    adjusted_keypoints2 = []
    for kp in kp2:
        x, y = kp.pt
        adjusted_keypoints2.append(cv2.KeyPoint(x * scale_x, y * scale_y, kp.size * scale_x))

    # Draw matches
    img_matches = cv2.drawMatches(img1_color, query_keypoints, resized_subregion, adjusted_keypoints2, good_matches, None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

    # Save the matches
    cv2.imwrite(f"output/sift_matches_{count}.png", img_matches)

def main(query_file_path, mask_file_path, db_name, train_file_path, output_path, n_best_matches):
    keypoints, descriptors = extract_keypoints_and_descriptors(query_file_path, mask_file_path)
    best_matches = find_closest_matches(db_name, keypoints, descriptors,n_best_matches)
    draw_matches(train_file_path, best_matches, output_path)

    for i, match in enumerate(best_matches):
        subregion = extract_subregion(train_file_path, match[1])
        display_sift_matches(query_file_path, keypoints, descriptors, subregion, i)
        print(match)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--query_file_path', type=str, default='/home/undadmin/Documents/GitHub/BEV_localization/Google_Earth_vids/ppl_v2/all_bevs/frame_0952.png', help='Path to the query image file.')
    parser.add_argument('--mask_file_path', type=str, default='/home/undadmin/Documents/GitHub/BEV_localization/Google_Earth_vids/ppl_v2/mask.png', help='Path to the mask image file.')
    parser.add_argument('--db_name', type=str, default='/home/undadmin/Documents/GitHub/BEV_localization/descriptor_data_bases/ppl_v2_4.db', help='Name of the database file.')
    parser.add_argument('--train_file_path', type=str, default='/home/undadmin/Documents/GitHub/BEV_localization/Google_Earth_vids/ppl_v2/sat4.png', help='Path to the training image file.')
    parser.add_argument('--output_path', type=str, default='output/output_image.png', help='Path to save the output image.')
    parser.add_argument('--n_best_matches', type=int, default=10, help='Number of best matches to return.')

    args = parser.parse_args()

    main(args.query_file_path, args.mask_file_path, args.db_name, args.train_file_path, args.output_path, args.n_best_matches)


