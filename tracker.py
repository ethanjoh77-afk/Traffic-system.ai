import numpy as np

class ByteLikeTracker:
    def __init__(self, iou_threshold=0.3):
        self.next_id = 0
        self.tracks = []  # active tracks
        self.iou_threshold = iou_threshold

    # ---------------- IOU CALC ----------------
    def iou(self, box1, box2):
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])

        inter_area = max(0, x2 - x1) * max(0, y2 - y1)

        box1_area = (box1[2]-box1[0]) * (box1[3]-box1[1])
        box2_area = (box2[2]-box2[0]) * (box2[3]-box2[1])

        union = box1_area + box2_area - inter_area

        if union == 0:
            return 0

        return inter_area / union

    # ---------------- UPDATE TRACKS ----------------
    def update(self, detections):
        """
        detections: [x1,y1,x2,y2,class]
        """

        updated_tracks = []
        used_detections = set()

        # STEP 1: match existing tracks
        for track in self.tracks:
            best_iou = 0
            best_det = None

            for i, det in enumerate(detections):
                if i in used_detections:
                    continue

                iou_score = self.iou(track["bbox"], det[:4])

                if iou_score > best_iou:
                    best_iou = iou_score
                    best_det = (i, det)

            # if good match found → update same ID
            if best_iou > self.iou_threshold and best_det:
                idx, det = best_det
                used_detections.add(idx)

                track["bbox"] = det[:4]
                track["class"] = det[4]
                track["age"] = 0

                updated_tracks.append(track)

            else:
                # no match → increase age
                track["age"] += 1
                if track["age"] < 5:
                    updated_tracks.append(track)

        # STEP 2: create new tracks
        for i, det in enumerate(detections):
            if i in used_detections:
                continue

            new_track = {
                "id": self.next_id,
                "bbox": det[:4],
                "class": det[4],
                "age": 0
            }

            self.next_id += 1
            updated_tracks.append(new_track)

        self.tracks = updated_tracks
        return self.tracks