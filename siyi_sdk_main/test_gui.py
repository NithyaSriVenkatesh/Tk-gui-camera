import tkinter as tk
from tkinter import ttk
import socket
import pickle
import threading
from PIL import Image, ImageTk
import cv2
import numpy as np

# Configuration
CONFIG_FILE = 'config.json'
PIECE_WIDTH = 320
PIECE_HEIGHT = 240
RESIZE_FACTOR = 0.5
FPS = 30

# Define server IP and port
server_ip = "192.168.6.203"  # Update with your server IP
server_port = 5600
MAX_DGRAM = 65507

camera_ips = {
    "cam1": "192.168.6.137",  # Update with your Cam1 IP
    "cam2": "192.168.6.214",  # Update with your Cam2 IP
    "cam3": "192.168.6.153",  # Update with your Cam3 IP
}

quality_array = ["360p", "SD", "HD", "Full_HD"]

def read_json(file):
    return {
        'camera_url': [
            0,  # Default webcam
            
        ]
    }

def write_json(file, data):
    pass

class CameraStream:
    def __init__(self, camera_ips):
        self.camera_ips = camera_ips
        self.cap_list = [cv2.VideoCapture(url) for url in camera_ips.values()]
        self.ret_image = [None] * len(camera_ips)
        self.running = True
        self.start_streams()

    def start_streams(self):
        for i in range(len(self.cap_list)):
            threading.Thread(target=self.receive_frame, args=(i,)).start()

    def receive_frame(self, index):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((server_ip, server_port + index))
        while self.running:
            data = b""
            while True:
                segment, _ = sock.recvfrom(MAX_DGRAM)
                data += segment
                if len(segment) < MAX_DGRAM:
                    break
            frame = pickle.loads(data)
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
            self.ret_image[index] = frame

    def stop(self):
        self.running = False
        for cap in self.cap_list:
            cap.release()

class VideoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Camera Viewer")

        self.setting = read_json(CONFIG_FILE)
        self.camera_list = list(camera_ips.keys())

        self.image_no_camera = np.zeros((PIECE_HEIGHT, PIECE_WIDTH, 3), dtype=np.uint8)  # Use a black image for no camera
        self.image_no_camera_small = cv2.resize(self.image_no_camera, (PIECE_WIDTH, PIECE_HEIGHT))

        self.class_main = CameraStream(camera_ips)

        self.canvas = tk.Canvas(root, width=960, height=720)
        self.canvas.pack()

        self.update_frame()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_frame(self):
        frame = self.get_frame()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
        self.canvas.image = imgtk
        self.root.after(int(1000 / FPS), self.update_frame)

    def get_frame(self):
        def get_piece_img(ind):
            if ind >= len(self.class_main.ret_image) or self.class_main.ret_image[ind] is None:
                return self.image_no_camera_small
            else:
                return cv2.resize(self.class_main.ret_image[ind], (PIECE_WIDTH, PIECE_HEIGHT))

        # Adjust layout for multiple cameras
        imgs = [get_piece_img(i) for i in range(len(self.camera_list))]
        num_cams = len(imgs)
        if num_cams == 1:
            frame = imgs[0]
        elif num_cams == 2:
            frame = np.concatenate(imgs, axis=1)
        elif num_cams == 4:
            frame = np.concatenate((np.concatenate((imgs[0], imgs[1]), axis=1),
                                    np.concatenate((imgs[2], imgs[3]), axis=1)), axis=0)
        else:
            # Default to a single row of images for any other number
            frame = np.concatenate(imgs, axis=1)

        return frame

    def on_closing(self):
        self.class_main.stop()
        self.root.destroy()

class ControlPanelApp:
    def __init__(self):
        print("%%%%%%")    	 
        self.root = root
        self.video_app = None
        self.camera_ips = camera_ips
        print("KKK")
        self.create_gui()

    def create_gui(self):
        self.root.title("Server Control Panel")
        self.root.geometry("1200x800")

        self.frame_home = tk.Frame(self.root)
        self.frame_home.grid(row=0, column=0, sticky="nsew")

        self.camera_select = ttk.Combobox(self.frame_home, values=list(camera_ips.keys()), state="readonly")
        self.camera_select.set("select_camera")
        self.camera_select.bind("<<ComboboxSelected>>", self.select_camera)
        self.camera_select.pack(side="left", padx=10, pady=10)

        self.quality_select = ttk.Combobox(self.frame_home, values=quality_array, state="readonly")
        self.quality_select.set(quality_array[2])
        self.quality_select.bind("<<ComboboxSelected>>", self.change_quality)
        self.quality_select.pack(side="left", padx=10, pady=10)

        self.btn_select_camera = tk.Button(self.frame_home, text="Select Camera", command=self.switch_to_camera_view)
        self.btn_select_camera.pack(side="left", padx=10, pady=10)

        self.frame_camera = tk.Frame(self.root)
        self.frame_camera.grid(row=0, column=0, sticky="nsew")

        self.label_camera = tk.Label(self.frame_camera)
        self.label_camera.pack(fill="both", expand=True)

        self.frame_home.tkraise()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def select_camera(self, event):
        selected_camera = self.camera_select.get()
        print(f"Selected camera: {selected_camera}")

    def change_quality(self, event):
        selected_quality = self.quality_select.get()
        print(f"Selected quality: {selected_quality}")

    def switch_to_camera_view(self):
        self.frame_camera.tkraise()
        if not self.video_app:
            self.video_app = VideoApp(self.root)

    def on_closing(self):
        if self.video_app:
            self.video_app.on_closing()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ControlPanelApp()
    root.mainloop()

