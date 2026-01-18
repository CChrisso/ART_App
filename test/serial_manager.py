import serial
import threading

class SerialManager:
    def __init__(self, port, baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.running = False
        self.callback = None

    def connect(self):
        self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
        self.running = True
        threading.Thread(target=self._read_loop, daemon=True).start()

    def disconnect(self):
        self.running = False
        if self.ser:
            self.ser.close()

    def send(self, msg):
        if self.ser:
            self.ser.write((msg + "\n").encode())

    def _read_loop(self):
        while self.running:
            try:
                line = self.ser.readline().decode(errors="ignore").strip()
                if line and self.callback:
                    self.callback(line)
            except Exception:
                pass
