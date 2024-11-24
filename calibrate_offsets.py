import asyncio

import cv2

import calibrate
import config
import detector
from calibrate import place_cube
from config import robot_middle_x, robot_middle_y, robot_ground_z, cam_lag_s, cam_tilt_x_mm
from dobot.dobotfun.dobotfun import DobotFun

cam_center_x_pixels = 320
cam_center_y_pixels = 240

robot = DobotFun()




async def task():
    detector.confidence = 0.90
    await place_cube()

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
