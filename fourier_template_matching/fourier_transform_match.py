import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import maximum_filter
import argparse
import os



def random_crop(image, crop_height, crop_width):
    """
    Randomly crops an image.

    Parameters:
    image (numpy.ndarray): The image to be cropped.
    crop_height (int): The height of the cropped region.
    crop_width (int): The width of the cropped region.

    Returns:
    numpy.ndarray: The randomly cropped image.
    """
    height, width = image.shape[:2]

    # Calculate the top, left, bottom, and right coordinates for the crop
    top = np.random.randint(0, height - crop_height)
    left = np.random.randint(0, width - crop_width)
    bottom = top + crop_height
    right = left + crop_width

    centroid_x = (left + right) / 2
    centroid_y = (top + bottom) / 2

    # # Draw a rectangle on the image to visualize the crop region
    # plt.figure()
    # plt.imshow(image)
    # plt.axis('off')
    # plt.gca().add_patch(plt.Rectangle((left, top), crop_width, crop_height, fill=False, color='green', linewidth=2))
    # plt.show()

    return image[top:bottom, left:right], (centroid_x, centroid_y)

def zero_mean_normalize(image):
    """
    Normalize an image by subtracting the mean and dividing by the standard deviation.

    Parameters:
    image (numpy.ndarray): The image to be normalized.

    Returns:
    numpy.ndarray: The normalized image.
    """

    mean = np.mean(image)
    std = np.std(image)
    return (image - mean) / std



def rotate_and_crop_template(template_img, rotation_angle, scale_factor):
    """
    Rotates and crops a template image.

    Parameters:
    template_img (numpy.ndarray): The template image to be rotated and cropped.
    rotation_angle (float): The angle of rotation in degrees.
    scale_factor (float): The scale factor for the crop size.

    Returns:
    numpy.ndarray: The rotated and cropped template image.
    """
    edit_h, edit_w = template_img.shape[:2]
    rotation_matrix = cv2.getRotationMatrix2D((edit_w / 2, edit_h / 2), rotation_angle, 1)
    rotated_img = cv2.warpAffine(template_img, rotation_matrix, (edit_w, edit_h))

    crop_height = int(edit_h / scale_factor)
    crop_width = int(edit_w / scale_factor)

    # Randomly crop the rotated image
    def is_single_color(image):
        # Check if all pixels in the image are the same color
        return np.all(image == image[0, 0])

    def safe_random_crop(image, crop_height, crop_width):
        while True:
            cropped_img, centroid = random_crop(image, crop_height, crop_width)
            if not is_single_color(cropped_img):
                return cropped_img, centroid

    # Usage
    cropped_img, centroid = safe_random_crop(rotated_img, crop_height, crop_width)

    return cropped_img, centroid

def compute_correlation(source_img, template_img):
    """
    Computes the correlation between the source image and the template image.

    Parameters:
    source_img (numpy.ndarray): The source image.
    template_img (numpy.ndarray): The template image.

    Returns:
    numpy.ndarray: The correlation between the source image and the template image.
    """
    # Compute the 2D Fourier transform of the source image
    dft_source = np.fft.fft2(source_img)

    # Compute the 2D Fourier transform of the template image, with the same shape as the source image
    dft_template = np.fft.fft2(template_img, s=source_img.shape)

    # Compute the complex conjugate of the Fourier transform of the template image
    dft_template_conj = np.conj(dft_template)

    # Compute the inverse 2D Fourier transform of the product of the Fourier transforms of the source image 
    # and the complex conjugate of the Fourier transform of the template image
    corr = np.fft.ifft2(dft_source * dft_template_conj)

    return np.abs(corr)

