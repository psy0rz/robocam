import cv2
import math
import numpy as np


def draw_corner_lines(img, pt1, pt2, color, thickness, line_length):
    x1, y1 = pt1
    x2, y2 = pt2

    # Calculate corner points for small line segments
    # Top-left corner horizontal and vertical lines
    cv2.line(img, (x1, y1), (x1 + line_length, y1), color, thickness,)
    cv2.line(img, (x1, y1), (x1, y1 + line_length), color, thickness)

    # Top-right corner horizontal and vertical lines
    cv2.line(img, (x2, y1), (x2 - line_length, y1), color, thickness)
    cv2.line(img, (x2, y1), (x2, y1 + line_length), color, thickness)

    # Bottom-left corner horizontal and vertical lines
    cv2.line(img, (x1, y2), (x1 + line_length, y2), color, thickness)
    cv2.line(img, (x1, y2), (x1, y2 - line_length), color, thickness)

    # Bottom-right corner horizontal and vertical lines
    cv2.line(img, (x2, y2), (x2 - line_length, y2), color, thickness)
    cv2.line(img, (x2, y2), (x2, y2 - line_length), color, thickness)


def draw_target_cross(img, center, color, thickness, line_length):

    # Draw horizontal line
    cv2.line(img, (center[0] - line_length, center[1]), (center[0] + line_length, center[1]), color, thickness)

    # Draw vertical line
    cv2.line(img, (center[0], center[1] - line_length), (center[0], center[1] + line_length), color, thickness)


def distance_between_points(point1, point2):
    # dist=cv2.norm(np.array(point1) - np.array(point2))
    dist=math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)

    return dist
    # # Convert points to NumPy arrays (OpenCV works well with NumPy)
    # point1 = np.array(point1, dtype=np.float32)
    # point2 = np.array(point2, dtype=np.float32)
    #
    # # Calculate the Euclidean distance using OpenCV
    # distance = cv2.norm(point1, point2, cv2.NORM_L2)
    # return distance



