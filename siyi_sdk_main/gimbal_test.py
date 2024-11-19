import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import threading
from siyi_sdk import SIYISDK
from joystick import Joystick

class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Camera Switcher")

        self.video_label = tk.Label(self.root)
        self.video_label.pack()

        self.btn_frame = tk.Frame(self.root)
        self.btn_frame.pack()

        self.cameras = [
            'rtspsrc location=rtsp://192.168.6.141:8554/main.264 latency=0 ! decodebin ! videoconvert ! appsink',
            'rtspsrc location=rtsp://192.168.6.161:8554/main.264 latency=0 ! decodebin ! videoconvert ! appsink'
        ]

        self.current_camera_index = 0
        self.cap = None
        self.stop_event = threading.Event()

        self.start_camera(self.current_camera_index)

        for i in range(len(self.cameras)):
            cam_btn = ttk.Button(self.btn_frame, text=f"Cam {i+1}", command=lambda i=i: self.select_camera(i))
            cam_btn.pack(side=tk.LEFT)

        self.quit_btn = ttk.Button(self.btn_frame, text="Quit", command=self.quit)
        self.quit_btn.pack(side=tk.LEFT)

        self.update_frame()

        # Joystick setup
        self.joystick = Joystick(self.root, width=200, height=200)
        self.joystick.pack(pady=20)

        # Gimbal control setup
        self.cam = SIYISDK(server_ip="192.168.6.141", port=37260)
        self.connected = False
        self.connect_to_gimbal()

        # Initial yaw and pitch
        self.yaw = 0
        self.pitch = 0

        # Start updating gimbal in a separate thread
        self.gimbal_thread = threading.Thread(target=self.gimbal_control_loop)
        self.gimbal_thread.start()

    def start_camera(self, index):
        if self.cap:
            self.cap.release()

        self.cap = cv2.VideoCapture(self.cameras[index], cv2.CAP_GSTREAMER)

        if not self.cap.isOpened():
            print(f"Failed to open camera {index + 1}")
        else:
            self.current_camera_index = index

    def select_camera(self, index):
        self.start_camera(index)

    def update_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.resize(frame, (720, 640))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)

        if not self.stop_event.is_set():
            self.root.after(10, self.update_frame)

    def quit(self):
        self.stop_event.set()
        if self.cap:
            self.cap.release()
        if self.connected:
            self.cam.disconnect()
        self.root.quit()
        self.root.destroy()

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

if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()

