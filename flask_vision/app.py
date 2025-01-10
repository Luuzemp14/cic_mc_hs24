import os
import requests
from flask import Flask, request, render_template, jsonify
import boto3
import re

app = Flask(__name__)

# Use environment variables for the monitor URL and worker ID
monitor_url = os.environ.get("MONITOR_URL", "http://monitor:5001")
worker_id = os.environ.get("WORKER_ID", "worker_1")

ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']


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


def is_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def secure_filename(filename):
    """
    Sanitize a file name to ensure it is safe for use on the file system.
    Removes unsafe characters and retains only alphanumeric characters,
    dashes, underscores, and periods.
    """
    filename = os.path.basename(filename)  # Remove any directory components
    filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)  # Replace unsafe characters
    return filename


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

    if os.getenv("MOCK_MODE", "False").lower() == "true":
        print("Mock mode enabled. Returning mock data.")
        return [{"Name": "John Doe", "Id": "12345"}]

    client = boto3.client(
        "rekognition",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
    )
    response = client.recognize_celebrities(Image={"Bytes": image})
    notify_monitor()
    celebrities = [{"Name": c["Name"], "Id": c["Id"]} for c in response["CelebrityFaces"]]
    return celebrities


@app.route("/", methods=["GET"])
def index():
    return render_template("upload.html")



@app.route("/find_celebrity", methods=["GET", "POST"])
def upload_image():
    # Determine the User-Agent
    user_agent = request.headers.get("User-Agent", "").lower()

    # Handle the image upload
    file = request.files.get("image")
    if not file or file.filename == '':
        if "curl" in user_agent:
            return jsonify({"error": "No image uploaded"}), 400
        else:
            return render_template("upload.html", message="No image uploaded"), 400

    if not is_allowed_file(file.filename):
        if "curl" in user_agent:
            return jsonify({"error": "Invalid file type. Only PNG, JPG, and JPEG are allowed."}), 400
        else:
            return render_template("upload.html", message="Invalid file type. Only PNG, JPG, and JPEG are allowed."), 400

    # Read the image content
    image_content = file.read()
    celebrities = detect_celebrities(image_content)

    # Return response based on User-Agent
    if "curl" in user_agent:
        return jsonify({"celebrities": celebrities})
    else:
        return render_template("upload.html", results=celebrities)


if __name__ == "__main__":
    register_worker()
    app.run(debug=True, host="0.0.0.0", port=5002)
