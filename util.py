import cv2
import math
import numpy as np

import config
from calculate import robot_to_screen_pixels, get_pix_per_mm_for_camera_height


def draw_corner_lines(img, box, color, thickness, line_length):
    x1, y1, x2, y2 = tuple(int(i) for i in box)

    # Calculate corner points for small line segments
    # Top-left corner horizontal and vertical lines
    cv2.line(img, (x1, y1), (x1 + line_length, y1), color, thickness, )
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


def draw_target_cross(img, target_box, color, thickness, line_length):
    (x1, y1, x2, y2) = target_box
    center_x = int((x1 + x2) / 2)
    center_y = int((y1 + y2) / 2)

    # Draw horizontal line
    cv2.line(img, (center_x - line_length, center_y), (center_x + line_length, center_y), color, thickness)

    # Draw vertical line
    cv2.line(img, (center_x, center_y - line_length), (center_x, center_y + line_length), color, thickness)


def draw_grid(output_frame, cam_center_mm, cam_angle_degrees):
    step = 10

    start_x = int(round(cam_center_mm[0], -1) - 50)
    end_x = int(round(cam_center_mm[0], -1) + 50)

    start_y = int(round(cam_center_mm[1], -1) - 50)
    end_y = int(round(cam_center_mm[1], -1) + 50)

    color = (200, 200, 200)

    for x in range(start_x, end_x, step):
        screen_coord_start = robot_to_screen_pixels(cam_center_mm, cam_angle_degrees, (x, start_y), True)
        screen_coord_end = robot_to_screen_pixels(cam_center_mm, cam_angle_degrees, (x, end_y - step), True)
        cv2.line(output_frame, screen_coord_start, screen_coord_end, color, 1, cv2.LINE_AA)

    for y in range(start_y, end_y, step):
        screen_coord_start = robot_to_screen_pixels(cam_center_mm, cam_angle_degrees, (start_x, y), True)
        screen_coord_end = robot_to_screen_pixels(cam_center_mm, cam_angle_degrees, (end_x - step, y), True)
        cv2.line(output_frame, screen_coord_start, screen_coord_end, color, 1, cv2.LINE_AA)


# get x1,y1,x2,y2 of the box that is closest to x,y (center coords)
def find_closest_box(boxes, target_x, target_y):
    closest_box = None
    min_distance = float('inf')

    for xyxy in boxes:
        (x1, y1, x2, y2) = xyxy

        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        distance = math.sqrt((center_x - target_x) ** 2 + (center_y - target_y) ** 2)

        if distance < min_distance:
            min_distance = distance
            closest_box = xyxy

    return closest_box


def draw_screen_center(img):
    cv2.circle(img, (config.cam_center_x_pixels, config.cam_center_y_pixels), 5, (255, 255, 255), 1,
               cv2.LINE_AA)


def draw_suction_cup(img, position_pixels, camera_height):
    pix_per_mm = get_pix_per_mm_for_camera_height(camera_height)

    radius = int(config.suction_cup_diameter * pix_per_mm / 2)
    cv2.circle(img, position_pixels,
               radius,
               (200, 200, 200), 2, cv2.LINE_AA)


def draw_radius_limits(img, camera_center_mm, camera_angle):
    pix_per_mm = get_pix_per_mm_for_camera_height(camera_center_mm[2])
    robot_center = robot_to_screen_pixels(camera_center_mm, camera_angle, (0,0),True)

    cv2.circle(img, robot_center,
               int(config.robot_min_radius * pix_per_mm),
               (0, 0, 255), 1, cv2.LINE_AA)

    cv2.circle(img, robot_center,
               int(config.robot_max_radius * pix_per_mm),
               (0, 0, 255), 1, cv2.LINE_AA)
