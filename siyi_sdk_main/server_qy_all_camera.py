import tkinter as tk
import socket
import pickle
import threading
from PIL import Image, ImageTk
import cv2

# Define server IP and ports for different cameras
server_ip = "192.168.6.220"
server_ports = {
    "cam2": 5602,
    "cam8": 5608,
    "cam9": 5609,
    "cam13": 5613,
    "cam15": 5615
    # Add more cameras as needed
}

# Maximum size for UDP datagram
MAX_DGRAM = 65507

# Define client IPs for different cameras
camera_ips = {
    "cam2": "192.168.6.152",
    "cam8": "192.168.6.158",
    "cam9": "192.168.6.159",
    "cam13": "192.168.6.163",
    "cam15": "192.168.6.165"
}

# Global variables
selected_cameras = []  # To store selected cameras
stop_events = []  # To store stop events for each camera
camera_threads = []  # To store camera threads
camera_frames = {}  # To store camera frames and labels

def update_image(label, imgtk):
    label.imgtk = imgtk
    label.configure(image=imgtk)

def handle_video_stream(label, port, event):
    def receive_frame(sock):
        data = b""
        while True:
            segment, _ = sock.recvfrom(MAX_DGRAM)
            data += segment
            if len(segment) < MAX_DGRAM:
                break
        frame = pickle.loads(data)
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        return frame

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((server_ip, port))

    while not event.is_set():
        try:
            frame = receive_frame(sock)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Resize frame to fit label dimensions
            label_width = 720
            label_height = 480
            frame = cv2.resize(frame, (label_width, label_height))

            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            label.after(0, update_image, label, imgtk)

        except Exception as e:
            print(f"Error receiving frame: {e}")

def clear_video_frames():
    for stop_event in stop_events:
        stop_event.set()  # Stop all video streams

    for frame in camera_frames.values():
        frame['label'].config(image='')

    stop_events.clear()
    camera_threads.clear()

def create_camera_frames(root, cameras):
    global selected_cameras, stop_events, camera_threads, camera_frames

    selected_cameras = ["cam2", "cam5", "cam8",  "cam9", "cam13", "cam15"]  # Example selected cameras
    clear_video_frames()  # Clear any existing video frames

    # Create frames for each camera in selected_cameras
    for i, camera in enumerate(selected_cameras):
        row = i // 3  # 2 columns per row
        col = i % 3   # Calculate column position

        if camera not in camera_frames:
            frame_camera = tk.Frame(root, width=720, height=480, borderwidth=2, relief="groove")
            frame_camera.grid(row=row, column=col, padx=3, pady=3)

            label_camera = tk.Label(frame_camera)
            label_camera.pack(fill="both", expand=True)

            camera_frames[camera] = {'frame': frame_camera, 'label': label_camera}
        else:
            frame_camera = camera_frames[camera]['frame']
            label_camera = camera_frames[camera]['label']
            frame_camera.grid(row=row, column=col, padx=3, pady=3)

        stop_event = threading.Event()
        stop_events.append(stop_event)

        port = server_ports.get(camera)
        if port:
            thread = threading.Thread(target=handle_video_stream, args=(label_camera, port, stop_event))
            camera_threads.append(thread)
            thread.start()

    # Adjust grid weights to make the layout responsive
    num_rows = (len(selected_cameras) // 3) + 1  # Calculate number of rows needed
    for row in range(num_rows):
        root.grid_rowconfigure(row, weight=1)
    for col in range(3):
        root.grid_columnconfigure(col, weight=1)

def on_closing(root):
    for event in stop_events:
        event.set()  # Stop all video streams
    root.destroy()

def main():
    global root
    root = tk.Tk()
    root.title("Multiple Camera Viewer")
    root.geometry("1000x800")

    create_camera_frames()
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))
    root.mainloop()

if __name__ == "__main__":
    main()

