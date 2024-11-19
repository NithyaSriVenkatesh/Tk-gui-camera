import tkinter as tk
import socket
import pickle
import threading
from PIL import Image, ImageTk
import cv2

# Define server IP and ports for different cameras
server_ip = "192.168.6.203"
server_ports = {
    "cam1": 5601,
    "cam2": 5602,
    "cam3": 5603,
    # Add more cameras as needed
}

# Maximum size for UDP datagram
MAX_DGRAM = 65507

# Define client IPs for different cameras
camera_ips = {
    "cam1": "192.168.6.252",
    "cam2": "192.168.6.138",
    "cam2": "192.168.6.214",
    
}

# Global variables
selected_cameras = []  # To store selected cameras
# Default quality
stop_events = []  # To store stop events for each camera

def update_image(label, imgtk):
    label.imgtk = imgtk
   
    label.configure(image=imgtk)
# Function to handle video stream for cam1
def handle_video_stream1(label, event):
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
    sock.bind((server_ip, server_ports["cam1"]))

    while not event.is_set():
        try:
            frame = receive_frame(sock)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Resize frame to fit label dimensions
            label_width = 640
            label_height = 480
            frame = cv2.resize(frame, (label_width, label_height))

            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            
            label.after(0, update_image, label, imgtk)

            # Update label with the new image
            label.imgtk = imgtk
            label.configure(image=imgtk)

        except Exception as e:
            print(f"Error receiving frame: {e}")

# Function to handle video stream for cam2
def handle_video_stream2(label, event):
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
    sock.bind((server_ip, server_ports["cam2"]))

    while not event.is_set():
        try:
            frame = receive_frame(sock)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Resize frame to fit label dimensions
            label_width = 640
            label_height = 480
            frame = cv2.resize(frame, (label_width, label_height))

            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            label.after(0, update_image, label, imgtk)
            # Update label with the new image
            label.imgtk = imgtk
            label.configure(image=imgtk)

        except Exception as e:
            print(f"Error receiving frame: {e}")

# Function to handle video stream for cam3
def handle_video_stream3(label, event):
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
    sock.bind((server_ip, server_ports["cam3"]))

    while not event.is_set():
        try:
            frame = receive_frame(sock)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Resize frame to fit label dimensions
            label_width = 640
            label_height = 480
            frame = cv2.resize(frame, (label_width, label_height))

            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            label.after(0, update_image, label, imgtk)
            # Update label with the new image
            label.imgtk = imgtk
            label.configure(image=imgtk)

        except Exception as e:
            print(f"Error receiving frame: {e}")
def switch_to_camera_view():
    global selected_cameras
    selected_cameras = list(camera_ips.keys())  # Select all cameras
    create_camera_frames()

def  create_camera_frames(root,cameras):
    print("EWRWRWEWERWTERT")
    global selected_cameras, stop_events
    selected_cameras=cameras
    stop_events = []  # Reset stop events
    print("selected_cameras-------------",selected_cameras)
    # Create frames for each camera in selected_cameras
    for i, camera in enumerate(selected_cameras):
        
        row = i // 3  # 3 columns per row
        col = i % 3   # Calculate column position
        print("!!!!!!!!!!!!",i,camera)

        frame_camera = tk.Frame(root, width=640, height=480, borderwidth=2, relief="groove")
        frame_camera.grid(row=row, column=col, padx=5, pady=5)
        print("jjjjjjjjj")

        label_camera = tk.Label(frame_camera)
        label_camera.pack(fill="both", expand=True)
        print("stop@@@@@@@@@@")
        stop_event = threading.Event()
        print("stop",stop_event)
        stop_events.append(stop_event)
        print("stopsssss",stop_events)

        if camera == "cam1":
            print("HELLLOOOOOO")
            threading.Thread(target=handle_video_stream1, args=(label_camera, stop_event)).start()
        elif camera == "cam2":
            threading.Thread(target=handle_video_stream2, args=(label_camera, stop_event)).start()
        elif camera == "cam3":
            threading.Thread(target=handle_video_stream3, args=(label_camera, stop_event)).start()
    # Adjust grid weights to make the layout responsive
    num_rows = (len(selected_cameras) // 3) + 1  # Calculate number of rows needed
    for row in range(num_rows):
        root.grid_rowconfigure(row, weight=1)
    for col in range(3):
        root.grid_columnconfigure(col, weight=1)
        

def on_closing(root):
    for event in stop_events:
        event.set()  # Stop all video streams
    #root.destroy()

def main():
    global root
    root = tk.Tk()
    root.title("Multiple Camera Viewer")
    root.geometry("1000x800")
    
    frame_home = tk.Frame(root)
    frame_home.grid(row=1, column=0, sticky="nsew")
    
    #switch_to_camera_view()

    #btn_all_cameras = tk.Button(frame_home, text="All Cameras", command=switch_to_camera_view)
    #btn_all_cameras.grid(row=0, column=0, pady=10, padx=10, columnspan=3)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
