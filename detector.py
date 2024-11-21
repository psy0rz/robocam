import asyncio
import sys
from asyncio import Event

import cv2
from ultralytics import YOLO

result=None
result_frame=None
result_ready=Event()


frame_delay=0


async def task():
    global result
    global result_frame

    cv2.namedWindow("YOLO Inference", flags=cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)

    print("Loading model...")
    # trained on yolo11l-obb.pt LARGE
    # model = YOLO("./runs/obb/train23/weights/best.pt")
    # trained on yolo11n-obb.pt small
    # model = YOLO("./runs/obb/train24/weights/best.pt")
    # trained on yolo11n.pt small, zonder rotate
    model = YOLO("./runs/detect/train/weights/best.pt")

    # model = YOLO("./runs/obb/train34/weights/best.pt")



    print("Loading model done.")

    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1088)

    # Loop through the video frames
    # cap = cv2.VideoCapture(0)
    cap=None
    for cam_nr in range(4,-1,-1):
            print(f"Trying cam {cam_nr}")
            cap = cv2.VideoCapture(cam_nr)
            if cap.isOpened():
                break

    if not cap.isOpened():
        print("NO CAMS FOUND")
        sys.exit(1)


    try:
        while True:
            # Read a frame from the video
            success, frame = cap.read()

            if success:
                # Run YOLO inference on the frame
                # results = model.predict(frame, imgsz=(1920,1088), conf=0.8)
                # results = model.track(frame, conf=0.5, persist=True, verbose=False)
                results = model.track(frame, conf=0.8, persist=True, verbose=False)

                # Visualize the results on the frame
                annotated_frame = results[0].plot(line_width=1)

                result=results[0]
                result_frame=frame
                result_ready.set()
                result_ready.clear()


                # Display the annotated frame
                cv2.putText(annotated_frame,f"{int(results[0].speed['inference'])} mS", (10,30),cv2.FONT_HERSHEY_SIMPLEX, 0.8, color=[0,200,00], thickness=2, lineType=cv2.LINE_AA)
                cv2.imshow("YOLO Inference", annotated_frame)


                cv2.waitKey(1)
                # Break the loop if 'q' is pressed
                # if cv2.waitKey(1) & 0xFF == ord("q"):
                #     break
            else:
                # Break the loop if the end of the video is reached
                print("Failed to capture frame")

            await asyncio.sleep(frame_delay)
    finally:
       cap.release()


