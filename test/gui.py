import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import os
from datetime import datetime

from serial_manager import SerialManager
from telemetry_buffer import TelemetryBuffer
from data_parser import parse_line

BG_BLACK = "#0d0d0d"
FRAME_BLACK = "#1a1a1a"
RED = "#c1121f"
RED_HOVER = "#a50f1a"
WHITE = "#ffffff"

SAMPLE_DT = 0.005 


class TelemetryApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Arrabona Racing - Telemetry")
        self.geometry("1000x700")
        self.configure(fg_color=BG_BLACK)

        self.buffer = TelemetryBuffer()
        self.serial = SerialManager(port="COM3")  
        self.serial.callback = self.on_serial_data

        self._build_ui()
        self._update_plot()


    def _build_ui(self):
        button_frame = ctk.CTkFrame(
            self,
            fg_color=FRAME_BLACK,
            corner_radius=10
        )
        button_frame.pack(pady=10, padx=10, fill="x")

        self.connect_btn = ctk.CTkButton(
            button_frame,
            text="Connect",
            fg_color=RED,
            hover_color=RED_HOVER,
            text_color=WHITE,
            command=self.toggle_connection
        )
        self.connect_btn.pack(side="left", padx=5, pady=5)

        self.cal_btn = ctk.CTkButton(
            button_frame,
            text="Calibrate Pedals",
            fg_color=RED,
            hover_color=RED_HOVER,
            text_color=WHITE,
            command=self.calibrate
        )
        self.cal_btn.pack(side="left", padx=5, pady=5)

        self.save_btn = ctk.CTkButton(
            button_frame,
            text="Save Run",
            fg_color=RED,
            hover_color=RED_HOVER,
            text_color=WHITE,
            command=self.save_run
        )
        self.save_btn.pack(side="left", padx=5, pady=5)

        # ----- FIGURE -----
        self.fig = Figure(figsize=(10, 6), facecolor=BG_BLACK)
        self.ax_pedals = self.fig.add_subplot(211)
        self.ax_imu = self.fig.add_subplot(212)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    # -------------------------------------------------

    def toggle_connection(self):
        if self.serial.running:
            self.serial.disconnect()
            self.connect_btn.configure(text="Connect")
        else:
            self.serial.connect()
            self.connect_btn.configure(text="Disconnect")

    def calibrate(self):
        self.serial.send("CAL_PEDALS")

    def on_serial_data(self, line):
        data = parse_line(line)
        if data:
            self.buffer.add(data)


    def _time_axis(self, length):
        return [i * SAMPLE_DT for i in range(length)]

    def _style_axis(self, ax):
        ax.set_facecolor(BG_BLACK)
        ax.tick_params(colors=WHITE)
        for spine in ax.spines.values():
            spine.set_color(WHITE)
        ax.grid(True, color="#333333")


    def _update_plot(self):
        self.ax_pedals.clear()
        self.ax_imu.clear()

        t_pedals = self._time_axis(len(self.buffer.gas))
        t_imu = self._time_axis(len(self.buffer.ax))

        self.ax_pedals.plot(t_pedals, self.buffer.gas, label="Gas", color="lime")
        self.ax_pedals.plot(t_pedals, self.buffer.brake, label="Brake", color="red")
        self.ax_pedals.set_title("Pedals", color=WHITE)
        self.ax_pedals.set_xlabel("Time (s)", color=WHITE)
        self.ax_pedals.set_ylabel("Pedal Position (%)", color=WHITE)
        self.ax_pedals.legend(facecolor=FRAME_BLACK, labelcolor=WHITE)
        self._style_axis(self.ax_pedals)

        # ---- IMU ----
        self.ax_imu.plot(t_imu, self.buffer.ax, label="Ax", color="cyan")
        self.ax_imu.plot(t_imu, self.buffer.ay, label="Ay", color="orange")
        self.ax_imu.plot(t_imu, self.buffer.az, label="Az", color="magenta")
        self.ax_imu.set_title("IMU Acceleration", color=WHITE)
        self.ax_imu.set_xlabel("Time (s)", color=WHITE)
        self.ax_imu.set_ylabel("Value (%)", color=WHITE)
        self.ax_imu.legend(facecolor=FRAME_BLACK, labelcolor=WHITE)
        self._style_axis(self.ax_imu)

        self.canvas.draw()
        self.after(50, self._update_plot)


    def save_run(self):
        base_dir = "saved"
        os.makedirs(base_dir, exist_ok=True)

        run_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        run_path = os.path.join(base_dir, run_name)
        os.makedirs(run_path)

        t_pedals = self._time_axis(len(self.buffer.gas))
        t_imu = self._time_axis(len(self.buffer.ax))

        # ---- Pedals ----
        pedal_fig = Figure(figsize=(8, 4), facecolor=BG_BLACK)
        ax1 = pedal_fig.add_subplot(111)
        ax1.plot(t_pedals, self.buffer.gas, label="Gas", color="lime")
        ax1.plot(t_pedals, self.buffer.brake, label="Brake", color="red")
        ax1.set_title("Pedals", color=WHITE)
        ax1.set_xlabel("Time (s)", color=WHITE)
        ax1.set_ylabel("Pedal Position (%)", color=WHITE)
        ax1.legend(facecolor=FRAME_BLACK, labelcolor=WHITE)
        ax1.grid(True, color="#333333")
        pedal_fig.savefig(os.path.join(run_path, "pedals.png"))

        # ---- IMU ----
        imu_fig = Figure(figsize=(8, 4), facecolor=BG_BLACK)
        ax2 = imu_fig.add_subplot(111)
        ax2.plot(t_imu, self.buffer.ax, label="Ax", color="cyan")
        ax2.plot(t_imu, self.buffer.ay, label="Ay", color="orange")
        ax2.plot(t_imu, self.buffer.az, label="Az", color="magenta")
        ax2.set_title("IMU Acceleration", color=WHITE)
        ax2.set_xlabel("Time (s)", color=WHITE)
        ax2.set_ylabel("Value (%)", color=WHITE)
        ax2.legend(facecolor=FRAME_BLACK, labelcolor=WHITE)
        ax2.grid(True, color="#333333")
        imu_fig.savefig(os.path.join(run_path, "imu.png"))

        print(f"Run saved to {run_path}")
