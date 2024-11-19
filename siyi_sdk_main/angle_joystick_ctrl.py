import sys
import os
import threading
import time
import tkinter as tk
from siyi_sdk import SIYISDK

class Joystick(tk.Canvas):
    def __init__(self, master, width=200, height=200, **kwargs):
        super().__init__(master, **kwargs)
        self.outer_circle_radius = 80
        self.inner_circle_radius = 30
        self.center = (self.winfo_reqwidth() / 2, self.winfo_reqheight() / 2)
        self.inner_circle_position = self.center
        self.outer_circle_color = "#000080"
        self.inner_circle_color = "#0000FF"

        self.create_oval(self.get_outer_circle_pos(), outline=self.outer_circle_color, width=2)
        self.inner_circle = self.create_oval(self.get_inner_circle_pos(), fill=self.inner_circle_color)

        self.bind("<Configure>", self.update_canvas)
        self.bind("<B1-Motion>", self.on_touch_move)

    def get_outer_circle_pos(self):
        return (
            self.center[0] - self.outer_circle_radius,
            self.center[1] - self.outer_circle_radius,
            self.center[0] + self.outer_circle_radius,
            self.center[1] + self.outer_circle_radius
        )

    def get_inner_circle_pos(self):
        return (
            self.inner_circle_position[0] - self.inner_circle_radius,
            self.inner_circle_position[1] - self.inner_circle_radius,
            self.inner_circle_position[0] + self.inner_circle_radius,
            self.inner_circle_position[1] + self.inner_circle_radius
        )

    def update_canvas(self, event=None):
        self.center = (self.winfo_width() / 2, self.winfo_height() / 2)
        self.coords(self.inner_circle, self.get_inner_circle_pos())

    def on_touch_move(self, event):
        distance = ((self.center[0] - event.x) ** 2 + (self.center[1] - event.y) ** 2) ** 0.5
        if distance <= self.outer_circle_radius:
            self.inner_circle_position = (event.x, event.y)
            self.coords(self.inner_circle, self.get_inner_circle_pos())

class GimbalControlApp(tk.Tk):
    def __init__(self):
        super().__init__()
        #self.parent = parent
        self.title("Gimbal Control")

        self.joystick = Joystick(self, width=200, height=200)
        self.joystick.pack(pady=20)

        self.cam = SIYISDK(server_ip="192.168.6.122", port=37260)
        self.connected = False
        self.connect_to_gimbal()

        # Initial yaw and pitch
        self.yaw = 0
        self.pitch = 0

        # Start updating gimbal in a separate thread
        self.stop_event = threading.Event()
        self.gimbal_thread = threading.Thread(target=self.gimbal_control_loop)
        self.gimbal_thread.start()

    def connect_to_gimbal(self):
        def connect():
            if self.cam.connect():
                self.connected = True
                print("Connected to gimbal")
            else:
                print("Failed to connect to gimbal")

        threading.Thread(target=connect).start()

    def gimbal_control_loop(self):
        while not self.stop_event.is_set():
            if self.connected:
                dx = (self.joystick.inner_circle_position[0] - self.joystick.center[0]) / self.joystick.outer_circle_radius
                dy = (self.joystick.inner_circle_position[1] - self.joystick.center[1]) / self.joystick.outer_circle_radius

                # Invert the controls
                self.yaw = int(-45 * dx)
                self.pitch = int(-90 * dy)  # Adjusted for correct pitch down movement

                self.cam.setGimbalRotation(self.yaw, self.pitch)
                print(f"Updated Gimbal Rotation to (Yaw: {self.yaw}, Pitch: {self.pitch})")
            else:
                print("Gimbal not connected")
            time.sleep(0.1)  # Update every 100ms

    def on_closing(self):
        self.stop_event.set()
        self.gimbal_thread.join()
        if self.connected:
            self.cam.disconnect()
            print("Disconnected from gimbal")
        self.destroy()


