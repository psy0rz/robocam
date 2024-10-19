import cv2
import numpy as np
import math

# Open the camera
cap = cv2.VideoCapture(0)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        break

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply GaussianBlur to reduce noise and improve edge detection
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply median blur to further reduce noise while preserving edges
    blurred = cv2.medianBlur(blurred, 5)

    # Use Canny Edge Detection to find edges
    edges = cv2.Canny(blurred, 30, 100)

    # Apply morphological operations to clean up the edges
    kernel = np.ones((3, 3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)
    edges = cv2.erode(edges, kernel, iterations=1)

    # Find contours externally
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Loop over the contours to detect squares
    for contour in contours:
        # Filter contours by area to reduce false positives
        area = cv2.contourArea(contour)
        if area < 1000:
            continue

        # Approximate the contour to a polygon
        epsilon = 0.04 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # Check if the polygon has 4 sides (i.e., it's a quadrilateral)
        if len(approx) == 4:
            # Create a mask for the detected quadrilateral
            mask = np.zeros_like(frame)
            cv2.drawContours(mask, [approx], 0, (255, 255, 255), -1)

            # Extract the region of interest using the mask
            roi = cv2.bitwise_and(frame, mask)

            # Convert the ROI to HSV for color detection
            roi_hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

            # Calculate the average color in the ROI
            mask_gray = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
            mean_color = cv2.mean(roi_hsv, mask=mask_gray)

            # Define color ranges (example for red, green, blue)
            colors = {
                'red': [(0, 120, 70), (10, 255, 255)],
                'green': [(40, 40, 40), (80, 255, 255)],
                'blue': [(100, 150, 0), (140, 255, 255)]
            }

            # Check the color of the detected cube
            detected_color = "unknown"
            for color, (lower, upper) in colors.items():
                lower = np.array(lower)
                upper = np.array(upper)
                mask = cv2.inRange(roi_hsv, lower, upper)
                if cv2.countNonZero(mask) > 0:
                    detected_color = color
                    break

            # Calculate the centroid of the contour to display color text
            M = cv2.moments(contour)
            if M['m00'] != 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                color_values_text = f"{detected_color} (H: {int(mean_color[0])}, S: {int(mean_color[1])}, V: {int(mean_color[2])})"
                cv2.putText(frame, color_values_text, (cx, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            # Draw the detected cube on the original frame with width 1
            cv2.drawContours(frame, [approx], 0, (0, 255, 0), 1)

            # Draw the centroid point of the detected cube with width 1
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), 1)

            # Calculate the angle of rotation of the detected quadrilateral
            # Using the first two points of the approximated polygon
            if len(approx) >= 2:
                (x1, y1) = approx[0][0]
                (x2, y2) = approx[1][0]
                angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
                # Draw a line to represent the angle direction
                line_length = 50
                end_x = int(cx + line_length * math.cos(math.radians(angle)))
                end_y = int(cy + line_length * math.sin(math.radians(angle)))
                cv2.line(frame, (cx, cy), (end_x, end_y), (0, 0, 255), 1)

    # Display the output
    cv2.imshow('Detected Cubes', frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close windows
cap.release()
cv2.destroyAllWindows()
