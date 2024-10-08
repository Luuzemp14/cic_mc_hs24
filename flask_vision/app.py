import os
import requests # using requests to communicate with the monitor
from flask import Flask, request, jsonify, render_template
from google.cloud import vision
import boto3

app = Flask(__name__)

monitor_url = os.environ.get('MONITOR_URL', 'http://monitor:5001')  # Replace 'monitor' with the monitor server's address
worker_id = os.environ.get('WORKER_ID', 'worker_1')  # Unique worker identifier

with open("secrets.txt") as f:
    for line in f:
        key, value = line.strip().split('=')
        os.environ[key] = value

# Function to notify the monitor server about a request
def notify_monitor():
    try:
        response = requests.post(f'{monitor_url}/track_request', json={'worker_id': worker_id})
        if response.status_code == 200:
            data = response.json()
            if data.get('stop_requests'):
                raise Exception("Cost limit exceeded. Requests stopped.")
        else:
            print(f"Error communicating with monitor: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Failed to notify monitor: {e}")


def register_worker():
    response = requests.post(f'{monitor_url}/register', json={'worker_id': worker_id})
    if response.status_code == 200:
        print(f"Worker {worker_id} registered successfully.")
    else:
        print(f"Failed to register worker: {response.text}")


def detect_celebrities(image):
    client = boto3.client('rekognition', region_name='us-east-1')

    response = client.recognize_celebrities(Image={'Bytes': image})

    # Notify monitor server about the request
    notify_monitor()

    print('Detected celebrities:')
    celebrities = []
    for celebrity in response['CelebrityFaces']:
        print('Name: ' + celebrity['Name'])
        celebrities.append({
            'Name': celebrity['Name'],
            'Id': celebrity['Id']
        })

    return celebrities

@app.route('/', methods=['GET'])
def index():
    # Render the upload HTML form
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_image():
    file = request.files['image']
    if not file:
        return render_template('upload.html', message="No image uploaded"), 400

    # Convert image to proper format for Google Vision
    image_content = file.read()

    # Send the image to Rekognition API
    celebrities = detect_celebrities(image_content)

    # Return the HTML template with the results
    return render_template('upload.html', results=celebrities)

if __name__ == '__main__':
    register_worker()
    app.run(debug=True, host='0.0.0.0')
