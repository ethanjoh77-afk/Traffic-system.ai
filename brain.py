from flask import Flask, jsonify, Response, request
from flask_cors import CORS
from ultralytics import YOLO
import cv2
import numpy as np

from tracker import ByteLikeTracker
from auth import init_auth_db, register_user, login_user, verify_token, is_paid
from payment import create_checkout_session, handle_webhook

app = Flask(__name__)
CORS(app)

# ---------------- INIT ----------------
init_auth_db()

model = YOLO("yolov8n.pt")
tracker = ByteLikeTracker()

cap = cv2.VideoCapture("traffic.mp4")

if not cap.isOpened():
    print("❌ Video not found")
    cap = None

latest_data = {
    "cars": 0,
    "buses": 0,
    "trucks": 0,
    "people": 0
}

# ---------------- VIDEO STREAM ----------------
def generate_frames():
    global latest_data

    while True:
        if cap is None:
            frame = np.ones((480, 640, 3), dtype=np.uint8) * 255
        else:
            success, frame = cap.read()
            if not success:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

        results = model(frame, verbose=False)

        detections = []
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls = int(box.cls[0])
                name = model.names[cls]

                if name in ["car", "bus", "truck", "person"]:
                    detections.append([x1, y1, x2, y2, name])

        tracked = tracker.update(detections)

        latest_data = {
            "cars": len([o for o in tracked if o["class"] == "car"]),
            "buses": len([o for o in tracked if o["class"] == "bus"]),
            "trucks": len([o for o in tracked if o["class"] == "truck"]),
            "people": len([o for o in tracked if o["class"] == "person"]),
        }

        for obj in tracked:
            x1, y1, x2, y2 = obj["bbox"]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        _, buffer = cv2.imencode(".jpg", frame)
        frame_bytes = buffer.tobytes()

        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")

# ---------------- AUTH ----------------
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    return jsonify({
        "success": register_user(data["username"], data["password"])
    })

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    token = login_user(data["username"], data["password"])

    if token:
        return jsonify({"token": token})
    return jsonify({"error": "invalid"}), 401

# ---------------- PAYMENT ----------------
@app.route("/pay")
def pay():
    token = request.headers.get("Authorization")

    if not token:
        return jsonify({"error": "unauthorized"}), 401

    user = verify_token(token)

    if not user:
        return jsonify({"error": "invalid token"}), 401

    url = create_checkout_session(user["username"])

    return jsonify({"url": url})

# ---------------- STRIPE WEBHOOK ----------------
@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.data
    sig = request.headers.get("Stripe-Signature")

    if handle_webhook(payload, sig):
        return "", 200

    return "", 400

# ---------------- PROTECTED DATA ----------------
@app.route("/data")
def data():
    token = request.headers.get("Authorization")

    if not token:
        return jsonify({"error": "unauthorized"}), 401

    user = verify_token(token)

    if not user:
        return jsonify({"error": "invalid token"}), 401

    if not is_paid(user["username"]):
        return jsonify({"error": "payment required"}), 403

    return jsonify(latest_data)

# ---------------- PROTECTED VIDEO ----------------
@app.route("/video")
def video():
    token = request.args.get("token")

    if not token:
        return jsonify({"error": "unauthorized"}), 401

    user = verify_token(token)

    if not user:
        return jsonify({"error": "invalid token"}), 401

    if not is_paid(user["username"]):
        return jsonify({"error": "payment required"}), 403

    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

# ---------------- RUN (DEPLOY READY) ----------------
if __name__ == "__main__":
    print("🚀 SaaS System Running (DEPLOY MODE)")
    app.run(host="0.0.0.0", port=10000)