import cv2

def is_blurred(image, threshold):
    laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
    return laplacian_var < threshold, laplacian_var