import asyncio

import cv2

import calibrate
import config
import detector
from config import robot_middle_x, robot_middle_y, robot_ground_z, cam_lag_s, cam_tilt_x_mm
from dobot.dobotfun.dobotfun import DobotFun

cam_center_x_pixels = 320
cam_center_y_pixels = 240

robot = DobotFun()


# moves robot around until detected cube is in the center of the screen
async def center_cube(calibrate_x, calibrate_y, z):
    while True:
        await asyncio.sleep(cam_lag_s)
        output_frame, w, h, detected_center_x, detected_center_y = await calibrate.get_box()

        cv2.circle(output_frame, (int(detected_center_x), int(detected_center_y)), 5, (255, 0, 255), 2, cv2.LINE_AA)
        cv2.circle(output_frame, (cam_center_x_pixels, cam_center_y_pixels), 7, (255, 255, 255), 1, cv2.LINE_AA)

        # cal robot y via screen x
        div_x_pixels = detected_center_x - cam_center_x_pixels
        step = abs(div_x_pixels) / 50
        if div_x_pixels > 0:
            calibrate_y = calibrate_y - step

        if div_x_pixels < 0:
            calibrate_y = calibrate_y + step

        # cal robot x via screen y
        div_y_pixels = detected_center_y - cam_center_y_pixels
        step = abs(div_y_pixels) / 50
        if div_y_pixels > 0:
            calibrate_x = calibrate_x - step

        if div_y_pixels < 0:
            calibrate_x = calibrate_x + step

        robot.move_to(calibrate_x, calibrate_y, z, r=90)

        if div_x_pixels < 0.5 and div_y_pixels < 0.5:
            calibrate.message(output_frame, "OK", (0, 255, 0))

            cv2.imshow("Calibrate", output_frame)
            cv2.waitKey(1)
            return calibrate_x, calibrate_y
        else:
            calibrate.message(output_frame, "Calibrating...", (0, 255, 0))

            cv2.imshow("Calibrate", output_frame)
            cv2.waitKey(1)


async def task():
    detector.confidence = 0.90

    print("PLEASE MOVE THE CUBE PERFECTLY UNDER THE SUCKION CUP...")
    robot.move_to(robot_middle_x, robot_middle_y, robot_ground_z + config.calibration_box_height + 50, r=90)
    robot.move_to(robot_middle_x, robot_middle_y, robot_ground_z + config.calibration_box_height, r=90)
    await asyncio.sleep(5)

    # start at approx location so that we can see the cube
    calibrate_x = robot_middle_x - config.cam_offset_x
    calibrate_y = robot_middle_y - config.cam_offset_y
    robot.move_to(calibrate_x, calibrate_y, robot_ground_z + 50, r=90)
    robot.move_to(calibrate_x, calibrate_y, robot_ground_z, r=90)

    calibrate_x, calibrate_y = await center_cube(calibrate_x, calibrate_y, robot_ground_z)

    cam_offset_x = robot_middle_x - calibrate_x
    cam_offset_y = robot_middle_y - calibrate_y

    # move up and get the offset per z increase . this compensates for small cam tilt
    delta_z = 200

    calibrate_high_x=calibrate_x+ (config.cam_tilt_x_mm*delta_z)
    calibrate_high_y=calibrate_y+ (config.cam_tilt_y_mm*delta_z)

    robot.move_to(calibrate_high_x, calibrate_high_y, robot_ground_z + delta_z,
                  r=90)
    calibrate_high_x, calibrate_high_y = await center_cube(calibrate_high_x, calibrate_high_y, robot_ground_z + delta_z)

    #tilt is in mm per z-increase
    cam_tilt_x_mm = float((calibrate_high_x - calibrate_x) / delta_z)
    cam_tilt_y_mm = float((calibrate_high_y - calibrate_y) / delta_z)

    print(cam_tilt_x_mm, cam_tilt_y_mm)

    print(f"CALIBRATED SETTINGS:")
    print(f"cam_offset_x={cam_offset_x}")
    print(f"cam_offset_y={cam_offset_y}")
    print(f"cam_tilt_x_mm={cam_tilt_x_mm}")
    print(f"cam_tilt_y_mm={cam_tilt_y_mm}")
    print(f"cam_tilt_base={robot_ground_z}")
