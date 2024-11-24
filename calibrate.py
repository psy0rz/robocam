import asyncio

import cv2

import config
import detector
from config import cam_center_x_pixels, cam_center_y_pixels
from util import find_closest_box


def message(output_frame, text, color):
    cv2.putText(output_frame, text,
                (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
                0.8, color=color, thickness=2, lineType=cv2.LINE_AA)


# wait for an calibration box. always gets the one clost to the center
# return: output_frame, width, height, center_x, center_y
async def get_cube():
    cv2.namedWindow("Calibrate", flags=cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)
    while True:
        await detector.result_ready.wait()
        output_frame = detector.result_frame.copy()

        cv2.circle(output_frame, (cam_center_x_pixels, cam_center_y_pixels), 7, (255, 255, 255), 1, cv2.LINE_AA)

        closest = find_closest_box(detector.result.boxes, cam_center_x_pixels, cam_center_y_pixels)
        if closest is not None:
            (x1, y1, x2, y2) = closest

            w = abs(x2 - x1)
            h = abs(y2 - y1)

            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2

            x1 = int(x1)
            y1 = int(y1)
            x2 = int(x2)
            y2 = int(y2)
            cv2.rectangle(output_frame, (x1, y1), (x2, y2), (0, 255, 0), 1)

            cv2.imshow("Calibrate", output_frame)
            cv2.waitKey(1)
            return output_frame, w, h, center_x, center_y
        else:
            message(output_frame, "Waiting for calibration block", (0, 0, 255))

            cv2.imshow("Calibrate", output_frame)
            cv2.waitKey(1)



async def place_cube(robot):
    print("PLEASE MOVE THE CUBE PERFECTLY UNDER THE SUCKION CUP...")
    robot.move_to(config.robot_middle_x, config.robot_middle_y, config.robot_ground_z + config.calibration_box_height + 50, r=90)
    robot.move_to(config.robot_middle_x, config.robot_middle_y, config.robot_ground_z + config.calibration_box_height+1, r=90)
    await asyncio.sleep(5)
    robot.move_to(config.robot_middle_x, config.robot_middle_y, config.robot_ground_z + config.calibration_box_height + 50, r=90)


# moves robot around until detected cube is in the center of the screen
async def center_cube(robot,calibrate_x, calibrate_y, z):
    while True:
        await asyncio.sleep(config.cam_lag_s)
        output_frame, w, h, detected_center_x, detected_center_y = await get_cube()

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
            message(output_frame, "OK", (0, 255, 0))

            cv2.imshow("Calibrate", output_frame)
            cv2.waitKey(1)
            return calibrate_x, calibrate_y
        else:
            message(output_frame, f"Calibrating: {div_x_pixels:.1f}  , {div_y_pixels:.1f}", (0, 255, 0))

            cv2.imshow("Calibrate", output_frame)
            cv2.waitKey(1)
