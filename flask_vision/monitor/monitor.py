from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Set a maximum cost limit
COST_LIMIT = float(os.environ.get('COST_LIMIT', 100.0))  # Example: $100
COST_PER_REQUEST = float(os.environ.get('COST_PER_REQUEST', 0.01))  # Example: $0.01 per request

# Dictionary to track requests per worker
workers_requests = {}

# Track total cost
total_cost = 0.0

@app.route('/register', methods=['POST'])
def register_worker():
    # Register a worker instance by its unique ID or IP address
    worker_id = request.json.get('worker_id')
    if worker_id not in workers_requests:
        workers_requests[worker_id] = 0
    return jsonify({"message": f"Worker {worker_id} registered"}), 200

@app.route('/track_request', methods=['POST'])
def track_request():
    global total_cost
    worker_id = request.json.get('worker_id')

    if worker_id not in workers_requests:
        return jsonify({"error": "Worker not registered"}), 400

    # Increment request count for the worker
    workers_requests[worker_id] += 1

    # Update total cost
    total_cost += COST_PER_REQUEST

    print(f"Worker {worker_id} made a request. Total cost: {total_cost}")

    # Check if cost limit is exceeded
    if total_cost > COST_LIMIT:
        return jsonify({
            "status": "error",
            "message": "Cost limit exceeded",
            "stop_requests": True
        }), 200

    return jsonify({
        "status": "success",
        "total_requests": workers_requests[worker_id],
        "total_cost": total_cost,
        "stop_requests": False
    }), 200

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({
        "total_cost": total_cost,
        "workers_requests": workers_requests
    }), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)