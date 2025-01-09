import os
import base64
import requests
import re
import boto3
from io import BytesIO
from flask import Flask
import dash
from dash import dcc, html, Input, Output, State, dash_table
from dash import dash_table

server = Flask(__name__)

# Use environment variables for the monitor URL and worker ID
monitor_url = os.environ.get("MONITOR_URL", "http://monitor:5001")
worker_id = os.environ.get("WORKER_ID", "worker_1")

ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']

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
    filename = os.path.basename(filename)  # Remove directory components
    filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)  # Replace unsafe characters
    return filename


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

register_worker()

# -----------------------
# Dash App Setup
# -----------------------
app = dash.Dash(__name__, server=server)

app.layout = html.Div(style={"font-family": "Arial, sans-serif", "margin":"50px"}, children=[
    html.H1("Celebrity Recognition Dashboard", style={"text-align":"center", "margin-bottom":"30px"}),
    html.Div(
        style={
            "width": "100%",
            "display": "flex",
            "justify-content": "center",
            "align-items": "center",
            "flex-direction": "column"
        },
        children=[
            dcc.Upload(
                id='upload-image',
                children=html.Div([
                    'Drag and Drop or Select an Image'
                ]),
                style={
                    'width': '100%',
                    'height': '100px',
                    'lineHeight': '100px',
                    'borderWidth': '2px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '20px',
                    'backgroundColor': '#f9f9f9'
                },
                multiple=False
            ),
            html.Div(id='output-message', style={"color":"red", "margin":"10px"}),
            html.Div(id='output-table', style={"margin-top":"30px", "width":"60%"}),
        ]
    )
])


@app.callback(
    [Output('output-table', 'children'),
     Output('output-message', 'children')],
    [Input('upload-image', 'contents')],
    [State('upload-image', 'filename')]
)
def update_output(contents, filename):
    if contents is None:
        return [None, None]

    # Check if file allowed
    if not is_allowed_file(filename):
        return [None, "Invalid file type. Only PNG, JPG, and JPEG are allowed."]

    # Decode the base64 image
    content_type, content_string = contents.split(',')
    image_data = base64.b64decode(content_string)

    # Detect celebrities
    try:
        results = detect_celebrities(image_data)
        if len(results) == 0:
            return [None, "No celebrities recognized."]
        
        # Create a nice table
        table = dash_table.DataTable(
            data=results,
            columns=[{"name": i, "id": i} for i in results[0].keys()],
            style_table={'margin-top': '20px', 'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '10px', 'fontFamily': 'Arial'},
            style_header={'backgroundColor': '#0074D9', 'color': 'white', 'fontWeight': 'bold'},
            style_data={'backgroundColor': 'white','border': '1px solid #ccc'},
        )
        return [table, None]

    except Exception as e:
        return [None, f"Error processing image: {str(e)}"]

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=5002)
