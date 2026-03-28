import time

class TrafficLight:
    def __init__(self):
        self.state = "RED"
        self.last_switch = time.time()
        self.green_time = 5
        self.yellow_time = 2
        self.red_time = 5

    def update(self, decision):
        now = time.time()
        elapsed = now - self.last_switch

        # BRT priority → force green
        if decision == "BRT_GREEN":
            self.state = "GREEN"
            self.last_switch = now
            return self.state

        # normal cycle
        if self.state == "GREEN" and elapsed > self.green_time:
            self.state = "YELLOW"
            self.last_switch = now

        elif self.state == "YELLOW" and elapsed > self.yellow_time:
            self.state = "RED"
            self.last_switch = now

        elif self.state == "RED" and elapsed > self.red_time:
            self.state = "GREEN"
            self.last_switch = now

        return self.state