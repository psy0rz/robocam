import asyncio

import cv2

import detector
from config import robot_middle_x, robot_middle_y, robot_ground_z, cam_approx_offset_x, cam_approx_offset_y, cam_lag_s
# from calulate import cam_angle, cam_position
from dobot.dobotfun.dobotfun import DobotFun

cam_center_x_pixels = 320
cam_center_y_pixels = 240


async def task():
    cv2.namedWindow("Calibrate offsets", flags=cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)
    robot = DobotFun()

    print("PLEASE MOVE THE SQUARE PERFECTLY UNDER THE SUCKION CUP...")
    robot.move_to(robot_middle_x, robot_middle_y, robot_ground_z, r=90)
    await asyncio.sleep(5)

    calibrate_x = robot_middle_x - cam_approx_offset_x
    calibrate_y = robot_middle_y - cam_approx_offset_y
    robot.move_to(calibrate_x, calibrate_y, robot_ground_z, r=90)


    await asyncio.sleep(cam_lag_s)

    while True:
        await  detector.result_ready.wait()

        if detector.result_frame is None:
            continue

        output_frame = detector.result_frame.copy()

        boxes = detector.result.boxes.xyxy
        if len(boxes) != 1:
            pass
            # print(f"Error, incorrect number of boxes detected"
            #       f": {len(boxes)}")
        else:

            (x1, y1, x2, y2) = boxes[0]
            x1 = int(x1)
            y1 = int(y1)
            x2 = int(x2)
            y2 = int(y2)

            w = abs(x2 - x1)
            h = abs(y2 - y1)

            detected_center_x = int((x1 + x2) / 2)
            detected_center_y = int((y1 + y2) / 2)

            cv2.circle(output_frame, (detected_center_x, detected_center_y), 5, (0, 0, 255), 2, cv2.LINE_AA)
            cv2.circle(output_frame, (cam_center_x_pixels, cam_center_y_pixels), 7, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.rectangle(output_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

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


            if div_x_pixels == 0 and div_y_pixels == 0:
                print(f"CALIBRATED SETTINGS:")
                print(f"cam_offset_x={cam_offset_x}")
                print(f"cam_offset_y={cam_offset_y}")

                #move back to square so user can tune it if needed
                robot.move_to(robot_middle_x, robot_middle_y, robot_ground_z, r=90)
                await asyncio.sleep(1)
                robot.move_to(calibrate_x, calibrate_y, robot_ground_z, r=90)
                await asyncio.sleep(cam_lag_s)

        cv2.imshow("Calibrate offsets", output_frame)



