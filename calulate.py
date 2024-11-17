import math


def distance_between_points(point1, point2):
    # dist=cv2.norm(np.array(point1) - np.array(point2))
    dist = math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)

    return dist


CAM_OFFSET = 50


# calculate the camera position from the robot arm position (real world coords)
def cam_position(robot_pos, invert=False):
    arm_len = math.sqrt(robot_pos[0] ** 2 + robot_pos[1] ** 2)

    if invert:
        arm_len_cam = arm_len - CAM_OFFSET
    else:
        arm_len_cam = arm_len + CAM_OFFSET

    arm_factor = arm_len_cam / arm_len

    return int(robot_pos[0] * arm_factor), int(robot_pos[1] * arm_factor)


# calculate the camera rotation angle from the robot arm position
def cam_angle(robot_pos):
    a = math.atan(robot_pos[1] / robot_pos[0])

    return a
