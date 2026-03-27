import cv2
import numpy as np

from detector import detect
from tracker import track
from lanes import BRT_ZONE, is_inside_zone
from brain import TrafficBrain
from traffic_light import TrafficLight

# -----------------------------
# INIT SYSTEMS
# -----------------------------
brain = TrafficBrain()
light = TrafficLight()

cap = cv2.VideoCapture("traffic.mp4")  # au 0 kwa camera

violations = set()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # -----------------------------
    # 1. DETECT + TRACK
    # -----------------------------
    detections = detect(frame)
    tracks = track(detections, frame)

    # -----------------------------
    # 2. COUNT LANES
    # -----------------------------
    count_a = 0
    count_brt = 0

    for (x, y, w, h, track_id) in tracks:
        cx = x + w // 2
        cy = y + h // 2

        if is_inside_zone(cx, cy, BRT_ZONE):
            count_brt += 1
        else:
            count_a += 1

    # -----------------------------
    # 3. AI DECISION
    # -----------------------------
    state = brain.decide(count_a, count_brt)

    # -----------------------------
    # 4. TRAFFIC LIGHT UPDATE
    # -----------------------------
    light_state = light.update(state)

    # -----------------------------
    # 5. DRAW BRT ZONE
    # -----------------------------
    cv2.polylines(frame, [np.array(BRT_ZONE)], True, (255, 0, 0), 2)

    # -----------------------------
    # 6. DRAW TRACKS + VIOLATIONS
    # -----------------------------
    for (x, y, w, h, track_id) in tracks:
        cx = x + w // 2
        cy = y + h // 2

        in_brt = is_inside_zone(cx, cy, BRT_ZONE)

        color = (0, 255, 0)  # normal

        if in_brt:
            color = (0, 0, 255)  # violation
            violations.add(track_id)

        # box
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

        # label
        cv2.putText(frame, f"ID {track_id}", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # -----------------------------
    # 7. UI INFO
    # -----------------------------
    cv2.putText(frame, f"STATE: {state}", (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    cv2.putText(frame, f"LIGHT: {light_state}", (50, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    cv2.putText(frame, f"Normal: {count_a}", (50, 140),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.putText(frame, f"BRT: {count_brt}", (50, 170),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    cv2.putText(frame, f"Violations: {len(violations)}", (50, 200),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    # -----------------------------
    # 8. DRAW TRAFFIC LIGHT (VISUAL)
    # -----------------------------
    color_map = {
        "GREEN": (0, 255, 0),
        "YELLOW": (0, 255, 255),
        "RED": (0, 0, 255)
    }

    cv2.circle(frame, (300, 80), 20, color_map[light_state], -1)

    # -----------------------------
    # 9. SHOW FRAME
    # -----------------------------
    cv2.imshow("Smart Traffic AI", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

# -----------------------------
# CLEANUP
# -----------------------------
cap.release()
cv2.destroyAllWindows()