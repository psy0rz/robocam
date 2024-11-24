import asyncio

import cv2

import calibrate
import config
import detector
from config import robot_middle_x, robot_middle_y, robot_ground_z, cam_approx_offset_x, cam_approx_offset_y, cam_lag_s
# from calulate import cam_angle, cam_position
from dobot.dobotfun.dobotfun import DobotFun

cam_center_x_pixels = 320
cam_center_y_pixels = 240


async def task():

    detector.confidence=0.95
    robot = DobotFun()

    print("PLEASE MOVE THE CUBE PERFECTLY UNDER THE SUCKION CUP...")
    robot.hop_to(robot_middle_x, robot_middle_y, robot_ground_z+config.calibration_box_height, r=90)
    await asyncio.sleep(5)

    #start at approx location so that we can see the cube
    calibrate_x = robot_middle_x - cam_approx_offset_x
    calibrate_y = robot_middle_y - cam_approx_offset_y
    robot.hop_to(calibrate_x, calibrate_y, robot_ground_z, r=90)


    await asyncio.sleep(cam_lag_s)

    while True:
        output_frame, w,h,detected_center_x, detected_center_y =await calibrate.get_box()

        cv2.circle(output_frame, (int(detected_center_x), int(detected_center_y)), 5, (255, 0, 255), 2, cv2.LINE_AA)
        cv2.circle(output_frame, (cam_center_x_pixels, cam_center_y_pixels), 7, (255, 255, 255), 1, cv2.LINE_AA)

        # cal robot y via screen x
        div_x_pixels = detected_center_x - cam_center_x_pixels
        step = abs(div_x_pixels) / 100
        if div_x_pixels > 0:
            calibrate_y = calibrate_y - step

        if div_x_pixels < 0:
            calibrate_y = calibrate_y + step

        # cal robot x via screen y
        div_y_pixels = detected_center_y - cam_center_y_pixels
        step = abs(div_y_pixels) / 100
        if div_y_pixels > 0:
            calibrate_x = calibrate_x - step

        if div_y_pixels < 0:
            calibrate_x = calibrate_x + step

        robot.move_to(calibrate_x, calibrate_y, robot_ground_z, r=90)
        await asyncio.sleep(cam_lag_s)

        cam_offset_x = robot_middle_x - calibrate_x
        cam_offset_y = robot_middle_y - calibrate_y
        print(
            f"Calibration: div_pixels={div_x_pixels, div_y_pixels} cam_offset=({cam_offset_x:.2f}, {cam_offset_y:.2f})")


        if div_x_pixels <1  and div_y_pixels <1:
            print(f"CALIBRATED SETTINGS:")
            print(f"cam_offset_x={cam_offset_x}")
            print(f"cam_offset_y={cam_offset_y}")

            #move back to square so user can tune it if needed
            robot.hop_to(robot_middle_x, robot_middle_y, robot_ground_z+config.calibration_box_height, r=90)
            await asyncio.sleep(1)
            robot.hop_to(calibrate_x, calibrate_y, robot_ground_z, r=90)
            await asyncio.sleep(cam_lag_s)


        cv2.imshow("Calibrate", output_frame)
        cv2.waitKey(1)

