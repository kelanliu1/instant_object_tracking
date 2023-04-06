import requests
import time

sample_videos = [
    "https://storage.googleapis.com/sieve-public-videos/celebrity-videos/dwyane_basketball.mp4",
    "https://storage.googleapis.com/sieve-public-videos/celebrity-videos/obama_interview.mp4",
    "https://storage.googleapis.com/sieve-public-videos/celebrity-videos/elon_podcast.mp4"
]

job_ids = []

def test_push():
    for url in sample_videos:
        response = requests.post('http://localhost:5000/push', data={'source_name': 'sample_video', 'source_url': url})
        job_id = response.json().get('id')
        if job_id:
            job_ids.append(job_id)
        print(response.json())

def test_status(id):
    response = requests.get(f'http://localhost:5000/status/{id}')
    print(response.json())

def test_query(id):
    response = requests.get(f'http://localhost:5000/query/{id}')
    print(response.json())

def test_list():
    response = requests.get('http://localhost:5000/list')
    print(response.json())

if __name__ == '__main__':
    test_push()
    test_list()
    # Wait for the video processing to finish before testing the /status and /query endpoints
    time.sleep(60)  # Wait for 60 seconds (adjust the waiting time based on your processing time)
    for job_id in job_ids:
        test_status(job_id)
        test_query(job_id)