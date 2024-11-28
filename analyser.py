import importlib

import cv2

import calculate
import detector
from calculate import screen_to_robot_mm
from dobot.dobotfun.dobotfun import DobotFun
from robot import robot
from selector import Selector


import util
importlib.reload(calculate)
importlib.reload(util)

from util import draw_grid, draw_screen_center, draw_suction_cup, draw_corner_lines, find_closest_box, \
    draw_target_cross, draw_radius_limits
import config

# Callback function for mouse click event


selector = Selector()

mouse_clicked = None

target_box=None
target_center_x_mm=None
target_center_y_mm=None





async def task():
    # robot.home()
    #
    # robot.move_to_nowait(x=190,y=0,z=0)
    # robot.move_to_nowait(x=380,y=0,z=0)
    # robot.move_to(x=200 , y=100 , z=-40, r=90)

    # robot.move_to_nowait(x=200                    ,y=-200,z=0,r=90)

    print(f"Using robot: {config.robot_name}")

    cv2.namedWindow("Robot", flags=cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)

    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:  # Left mouse button click
            print(f"Mouse clicked at position ({x}, {y})")
            # selector.search_point = (x, y)
            mouse_clicked = (x, y)

            global target_center_x_mm
            global target_center_y_mm
            (target_center_x_mm, target_center_y_mm) = screen_to_robot_mm(cam_center_mm, robot_angle_degrees, (x, y))

    cv2.setMouseCallback('Robot', click_event)

    # selector.search_color = "orange"

    while True:
        await  detector.result_ready.wait()

        if detector.result_frame is None:
            continue

        output_frame = detector.result_frame.copy()

        ###############3# robot arm

        robot_pose = robot.get_pose()
        robot_x_mm = (robot_pose.position.x)
        robot_y_mm = (robot_pose.position.y)
        robot_z_mm = (robot_pose.position.z)
        robot_position_mm = (robot_x_mm, robot_y_mm, robot_z_mm-config.calibration_box_height)

        robot_angle_degrees = robot_pose.joints.j1

        cam_center_mm = calculate.calculate_camera_position_mm(robot_position_mm, robot_angle_degrees)
        # cam_center_mm[2]=cam_center_mm[2]-config.calibration_box_height

        robot_position_pixels = calculate.robot_to_screen_pixels(cam_center_mm, robot_angle_degrees,
                                                                 (robot_x_mm, robot_y_mm), True)

        draw_grid(output_frame, cam_center_mm, robot_angle_degrees)
        draw_radius_limits(output_frame, cam_center_mm, robot_angle_degrees)
        draw_screen_center(output_frame)
        draw_suction_cup(output_frame, robot_position_pixels, cam_center_mm[2])


        for box in detector.result.boxes.xyxy:
            draw_corner_lines(output_frame, box, (0,255,0),2,10)

        global target_box
        target_box=find_closest_box(detector.result.boxes.xyxy, config.cam_center_x_pixels, config.cam_center_y_pixels)

        if target_box is not None:

            draw_target_cross(output_frame, target_box, (100, 100, 255), 2, 10)

            global target_center_x_mm
            global target_center_y_mm
            (x1, y1, x2, y2) = target_box
            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)

            (target_center_x_mm, target_center_y_mm)=screen_to_robot_mm(cam_center_mm,  robot_angle_degrees, (center_x, center_y))


        cv2.imshow('Robot', output_frame)

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