def detect_peaks(corr, min_dist, num_peaks):
    """
    Detects the peaks in the correlation matrix.

    Parameters:
    corr (numpy.ndarray): The correlation matrix.
    min_dist (int): The minimum distance between peaks.
    num_peaks (int): The maximum number of peaks to detect.

    Returns:
    tuple: A tuple containing the detected peaks and their strengths.
    """
    # Define the neighborhood size for maximum filter
    neighborhood_size = min_dist * 2 + 1

    # Apply maximum filter to find local maxima
    local_max = maximum_filter(corr, size=neighborhood_size)

    # Get the indices of local maxima
    peak_locations = np.where(corr == local_max)


    peak_strengths = corr[peak_locations]
    sorted_indices = np.argsort(peak_strengths.flatten())[::-1]
    top_locs = list(zip(peak_locations[0][sorted_indices], peak_locations[1][sorted_indices]))

    # Filter the top locations based on the minimum distance requirement
    filtered_locs = []
    for loc in top_locs:
        if len(filtered_locs) == num_peaks:
            break
        if all(np.linalg.norm(np.array(loc) - np.array(accepted_loc)) >= min_dist for accepted_loc in filtered_locs):
            filtered_locs.append(loc)

    return filtered_locs[:num_peaks], peak_strengths[sorted_indices[:num_peaks]]

