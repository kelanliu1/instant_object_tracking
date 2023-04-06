import json
import os
import cv2
import torch
import yaml
import numpy as np
import torch
from sort import Sort
from flask import Flask, request, jsonify
import uuid
import threading
import time
import queue


job_queue = queue.Queue()

app = Flask(__name__)

video_jobs, job_status = {}, {}
video_processing_queue = queue.Queue()

# Load the YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

def load_classes(file):
    with open(file, 'r') as f:
        config = yaml.safe_load(f)
    return config['names']

classes = load_classes('coco.yaml')

def worker():
    while True:
        job_id, source_url = video_processing_queue.get()
        process_video(job_id, source_url)
        video_processing_queue.task_done()

num_worker_threads = 4  # Adjust this based on your system's capabilities
for _ in range(num_worker_threads):
    t = threading.Thread(target=worker)
    t.daemon = True  # Mark as a daemon thread so it exits when the main thread exits
    t.start()


# Route to handle push
@app.route('/push', methods=['POST'])
def push():
    source_name = request.form.get('source_name')
    source_url = request.form.get('source_url')

    if not source_name or not source_url:
        return jsonify({'error': 'source_name and source_url are required'}), 400

    # Generate a unique job ID
    job_id = str(uuid.uuid4())

    # Add the job to the processing queue
    video_processing_queue.put((job_id, source_url))

    # Return the job ID to the client
    return jsonify({'id': job_id})


# Route to handle status
@app.route('/status/<job_id>', methods=['GET']) 
def status(job_id):
    if job_id in video_jobs:
        return jsonify({'status': video_jobs[job_id]})
    else:
        return jsonify({'error': 'job id not found'}), 404

# Route to handle query
@app.route('/query/<id>', methods=['GET'])
def query(id):
    if id in video_jobs:
        if video_jobs[id]['status'] == 'finished':
            return jsonify({'data': video_jobs[id]['data']})
        else:
            return jsonify({'error': 'Video is still processing'}), 400
    else:
        return jsonify({'error': 'ID not found'}), 404

# Route to handle list
@app.route('/list', methods=['GET'])
def list_jobs():
    return jsonify({'data': list(video_jobs.keys())})

def get_tracked_objects(detections):
    tracked_objects = []
    for frame_det in detections:
        if frame_det.size == 0:  # Check if frame_det is empty
            continue  # Skip this iteration if frame_det is empty

        frame_number = frame_det[0]
        for det in frame_det[1:]:
            x1, y1, x2, y2, obj_id, cls_id, conf = det
            tracked_objects.append((int(obj_id), int(frame_number), int(cls_id), float(conf), int(x1), int(y1), int(x2), int(y2)))
    return tracked_objects

# process video
def process_video(job_id, source_url, yolo_model_name='yolov5s'):
    #device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    cap = cv2.VideoCapture(source_url)
    frame_number = 0
    detections = []

    # Initialize the SORT tracker
    tracker = Sort()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Resize the frame to the input size expected by the YOLOv5 model
        input_size = 640  # This is the default input size for the YOLOv5 model; adjust if necessary
        frame = cv2.resize(frame, (input_size, input_size))

        # YOLOv5 detection
        results = model(frame)

        # Convert the detections to the format required by the SORT tracker
        det_for_sort = []
        for *xyxy, conf, cls in results.xyxy[0]:
            x1, y1, x2, y2 = xyxy
            det_for_sort.append([x1.item(), y1.item(), x2.item(), y2.item(), conf.item()])

        det_for_sort = np.array(det_for_sort)

        # Update the SORT tracker with the detections if there are any
        if len(det_for_sort) > 0:
            tracked_objects = tracker.update(det_for_sort)
        else:
            tracked_objects = np.array([])

        # Add the frame number to the tracked objects and append them to the detections list
        if tracked_objects.ndim > 1:
            detections.append(np.insert(tracked_objects, 0, frame_number, axis=1))

        frame_number += 1

    cap.release()

    # Save results and update job status
    tracked_objects = get_tracked_objects(detections)
    video_jobs[job_id] = {
        'status': 'finished',
        'data': tracked_objects,
    }

if __name__ == '__main__':
    app.run(debug=True)