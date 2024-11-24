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



# get x1,y1,x2,y2 of the box that is closest to x,y (center coords)
def get_closest_box(boxes, target_x,target_y):

    closest_box = None
    min_distance = float('inf')

    for xyxy in boxes.xyxy:
            (x1, y1, x2, y2) = xyxy

            center_x = (x1 + x2)/2
            center_y = (y1 + y2) /2
            distance = math.sqrt((center_x - target_x) ** 2 + (center_y - target_y) ** 2)

            if distance < min_distance:
                    min_distance = distance
                    closest_box = xyxy

    return closest_box
