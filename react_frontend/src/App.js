import React, { useState, useEffect } from "react";
import Button from "react-bootstrap/Button";
import Form from 'react-bootstrap/Form';
import "bootstrap/dist/css/bootstrap.min.css";
import ReactPlayer from 'react-player';
import TrackingProgressBar from "./ProgressBar";
//import { pushJob, checkJobStatus, getJobResults } from "./Api";

const App = () => {
  const [url, setUrl] = useState("");
  const [videoUrl, setVideoUrl] = useState(''); // State to hold the new video URL
  const [jobId, setJobId] = useState(null);
  const [jobStatus, setJobStatus] = useState('');  // Possible values: '', 'queued', 'processing', 'finished'


  // Handle process button click
  const handleProcess = async () => {
    try{
      const response = await fetch("http://localhost:5000/push", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
          source_name: "Video Source",
          source_url: url,
        }),
      });
      const data = await response.json();
      if (data['id (/push)']){
        const job_id = data['id (/push)'];
        setJobId(job_id); // set job id
        setJobStatus('queued'); // set job status
      }
    } catch (error) {
      console.log("An error occurred: ", error);
    }
  }
  
  const checkJobStatus = async () => {
    if (jobId){
      try{
        const response = await fetch(`http://localhost:5000/status/${jobId}`);
        const data = await response.json();
        console.log(data);
        if (data['status']){
          const status = data['status'];
          setJobStatus(status);
        }
      } catch (error) {
        console.log("Failed to fetch job status: ", error);
      }
    }
  }

  const getResults = async () => { // query job for results
    if (jobId){
      try{
        const response = await fetch(`http://localhost:5000/query/${jobId}`);
        const data = await response.json();
        console.log(data['data (/query)']);
        const vidUrl = `http://localhost:5000${data['video_url']}`;
        setVideoUrl(vidUrl); // Set the video URL if it exists
        console.log(vidUrl);
      
      } catch (error) {
        console.log("Failed to fetch job status: ", error);
      }
    }
  }

  useEffect(() => {
    let intervalId;
  
    if (jobStatus === 'queued' || jobStatus === 'processing') {
      intervalId = setInterval(checkJobStatus, 5000);  // Check every 5 seconds
    } else if (jobStatus === 'finished') {
      getResults();
      clearInterval(intervalId);
    }
  
    return () => {
      // Cleanup: clear the interval when the component is unmounted or if the jobId/jobStatus changes
      clearInterval(intervalId);
    };
  }, [jobId, jobStatus]);
  
  return (
    <>
      <h1>Instant Object Tracking</h1>
      <Form.Group className="mb-3" controlId="exampleForm.ControlInput1">
        <Form.Label>Input URL</Form.Label>
        <Form.Control 
          type="url" 
          placeholder="https://www.example.com" 
          value={url} 
          onChange={(e) => setUrl(e.target.value)}
        />
      </Form.Group>
      <Button onClick={handleProcess} >Process</Button>

      <div>
        {url && (
          <video width="768" height="576" controls>
            <source src={ url } type="video/mp4" />
            Your browser does not support the video tag.
          </video>
        )}
      
        {videoUrl && (
          <video width="768" height="576" controls crossOrigin="anonymous" style={{ paddingLeft: '20px' }}>
              <source src={videoUrl} type="video/webm" />
              Your browser does not support the video tag.
          </video>
        )}
      </div>
      <TrackingProgressBar status={jobStatus} />
    </>
  );
}

export default App;