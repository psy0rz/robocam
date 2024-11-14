# trainen met:
# yolo obb train data=/home/psy/datasets/cubes/data.yaml model=yolo11l-obb.pt  epochs=100 imgsz=640
# import paho.mqtt.client as mqtt
import asyncio

from ultralytics import YOLO
from PIL import Image
import cv2
import json

# trained on yolo11l-obb.pt LARGE
# model = YOLO("/app/runs/obb/train23/weights/best.pt")
# trained on yolo11n-obb.pt small
# model = YOLO("/app/runs/obb/train24/weights/best.pt")

# trained on yolo11n.pt small, zonder rotate
print("Loading model...")
model = YOLO("./runs/detect/train/weights/best.pt", verbose=True)

print ("DONE")
import cv2

cap = cv2.VideoCapture(0)

# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1088)

async def loop():

    # Loop through the video frames
    while cap.isOpened():
        # Read a frame from the video
        success, frame = cap.read()

        if success:
            # Run YOLO inference on the frame
            # results = model.predict(frame, imgsz=(1920,1088), conf=0.8)
            results = model.track(frame, conf=0.70, persist=True, verbose=False)

            # Visualize the results on the frame
            annotated_frame = results[0].plot(line_width=1)

            # print(results[0].boxes)
            middles = []
            for r in results[0].boxes.xyxy:
                (x1, y1, x2, y2) = r
                x1 = int(x1)
                y1 = int(y1)
                x2 = int(x2)
                y2 = int(y2)
                # cv2.rectangle(annotated_frame, (x1,y1), (x2,y2), [255,255,255])

                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)
                cv2.circle(annotated_frame, (center_x, center_y), 5, (0, 0, 255), -1)  # Red filled circle
                middles.append([center_x, center_y])

            # Display the annotated frame
            cv2.imshow("YOLO Inference", annotated_frame)

            # print(json.dumps(middles))
            # publish(json.dumps(middles))

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        else:
            # Break the loop if the end of the video is reached
            break
        await asyncio.sleep(0)

task=asyncio.create_task(loop())

def on_unload():

    # Release the video capture object and close the display window
    task.cancel()
    cap.release()
