import requests

sample_videos = [
    "https://storage.googleapis.com/sieve-public-videos/celebrity-videos/dwyane_basketball.mp4",
    "https://storage.googleapis.com/sieve-public-videos/celebrity-videos/obama_interview.mp4",
    "https://storage.googleapis.com/sieve-public-videos/celebrity-videos/elon_podcast.mp4"
]

def test_push():
    for url in sample_videos:
        response = requests.post('http://localhost:5000/push', data={'source_name': 'sample_video', 'source_url': url})
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
    # Replace the following placeholders with actual job IDs to test the /status and /query endpoints
    job_id = "YOUR_JOB_ID"
    test_status(job_id)
    test_query(job_id)
