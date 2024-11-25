import os
import requests
from flask import Flask, request, jsonify, render_template
import boto3

app = Flask(__name__)

# Use environment variables for the monitor URL and worker ID
monitor_url = os.environ.get("MONITOR_URL", "http://monitor:5001")
worker_id = os.environ.get("WORKER_ID", "worker_1")

# Function to notify monitor server
def notify_monitor():
    try:
        response = requests.post(f"{monitor_url}/track_request", json={"worker_id": worker_id})
        if response.status_code == 200:
            data = response.json()
            if data.get("stop_requests"):
                raise Exception("Cost limit exceeded. Requests stopped.")
        else:
            print(f"Monitor error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Failed to notify monitor: {e}")

# Worker registration function
def register_worker():
    try:
        response = requests.post(f"{monitor_url}/register", json={"worker_id": worker_id})
        if response.status_code == 200:
            print(f"Worker {worker_id} registered successfully.")
        else:
            print(f"Failed to register worker: {response.text}")
    except requests.ConnectionError as e:
        print(f"Connection error: {e}")

# Celebrity detection function
def detect_celebrities(image):
    client = boto3.client("rekognition", region_name="us-east-1")
    response = client.recognize_celebrities(Image={"Bytes": image})
    notify_monitor()
    celebrities = [{"Name": c["Name"], "Id": c["Id"]} for c in response["CelebrityFaces"]]
    return celebrities

@app.route("/", methods=["GET"])
def index():
    return render_template("upload.html")

@app.route("/upload", methods=["POST"])
def upload_image():
    file = request.files["image"]
    if not file:
        return render_template("upload.html", message="No image uploaded"), 400
    image_content = file.read()
    celebrities = detect_celebrities(image_content)
    return render_template("upload.html", results=celebrities)

if __name__ == "__main__":
    register_worker()
    app.run(debug=True, host="0.0.0.0", port=5002)