import requests
import time

sample_videos = [
    "https://storage.googleapis.com/sieve-public-videos/celebrity-videos/dwyane_basketball.mp4",
]

job_ids = []

def test_push():
    for url in sample_videos: 
        response = requests.post('http://localhost:5000/push', data={'source_name': 'sample_video', 'source_url': url})
        print("Server response:", response.json())  # Add this line to print the server's response
        job_id = response.json().get('id (/push)')
        if job_id:
            job_ids.append(job_id)
        print(response.json())

def test_status(id): # returns 'queued', 'processing', or 'finished'
    response = requests.get(f'http://localhost:5000/status/{id}')
    print(f"(Job {id}):", response.json())

def test_query(id): # returns the output of the video processing job
    response = requests.get(f'http://localhost:5000/query/{id}')
    print(response.json())

def test_list(): # returns a list of job IDs
    response = requests.get('http://localhost:5000/list')
    print(response.json())
    
if __name__ == '__main__':
    test_push()
    test_list()

    unfinished_jobs = set(job_ids)

    # Continuously check the /status endpoint until all video processing jobs are finished
    while unfinished_jobs:
        for job_id in list(unfinished_jobs):
            test_status(job_id)
            response = requests.get(f'http://localhost:5000/status/{job_id}')
            status = response.json().get('status')

            if status == 'finished':
                test_query(job_id)
                unfinished_jobs.remove(job_id)

        time.sleep(10)  # Wait for 10 seconds before checking the status again