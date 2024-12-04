import asyncio
import importlib
from asyncio import Event

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


import config

# Callback function for mouse click event


selector = Selector()

mouse_clicked = [config.cam_center_x_pixels, config.cam_center_y_pixels]

target_ready=Event()
target_box=None
target_center_x_mm=None
target_center_y_mm=None




async def wait_for_target(x,y, timeout):
    mouse_clicked[0]=x
    mouse_clicked[1]=y

    try:
        await asyncio.wait_for(target_ready.wait(),timeout)
    except asyncio.TimeoutError:
        return False

    return True


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
            mouse_clicked[0]=x
            mouse_clicked[1]=y

            # global target_center_x_mm
            # global target_center_y_mm
            # global target_box
            # target_box=1
            # (target_center_x_mm, target_center_y_mm) = screen_to_robot_mm(cam_center_mm, robot_angle_degrees, (x, y))

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
        robot_position_mm = (robot_x_mm, robot_y_mm, robot_z_mm)

        robot_angle_degrees = robot_pose.joints.j1

        cam_center_mm = calculate.calculate_camera_position_mm(robot_position_mm, robot_angle_degrees)

        # cam_center_mm=(cam_center_mm[0], cam_center_mm[1],cam_center_mm[2]+config.calibration_box_height)

        robot_position_pixels = calculate.robot_to_screen_pixels(cam_center_mm, robot_angle_degrees,
                                                                 (robot_x_mm, robot_y_mm), True)

        util.draw_grid(output_frame, cam_center_mm, robot_angle_degrees)
        util.draw_radius_limits(output_frame, cam_center_mm, robot_angle_degrees)
        util.draw_screen_center(output_frame)
        util.draw_suction_cup(output_frame, robot_position_pixels, cam_center_mm[2])

        valid_boxes=[]
        for box in detector.result.boxes.xyxy:

            center_x, center_y=calculate.cube_get_center_pixel(box)
            center_x_mm,center_y_mm=calculate.screen_to_robot_mm(cam_center_mm, robot_angle_degrees, (center_x, center_y))
            if calculate.point_in_range(center_x_mm, center_y_mm):

                util.draw_corner_lines(output_frame, box, (0,255,0),2,10)
                valid_boxes.append(box)
            else:
                util.draw_corner_lines(output_frame, box, (0,0,255),2,10)

        global target_box
        target_box=util.find_closest_box(valid_boxes, mouse_clicked[0], mouse_clicked[1])

        if target_box is not None:
            global target_center_x_mm
            global target_center_y_mm
            center_x, center_y=calculate.cube_get_center_pixel(target_box)

            util.draw_target_cross(output_frame, center_x, center_y, (255, 255, 255), 2, 10)

            (target_center_x_mm, target_center_y_mm)=screen_to_robot_mm(cam_center_mm,  robot_angle_degrees, (center_x, center_y))

            target_ready.set()
            target_ready.clear()

        cv2.imshow('Robot', output_frame)





        #
        #
        #
        #     # color label
        #     cv2.rectangle(output_frame, (x1, y1), (x1 + 80, y1 - 12), [255, 0, 0], lineType=cv2.LINE_AA, thickness=-1)
        #     cv2.putText(output_frame, color_name,
        #                 (x1, y1 - 2), cv2.FONT_HERSHEY_SIMPLEX,
        #                 0.3, color=[255, 255, 255], thickness=1, lineType=cv2.LINE_AA)
        #
