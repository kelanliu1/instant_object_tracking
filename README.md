# Instant Object Tracking

This project is a mini version of Sieve that allows users to send a video, process the video, and retrieve the information that has been processed (bounding boxes, classification, class probabilties, etc.). The project is implemented in Python using the Flask framework.

## Running the Project

1. Run the Flask back-end by executing the following command in the terminal or command prompt:

```python main.py```

This will start the Flask development server, usually at `http://127.0.0.1:5000/` (also accessible via `http://localhost:5000/`).

2. Keep the Flask app running while testing it with the `test.py` script on a different terminal.

3. Run the test script by executing the following command (optional):

```python test.py```

This script will send HTTP requests to the Flask app endpoints and display the responses in the terminal or command prompt

4. Run the React front-end by executing the following command in another terminal or command prompt:

```npm start```

This will start the React app, at `http://127.0.0.1:3000/` (also accessible via `http://localhost:3000/`).

Here's a sample video link you can use as an example: https://storage.googleapis.com/sieve-public-videos/celebrity-videos/dwyane_basketball.mp4

## Sample Video Output

https://user-images.githubusercontent.com/67593159/230647210-5fe0d970-b998-4e33-8d18-123ab625943e.mp4

## License

This project is open-source and available under the [MIT License](LICENSE).
