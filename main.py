from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)

video_jobs = {}

# Route to handle push
@app.route('/push', methods=['POST'])
def push():
    source_name = request.form.get('source_name')
    source_url = request.form.get('source_url')
    job_id = str(uuid.uuid4())
    video_jobs[job_id] = {
        'source_name': source_name,
        'source_url': source_url,
        'status': 'queued',
        'data': None
    }
    # TODO: Process the video asynchronously
    return jsonify({'id': job_id})

# Route to handle status
@app.route('/status/<job_id>', methods=['GET']) 
def status(job_id):
    if id in video_jobs:
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

if __name__ == '__main__':
    app.run(debug=True)