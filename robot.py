import math

import cv2
import numpy as np

import detector
from calulate import cam_angle, cam_position
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
        robot_x = mouse_clicked[0]
        robot_y = mouse_clicked[1]

        center = cam_position((robot_x, robot_y))
        angle = cam_angle((robot_x, robot_y))

        cv2.putText(output_frame, f"robot={robot_x, robot_y}",
                    (screen_center_x,screen_center_y+100), cv2.FONT_HERSHEY_SIMPLEX,
                    0.3, color=[255, 255, 255], thickness=1, lineType=cv2.LINE_AA)


        cv2.putText(output_frame, f"cam={center} {math.degrees(angle):.1f} degrees",
                    (screen_center_x+10, screen_center_y), cv2.FONT_HERSHEY_SIMPLEX,
                    0.3, color=[255, 255, 255], thickness=1, lineType=cv2.LINE_AA)

        # robot_x=100
        # robot_y=150

        #

        # center of the current image

        # caculate the on screen location from real coordinates
        def real_to_pixels(cam_center, cam_angle, robot_pos):

            # offset from camera center (real coords)
            offset = (robot_pos[0] - cam_center[0], robot_pos[1] - cam_center[1])

            # convert to pixels
            factor=4
            offset_pixels=(offset[0]*factor, offset[1]*factor)

            #absolute pixel coords
            pixel_coord=( int(screen_center_x+offset_pixels[0]), int(screen_center_y+offset_pixels[1]))

            return pixel_coord


        def draw_grid(cam_center, cam_angle):
            #FIX: angle

            step=10

            start_x=round(cam_center[0],-1)-50
            end_x=round(cam_center[0],-1)+50

            start_y=round(cam_center[1],-1)-50
            end_y=round(cam_center[1],-1)+50

            for x in range(start_x, end_x, step):
                screen_coord_start=real_to_pixels(cam_center, cam_angle, (x,start_y))
                screen_coord_end=real_to_pixels(cam_center, cam_angle, (x,end_y-step))
                cv2.line(output_frame, screen_coord_start, screen_coord_end, (0, 255,0), 1)

            for y in range(start_y, end_y, step):
                screen_coord_start = real_to_pixels(cam_center, cam_angle, (start_x, y))
                screen_coord_end = real_to_pixels(cam_center, cam_angle, (end_x-step, y))
                cv2.line(output_frame, screen_coord_start, screen_coord_end, (0, 255, 0), 1)

        draw_grid(center, angle)


    #show robot arm position
        cv2.circle(output_frame, real_to_pixels(center, angle, (robot_x,robot_y)), 15, (0, 255,0), 1, cv2.LINE_AA)

        # simulated robot arm (top left click line thingy)
        cv2.line(output_frame, (0, 0), (robot_x, robot_y), (255, 255, 255), 4)
        cv2.line(output_frame, (0, 0), cam_position((robot_x, robot_y)), (0, 0, 255), 1)

        cv2.imshow('Robot', output_frame)
        cv2.setMouseCallback('Robot', click_event)





        # print(cam_angle(mouse_clicked))
