# trainen met:
#yolo obb train data=/home/psy/datasets/cubes/data.yaml model=yolo11l-obb.pt  epochs=100 imgsz=640
import paho.mqtt.client as mqtt


from ultralytics import YOLO
from PIL import Image
import cv2
import json

model = YOLO("/app/runs/obb/train23/weights/best.pt")

import cv2
from ultralytics import YOLO


# Open the video file
#usb
cap = cv2.VideoCapture(4)

# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1088)


client = mqtt.Client()

# Connect to the broker
client.connect('localhost')

# Publish a message to the topic
def publish(middles):
    client.publish("middles", middles)


# Loop through the video frames
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()

    if success:
        # Run YOLO inference on the frame
        # results = model.predict(frame, imgsz=(1920,1088), conf=0.8)
        results = model.predict(frame, conf=0.8)


        # Visualize the results on the frame
        annotated_frame = results[0].plot(line_width=1)

        # print(results[0].obb)
        middles=[]
        for xyxyxyxy in results[0].obb.xyxyxyxy:
            (x1,y1)=xyxyxyxy[0]
            (x2,y2)=xyxyxyxy[1]
            (x3,y3)=xyxyxyxy[2]
            (x4,y4)=xyxyxyxy[3]
            x1=int(x1)
            y1=int(y1)
            x2=int(x2)
            y2=int(y2)
            x3=int(x3)
            y3=int(y3)
            x4=int(x4)
            y4=int(y4)
            # cv2.rectangle(annotated_frame, (x1,y1), (x2,y2), [255,255,255])
            
            center_x = int((x1 + x2 + x3 + x4) / 4)
            center_y = int((y1 + y2 + y3 + y4) / 4)
            cv2.circle(annotated_frame, (center_x, center_y), 5, (0, 0, 255), -1)  # Red filled circle
            middles.append([center_x, center_y])

        # Display the annotated frame
        cv2.imshow("YOLO Inference", annotated_frame)

        # print(json.dumps(middles))
        publish(json.dumps(middles))

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        # Break the loop if the end of the video is reached
        break

# Release the video capture object and close the display window
cap.release()
# cv2.destroyAllWindows()
#
# # Define VideoCapture Object from OpenCV
# vidcap = cv2.VideoCapture(0)
#
# # Set the streaming resolution
# # vidcap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
# # vidcap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
#
# # Read the first input frame
# suc, img = vidcap.read()
#
# while suc:
#     # Predict the image img from the stream
#     results = model.predict(img,
#                             # conf=0.8,
#                             # iou=0.6,
#                             show=True, line_width=1
#                              )
#     # read the next frame, if it exists
#     suc, img = vidcap.read()
#     # cv2.imshow('Video', img)
#     cv2.waitKey(1)
#
# # Release the stream and destroy all OpenCV windows.
# vidcap.release()
# cv2.destroyAllWindows()
# #
#
# for result in model(source=1, stream=True, show=True,imgsz=(1280, 1024)):
#
#     pass#print(result.orign)
#
#     # for i, r in enumerate(results):
#     # Plot results image
#     # im_bgr = results[0].plot()  # BGR-order numpy array
#     # im_rgb = Image.fromarray(im_bgr[..., ::-1])  # RGB-order PIL image
#     # results[0].show()
#
#     # cv2.imshow('res', im_rgb)
#
# #     cv2.imshow('bla',frame)
#
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
# capture.release()
# cv2.destroyAllWindows()
