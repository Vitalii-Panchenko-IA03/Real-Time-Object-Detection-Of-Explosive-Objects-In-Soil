"""
This file contains a shared variables class and a mss screen stream capture class
"""
from mss import mss
from PIL import Image
from threading import Thread
from ml.torch.yolo import YOLO

import numpy as np
import cv2
import time
import logging


# Global shared variables
# an instance of this class share variables between system threads
class SharedVariables:
    model = YOLO

    tracking_boxes = []
    _initialized = 0
    OFFSET = (0, 0)
    WIDTH, HEIGHT = 1920, 1080  # 2560, 1440
    detection_ready = False
    category_index = None
    OutputFrame = None
    frame = None
    boxes = None
    category_list = []
    category_max = None
    stream_running = True
    detection_running = True
    list = []
    DETECTION_SIZE = 640
    DETECTION_SCALE = 0
    RED_NUMBER = 240

    def __init__(self):
        Thread.__init__(self)
        self._initialized = 1
        ScreenStreamer(shared_variables=self).start()


class ScreenStreamer(Thread):
    def __init__(self, shared_variables=None):
        Thread.__init__(self)
        self.shared_variables = shared_variables

    # Performs downscaling
    def downscale(self, image):
        scale = None
        image_size_threshold = self.shared_variables.DETECTION_SIZE
        height, width, channel = image.shape

        if height > image_size_threshold:
            scale = height / image_size_threshold

            image = cv2.resize(image, (int(width / scale), int(height / scale)))

        return image, scale

    # Performs screen capture
    def run(self):
        sct = mss()
        monitor = {'top': self.shared_variables.OFFSET[0], 'left': self.shared_variables.OFFSET[1],
                   'width': self.shared_variables.WIDTH, 'height': self.shared_variables.HEIGHT}
        logging.info(f"MSS started with monitor : {monitor}")

        while self.shared_variables.stream_running:
            if self.shared_variables.detection_ready:
                img = Image.frombytes('RGB', (self.shared_variables.WIDTH, self.shared_variables.HEIGHT),
                                      sct.grab(monitor).rgb)
                self.shared_variables.OutputFrame, self.shared_variables.DETECTION_SCALE = self.downscale(np.array(img))
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    cv2.destroyAllWindows()
                    break
            else:
                time.sleep(0.1)
