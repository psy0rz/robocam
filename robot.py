import cv2
import numpy as np
from PyQt5.QtCore import center

import detector

def draw_corner_lines(img, pt1, pt2, color, thickness, line_length):
    x1, y1 = pt1
    x2, y2 = pt2

    # Calculate corner points for small line segments
    # Top-left corner horizontal and vertical lines
    cv2.line(img, (x1, y1), (x1 + line_length, y1), color, thickness,)
    cv2.line(img, (x1, y1), (x1, y1 + line_length), color, thickness)

    # Top-right corner horizontal and vertical lines
    cv2.line(img, (x2, y1), (x2 - line_length, y1), color, thickness)
    cv2.line(img, (x2, y1), (x2, y1 + line_length), color, thickness)

    # Bottom-left corner horizontal and vertical lines
    cv2.line(img, (x1, y2), (x1 + line_length, y2), color, thickness)
    cv2.line(img, (x1, y2), (x1, y2 - line_length), color, thickness)

    # Bottom-right corner horizontal and vertical lines
    cv2.line(img, (x2, y2), (x2 - line_length, y2), color, thickness)
    cv2.line(img, (x2, y2), (x2, y2 - line_length), color, thickness)


def draw_target_cross(img, center, color, thickness, line_length):
    # Draw horizontal line
    cv2.line(img, (center[0] - line_length, center[1]), (center[0] + line_length, center[1]), color, thickness)

    # Draw vertical line
    cv2.line(img, (center[0], center[1] - line_length), (center[0], center[1] + line_length), color, thickness)

def distance_between_points(point1, point2):
    # Convert points to NumPy arrays (OpenCV works well with NumPy)
    point1 = np.array(point1, dtype=np.float32)
    point2 = np.array(point2, dtype=np.float32)

    # Calculate the Euclidean distance using OpenCV
    distance = cv2.norm(point1, point2, cv2.NORM_L2)
    return distance


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


    while True:
        await  detector.result_ready.wait()

        output_frame = detector.result_frame.copy()
        if detector.result_frame is None:
            continue

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
                if distance_between_points( last_clicked, (center_x,center_y)) < distance_between_points(last_clicked, closest_point):
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
            draw_corner_lines(output_frame,(sample_x1, sample_y1), (sample_x2, sample_y2), [255, 255, 255],1, 5 )

            #color label
            # cv2.rectangle(output_frame, (x1, y1), (x1 + 80, y1 - 12), [255, 0, 0], lineType=cv2.LINE_AA, thickness=-1)
            # cv2.putText(output_frame, f" r{average_color[2]:.0f} g{average_color[1]:.0f} b{average_color[0]:.0f}",
            #             (x1, y1-2), cv2.FONT_HERSHEY_SIMPLEX,
            #             0.3, color=[255, 255, 255], thickness=1, lineType=cv2.LINE_AA)

            #this is the one we track?
            if detector.result.boxes.id is not None and tracking_id==detector.result.boxes.id[id_nr]:
                tracking_center=(center_x, center_y)


            id_nr=id_nr+1

        draw_target_cross(output_frame, tracking_center, (0,0,255), 1,1000)


        if closest_id!=-1:
            tracking_id=closest_id

        last_clicked[0]=None
        cv2.imshow('Robot', output_frame)
        cv2.setMouseCallback('Robot', click_event)
