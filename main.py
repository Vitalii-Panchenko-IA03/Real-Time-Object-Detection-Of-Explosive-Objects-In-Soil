"""
This file starts the program
"""

from utils.shared_variables import SharedVariables
from utils import screen_overlay_handler
from utils.ThreadPool import *
from pyfiglet import Figlet

import time
import logging

logging.basicConfig(
    level=logging.DEBUG,  # Set the logging threshold to DEBUG (or another level)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='last-run.log',  # Log messages to a file (optional)
    filemode='w'  # Append mode for the log file (optional)
)
console_handler = logging.StreamHandler()  # Use the default stream (sys.stdout)

# Create a formatter for the console handler (optional)
console_formatter = logging.Formatter('%(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# Add the console handler to the root logger
root_logger = logging.getLogger()
root_logger.addHandler(console_handler)

# Create a logger for your module
logger = logging.getLogger('realtime-screen-object-detection.rsod')

# Variables that can be changed
MAX_BOX_AREA = 100000000  # pixels^2
PRECISION = 0.3  # 30 % detection threshold
MAX_DETECTION = 100
MAX_TRACKING_MISSES = 5
WIDTH = 1920  # 2560  # pixels
HEIGHT = 1080  # 1440  # pixels
SHOW_ONLY = ["FMCW-Radar-Output"]  # Start Empty, receive items to show
OFFSET = (0, 0)
DETECTION_SIZE = 640  # was 480
DETECTION_DURATION = 1
RESET_SHOW_ONLY_ON_START = False
RED_NUMBER = 240


class MainGUI(QMainWindow):

    def initiate_shared_variables(self):
        self.shared_variables = SharedVariables()
        self.shared_variables.MAX_BOX_AREA = MAX_BOX_AREA
        self.shared_variables.PRECISION = PRECISION
        self.shared_variables.MAX_DETECTION = MAX_DETECTION
        self.shared_variables.WIDTH = WIDTH
        self.shared_variables.HEIGHT = HEIGHT
        self.shared_variables.SHOW_ONLY = SHOW_ONLY
        self.shared_variables.list = []
        self.shared_variables.OFFSET = OFFSET
        self.shared_variables.DETECTION_SIZE = DETECTION_SIZE
        self.shared_variables.DETECTION_DURATION = DETECTION_DURATION
        self.shared_variables.MAX_TRACKING_MISSES = MAX_TRACKING_MISSES
        self.shared_variables.RED_NUMBER = RED_NUMBER

        if RESET_SHOW_ONLY_ON_START:
            self.shared_variables.SHOW_ONLY = []

    def __init__(self):
        super(MainGUI, self).__init__()

        self.initiate_shared_variables()

        # Create detection and load model
        self.detection_model = self.shared_variables.model(shared_variables=self.shared_variables)
        self.detection_model.download_model()
        self.detection_model.load_model()

        self.threadpool = QThreadPool()

        logging.info("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        self.timer = QTimer()
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.print_output)
        self.timer.start()

        # Start Detection thread
        self.start_worker()

    # detects object in background mode
    def background_detection(self, progress_callback):
        while True:

            if len(self.shared_variables.SHOW_ONLY) == 0:
                # how often detections are made
                pass
            else:
                logging.debug("Trigger Detection...")
                if self.shared_variables.OutputFrame is not None:  # wait for the first frame
                    progress_callback.emit(self.detection_model.predict())  # detect and emit boxes

            time.sleep(self.shared_variables.DETECTION_DURATION)

    def create_tracking_boxes(self, boxes):
        if len(boxes) > 0:
            logging.debug(f"got detection now create trackerbox: {boxes}")

        for box in boxes:
            if len(self.shared_variables.list) < MAX_DETECTION:
                self.shared_variables.list.append(
                    screen_overlay_handler.TrackingBox(len(self.shared_variables.list), self.shared_variables, box[0],
                                                       box[1], box[2]))

    # Print output
    def print_output(self):
        remove = []
        index = 0
        for box in self.shared_variables.list:
            if box.done:
                box.finish(self)
                remove.insert(0, index)
            index += 1

        for i in remove:
            del self.shared_variables.list[i]

    def thread_complete(self):
        logging.debug("Thread closed")
        pass

    def start_worker(self):
        # Pass the function to execute
        worker = Worker(self.background_detection)  # Any other args, kwargs are passed to the run function
        worker.signals.progress.connect(self.create_tracking_boxes)
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.thread_complete)
        # Execute
        self.threadpool.start(worker)


# Main start here
if __name__ == "__main__":
    f = Figlet(font='slant')
    logging.info(f.renderText('Realtime Screen stream with Ai detection Overlay'))
    logging.info("This program starts several threads that stream pc screen and" +
                 "run object detection on it and show detections with PyQt5 overlay.")

    logging.info("Starting Program...")
    logging.info("All threads started, will take a few seconds to load model")

    logging.info("")
    logging.info("----- Settings -----")
    logging.info("Max box size : " + str(MAX_BOX_AREA))
    logging.info("Detection precision treshhold : " + str(100 * PRECISION) + "%")
    logging.info("Max amount of detection : " + str(MAX_DETECTION))
    logging.info("Max amount of tracking misses : " + str(MAX_TRACKING_MISSES))
    logging.info("Do detections every : " + str(DETECTION_DURATION) + " second")
    logging.info("Rescale image detection size : " + str(DETECTION_SIZE))
    logging.info("Classifications : " + str(SHOW_ONLY) + " * if empty all detections are allowed.")
    logging.info("Screen size : " + str(WIDTH) + "x" + str(HEIGHT))
    logging.info("Screen offset : " + str(OFFSET))
    logging.info("Average amount of red : " + str(RED_NUMBER))
    logging.info("")

    logging.info("")
    logging.info("----- Usage -----")
    logging.info("Exit by typing : 'ctrl+c'")
    logging.info("")

    app = QApplication([])

    MainGUI()

    app.exec_()