def plot_correlation_matrix(corr, peak_locations, peak_confidences, output_path, save_output):
    """
    Plots the correlation matrix with labeled peaks.

    Parameters:
    corr (numpy.ndarray): The correlation matrix.
    peak_locations (list): The locations of the peaks in the correlation matrix.
    peak_confidences (list): The confidences of the peaks.
    output_path (str): The path to save the plot.
    """
    # Normalize the correlation matrix to 0-255
    normalized_corr = cv2.normalize(corr, None, 0, 255, cv2.NORM_MINMAX)
    normalized_corr = np.uint8(normalized_corr)

    # Apply a colormap
    colored_corr = cv2.applyColorMap(normalized_corr, cv2.COLORMAP_JET)

    # Draw text annotations for peak locations
    for i, (row, col) in enumerate(peak_locations):
        text = f'{i + 1} ({peak_confidences[i]:.2f})'
        cv2.putText(colored_corr, text, (col, row), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

    # Save the image
    if save_output is True:
        cv2.imwrite(output_path, colored_corr)

def plot_fourier_transform(template_img, output_path, save_output):
    """
    This function computes the 2D Fourier transform of the template image and plots the magnitude spectrum.

    Args:
        template_img (numpy.ndarray): The input template image.
        output_path (str): The path to save the plot.
    """
    # Compute the 2D Fourier transform of the template image
    dft_template = np.fft.fft2(template_img)
    
    # Shift the zero frequency component to the center of the spectrum
    dft_shift = np.fft.fftshift(dft_template)
    
    # Compute the magnitude spectrum of the Fourier transform
    magnitude_spectrum = 20 * np.log(np.abs(dft_shift))


    # Assuming magnitude_spectrum is a numpy array
    height, width = magnitude_spectrum.shape

    # Create a blank image with the same dimensions
    blank_image = np.zeros((height, width), dtype=np.uint8)

    # Normalize magnitude spectrum to 0-255
    normalized_spectrum = cv2.normalize(magnitude_spectrum, None, 0, 255, cv2.NORM_MINMAX)
    normalized_spectrum = np.uint8(normalized_spectrum)

    # Put the normalized spectrum on the blank image
    colored_spectrum = cv2.applyColorMap(normalized_spectrum, cv2.COLORMAP_JET)

    # Save the image
    if save_output is True:
        cv2.imwrite(output_path, colored_spectrum)

def draw_detections_on_image(source_img_color, peak_locations, peak_confidences, template_shape, output_path, cropped_centroid, save_output):
    global DISTANCES
    """
    Draws the detected locations on the source image and saves the result.

    Args:
        source_img_color (numpy.ndarray): The colored source image.
        peak_locations (List[Tuple[int, int]]): The locations of the detected peaks.
        peak_confidences (List[float]): The confidences of the detected peaks.
        template_shape (Tuple[int, int]): The shape of the template.
        output_path (str): The path to save the result image.
    """
    h, w = template_shape

    source_img_rect = source_img_color.copy()

    correct_location_found = False

    
    # Draw black circle with cross centered at cropped centroid
    center = (int(cropped_centroid[0]), int(cropped_centroid[1]))
    radius = 10
    thickness = 4  
    # Draw the outer circle
    cv2.circle(source_img_rect, center, radius, (0, 0, 0), thickness)
    # Draw the inner circle
    cv2.circle(source_img_rect, center, radius-2, (255, 255, 255), thickness)
    # Draw the horizontal line
    cv2.line(source_img_rect, (center[0]-5, center[1]), (center[0]+5, center[1]), (0, 0, 0), thickness)
    # Draw the vertical line
    cv2.line(source_img_rect, (center[0], center[1]-5), (center[0], center[1]+5), (0, 0, 0), thickness)
    

    for i, (row, col) in enumerate(peak_locations):
        top_left = (col, row)
        bottom_right = (col + w, row + h)

        # Compute centroid
        centroid_x = (top_left[0] + bottom_right[0]) / 2
        centroid_y = (top_left[1] + bottom_right[1]) / 2

        centroid = (centroid_x, centroid_y)

        distance = np.sqrt((centroid[0] - cropped_centroid[0])**2 + (centroid[1] - cropped_centroid[1])**2)


        if distance < 25 and not correct_location_found:
            correct_location_idx = i + 1
            correct_location_found = True

        if save_output:
            DISTANCES.append(distance)
            # Draw a white outline around the rectangle
            cv2.rectangle(source_img_rect, (top_left[0] - 2, top_left[1] - 2), (bottom_right[0] + 2, bottom_right[1] + 2), (255, 255, 255), 2)
            cv2.rectangle(source_img_rect, top_left, bottom_right, (0, 0, 255), 2)
            cv2.rectangle(source_img_rect, (top_left[0] + 2, top_left[1] + 2), (bottom_right[0] - 2, bottom_right[1] - 2), (255, 255, 255), 2)

            # Calculate the text size and position
            text = f'{peak_confidences[i]:.2f}'
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            thickness = 1
            text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
            text_w, text_h = text_size
            text_x = col - text_w // 2
            text_y = row - 10

            # Draw a white outline around the text
            cv2.putText(source_img_rect, text, (text_x - 1, text_y - 1), font, font_scale, (255, 255, 255), thickness + 1, cv2.LINE_AA)
            cv2.putText(source_img_rect, text, (text_x + 1, text_y - 1), font, font_scale, (255, 255, 255), thickness + 1, cv2.LINE_AA)
            cv2.putText(source_img_rect, text, (text_x - 1, text_y + 1), font, font_scale, (255, 255, 255), thickness + 1, cv2.LINE_AA)
            cv2.putText(source_img_rect, text, (text_x + 1, text_y + 1), font, font_scale, (255, 255, 255), thickness + 1, cv2.LINE_AA)

            # Draw the main red text
            cv2.putText(source_img_rect, text, (text_x, text_y), font, font_scale, (0, 0, 255), thickness, cv2.LINE_AA)

            cv2.imwrite(output_path, source_img_rect)

    if correct_location_found:
        return correct_location_found, correct_location_idx

    return correct_location_found, None

def fourier_transform_match(source_img_path, template_img_path, num_peaks, rotation_angle, scale_factor, save_output, blur_levl = 0):
    """
    Perform Fourier transform-based template matching on the source and template images.

    Args:
        source_img_path (str): Path to the source image file.
        template_img_path (str): Path to the template image file.
        num_peaks (int): Number of peaks to detect.
        rotation_angle (int): The degree of rotation to apply to the template image.
        scale_factor (int): The pixel scale difference between the source and template images.
    """
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(parent_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)

    # Read the source and template images
    source_img_color = cv2.imread(source_img_path)
    source_img = cv2.cvtColor(source_img_color, cv2.COLOR_BGR2GRAY).astype(np.float32)
    template_img = cv2.imread(template_img_path, 0).astype(np.float32)

    # Rotate and crop the template image
    template_img, cropped_centroid = rotate_and_crop_template(template_img, rotation_angle, scale_factor)
    if blur_levl > 0:
        template_img = cv2.GaussianBlur(template_img, (blur_levl, blur_levl), 0)
    if save_output is True:
        cv2.imwrite(os.path.join(output_dir, 'rotated_template.png'), template_img)

    # Get the height and width of the template image
    h, w = template_img.shape[:2]

    source_img = zero_mean_normalize(source_img)
    template_img = zero_mean_normalize(template_img)

    corr = compute_correlation(source_img, template_img)

    peak_locations, peak_confidences = detect_peaks(corr, h, num_peaks)
    peak_confidences = peak_confidences / np.max(corr)  # Normalize confidence scores

    plot_correlation_matrix(corr, peak_locations, peak_confidences, os.path.join(output_dir, 'correlation_peaks.png'), save_output)

    plot_fourier_transform(template_img, os.path.join(output_dir, 'fourier_template.png'), save_output)

    correct_location_found, correct_location_idx = draw_detections_on_image(source_img_color, peak_locations, peak_confidences, (h, w), os.path.join(output_dir, 'detected.png'), cropped_centroid, save_output)

    return correct_location_found, correct_location_idx

if __name__ == '__main__':
    DISTANCES = []
    parser = argparse.ArgumentParser()
    parser.add_argument('--source_img', type=str, default='/home/undadmin/Documents/GitHub/BEV_localization/fourier_template_matching/test2.png', help='Path to the source image file.')
    parser.add_argument('--template_img', type=str, default='/home/undadmin/Documents/GitHub/BEV_localization/fourier_template_matching/test3.png', help='Path to the template image file.')
    parser.add_argument('--num_peaks', type=int, default=3, help='Number of peaks to detect.')
    parser.add_argument('--rotation_angle', type=int, default=0, help='The degree of rotation to apply to the template image.')
    parser.add_argument('--scale_factor', type=int, default=5, help='The pixel scale difference between the source and template images.')
    parser.add_argument('--save_output', type=bool, default=True, help='Whether to save the output images.')

    args = parser.parse_args()
    count = 0

    runs = 100
    for _ in range(runs):
        correct_location_found, correct_location_idx = fourier_transform_match(args.source_img, args.template_img, args.num_peaks, args.rotation_angle, args.scale_factor, args.save_output)

        if correct_location_found:
            count += 1
            print(f'Found correct location at index {correct_location_idx}.')
        else:
            print('Could not find correct location.')

    print()
    print(f'Found {count} correct locations out of {runs}.')
    print()
    print(f'Mean: {np.mean(DISTANCES)}')
    print(f'Median: {np.median(DISTANCES)}')
    print(f'Average: {np.average(DISTANCES)}')
    print(f'Min: {np.min(DISTANCES)}')
    print(f'Max: {np.max(DISTANCES)}')
    print(f'90th percentile: {np.percentile(DISTANCES, 90)}')
    print(f'80th percentile: {np.percentile(DISTANCES, 80)}')
    print(f'70th percentile: {np.percentile(DISTANCES, 70)}')
    print(f'60th percentile: {np.percentile(DISTANCES, 60)}')
    print(f'50th percentile: {np.percentile(DISTANCES, 50)}')
    print(f'40th percentile: {np.percentile(DISTANCES, 40)}')
    print(f'30th percentile: {np.percentile(DISTANCES, 30)}')
    print(f'20th percentile: {np.percentile(DISTANCES, 20)}')
    print(f'10th percentile: {np.percentile(DISTANCES, 10)}')
    print(f'5th percentile: {np.percentile(DISTANCES, 5)}')    
