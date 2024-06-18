# Real-Time-Object-Detection-Of-Explosive-Objects-In-Soil

This is a project for Automatic Detection System of Explosive Objects in Soil Based on Geospatial Snapshot Analysis.

Short summary of the process: Ground Penetrating Radar (GPR) collects data by scanning soil -> Received data is interpreted and presented as a graph -> YOLO is trained on dataset and used to recognize color and shape patterns (only color patterns as of now). 

Contents:
- yolov8n.pt, yolov8s.pt - predefined YOLO weights;
- results.csv - results of YOLO training;
- requirements.txt - important libraries for this project;
- last-run.log - log of the last run;
- best.pt - YOLO model, trained on custom dataset;
- generateBlobs.txt - MATLAB script for generating fake synthetic GPR data;
- main.py - starts real-time object detection;
- singleImageDetection - script for testing detection on a single provided image + some test images and YOLO weights;
- utils - utilities (read in-script comments);
- ml - detector (read in-script comments);
- docs/box.png - box to draw around detected object;
- interactWithGPR - GUI for GPR and script for calculating DAC (read in-script comments);
- Real-Time Object Detection Demo.mp4 - short demo.

Huge shoutout to other GitHub authors whose works became an inspiration for this project.

Link for real-time object detection project: https://github.com/grebtsew/Realtime-Screen-Object-Detection
Link for GPR project: https://github.com/Ritchizh/GPR_Project_2017/tree/master
