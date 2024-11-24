
import cv2

import detector

# wait for exactly one calibration box to be detected
# return: output_frame, width, height, center_x, center_y
async def get_box():
    cv2.namedWindow("Calibrate", flags=cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)
    while True:
        await detector.result_ready.wait()
        output_frame = detector.result_frame.copy()

        boxes = detector.result.boxes.xyxy
        if detector.result_frame is not None and len(boxes) == 1:
            (x1, y1, x2, y2) = boxes[0]

            w = abs(x2 - x1)
            h = abs(y2 - y1)

            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2

            x1 = int(x1)
            y1 = int(y1)
            x2 = int(x2)
            y2 = int(y2)
            cv2.rectangle(output_frame, (x1, y1), (x2, y2), (0, 255, 0), 1)



            return output_frame, w, h, center_x, center_y
        else:
            cv2.putText(output_frame, f"Waiting for exactly one calibration box",
                        (10,20), cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, color=[0,0, 255], thickness=2, lineType=cv2.LINE_AA)


            cv2.imshow("Calibrate", output_frame)
            cv2.waitKey(1)
