import cv2

import detector


async def task():


    while True:
        await  detector.result_ready.wait()

        output_frame=detector.result_frame

        # center_x=detector.result.orig_shape[0]
        print(detector.result.orig_shape)

        # print(detector.result)
        middles = []
        for r in detector.result.boxes.xyxy:
            # cv2.rectangle()
            (x1, y1, x2, y2) = r
            x1 = int(x1)
            y1 = int(y1)
            x2 = int(x2)
            y2 = int(y2)



            # cv2.rectangle(annotated_frame, (x1,y1), (x2,y2), [255,255,255])

            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)
            # cv2.circle(output_frame, (center_x, center_y), 5, (0, 0, 255), -1)  # Red filled circle
            middles.append([center_x, center_y])

        cv2.imshow('Robot', output_frame)
