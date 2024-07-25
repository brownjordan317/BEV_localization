import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import maximum_filter
import argparse
import os

def fourier_transform_match(source_img_path, template_img_path, num_peaks, rotation_angle, scale_factor):
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(parent_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)


    source_img = cv2.imread(source_img_path, 0)
    source_img_h, source_img_w = source_img.shape
    template_img = cv2.imread(template_img_path, 0)
    edit_h, edit_w = template_img.shape[:2]  # Template image dimensions
    rotation_matrix = cv2.getRotationMatrix2D((edit_w/2, edit_h/2), rotation_angle, 1)
    template_img = cv2.warpAffine(template_img, rotation_matrix, (edit_w, edit_h))
    # cv2.imshow('Rotated', template_img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    template_img = cv2.resize(template_img, (int(edit_h / scale_factor), int(edit_w / scale_factor)))
    h, w = template_img.shape[:2]  # Template image dimensions

    # Minimum distance between each found region
    min_dist = h

    # Compute Fourier Transform
    dft_source = np.fft.fft2(source_img)
    dft_template = np.fft.fft2(template_img, s=source_img.shape)
    dft_template_conj = np.conj(dft_template)

    # Perform multiplication in frequency domain
    corr = np.fft.ifft2(dft_source * dft_template_conj)
    corr = np.abs(corr)

    # Use maximum filter for peak detection
    neighborhood_size = min_dist * 2 + 1
    local_max = maximum_filter(corr, size=neighborhood_size)
    peak_locations = np.where(corr == local_max)

    # Sort peak locations by correlation strength
    peak_strengths = corr[peak_locations]
    sorted_indices = np.argsort(peak_strengths.flatten())[::-1]
    top_locs = list(zip(peak_locations[0][sorted_indices], peak_locations[1][sorted_indices]))

    # Filter locations based on minimum distance
    filtered_locs = []
    for loc in top_locs:
        if len(filtered_locs) == num_peaks:
            break
        
        # Check if loc is at least min_dist away from all accepted locations
        if all(np.linalg.norm(np.array(loc) - np.array(accepted_loc)) >= min_dist for accepted_loc in filtered_locs):
            # Check if loc is not within h//2 of the image edge
            y, x = loc
            if y >= h // 2 and y <= source_img_h - h // 2 and x >= w // 2 and x <= source_img_w - w//2:
                filtered_locs.append(loc)

    # Now you have the top x locations based on your criteria
    top_x_locs = filtered_locs[:num_peaks]

    # Plotting the correlation matrix
    plt.figure(figsize=(10, 8))
    plt.imshow(corr, cmap='hot')
    plt.title('Correlation Matrix')
    plt.colorbar()

    # Mark the detected peaks
    peak_rows, peak_cols = zip(*top_x_locs)
    for i, (row, col) in enumerate(zip(peak_rows, peak_cols)):
        plt.text(col, row, str(i + 1), ha='center', va='center', color='red', fontsize=10)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'correlation_peaks.png'))
    plt.close()

    # Fourier transform of the template image
    dft_template = np.fft.fft2(template_img)
    dft_shift = np.fft.fftshift(dft_template)
    magnitude_spectrum = 20 * np.log(np.abs(dft_shift))

    # Plot the Fourier transform of the template image
    plt.figure(figsize=(template_img.shape[1], template_img.shape[0]))
    plt.imshow(magnitude_spectrum, cmap='gray')
    plt.axis('off')
    plt.savefig(os.path.join(output_dir, 'fourier_template.png'), bbox_inches='tight', pad_inches=0)
    plt.close()

    # Draw rectangles on the source image
    source_img_rect = cv2.cvtColor(source_img, cv2.COLOR_GRAY2BGR)
    for i, (row, col) in enumerate(zip(peak_rows, peak_cols)):
        center = (col, row)
        cv2.circle(source_img_rect, center, 5, (0, 0, 255), -1)
        top_left = (col, row)
        bottom_right = (col + w, row + h)
        cv2.rectangle(source_img_rect, top_left, bottom_right, (0, 0, 255), 10)

    # Save the result with rectangles
    cv2.imwrite(os.path.join(output_dir, 'detected.png'), source_img_rect)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source_img', type=str, default='/home/undadmin/Documents/GitHub/BEV_localization/images/cropped.png', help='Path to the source image file.')
    parser.add_argument('--template_img', type=str, default='/home/undadmin/Documents/GitHub/BEV_localization/attempt_at_superglue/assets_randolph_zoomed/query/drone_query_2.jpg', help='Path to the template image file.')
    parser.add_argument('--num_peaks', type=int, default=3, help='Number of peaks to detect.')
    parser.add_argument('--rotation_angle', type=int, default=180, help='The degree of rotation to apply to the template image.')
    parser.add_argument('--scale_factor', type=int, default=10, help='The pixel scale difference between the source and template images.')

    args = parser.parse_args()

    fourier_transform_match(args.source_img, args.template_img, args.num_peaks, args.rotation_angle, args.scale_factor)

