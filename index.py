from flask import Flask, request, jsonify
from redis import Redis
import time

app = Flask(__name__)
redis = Redis(host='localhost', port=6379)

@app.route('/submit-event', methods=['POST'])
def submit_event():
    event_data = request.json
    timestamp = int(time.time())
    
    # Store event in Redis sorted set with the current timestamp
    redis.zadd('events', {event_data['event_id']: timestamp})
    
    return jsonify({"status": "Event received"}), 200


if name == "__main__":
    app.run(debug=True)