import importlib

import cv2
import numpy as np


import calculate
import detector
from dobot.dobotfun.dobotfun import DobotFun
from selector import Selector
from util import draw_grid
import config

# Callback function for mouse click event


selector = Selector()

mouse_clicked = [100, 100]


def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:  # Left mouse button click
        print(f"Mouse clicked at position ({x}, {y})")
        # selector.search_point = (x, y)
        mouse_clicked[0] = x
        mouse_clicked[1] = y


async def task():
    robot = DobotFun()
    # robot.home()
    #
    # robot.move_to_nowait(x=190,y=0,z=0)
    # robot.move_to_nowait(x=380,y=0,z=0)
    robot_middle = ((190 + 380) / 2, 0)
    robot.move_to(x=robot_middle[0], y=robot_middle[1], z=config.robot_ground_z+40, r=90)
    # robot.move_to(x=200 , y=100 , z=-40, r=90)

    # robot.move_to_nowait(x=200                    ,y=-200,z=0,r=90)

    cv2.namedWindow("Robot", flags=cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)

    # selector.search_color = "orange"

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
        calculate.update_camera_matrix(cam_center_z_mm)
        print(calculate.camera_matrix)
        camera_matrix_inv = np.linalg.inv(calculate.camera_matrix)
        real_world_homogeneous = np.dot(camera_matrix_inv, screen_coords_homogeneous)

        # Normalize homogeneous coordinates to get real-world coordinates in the camera frame
        real_world_coords_camera_frame = real_world_homogeneous[:2] / real_world_homogeneous[2]

        # Reverse the camera's rotation
        rotated_coords = np.dot(reverse_rotation_matrix, real_world_coords_camera_frame)

        # Convert back to the global frame (add the camera center, swapping axes back)
        point_y_mm = -rotated_coords[0] + cam_center_y_mm
        point_x_mm = -rotated_coords[1] + cam_center_x_mm

        return point_x_mm, point_y_mm




    while True:
        await  detector.result_ready.wait()
        importlib.reload(calculate)

        if detector.result_frame is None:
            continue

        output_frame = detector.result_frame.copy()

        ###############3# robot arm

        # calculate coordinates of the cam, from robot arm coords

        robot_pose = robot.get_pose()
        robot_x_mm = (robot_pose.position.x)
        robot_y_mm = (robot_pose.position.y)
        robot_z_mm = (robot_pose.position.z)

        robot_position_mm = (robot_x_mm, robot_y_mm, robot_z_mm)

        robot_angle_degrees = robot_pose.joints.j1
        # robot_angle_degrees=cam_angle((robot_x_mm, robot_y_mm))


        cam_center_mm = calculate.calculate_camera_position_mm(robot_position_mm, robot_angle_degrees)
        # print(f"robot={(robot_x_mm, robot_y_mm)} cam={cam_center_mm}")

        # fixed test point
        #
        # cv2.circle(output_frame, calulate.robot_to_screen_pixels(cam_center_mm, robot_angle_degrees, (330, 0)), 2, (255, 255, 0),
        #            2, cv2.LINE_AA)

        # show suckion cup position
        suction_xy=calculate.robot_to_screen_pixels(cam_center_mm, robot_angle_degrees, (robot_x_mm, robot_y_mm))
        cv2.circle(output_frame, suction_xy,
                   15,
                   (0, 255, 255), 1, cv2.LINE_AA)

        # cv2.circle(output_frame, (320, 240), 20,
        #            (0, 255, 255), 2, cv2.LINE_AA)

        cv2.circle(output_frame, (320, 240), 5, (255, 255, 255), 1, cv2.LINE_AA)


        print (f"Input: {robot_x_mm, robot_y_mm}, xy={suction_xy}")
        reverse=screen_to_robot_mm(cam_center_mm, robot_angle_degrees, suction_xy)
        print (f"reverse: {reverse}")


        draw_grid(output_frame,cam_center_mm, robot_angle_degrees)

        # simulated robot arm (top left click line thingy)
        # cv2.line(output_frame, (0, 0), (robot_x, robot_y), (255, 255, 255), 4)
        # cv2.line(output_frame, (0, 0), cam_position((robot_x, robot_y)), (0, 0, 255), 1)

        # print(cam_angle(mouse_clicked))
        cv2.imshow('Robot', output_frame)
        cv2.setMouseCallback('Robot', click_event)

        # # camera center
        # screen_center_x = int(detector.result.orig_shape[1] / 2)
        # screen_center_y = int(detector.result.orig_shape[0] / 2)
        #
        # if selector.search_point is None:
        #     selector.search_point = (screen_center_x, screen_center_y)
        #
        # # print(detector.result.boxes.id)
        #
        # selector.reset()
        # middles = []
        # id_nr = 0
        # # print (detector.result.obb)
        # # for xyxy in detector.result.boxes.xyxy:
        # for xyxy in detector.result.boxes.xyxy:
        #     (x1, y1, x2, y2) = xyxy
        #     x1 = int(x1)
        #     y1 = int(y1)
        #     x2 = int(x2)
        #     y2 = int(y2)
        #
        #     w = abs(x2 - x1)
        #     h = abs(y2 - y1)
        #
        #
        #     center_x = int((x1 + x2) / 2)
        #     center_y = int((y1 + y2) / 2)
        #     middles.append([center_x, center_y])
        #
        #     # determine color sampling region
        #     sample_x1 = int(center_x - w / 4)
        #     sample_x2 = int(center_x + w / 4)
        #     sample_y1 = int(center_y - h / 4)
        #     sample_y2 = int(center_y + h / 4)
        #
        #     # average color of this region
        #     sample_image = detector.result_frame[sample_y1:sample_y2, sample_x1:sample_x2]
        #     average_color = np.mean(sample_image, axis=(0, 1))
        #
        #     # remapt to rgb
        #     average_color = (average_color[2], average_color[1], average_color[0])
        #     (color_name, neasest_color) = colormapper.find_closest_color(average_color)
        #
        #     #probaly paper grid
        #     if color_name=="gray":
        #         continue
        #
        #     # normal yolo outline
        #     draw_corner_lines(output_frame, (x1, y1), (x2, y2), (0, 0, 0), 1, 5)
        #     draw_corner_lines(output_frame, (sample_x1, sample_y1), (sample_x2, sample_y2), [255, 255, 255], 1, 5)
        #
        #
        #
        #
        #
        #     # color label
        #     cv2.rectangle(output_frame, (x1, y1), (x1 + 80, y1 - 12), [255, 0, 0], lineType=cv2.LINE_AA, thickness=-1)
        #     cv2.putText(output_frame, color_name,
        #                 (x1, y1 - 2), cv2.FONT_HERSHEY_SIMPLEX,
        #                 0.3, color=[255, 255, 255], thickness=1, lineType=cv2.LINE_AA)
        #
        #     if detector.result.boxes.id is not None:
        #         id = detector.result.boxes.id[id_nr]
        #         selector.update((center_x, center_y), color_name)
        #
        #     id_nr = id_nr + 1
        #
        # cv2.circle(output_frame, selector.search_point, 5, (255, 255, 255), 1, cv2.LINE_AA)
        #
        # if (selector.current_point is not None):
        #     draw_target_cross(output_frame, selector.current_point, (50, 50, 255), 1, 1000)

        # cv2.putText(output_frame, f"robot={robot_x, robot_y}",
        #             (screen_center_x,screen_center_y+100), cv2.FONT_HERSHEY_SIMPLEX,
        #             0.3, color=[255, 255, 255], thickness=1, lineType=cv2.LINE_AA)
        #
        #
        # cv2.putText(output_frame, f"cam={center} (robot degrees={robot_angle:.1f})",
        #             (screen_center_x+10, screen_center_y), cv2.FONT_HERSHEY_SIMPLEX,
        #             0.3, color=[255, 255, 255], thickness=1, lineType=cv2.LINE_AA)
