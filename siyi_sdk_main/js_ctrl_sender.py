import socket
import tkinter as tk
import threading
import time

# Define the UDP socket for sending data
js_sender_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
js_sender_sock_address = ('', 12009)  # Receiver address

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
        self.title("Gimbal Control")

        self.joystick = Joystick(self, width=200, height=200)
        self.joystick.pack(pady=20)

        # Initial yaw and pitch
        self.yaw = 0
        self.pitch = 0

        # Start updating gimbal in a separate thread
        self.stop_event = threading.Event()
        self.gimbal_thread = threading.Thread(target=self.gimbal_control_loop, daemon=True)
        self.gimbal_thread.start()

    def gimbal_control_loop(self):
        while not self.stop_event.is_set():
            dx = (self.joystick.inner_circle_position[0] - self.joystick.center[0]) / self.joystick.outer_circle_radius
            dy = (self.joystick.inner_circle_position[1] - self.joystick.center[1]) / self.joystick.outer_circle_radius

            # Invert the controls
            self.yaw = int(-45 * dx)
            self.pitch = int(-90 * dy)  # Adjusted for correct pitch down movement
            msg = f"{self.yaw},{self.pitch}"
            js_sender_sock.sendto(msg.encode(), js_sender_sock_address)
            print(f"Sent Gimbal Rotation (Yaw: {self.yaw}, Pitch: {self.pitch})")
            time.sleep(0.1)  # Update every 100ms

    def on_closing(self):
        self.stop_event.set()
        self.gimbal_thread.join()
        self.destroy()

if __name__ == "__main__":
    app = GimbalControlApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()

