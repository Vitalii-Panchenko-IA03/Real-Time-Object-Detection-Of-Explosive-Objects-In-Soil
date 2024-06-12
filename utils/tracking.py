"""
This file realizes object tracking in videostream using OpenCV and Kalman filter
"""

import numpy as np
import cv2


# Realize tracking of single object
class Tracking:
    tracker_test = None  # result
    tracker = None  # OpenCV tracker
    frame = None  # current frame
    running = True  # status

    fail_counter = 0

    start_time = None  # tracking start time
    end_time = None  # tracking enc time
    first_time = True  # flag
    first = True  # flag

    # Initiate thread
    def __init__(self, box, shared_variables):
        self.box = box  # starting coordinates and size
        self.shared_variables = shared_variables

        # Kalman filter init
        self.kalman = cv2.KalmanFilter(4, 2, 0)
        self.kalman.measurementMatrix = np.array([[1, 0, 0, 0],
                                                  [0, 1, 0, 0]], np.float32)

        self.kalman.transitionMatrix = np.array([[1, 0, 1, 0],
                                                 [0, 1, 0, 1],
                                                 [0, 0, 1, 0],
                                                 [0, 0, 0, 1]], np.float32)

        self.kalman.processNoiseCov = np.array([[1, 0, 0, 0],
                                                [0, 1, 0, 0],
                                                [0, 0, 1, 0],
                                                [0, 0, 0, 1]], np.float32) * 0.03

    # Thread run function
    def run(self):
        self.frame = self.shared_variables.OutputFrame  # updates current frame

        if self.frame is not None:
            if self.first_time:  # if first time, initializes tracker
                self.update_custom_tracker()
                self.first_time = False
            self.object_custom_tracking()  # performs tracking

    # Create_custom_tracker
    def create_custom_tracker(self):
        # Test which one suits the best
        # self.tracker = cv2.legacy.TrackerCSRT.create()
        # self.tracker = cv2.legacy.TrackerKCF.create()
        self.tracker = cv2.legacy.TrackerMOSSE.create()

    # Set and reset custom tracker. Initializes tracker on current frame
    def update_custom_tracker(self):
        self.create_custom_tracker()
        print(self.frame.shape, self.box)
        self.tracker_test = self.tracker.init(self.frame, self.box)

    def get_box(self):
        return self.box

    # This function uses the OpenCV tracking from update_custom_tracker
    def object_custom_tracking(self):
        self.tracker_test, box = self.tracker.update(self.frame)  # Calculate

        # Update tracker box
        if self.tracker_test:
            if self.first:
                A = self.kalman.statePost
                A[0:4] = np.array([[np.float32(box[0])], [np.float32(box[1])], [0], [0]])
                self.kalman.statePost = A
                self.kalman.statePre = A
                self.first = False

            current_measurement = np.array([[np.float32(box[0])], [np.float32(box[1])]])
            self.kalman.correct(current_measurement)  # correcting tracking results
            prediction = self.kalman.predict()
            self.box = [int(prediction[0]), int(prediction[1]), box[2], box[3]]
            self.fail_counter = 0
        else:  # if tracking fails
            self.fail_counter += 1  # increase fail counter
            if self.fail_counter > self.shared_variables.MAX_TRACKING_MISSES:  # misses reached maximum amount
                self.running = False  # aborting tracking


# Realize tracking of multiple objects
class MultiTracking:
    tracker_test = None  # result
    tracker = None  # OpenCV tracker
    frame = None  # current frame
    running = True  # status

    fail_counter = 0

    start_time = None  # tracking start time
    end_time = None  # tracking enc time
    first_time = True  # flag
    first = True  # flag

    def __init__(self, box, shared_variables):
        self.box = box
        self.shared_variables = shared_variables

    def run(self):
        self.frame = self.shared_variables.OutputFrame

        if self.frame is not None:
            if self.first_time:
                self.update_custom_tracker()
                self.first_time = False
            self.object_custom_tracking()

    def create_custom_tracker(self):
        self.Tracker = cv2.legacy.MultiTracker.create()

    def update_custom_tracker(self):
        self.create_custom_tracker()
        print(self.frame.shape, self.box)
        self.tracker_test = self.tracker.init(self.frame, self.box)

    def get_box(self):
        return self.box

    # def add_tracker(self, frame, box):
    def add_tracker(self, frame, bboxes):
        # Initialize MultiTracker
        for bbox in bboxes:
            # self.tracker.add(cv2.legacy.TrackerCSRT.create(), frame, bbox)
            # self.tracker.add(cv2.legacy.TrackerKCF.create(), frame, bbox)
            self.tracker.add(cv2.legacy.TrackerMOSSE.create(), frame, bbox)

    def object_custom_tracking(self):
        # Calculate
        self.tracker_test, box = self.tracker.update(self.frame)

        # Update tracker box
        if self.tracker_test:
            self.box = box
            self.fail_counter = 0
        else:
            self.fail_counter += 1
            if self.fail_counter > self.shared_variables.MAX_TRACKING_MISSES:  # misses reached maximum amount
                self.running = False  # abort tracking
