import cv2
import numpy as np

def pencil_sketch(image_path, output_path, intensity=0.5, edge_strength=0.5):
    """
    Converts an image to a pencil sketch.
    :param image_path: Path to the input image.
    :param output_path: Path to save the output image.
    :param intensity: Determines the sigma_s value for cv2.pencilSketch (0 to 1).
    :param edge_strength: Determines the sigma_r value for cv2.pencilSketch (0 to 1).
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Could not read the image")

    # Map the 0-1 range to appropriate parameters for pencilSketch
    # sigma_s (spatial): 0 to 200
    sigma_s = int(intensity * 180) + 20
    # sigma_r (range): 0 to 1
    sigma_r = edge_strength * 0.9 + 0.1

    gray_sketch, color_sketch = cv2.pencilSketch(img, sigma_s=sigma_s, sigma_r=sigma_r, shade_factor=0.05)
    
    cv2.imwrite(output_path, gray_sketch)
    return True


def watercolor_sketch(image_path, output_path, smoothness=0.5):
    """
    Converts an image to a watercolor sketch.
    :param image_path: Path to the input image.
    :param output_path: Path to save the output image.
    :param smoothness: Determines the smoothing amount (0 to 1).
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Could not read the image")

    # Map smoothness (0-1) to sigma_s (0-200) and sigma_r (0-1)
    sigma_s = int(smoothness * 180) + 20
    sigma_r = smoothness * 0.8 + 0.1
    
    # 1. Edge preserving filter for smoothing
    smoothed = cv2.edgePreservingFilter(img, flags=1, sigma_s=sigma_s, sigma_r=sigma_r)
    
    # 2. Stylization for watercolor effect
    stylized = cv2.stylization(smoothed, sigma_s=sigma_s, sigma_r=sigma_r)
    
    cv2.imwrite(output_path, stylized)
    return True
