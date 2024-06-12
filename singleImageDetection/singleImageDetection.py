"""
This file is used for testing YOLO detection capabilities on a single image
"""

from ultralytics import YOLO
import cv2
import matplotlib.pyplot as plt
import numpy as np

# Load model
model = YOLO('best.pt')

# Load image
image_path = 'testImages/3.jpg'
image = cv2.imread(image_path)
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Use Gaussian Blur
# blurred_image = cv2.GaussianBlur(image, (7, 7), 0)

# Make prediction
results = model.predict(image)

# Show results
for result in results:
    for box in result.boxes:
        x1, y1, x2, y2 = int(box.xyxy[0][0]), int(box.xyxy[0][1]), int(box.xyxy[0][2]), int(box.xyxy[0][3])
        confidence = box.conf[0]
        class_id = int(box.cls[0])

        # Cutting ROI for color check
        roi = image[y1:y2, x1:x2]

        # Checking ROI average color
        avg_color_per_row = np.average(roi, axis=0)
        avg_color = np.average(avg_color_per_row, axis=0)
        red_avg, green_avg, blue_avg = avg_color

        # If amount of red exceeds threshold
        if red_avg >= 240 and red_avg > green_avg and red_avg > blue_avg:
            # Draw rectangle around detected object
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(image, f'{model.names[class_id]}: {confidence:.2f}', (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

# Show image with prediction
plt.imshow(image)
plt.axis('off')
plt.show()
