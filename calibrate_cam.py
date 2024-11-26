import asyncio

import cv2

import config
import detector
from calculate import get_pix_per_mm_for_camera_height
from calibrate import place_cube, center_cube, get_cube
from config import robot_middle_x, robot_middle_y, robot_ground_z, cam_lag_s, cam_center_x_pixels, \
    calibration_box_height
from dobot.dobotfun.dobotfun import DobotFun



async def task():
    robot = DobotFun()

    detector.confidence=0.9

    await place_cube(robot)


    low_z = robot_ground_z+20
    low_x_move=12
    delta_z = 100

    high_z = low_z + delta_z
    high_x_move=12

    calibrate_x = robot_middle_x - config.cam_offset_x
    calibrate_y = robot_middle_y - config.cam_offset_y

    ## LOW

    #make sure robot is exactly on cube:
    robot.move_to(calibrate_x, calibrate_y, low_z, r=90)
    # await center_cube(robot, calibrate_x, calibrate_y, low_z)

    #move and get pix per mm
    robot.move_to(calibrate_x+low_x_move, calibrate_y, low_z, r=90)
    await asyncio.sleep(1)
    output_frame, width, height, center_x_pixels, center_y_pixels_top=await get_cube()

    robot.move_to(calibrate_x-low_x_move, calibrate_y, low_z, r=90)
    await asyncio.sleep(1)
    output_frame, width, height, center_x_pixels, center_y_pixels_bottom=await get_cube()

    #NOTE: robot and screen x,y are swapped
    config.low_x_pix_per_mm = (-center_y_pixels_bottom+center_y_pixels_top)/(low_x_move*2)
    print(f"low_x_pix_per_mm = {config.low_x_pix_per_mm:0.2f} pixels/mm")


    ## HIGH
    robot.move_to(calibrate_x, calibrate_y, high_z, r=90)
    # await center_cube(robot, calibrate_x, calibrate_y, high_z)


    #move and get pix per mm
    robot.move_to(calibrate_x+high_x_move, calibrate_y, high_z, r=90)
    await asyncio.sleep(1)
    output_frame, width, height, center_x_pixels, center_y_pixels_top=await get_cube()

    robot.move_to(calibrate_x-high_x_move, calibrate_y, high_z, r=90)
    await asyncio.sleep(1)
    output_frame, width, height, center_x_pixels, center_y_pixels_bottom=await get_cube()

    #NOTE: robot and screen x,y are swapped
    high_x_pix_per_mm = (-center_y_pixels_bottom+center_y_pixels_top)/(low_x_move*2)
    print(f"high_x_pix_per_mm = {high_x_pix_per_mm:0.2f} pixels/mm")

    config.low_cam_height = (delta_z * high_x_pix_per_mm) / (config.low_x_pix_per_mm - high_x_pix_per_mm)
    print(f"low_cam_height = {config.low_cam_height:0.2f} mm")
    #68.09

    config.cam_offset_z = config.low_cam_height - low_z + config.calibration_box_height
    print(f"cam_z_offset = {config.cam_offset_z} mm")

    print("CALIBRATED SETTINGS:")
    print(f"cam_offset_z={config.cam_offset_z}")
    print(f"low_cam_height={config.low_cam_height}")
    print(f"low_x_pix_per_mm={config.low_x_pix_per_mm}")

    ### test
    print("TESTING")

    for z in range(robot_ground_z, 170, 25):
        robot.move_to(calibrate_x, calibrate_y, z, r=90)
        await asyncio.sleep(1)
        output_frame, width, height, center_x_pixels, center_y_pixels_top = await get_cube()
        pix_per_mm = get_pix_per_mm_for_camera_height(z-calibration_box_height)


        w_mm = height / pix_per_mm
        print(f"z={z}, cube-width={w_mm:.2f} mm, {height}")





