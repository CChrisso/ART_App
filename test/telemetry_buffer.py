class TelemetryBuffer:
    def __init__(self, max_len=1000):
        self.max_len = max_len

        self.time = []

        self.gas = []
        self.brake = []

        self.ax = []
        self.ay = []
        self.az = []

    def _append(self, arr, value):
        arr.append(value)
        if len(arr) > self.max_len:
            arr.pop(0)

    def add(self, data):
        #all from 0 to 100
        self._append(self.time, data["time"])

        self._append(self.gas, data["gas"])
        self._append(self.brake, data["brake"])

        self._append(self.ax, data["ax"])
        self._append(self.ay, data["ay"])
        self._append(self.az, data["az"])
