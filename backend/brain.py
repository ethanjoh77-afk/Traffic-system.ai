import cv2
from flask import Flask, Response, jsonify
from ultralytics import YOLO
import threading

app = Flask(__name__)

# LOAD YOLO MODEL
model = YOLO("yolov8n.pt")

# GLOBAL DATA
latest_data = {
    "cars": 0,
    "buses": 0,
    "trucks": 0,
    "people": 0
}

# VIDEO SOURCE
cap = cv2.VideoCapture(0)

def detect_loop():
    global latest_data

    while True:
        success, frame = cap.read()
        if not success:
            break

        results = model(frame)

        # RESET COUNTS
        new = {
            "cars": 0,
            "buses": 0,
            "trucks": 0,
            "people": 0
        }

        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                label = model.names[cls]

                if label == "car":
                    new["cars"] += 1
                elif label == "bus":
                    new["buses"] += 1
                elif label == "truck":
                    new["trucks"] += 1
                elif label == "person":
                    new["people"] += 1

        latest_data = new

# START DETECTION THREAD
threading.Thread(target=detect_loop, daemon=True).start()

# VIDEO STREAM
def generate_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# ROUTES
@app.route("/")
def home():
    return "🚦 Traffic AI System LIVE"

@app.route("/video")
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/stats")
def stats():
    return jsonify(latest_data)

# RUN SERVER
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)