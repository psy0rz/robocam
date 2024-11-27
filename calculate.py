import math

import config

import numpy as np

def distance_between_points(point1, point2):
    # dist=cv2.norm(np.array(point1) - np.array(point2))
    dist = math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)

    return dist

def get_pix_per_mm_for_camera_height(camera_height):

    return (config.low_cam_height / camera_height) * config.low_x_pix_per_mm


# NOTE: just get j1 from dobot itself instead of calculating
# calculate the camera rotation angle from the robot arm position
def cam_angle(robot_pos):
    a = math.atan(robot_pos[1] / robot_pos[0])

    return a


def calculate_camera_position_mm(robot_position_mm, robot_angle_degrees):
    """
    Calculate the camera's position based on the suction cup's position, offset, and orientation.

    :param robot_position_mm: Tuple (x_suction, y_suction) representing the suction cup's global position.
    :param camera_offset: Tuple (offset_x, offset_y) representing the camera's offset relative to the suction cup.
    :param robot_angle_degrees: Robot's orientation angle in degrees.
    :return: Tuple (x_camera, y_camera) representing the camera's global position. z is cam measured from floor
    """
    # Unpack inputs
    x_suction, y_suction, z_suction = robot_position_mm

    # Convert angle to radians
    angle_rad = np.radians(robot_angle_degrees)

    # use the static x offsets + the offset-per-mm for camera tilt compensation
    delta_z = z_suction - config.cam_tilt_base
    offset_x = config.cam_offset_x - delta_z * config.cam_tilt_x_mm
    offset_y = config.cam_offset_y - delta_z * config.cam_tilt_y_mm

    # Rotate the offset
    offset_x_rotated = offset_x * np.cos(angle_rad) - offset_y * np.sin(angle_rad)
    offset_y_rotated = offset_x * np.sin(angle_rad) + offset_y * np.cos(angle_rad)

    # Calculate camera position
    x_camera = x_suction + offset_x_rotated
    y_camera = y_suction + offset_y_rotated
    z_camera = z_suction + config.cam_offset_z

    return x_camera, y_camera, z_camera

camera_matrix = np.array([
    [None, 0, config.cam_center_x_pixels],  # fill be filled in later
    [0, None, config.cam_center_y_pixels],
    [0, 0, 1]  # 0, 0, 1
], dtype=np.float64)


def update_camera_matrix(camera_height):
    pix_per_mm = get_pix_per_mm_for_camera_height(camera_height)
    camera_matrix[0, 0] = np.float64(pix_per_mm)
    camera_matrix[1, 1] = np.float64(pix_per_mm)


def robot_to_screen_pixels(camera_center_mm, camera_angle_mm, point_mm):
    """
    Convert a real-world point to screen coordinates, accounting for the robot's camera position and orientation.

    :param camera_center_mm: Tuple (robot_x, robot_y, robot_z) representing the camera's center in world units.
    :param camera_angle_mm: Camera rotation angle (in degrees, counterclockwise).
    :param point_mm: Tuple (point_x, point_y) representing the real-world point to project.
    :param camera_matrix: Intrinsic camera matrix (3x3 numpy array).
    :return: Screen coordinates as a tuple (x_screen, y_screen).
    """
    # Convert angle to radians
    cam_angle_rad = np.radians(camera_angle_mm)

    # Rotation matrix for the camera
    rotation_matrix = np.array([
        [np.cos(cam_angle_rad), -np.sin(cam_angle_rad)],
        [np.sin(cam_angle_rad), np.cos(cam_angle_rad)]
    ])

    # Extract the coordinates
    cam_center_x, cam_center_y , cam_center_z= camera_center_mm
    point_x, point_y = point_mm

    # Adjust point to the camera's frame of reference (relative to camera center)
    # x and y axis swapped!
    relative_coords = np.array([ cam_center_y-point_y,  cam_center_x-point_x])

    # Rotate the adjusted coordinates into the camera's orientation
    rotated_coords = np.dot(rotation_matrix, relative_coords)

    # Add homogeneous coordinate (z=1 for 2D projection)
    homogeneous_coords = np.append(rotated_coords, 1)

    # Project to screen coordinates using the intrinsic camera matrix
    update_camera_matrix(cam_center_z)
    screen_coords_homogeneous = np.dot(camera_matrix, homogeneous_coords)
    x_screen = screen_coords_homogeneous[0] / screen_coords_homogeneous[2]
    y_screen = screen_coords_homogeneous[1] / screen_coords_homogeneous[2]

    return x_screen, y_screen


def screen_to_robot_mm(camera_center_mm, camera_angle_mm, point_pixels):

    # Convert angle to radians
    cam_angle_rad = np.radians(camera_angle_mm)

    # Rotation matrix for the camera
    reverse_rotation_matrix = np.array([
        [np.cos(cam_angle_rad), np.sin(cam_angle_rad)],
        [-np.sin(cam_angle_rad), np.cos(cam_angle_rad)]
    ])

    # Extract the coordinates
    cam_center_x_mm, cam_center_y_mm, cam_center_z_mm = camera_center_mm
    point_x_pixels, point_y_pixels = point_pixels

    # Convert screen coordinates to homogeneous form
    screen_coords_homogeneous = np.array([point_x_pixels, point_y_pixels, 1])

    # Reverse the projection (intrinsic matrix inverse)
    update_camera_matrix(cam_center_z_mm)
    # print(calculate.camera_matrix)
    camera_matrix_inv = np.linalg.inv(camera_matrix)
    real_world_homogeneous = np.dot(camera_matrix_inv, screen_coords_homogeneous)

    # Normalize homogeneous coordinates to get real-world coordinates in the camera frame
    real_world_coords_camera_frame = real_world_homogeneous[:2] / real_world_homogeneous[2]

    # Reverse the camera's rotation
    rotated_coords = np.dot(reverse_rotation_matrix, real_world_coords_camera_frame)

    # Convert back to the global frame (add the camera center, swapping axes back)
    point_y_mm = -rotated_coords[0] + cam_center_y_mm
    point_x_mm = -rotated_coords[1] + cam_center_x_mm

    return point_x_mm, point_y_mm

