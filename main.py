import cv2
import torch
from sort import *
from flask import Flask, request, jsonify
import uuid
import threading
import queue
import os
from flask_cors import CORS
from flask import send_from_directory

# Initialize the Flask app
app = Flask(__name__)
CORS(app)

# Video path
VIDEO_SAVE_PATH = "videos"
if not os.path.exists(VIDEO_SAVE_PATH):
    os.makedirs(VIDEO_SAVE_PATH)

### Global variables ##################################################################################################
DEBUG = False
NUM_WORKER_THREADS = 4  # Change this to adjust the number of parallel workers
video_jobs = {}
video_processing_queue = queue.Queue()

# Load the YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
#######################################################################################################################

def worker():
    while True:
        job_id, source_url = video_processing_queue.get()
        process_video(job_id, source_url)
        video_processing_queue.task_done()

for _ in range(NUM_WORKER_THREADS):
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

    # Update the job status
    video_jobs[job_id] = {
        'status': 'queued',
        'data': None,
    }

    # Return the job ID to the client
    return jsonify({'id (/push)': job_id})

# Route to handle status
@app.route('/status/<id>', methods=['GET']) 
def status(id):
    if id in video_jobs:
        if video_jobs[id]['status'] == 'finished':
            return jsonify({'status': 'finished'})
        elif video_jobs[id]['status'] == 'processing':
            return jsonify({'status': 'processing'})
        elif video_jobs[id]['status'] == 'queued':
            return jsonify({'status': 'queued'})
    else:
        return jsonify({'error (/status)': 'ID not found'}), 404

# Route to handle query
@app.route('/query/<job_id>', methods=['GET'])
def query(job_id):
    if job_id in video_jobs:
        video_path = video_jobs[job_id].get('video_path')
        if video_path:
            video_url = f"/videos/{os.path.basename(video_path)}"

            return jsonify({
                'video_url': video_url,
                'data (/query)': video_jobs[job_id]['data']
            })
        else:
            return jsonify({'error (/query)': 'video not processed'}), 404
    else:
        return jsonify({'error (/query)': 'job id not found'}), 404

@app.route('/videos/<filename>', methods=['GET'])
def serve_video(filename):
    return send_from_directory(VIDEO_SAVE_PATH, filename, as_attachment=False, mimetype='video/mp4')

# Route to handle list
@app.route('/list', methods=['GET'])
def list_jobs():
    return jsonify({'data (/list)': list(video_jobs.keys())})

def process_video(job_id, source_url, yolo_model_name='yolov5s'):
    # Initial status
    video_jobs[job_id] = {
        'status': 'processing',
        'data': None,
    }

    # Check if the source URL is valid and the video can be opened
    cap = cv2.VideoCapture(source_url)
    if not cap.isOpened():
        video_jobs[job_id]['status'] = 'error'
        video_jobs[job_id]['error_msg'] = 'Cannot open video source'
        return
    
    frame_number = 0
    detections = []

    frame_width  = int(cap.get(3))
    frame_height = int(cap.get(4))

    output_path = os.path.join(VIDEO_SAVE_PATH, f"{job_id}.webm")
    fourcc = cv2.VideoWriter_fourcc(*'vp80')
    out = cv2.VideoWriter(output_path, fourcc, 20.0, (frame_width, frame_height))

    model.float()
    model.eval()
    tracker = Sort()

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            preds = model(frame)
            yolov5_detections = preds.pred[0].numpy()
            tracked_objects = tracker.update(yolov5_detections)

            for j in range(len(tracked_objects.tolist())):
                coords = tracked_objects.tolist()[j]
                x1, y1, x2, y2, track_id = int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3]), int(coords[4])

                class_idx = int(yolov5_detections[j, 5])
                class_name = preds.names[class_idx]
                class_prob = float(yolov5_detections[j, 4])

                detections.append({
                    'frame': frame_number,
                    'x1': x1,
                    'y1': y1,
                    'x2': x2,
                    'y2': y2,
                    'id': int(track_id),
                    'class_id': int(class_idx),
                    'class_name': class_name,
                    'confidence': class_prob,
                })

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label = f"{class_name} {class_prob:.2f}"
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
            
            out.write(frame)
            frame_number += 1

        cap.release()
        out.release()

        video_jobs[job_id] = {
            'status': 'finished',
            'data': detections,
            'video_path': output_path
        }
    except Exception as e:
        # If an error occurs during processing, update the status and capture the error message
        video_jobs[job_id]['status'] = 'error'
        video_jobs[job_id]['error_msg'] = str(e)

    if DEBUG: print(video_jobs[job_id]['data'])

if __name__ == '__main__':
    app.run(debug=True)