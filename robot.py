import cv2
import numpy as np

import detector
from util import draw_corner_lines, draw_target_cross, distance_between_points

# Callback function for mouse click event

last_clicked=[None,None]
def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:  # Left mouse button click
        print(f"Mouse clicked at position ({x}, {y})")
        last_clicked[0]=x
        last_clicked[1]=y


async def task():

    tracking_id=0
    tracking_center=(-1,-1)

    cv2.namedWindow("Robot", flags=cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)


    while True:
        await  detector.result_ready.wait()

        if detector.result_frame is None:
            continue

        output_frame = detector.result_frame.copy()

        # camera center
        cam_center_x = int(detector.result.orig_shape[1] / 2)
        cam_center_y = int(detector.result.orig_shape[0] / 2)
        cv2.circle(output_frame, (cam_center_x, cam_center_y), 5, (255, 255, 255), 1, cv2.LINE_AA)

        # print(detector.result.boxes.id)

        # find closed to lastclicked
        closest_id = -1
        closest_point = (-10000, -10000)

        middles = []
        id_nr=0
        # print (detector.result.obb)
        # for xyxy in detector.result.boxes.xyxy:
        for xyxy in detector.result.boxes.xyxy:
            # cv2.rectangle()
            (x1, y1, x2, y2) = xyxy
            x1 = int(x1)
            y1 = int(y1)
            x2 = int(x2)
            y2 = int(y2)

            w = abs(x2 - x1)
            h = abs(y2 - y1)

            #normal yolo outline
            draw_corner_lines(output_frame, (x1, y1), (x2, y2), (0, 0, 0), 1, 5)

            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)
            middles.append([center_x, center_y])

            if last_clicked[0] is not None:
                if distance_between_points(last_clicked, (center_x, center_y)) < distance_between_points(last_clicked, closest_point):
                    closest_point=(center_x,center_y)
                    closest_id=detector.result.boxes.id[id_nr]


            # determine color sampling region
            sample_x1 = int(center_x - w / 4)
            sample_x2 = int(center_x + w / 4)
            sample_y1 = int(center_y - h / 4)
            sample_y2 = int(center_y + h / 4)

            # average color of this region
            sample_image = detector.result_frame[sample_y1:sample_y2, sample_x1:sample_x2]
            average_color = np.mean(sample_image, axis=(0, 1))
            # print(average_color)

            # color box
            cv2.rectangle(output_frame, (sample_x1, sample_y1), (sample_x2, sample_y2), average_color,
                          lineType=cv2.LINE_AA, thickness=-1)

            # cv2.rectangle(output_frame, (sample_x1, sample_y1), (sample_x2, sample_y2), [255, 255, 255],
            #               lineType=cv2.LINE_AA, thickness=1)
            draw_corner_lines(output_frame, (sample_x1, sample_y1), (sample_x2, sample_y2), [255, 255, 255], 1, 5)

            #color label
            # cv2.rectangle(output_frame, (x1, y1), (x1 + 80, y1 - 12), [255, 0, 0], lineType=cv2.LINE_AA, thickness=-1)
            # cv2.putText(output_frame, f" r{average_color[2]:.0f} g{average_color[1]:.0f} b{average_color[0]:.0f}",
            #             (x1, y1-2), cv2.FONT_HERSHEY_SIMPLEX,
            #             0.3, color=[255, 255, 255], thickness=1, lineType=cv2.LINE_AA)

            #this is the one we track?
            if detector.result.boxes.id is not None and tracking_id==detector.result.boxes.id[id_nr]:
                tracking_center=(center_x, center_y)


            id_nr=id_nr+1

        draw_target_cross(output_frame, tracking_center, (50, 50, 255), 1, 1000)


        if closest_id!=-1:
            tracking_id=closest_id

        last_clicked[0]=None
        cv2.imshow('Robot', output_frame)
        cv2.setMouseCallback('Robot', click_event)
