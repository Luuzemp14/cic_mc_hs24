from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Monitor settings
COST_LIMIT = float(os.environ.get("COST_LIMIT", 100.0))
COST_PER_REQUEST = float(os.environ.get("COST_PER_REQUEST", 0.01))
workers_requests = {}
total_cost = 0.0

@app.route("/register", methods=["POST"])
def register_worker():
    worker_id = request.json.get("worker_id")
    if worker_id not in workers_requests:
        workers_requests[worker_id] = 0
    return jsonify({"message": f"Worker {worker_id} registered"}), 200

@app.route("/track_request", methods=["POST"])
def track_request():
    global total_cost
    worker_id = request.json.get("worker_id")
    if worker_id not in workers_requests:
        return jsonify({"error": "Worker not registered"}), 400
    workers_requests[worker_id] += 1
    total_cost += COST_PER_REQUEST
    if total_cost > COST_LIMIT:
        return jsonify({"stop_requests": True, "total_cost": total_cost}), 200
    return jsonify({"stop_requests": False, "total_cost": total_cost}), 200

@app.route("/status", methods=["GET"])
def get_status():
    return jsonify({"total_cost": total_cost, "workers_requests": workers_requests}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)