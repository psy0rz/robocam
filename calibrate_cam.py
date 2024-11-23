import asyncio

import cv2

import detector
from config import robot_middle_x, robot_middle_y, robot_ground_z, cam_approx_offset_x, cam_approx_offset_y, cam_lag_s, \
    calibration_square
# from calulate import cam_angle, cam_position
from dobot.dobotfun.dobotfun import DobotFun

cam_center_x_pixels = 320
cam_center_y_pixels = 240


async def task():
    cv2.namedWindow("Calibrate camera", flags=cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)
    robot = DobotFun()

    calibrate_x = robot_middle_x - cam_approx_offset_x
    calibrate_y = robot_middle_y - cam_approx_offset_y
    robot.move_to(calibrate_x, calibrate_y, robot_ground_z, r=90)

    # this much higher from robot_ground_z
    calibrate_delta_z = 100


    calibrate_z_offset = robot_ground_z
    calibrate_z_factor = 0
    # pixels per mm at ground level
    low_x_pix_per_mm = 0
    calibrate_y_pix_per_mm = 0

    async def get_w_h():
        while True:
            await detector.result_ready.wait()
            output_frame = detector.result_frame.copy()

            boxes = detector.result.boxes.xyxy
            if detector.result_frame is not None and len(boxes) == 1:
                (x1, y1, x2, y2) = boxes[0]

                w = abs(x2 - x1)
                h = abs(y2 - y1)

                x1 = int(x1)
                y1 = int(y1)
                x2 = int(x2)
                y2 = int(y2)
                cv2.rectangle(output_frame, (x1, y1), (x2, y2), (0, 255, 0), 1)

                cv2.imshow("Calibrate camera", output_frame)
                cv2.waitKey(1)

                return w, h
            else:
                print("Waiting for 1 square...")
                cv2.imshow("Calibrate camera", output_frame)
                cv2.waitKey(1)

    # get ground pix per mm

    # get ground floor calibration
    robot.move_to(calibrate_x, calibrate_y, robot_ground_z, r=90)
    await asyncio.sleep(1)
    w, h = await get_w_h()
    low_x_pix_per_mm = w / calibration_square
    print(f"x={low_x_pix_per_mm:0.2f} pixels/mm")

    # determine calibrate_z_factor by moving camera higher
    robot.move_to(calibrate_x, calibrate_y, robot_ground_z + calibrate_delta_z, r=90)
    await asyncio.sleep(1)
    w, h = await get_w_h()
    high_x_pix_per_mm = w / calibration_square
    print(f"high pix/mm={high_x_pix_per_mm:0.2f} ")


    # high_height=(calibrate_delta_z*low_x_pix_per_mm)/(low_x_pix_per_mm-high_x_pix_per_mm)
    low_cam_height=(calibrate_delta_z*high_x_pix_per_mm)/(low_x_pix_per_mm-high_x_pix_per_mm)
    print(f"low z={low_cam_height:0.2f} mm")
    # print(f"high z={high_height:0.2f} mm")

    cam_z_offset=low_cam_height-robot_ground_z
    print(f"cam_z_offset {cam_z_offset}")

    z=robot_ground_z+20
    robot.move_to(calibrate_x, calibrate_y, z , r=90)
    print(f"cam height from robot z {z+cam_z_offset}")

    return
    def get_pix_per_mm_for_z(z):
        delta_z=z-calibrate_z_offset

        z_percentage=delta_z/calibrate_delta_z
        factor= low_x_pix_per_mm + ( low_x_pix_per_mm - high_x_pix_per_mm)*z_percentage

        return factor

    # test
    print("TESTING")
    for z in range(robot_ground_z, robot_ground_z+110, 10):
        robot.move_to(calibrate_x, calibrate_y, z, r=90)
        await asyncio.sleep(1)
        w, h = await get_w_h()
        pix_per_mm=get_pix_per_mm_for_z(z)

        w_mm = w / pix_per_mm
        print(f"z={z}, width={w_mm:.2f} mm")
