import cv2
import numpy as np
import sqlite3
from tqdm import tqdm
import os
import argparse
from multiprocessing import Pool, cpu_count

def load_image(image_path):
    """
    Load an image from the given path and convert it to grayscale.

    Parameters:
        image_path (str): The path to the image file.

    Returns:
        numpy.ndarray: The loaded grayscale image.
    """
    return cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

def sample_locations(img, subregion_size, step):
    """
    Generates a list of subregion coordinates for a given image.

    Args:
        img (numpy.ndarray): The input image.
        subregion_size (int): The size of each subregion.
        step (int, optional): The step size for iterating over the image. Defaults to 2.

    Returns:
        list: A list of tuples containing the center coordinates (center_y, center_x), top-left coordinates 
              (top_left_y, top_left_x), and bottom-right coordinates (bottom_right_y, bottom_right_x) for each 
              subregion.
    """
    height, width = img.shape[:2]
    subregion_coordinates = []
    half_subregion = subregion_size // 2

    for i in range(0, height - subregion_size + 1, step):
        for j in range(0, width - subregion_size + 1, step):
            top_left_y, top_left_x = i, j
            bottom_right_y, bottom_right_x = i + subregion_size - 1, j + subregion_size - 1
            center_y, center_x = i + half_subregion, j + half_subregion
            subregion_coordinates.append((center_y, center_x, top_left_y, top_left_x, bottom_right_y, bottom_right_x))
    
    return subregion_coordinates

def process_subregion(args):
    """
    Process a single subregion to extract SIFT descriptors.
    
    Args:
        args (tuple): A tuple containing the image and coordinates of the subregion.
    
    Returns:
        list: A list of tuples containing the descriptors and their corresponding subregion coordinates.
    """
    image, coords = args
    center_y, center_x, top_left_y, top_left_x, bottom_right_y, bottom_right_x = coords
    subregion = image[top_left_y:bottom_right_y + 1, top_left_x:bottom_right_x + 1]
    
    sift = cv2.SIFT_create()
    keypoints, descriptors = sift.detectAndCompute(subregion, None)
    
    result = []
    if descriptors is not None:
        for descriptor in descriptors:
            result.append((descriptor, coords))
    
    return result

def extract_descriptors(image, subregion_coords, subregion_size):
    """
    Extracts descriptors from an image using the SIFT algorithm with multiprocessing.

    Args:
        image (numpy.ndarray): The input image.
        subregion_coords (list): A list of tuples containing the center coordinates (center_y, center_x), 
                                 top-left coordinates (top_left_y, top_left_x), and bottom-right coordinates 
                                 (bottom_right_y, bottom_right_x) for each subregion.
        subregion_size (int): The size of each subregion.

    Returns:
        list: A list of tuples containing the descriptors and their corresponding subregion coordinates.
              Each tuple consists of a descriptor (numpy.ndarray) and a coordinate tuple (center_y, center_x, 
              top_left_y, top_left_x, bottom_right_y, bottom_right_x).
    """
    descriptors_list = []
    
    # Prepare arguments for multiprocessing
    args = [(image, coords) for coords in subregion_coords]
    
    # Use multiprocessing to process subregions in parallel
    with Pool(cpu_count()) as pool:
        for result in tqdm(pool.imap_unordered(process_subregion, args), total=len(subregion_coords), desc="Extracting Descriptors"):
            descriptors_list.extend(result)
    
    return descriptors_list

def create_database(db_name):
    """
    Creates a SQLite database with a table named `descriptors` to store descriptors.

    Args:
        db_name (str): The name of the database file.

    Returns:
        tuple: A tuple containing the database connection and cursor.
    """
    # Remove existing database file if it exists
    if os.path.exists(db_name):
        os.remove(db_name)
    
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS descriptors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descriptor BLOB,
            center_y INTEGER,
            center_x INTEGER,
            top_left_y INTEGER,
            top_left_x INTEGER,
            bottom_right_y INTEGER,
            bottom_right_x INTEGER
        )
    ''')
    conn.commit()
    return conn, c

def insert_descriptors(conn, c, descriptors_list):
    """
    Inserts descriptors into the `descriptors` table of the database.

    Args:
        conn: Connection to the SQLite database.
        c: Cursor for the database connection.
        descriptors_list: List of tuples containing descriptors and their coordinates.

    Returns:
        None
    """
    for descriptor, coords in tqdm(descriptors_list, desc="Inserting Descriptors"):
        center_y, center_x, top_left_y, top_left_x, bottom_right_y, bottom_right_x = coords
        c.execute('''
            INSERT INTO descriptors (descriptor, center_y, center_x, top_left_y, top_left_x, bottom_right_y, bottom_right_x)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', [descriptor.tobytes(), center_y, center_x, top_left_y, top_left_x, bottom_right_y, bottom_right_x])
    conn.commit()

def main(image_path, subregion_size, step, db_name):
    image = load_image(image_path)
    subregion_coords = sample_locations(image, subregion_size, step)
    descriptors_list = extract_descriptors(image, subregion_coords, subregion_size)
    conn, c = create_database(db_name)
    insert_descriptors(conn, c, descriptors_list)
    conn.close()
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a descriptor database.')
    parser.add_argument('--image_path', type=str, default='/home/undadmin/Documents/GitHub/BEV_localization/Google_Earth_vids/ppl_v2/sat4.png', help='Path to the image file.')
    parser.add_argument('--subregion_size', type=int, default=120, help='Size of subregions.')
    parser.add_argument('--step', type=int, default=20, help='Step size for sampling.')
    parser.add_argument('--db_name', type=str, default='descriptor_data_bases/ppl_v2_4.db', help='Name of the database file.')

    args = parser.parse_args()

    main(args.image_path, args.subregion_size, args.step, args.db_name)
