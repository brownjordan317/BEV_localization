
import cv2
import numpy as np


def resize_image(image, size):
    '''Resize an image to a specific size.

    Args:
        image: The input image.
        size: The size to resize the image to.

    Returns:
        The resized image.
    '''
    width, height, _ = image.shape
    new_height, new_width = size
    print(new_height, new_width)
    resized_image = cv2.resize(image, (new_width, new_height),
                               interpolation=cv2.INTER_NEAREST)
    return resized_image


image = cv2.imread('/home/undadmin/Documents/GitHub/BEV_localization/fourier_template_matching/source_sat.png')
resized_image = resize_image(image, (589, 511))
cv2.imwrite('resized_image.png', resized_image)
