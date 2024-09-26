import os
from flask import Flask, request, jsonify, render_template
from google.cloud import vision
import boto3

app = Flask(__name__)

"""# Authenticate using the credentials JSON file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "cic-fhnw-hs24-d19c48545d67.json"

# Initialize Google Vision API client
client = vision.ImageAnnotatorClient()"""

with open("secrets.txt") as f:
    for line in f:
        key, value = line.strip().split('=')
        os.environ[key] = value

def detect_celebrities(image):
    client = boto3.client('rekognition', region_name='us-east-1')

    response = client.recognize_celebrities(Image={'Bytes': image})

    print('Detected celebrities:')

    # Create a list to gather celebrities
    celebrities = []

    for celebrity in response['CelebrityFaces']:
        print('Name: ' + celebrity['Name'])
        celebrities.append({
            'Name': celebrity['Name'],
            'Id': celebrity['Id']
        })

    # Return the list
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
    app.run(debug=True)