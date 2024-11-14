import asyncio
from asyncio import Event

import cv2
from ultralytics import YOLO

result=None
result_frame=None
result_ready=Event()


async def task():
    global result
    global result_frame

    print("Loading model...")
    # trained on yolo11l-obb.pt LARGE
    # model = YOLO("/app/runs/obb/train23/weights/best.pt")
    # trained on yolo11n-obb.pt small
    # model = YOLO("/app/runs/obb/train24/weights/best.pt")
    # trained on yolo11n.pt small, zonder rotate
    model = YOLO("./runs/detect/train/weights/best.pt", verbose=True)
    print("DONE")

    cap = cv2.VideoCapture(0)
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1088)

    # Loop through the video frames
    try:
        while True:
            # Read a frame from the video
            success, frame = cap.read()

            if success:
                # Run YOLO inference on the frame
                # results = model.predict(frame, imgsz=(1920,1088), conf=0.8)
                results = model.track(frame, conf=0.10, persist=True, verbose=False)

                # Visualize the results on the frame
                annotated_frame = results[0].plot(line_width=1)

                result=results[0]
                result_frame=frame
                result_ready.set()
                result_ready.clear()

                # Display the annotated frame
                cv2.imshow("YOLO Inference", annotated_frame)


                cv2.waitKey(1)
                # Break the loop if 'q' is pressed
                # if cv2.waitKey(1) & 0xFF == ord("q"):
                #     break
            else:
                # Break the loop if the end of the video is reached
                print("Failed to capture frame")

            await asyncio.sleep(0)
    except asyncio.CancelledError:
       cap.release()



# task=asyncio.create_task(loop())

# def on_unload():
#
#     # Release the video capture object and close the display window
#     # task.cancel()
#     cap.release()

