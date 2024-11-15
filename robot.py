import cv2
import numpy as np

import detector
from util import draw_corner_lines, draw_target_cross, distance_between_points

# Callback function for mouse click event

last_clicked = [None, None]


class Selector:
    # can search for a new object close to x,y,color, and keep tracking the ID when it has found one
    def __init__(self):
        # search for a new object
        self.search_point = None
        self.search_color = None

        # current object
        self.track_id = None
        self.current_point = (0,0)
        self.color = None

    def update(self, point, color, id):
        if (self.search_point is not None
                and distance_between_points(point, self.search_point) < distance_between_points(point,
                                                                                                self.current_point)):
            self.color = color
            self.track_id = id

        #update position
        if id==self.track_id:
            self.current_point = point


        pass


selector = Selector()


def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:  # Left mouse button click
        print(f"Mouse clicked at position ({x}, {y})")
        selector.search_point = (x, y)


async def task():
    cv2.namedWindow("Robot", flags=cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)

    while True:
        await  detector.result_ready.wait()

        if detector.result_frame is None:
            continue

        output_frame = detector.result_frame.copy()

        # camera center
        cam_center_x = int(detector.result.orig_shape[1] / 2)
        cam_center_y = int(detector.result.orig_shape[0] / 2)

        if selector.search_point is None:
            selector.search_point=(cam_center_x, cam_center_y)

        # print(detector.result.boxes.id)

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

            # normal yolo outline
            draw_corner_lines(output_frame, (x1, y1), (x2, y2), (0, 0, 0), 1, 5)

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

            # color box
            cv2.rectangle(output_frame, (sample_x1, sample_y1), (sample_x2, sample_y2), average_color,
                          lineType=cv2.LINE_AA, thickness=-1)

            # cv2.rectangle(output_frame, (sample_x1, sample_y1), (sample_x2, sample_y2), [255, 255, 255],
            #               lineType=cv2.LINE_AA, thickness=1)
            draw_corner_lines(output_frame, (sample_x1, sample_y1), (sample_x2, sample_y2), [255, 255, 255], 1, 5)

            # color label
            # cv2.rectangle(output_frame, (x1, y1), (x1 + 80, y1 - 12), [255, 0, 0], lineType=cv2.LINE_AA, thickness=-1)
            # cv2.putText(output_frame, f" r{average_color[2]:.0f} g{average_color[1]:.0f} b{average_color[0]:.0f}",
            #             (x1, y1-2), cv2.FONT_HERSHEY_SIMPLEX,
            #             0.3, color=[255, 255, 255], thickness=1, lineType=cv2.LINE_AA)

            # this is the one we track?
            # if detector.result.boxes.id is not None and tracking_id == detector.result.boxes.id[id_nr]:
            #     tracking_center = (center_x, center_y)

            if detector.result.boxes.id is not None:
                id=detector.result.boxes.id[id_nr]
                selector.update((center_x, center_y), average_color, id)

            id_nr = id_nr + 1

        cv2.circle(output_frame, selector.search_point, 5, (255, 255, 255), 1, cv2.LINE_AA)

        draw_target_cross(output_frame, selector.current_point, (50, 50, 255), 1, 1000)

        last_clicked[0] = None
        cv2.imshow('Robot', output_frame)
        cv2.setMouseCallback('Robot', click_event)
