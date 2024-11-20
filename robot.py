import math

import cv2
import numpy as np

import detector
from calulate import cam_angle, cam_position
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

    cv2.namedWindow("Robot", flags=cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)

    # selector.search_color = "orange"

    while True:
        await  detector.result_ready.wait()


        if detector.result_frame is None:
            continue

        output_frame = detector.result_frame.copy()

        # camera center
        screen_center_x = int(detector.result.orig_shape[1] / 2)
        screen_center_y = int(detector.result.orig_shape[0] / 2)

        if selector.search_point is None:
            selector.search_point = (screen_center_x, screen_center_y)

        # print(detector.result.boxes.id)

        selector.reset()
        middles = []
        id_nr = 0
        # print (detector.result.obb)
        # for xyxy in detector.result.boxes.xyxy:
        for xyxy in detector.result.boxes.xyxy:
            (x1, y1, x2, y2) = xyxy
            x1 = int(x1)
            y1 = int(y1)
            x2 = int(x2)
            y2 = int(y2)

            w = abs(x2 - x1)
            h = abs(y2 - y1)


            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)
            middles.append([center_x, center_y])

            # determine color sampling region
            sample_x1 = int(center_x - w / 4)
            sample_x2 = int(center_x + w / 4)
            sample_y1 = int(center_y - h / 4)
            sample_y2 = int(center_y + h / 4)

            # average color of this region
            sample_image = detector.result_frame[sample_y1:sample_y2, sample_x1:sample_x2]
            average_color = np.mean(sample_image, axis=(0, 1))

            # remapt to rgb
            average_color = (average_color[2], average_color[1], average_color[0])
            (color_name, neasest_color) = colormapper.find_closest_color(average_color)

            #probaly paper grid
            if color_name=="gray":
                continue

            # normal yolo outline
            draw_corner_lines(output_frame, (x1, y1), (x2, y2), (0, 0, 0), 1, 5)
            draw_corner_lines(output_frame, (sample_x1, sample_y1), (sample_x2, sample_y2), [255, 255, 255], 1, 5)





            # color label
            cv2.rectangle(output_frame, (x1, y1), (x1 + 80, y1 - 12), [255, 0, 0], lineType=cv2.LINE_AA, thickness=-1)
            cv2.putText(output_frame, color_name,
                        (x1, y1 - 2), cv2.FONT_HERSHEY_SIMPLEX,
                        0.3, color=[255, 255, 255], thickness=1, lineType=cv2.LINE_AA)

            if detector.result.boxes.id is not None:
                id = detector.result.boxes.id[id_nr]
                selector.update((center_x, center_y), color_name)

            id_nr = id_nr + 1

        cv2.circle(output_frame, selector.search_point, 5, (255, 255, 255), 1, cv2.LINE_AA)

        if (selector.current_point is not None):
            draw_target_cross(output_frame, selector.current_point, (50, 50, 255), 1, 1000)

        ###############3# robot arm

        # calculate coordinates of the cam, from robot arm coords


        # simulate robot pos with mouse (middle is 0,0)
        robot_pose=robot.get_pose()
        robot_x = int(robot_pose.position.x)
        robot_y = int(robot_pose.position.y)
        robot_angle=robot_pose.joints.j1

        center = cam_position((robot_x, robot_y))

        cv2.putText(output_frame, f"robot={robot_x, robot_y}",
                    (screen_center_x,screen_center_y+100), cv2.FONT_HERSHEY_SIMPLEX,
                    0.3, color=[255, 255, 255], thickness=1, lineType=cv2.LINE_AA)


        cv2.putText(output_frame, f"cam={center} (robot degrees={robot_angle:.1f})",
                    (screen_center_x+10, screen_center_y), cv2.FONT_HERSHEY_SIMPLEX,
                    0.3, color=[255, 255, 255], thickness=1, lineType=cv2.LINE_AA)

        # robot_x=100
        # robot_y=150

        #

        # center of the current image

        # caculate the on screen location from real coordinates
        # def real_to_pixels(cam_center, cam_angle, robot_pos):
        #
        #     # offset from camera center (real coords)
        #     offset = (robot_pos[0] - cam_center[0], robot_pos[1] - cam_center[1])
        #
        #     # convert to pixels
        #     factor=4
        #     offset_pixels_x=offset[0]*factor
        #     offset_pixels_y=offset[1]*factor
        #
        #     # Calculate the end coordinates
        #     print(cam_angle)
        #     angle_rad = math.radians(cam_angle)
        #     end_x = int(screen_center_x - offset_pixels_x * math.cos(angle_rad))
        #     end_y = int(screen_center_y - offset_pixels_y * math.sin(angle_rad))
        #
        #     #absolute pixel coords
        #     # pixel_coord=( int(screen_center_x+offset_pixels[0]), int(screen_center_y+offset_pixels[1]))
        #
        #     return (end_x, end_y)


        # Example Usage
        # Intrinsic camera matrix (example, update with your camera parameters)
        camera_matrix = np.array([
            [3, 0, 320],  # fx, 0, cx
            [0, 3, 240],  # 0, fy, cy
            [0, 0, 1]  # 0, 0, 1
        ])

        def robot_to_screen(robot_center, robot_angle, point):
            """
            Convert a real-world point to screen coordinates, accounting for the robot's camera position and orientation.

            :param robot_center: Tuple (robot_x, robot_y) representing the camera's center in world units.
            :param robot_angle: Camera rotation angle (in degrees, counterclockwise).
            :param point: Tuple (point_x, point_y) representing the real-world point to project.
            :param camera_matrix: Intrinsic camera matrix (3x3 numpy array).
            :return: Screen coordinates as a tuple (x_screen, y_screen).
            """
            # Convert angle to radians
            angle_rad = np.radians(robot_angle)

            # Rotation matrix for the camera
            rotation_matrix = np.array([
                [np.cos(angle_rad), -np.sin(angle_rad)],
                [np.sin(angle_rad), np.cos(angle_rad)]
            ])

            # Extract the coordinates
            robot_x, robot_y = robot_center
            point_x, point_y = point

            # Adjust point to the camera's frame of reference (relative to camera center)
            relative_coords = np.array([point_x - robot_x, point_y - robot_y])

            # Rotate the adjusted coordinates into the camera's orientation
            rotated_coords = np.dot(rotation_matrix, relative_coords)

            # Add homogeneous coordinate (z=1 for 2D projection)
            homogeneous_coords = np.append(rotated_coords, 1)

            # Project to screen coordinates using the intrinsic camera matrix
            screen_coords_homogeneous = np.dot(camera_matrix, homogeneous_coords)
            x_screen = screen_coords_homogeneous[0] / screen_coords_homogeneous[2]
            y_screen = screen_coords_homogeneous[1] / screen_coords_homogeneous[2]

            return int(x_screen), int(y_screen)

        def draw_grid(cam_center, cam_angle):
            #FIX: angle

            step=10

            start_x=round(cam_center[0],-1)-50
            end_x=round(cam_center[0],-1)+50

            start_y=round(cam_center[1],-1)-50
            end_y=round(cam_center[1],-1)+50

            for x in range(start_x, end_x, step):
                screen_coord_start=robot_to_screen(cam_center, cam_angle, (x,start_y))
                screen_coord_end=robot_to_screen(cam_center, cam_angle, (x,end_y-step))
                cv2.line(output_frame, screen_coord_start, screen_coord_end, (0, 255,0), 1)

            for y in range(start_y, end_y, step):
                screen_coord_start = robot_to_screen(cam_center, cam_angle, (start_x, y))
                screen_coord_end = robot_to_screen(cam_center, cam_angle, (end_x-step, y))
                cv2.line(output_frame, screen_coord_start, screen_coord_end, (0, 255, 0), 1)

        draw_grid(center, robot_angle)


    #show robot arm position
        cv2.circle(output_frame, robot_to_screen(center, robot_angle, (robot_x,robot_y)), 15, (0, 255,0), 1, cv2.LINE_AA)

        # simulated robot arm (top left click line thingy)
        cv2.line(output_frame, (0, 0), (robot_x, robot_y), (255, 255, 255), 4)
        cv2.line(output_frame, (0, 0), cam_position((robot_x, robot_y)), (0, 0, 255), 1)


        # print(cam_angle(mouse_clicked))
        cv2.imshow('Robot', output_frame)
        cv2.setMouseCallback('Robot', click_event)
