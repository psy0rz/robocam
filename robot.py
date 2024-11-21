import importlib
import math

import cv2
import numpy as np

import calulate
import detector
from calulate import cam_angle
# from calulate import cam_angle, cam_position
from dobot.dobotfun.dobotfun import DobotFun
from selector import Selector
from util import draw_corner_lines, draw_target_cross
import colormapper

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
    robot.move_to_nowait(x=robot_middle[0]+20, y=robot_middle[1]+50, z=0, r=90)


    # robot.move_to_nowait(x=200                    ,y=-200,z=0,r=90)

    cv2.namedWindow("Robot", flags=cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)

    # selector.search_color = "orange"

    while True:
        await  detector.result_ready.wait()
        importlib.reload(calulate)

        if detector.result_frame is None:
            continue

        output_frame = detector.result_frame.copy()

        ###############3# robot arm

        # calculate coordinates of the cam, from robot arm coords

        robot_pose = robot.get_pose()
        robot_x_mm = (robot_pose.position.x)
        robot_y_mm = (robot_pose.position.y)
        robot_z_mm = (robot_pose.position.z)

        robot_position_mm=(robot_x_mm, robot_y_mm, robot_z_mm)

        robot_angle_degrees = robot_pose.joints.j1
        # print(f"{robot_x_mm}, {robot_y_mm}, {robot_angle_degrees}")

        #camera offset from suction cup (xy) and floor (z)
        # z offset is measured from the floor when robot-z is zero
        camera_offset_mm = [53, 2,118]

        #camera should now move to exactly where the suction cup just was (if not, adjust offsets)
        # robot.move_to_nowait(x=robot_middle[0]-camera_offset_mm[0], y=robot_middle[1]-camera_offset_mm[1], z=-50, r=90)

        # note: some trickyness since x and y are swapped for the robot
        pixels_per_mm_x = float(8.15)
        pixels_per_mm_y = pixels_per_mm_x
        cam_center_x_pixels = 320
        cam_center_y_pixels = 240
        camera_matrix_z=camera_offset_mm[2]-50 #base "zoom" level / camera height that corresponds the the camera_matrix below
        camera_matrix = np.array([
            [pixels_per_mm_x, 0, cam_center_x_pixels],
            [0, pixels_per_mm_y, cam_center_y_pixels],
            [0, 0, 1]  # 0, 0, 1
        ])



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
            cam_center_x, cam_center_y, cam_center_z = camera_center_mm
            point_x, point_y = point_mm

            # Adjust point to the camera's frame of reference (relative to camera center)
            # x and y axis swapped!
            relative_coords = np.array([-point_y + cam_center_y, -point_x + cam_center_x])

            # Rotate the adjusted coordinates into the camera's orientation
            rotated_coords = np.dot(rotation_matrix, relative_coords)

            # Add homogeneous coordinate (z=1 for 2D projection)
            homogeneous_coords = np.append(rotated_coords, 1)

            #adjust for z height of cam
            zoomed_camera_matrix=camera_matrix.copy()
            zoom_factor=camera_matrix_z/ cam_center_z
            zoomed_camera_matrix[0, 0] *= zoom_factor  # Adjust fx
            zoomed_camera_matrix[1, 1] *= zoom_factor  # Adjust fy

            # Project to screen coordinates using the intrinsic camera matrix
            screen_coords_homogeneous = np.dot(zoomed_camera_matrix, homogeneous_coords)
            x_screen = screen_coords_homogeneous[0] / screen_coords_homogeneous[2]
            y_screen = screen_coords_homogeneous[1] / screen_coords_homogeneous[2]

            return int(x_screen), int(y_screen)

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
            offset_x, offset_y, offset_z = camera_offset_mm

            # Convert angle to radians
            angle_rad = np.radians(robot_angle_degrees)

            # Rotate the offset
            offset_x_rotated = offset_x * np.cos(angle_rad) - offset_y * np.sin(angle_rad)
            offset_y_rotated = offset_x * np.sin(angle_rad) + offset_y * np.cos(angle_rad)

            # Calculate camera position
            x_camera = x_suction + offset_x_rotated
            y_camera = y_suction + offset_y_rotated
            z_camera = z_suction + offset_z

            return x_camera, y_camera, z_camera


        cam_center_mm = calculate_camera_position_mm(robot_position_mm, robot_angle_degrees)
        # print(f"robot={(robot_x_mm, robot_y_mm)} cam={cam_center_mm}")

        # fixed test point
        cv2.circle(output_frame, robot_to_screen_pixels(cam_center_mm, robot_angle_degrees, (330,0)), 2, (255, 255,0), 2, cv2.LINE_AA)

        # show suckion cup position
        cv2.circle(output_frame, robot_to_screen_pixels(cam_center_mm, robot_angle_degrees, (robot_x_mm, robot_y_mm)), 15,
                   (0, 255, 255), 2, cv2.LINE_AA)

        cv2.circle(output_frame, (320, 240), 5, (255, 255, 255), 1, cv2.LINE_AA)

        def draw_grid(cam_center_mm, cam_angle_degrees):

            step = 10

            start_x = int(round(cam_center_mm[0], -1) - 50)
            end_x = int(round(cam_center_mm[0], -1) + 50)

            start_y = int(round(cam_center_mm[1], -1) - 50)
            end_y = int(round(cam_center_mm[1], -1) + 50)

            for x in range(start_x, end_x, step):
                screen_coord_start = robot_to_screen_pixels(cam_center_mm, cam_angle_degrees, (x, start_y))
                screen_coord_end = robot_to_screen_pixels(cam_center_mm, cam_angle_degrees, (x, end_y - step))
                cv2.line(output_frame, screen_coord_start, screen_coord_end, (0, 255, 0), 1, cv2.LINE_AA)

            for y in range(start_y, end_y, step):
                screen_coord_start = robot_to_screen_pixels(cam_center_mm, cam_angle_degrees, (start_x, y))
                screen_coord_end = robot_to_screen_pixels(cam_center_mm, cam_angle_degrees, (end_x - step, y))
                cv2.line(output_frame, screen_coord_start, screen_coord_end, (0, 255, 0), 1,cv2.LINE_AA)

        draw_grid(cam_center_mm, robot_angle_degrees)

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
