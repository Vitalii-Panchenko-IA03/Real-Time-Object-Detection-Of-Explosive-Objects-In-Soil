"""
This file contains functions for showing overlay detections
"""

from utils.ThreadPool import *
from utils.tracking import Tracking

import logging


# Used to show tracking box over other screen elements
class TrackingBox(QSplashScreen):
    splash_pix = None
    done = False

    def __init__(self, id, shared_variables, score, classification, box, *args, **kwargs):
        super(TrackingBox, self).__init__(*args, **kwargs)
        self.classification = classification
        self.shared_variables = shared_variables
        self.counter = 0

        # Calculates coordinates and size of the box based on scale
        self.x = int(box[0] * (self.shared_variables.WIDTH / self.shared_variables.DETECTION_SCALE) - (
                    box[2] * (self.shared_variables.WIDTH / self.shared_variables.DETECTION_SCALE)) / 2)
        self.y = int(box[1] * (self.shared_variables.HEIGHT / self.shared_variables.DETECTION_SCALE) - (
                    box[3] * (self.shared_variables.HEIGHT / self.shared_variables.DETECTION_SCALE)) / 2)
        self.width = int(box[2] * (self.shared_variables.WIDTH / self.shared_variables.DETECTION_SCALE))
        self.height = int(box[3] * (self.shared_variables.HEIGHT / self.shared_variables.DETECTION_SCALE))
        self.id = id

        # Loading and scaling box
        self.splash_pix = QPixmap('./docs/box.png')
        self.splash_pix = self.splash_pix.scaled(round(self.width * self.shared_variables.DETECTION_SCALE),
                                                 round(self.height * self.shared_variables.DETECTION_SCALE))
        self.setPixmap(self.splash_pix)

        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)

        # Creating a label for detected object with the score and classification
        label = QLabel(self)
        label.setWordWrap(True)
        label.move(30, 30)
        label.setStyleSheet(" color: rgb(0, 100, 200); font-size: 15pt; ")

        label.setText(str(int(100 * score)) + "%" + " " + classification)
        self.move(self.x, self.y)
        self.show()

        # Creating tracking object
        self.tracking = Tracking((self.x, self.y, self.width, self.height), self.shared_variables)

        # Initializing thread pool for tracking processing
        self.threadpool = QThreadPool()

        logging.debug(f"New Box Created at {str(self.x)} {str(self.y)}  Size {str(self.width)} {str(self.height)}")

        self.start_worker()

    # Processing progress
    def progress_fn(self, n):
        logging.debug("%d%% done" % n)
        pass

    # Removes box from tracking box list and stops the thread pool
    def remove(self):
        self.shared_variables.list.remove(self)
        self.done = True
        self.threadpool.cancel

    # Checks if tracking is still active and executes tracking if so
    def background_detection(self, progress_callback):
        if not self.tracking.running:
            if not self.done:  # Remove self from gui list
                self.shared_variables.list.remove(self)
                self.done = True
                self.threadpool.cancel
        else:
            self.tracking.run()

        return "Done."

    # Changes box position and size based on new tracking data
    def print_output(self, s):
        self.hide()
        self.repaint_size(round(self.tracking.box[2] * self.shared_variables.DETECTION_SCALE),
                          round(self.tracking.box[3] * self.shared_variables.DETECTION_SCALE))
        self.move(round(self.tracking.box[0] * self.shared_variables.DETECTION_SCALE),
                  round(self.tracking.box[1] * self.shared_variables.DETECTION_SCALE))
        self.show()

    # Starts new thread once old is finished
    def thread_complete(self):
        # logging.debug("Thread complete")
        self.start_worker()

    # Starts new thread for tracking processing
    def start_worker(self):
        # Pass the function to execute
        worker = Worker(self.background_detection)  # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)

        # Execute
        self.threadpool.start(worker)

    # Box scaling
    def repaint_size(self, width, height):
        self.splash_pix = self.splash_pix.scaled(width, height)
        self.setPixmap(self.splash_pix)

    # Returns box size and coordinates
    def get_box(self):
        return self.tracking.box


# Show an overlay box without label
def create_box(x, y, width, height):

    splash_pix = QPixmap('.docs/box.png')
    splash_pix = splash_pix.scaled(width, height)

    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setWindowOpacity(0.2)

    splash.setAttribute(Qt.WA_NoSystemBackground)
    splash.move(x, y)

    splash.show()
    return splash


# Show an overlay box with label that shows score and classification
def create_box_with_score_classification(score, classification, x, y, width, height):

    splash_pix = QPixmap('.docs/box.png')
    splash_pix = splash_pix.scaled(width, height)

    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setWindowOpacity(0.2)

    label = QLabel(splash)
    label.setWordWrap(True)
    label.setText(str(int(100 * score)) + "%" + " " + classification)

    splash.setAttribute(Qt.WA_NoSystemBackground)
    splash.move(x, y)

    splash.show()
    return splash


# Show an overlay box with label that shows score and classification
def create_box_with_image_score_classification(image_path, score, classification, x, y, width, height):

    splash_pix = QPixmap(image_path)
    splash_pix = splash_pix.scaled(width, height)

    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setWindowOpacity(0.2)

    label = QLabel(splash)
    label.setWordWrap(True)
    label.setText(str(int(100 * score)) + "%" + " " + classification)

    splash.setAttribute(Qt.WA_NoSystemBackground)
    splash.move(x, y)
    splash.show()
    return splash
