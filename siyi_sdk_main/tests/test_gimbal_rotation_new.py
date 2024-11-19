import tkinter as tk
import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent_directory = os.path.dirname(current)
  
sys.path.append(parent_directory)
from siyi_sdk import SIYISDK

class GimbalControlApp:
    def __init__(self, root, server_ip="192.168.5.122", port=37260):
        self.root = root
        self.root.title("Gimbal Control")
        
        self.cam = SIYISDK(server_ip=server_ip, port=port)
        if not self.cam.connect():
            print("No connection")
            exit(1)

        # Initial yaw and pitch
        self.yaw = 0
        self.pitch = 0
        self.yaw_limit = (-45, 45)
        self.pitch_limit = (-90, 25)

        # Create buttons
        self.create_widgets()

    def create_widgets(self):
        self.yaw_up_button = tk.Button(self.root, text="Yaw Up", command=self.yaw_up)
        self.yaw_up_button.pack()

        self.yaw_down_button = tk.Button(self.root, text="Yaw Down", command=self.yaw_down)
        self.yaw_down_button.pack()

        self.pitch_up_button = tk.Button(self.root, text="Pitch Up", command=self.pitch_up)
        self.pitch_up_button.pack()

        self.pitch_down_button = tk.Button(self.root, text="Pitch Down", command=self.pitch_down)
        self.pitch_down_button.pack()

    def yaw_up(self):
        if self.yaw < self.yaw_limit[1]:
            self.yaw += 5
            self.update_gimbal()
        else:
            print("Yaw up limit reached")

    def yaw_down(self):
        if self.yaw > self.yaw_limit[0]:
            self.yaw -= 5
            self.update_gimbal()
        else:
            print("Yaw down limit reached")

    def pitch_up(self):
        if self.pitch < self.pitch_limit[1]:
            self.pitch += 5
            self.update_gimbal()
        else:
            print("Pitch up limit reached")

    def pitch_down(self):
        if self.pitch > self.pitch_limit[0]:
            self.pitch -= 5
            self.update_gimbal()
        else:
            print("Pitch down limit reached")

    def update_gimbal(self):
        self.cam.setGimbalRotation(self.yaw, self.pitch)
        print(f"Updated Gimbal Rotation to (Yaw: {self.yaw}, Pitch: {self.pitch})")

    def close(self):
        self.cam.disconnect()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = GimbalControlApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()
