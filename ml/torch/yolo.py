"""
This file contains YOLO class used for object detection
"""

from ml import detector as d
from ultralytics import YOLO as y
import numpy as np


class YOLO(d.Detector):
    def __init__(self, shared_variables):
        self.shared_variables = shared_variables

    def download_model(self):
        pass

    def load_model(self):
        # Load model
        self.model = y('best.pt')
        self.shared_variables.detection_ready = True

    def predict(self):
        # Receives image for further predictions
        image = self.shared_variables.OutputFrame

        # Performs prediction
        results = self.model.predict(image)

        # Access detected objects and their attributes
        detected_objects = []

        for obj in results:
            classes = obj.names
            for i in range(len(obj.boxes.cls.tolist())):
                _box = obj.boxes.xywhn.tolist()[i]

                # Convert normalized coordinates to actual image coordinates
                h, w, _ = image.shape
                x1 = int((_box[0] - _box[2] / 2) * w)
                y1 = int((_box[1] - _box[3] / 2) * h)
                x2 = int((_box[0] + _box[2] / 2) * w)
                y2 = int((_box[1] + _box[3] / 2) * h)

                box = (_box[0], _box[1], _box[2], _box[3])

                score = obj.boxes.conf.tolist()[i]
                classification = obj.boxes.cls.tolist()[i]

                __box = obj.boxes.xywh.tolist()[i]

                # Apply filters
                if len(self.shared_variables.SHOW_ONLY) > 0:
                    # Check if precision is more than predefined threshold
                    if score >= self.shared_variables.PRECISION:
                        if classes[classification] in self.shared_variables.SHOW_ONLY:
                            if __box[2] * __box[3] <= self.shared_variables.MAX_BOX_AREA:
                                # Extract ROI
                                roi = image[y1:y2, x1:x2]

                                # Check average color of ROI
                                avg_color_per_row = np.average(roi, axis=0)
                                avg_color = np.average(avg_color_per_row, axis=0)
                                red_avg, green_avg, blue_avg = avg_color

                                # Check if the average red color exceeds a predefined threshold
                                if (red_avg >= self.shared_variables.RED_NUMBER
                                        and red_avg > green_avg
                                        and red_avg > blue_avg):
                                    detected_objects.append((score, classes[classification], box))

                else:
                    # Check if precision is more than predefined threshold
                    if score > self.shared_variables.PRECISION:
                        if __box[2] * __box[3] <= self.shared_variables.MAX_BOX_AREA:
                            # Extract ROI
                            roi = image[y1:y2, x1:x2]

                            # Check average color of ROI
                            avg_color_per_row = np.average(roi, axis=0)
                            avg_color = np.average(avg_color_per_row, axis=0)
                            red_avg, green_avg, blue_avg = avg_color

                            # Check if the average red color exceeds a predefined threshold
                            if (red_avg >= self.shared_variables.RED_NUMBER
                                    and red_avg > green_avg
                                    and red_avg > blue_avg):
                                detected_objects.append((score, classes[classification], box))

        return detected_objects
