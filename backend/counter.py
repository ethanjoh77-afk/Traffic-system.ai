class VehicleCounter:
    def __init__(self, line_y):
        self.line_y = line_y
        self.count = 0
        self.tracked = set()

    def update(self, detections):
        for (x1, y1, x2, y2, cls) in detections:
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            if cy > self.line_y:
                key = (cx, cy)

                if key not in self.tracked:
                    self.tracked.add(key)
                    self.count += 1

        return self.count