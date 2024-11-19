import tkinter as tk
from tkinter import messagebox, ttk
import socket
import pickle
import threading
from PIL import Image, ImageTk
import cv2

# Define server IP and port
server_ip = "192.168.1.109"  # Update with your server IP
server_port = 5600
# Maximum size for UDP datagram
MAX_DGRAM = 65507

# Define client IPs for different cameras
camera_ips = {
    "Cam1": "192.168.1.109",  # Update with your Cam1 IP
    "Cam2": "192.168.1.105",  # Update with your Cam2 IP
    "Cam3": "192.168.1.106",  # Update with your Cam3 IP
}

client_ip = camera_ips["Cam1"]  # Default client IP


# Function to send messages to client
def send_message(message):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s_add = (client_ip, server_port)
    s.sendto(message.encode(), s_add)
    s.close()


# Function to handle gimbal control
def control_gimbal(direction):
    # Add actual gimbal control code here
    print(f"Gimbal move: {direction}")


# Function to handle video stream
def handle_video_stream(label, event):
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
    sock.bind((server_ip, server_port))

    while not event.is_set():
        try:
            frame = receive_frame(sock)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            # Update the UI in the main thread
            label.after(0, update_image, label, imgtk)
        except Exception as e:
            print(f"Error receiving frame: {e}")


def update_image(label, imgtk):
    label.imgtk = imgtk
    label.configure(image=imgtk)


# Function to create the main GUI
def create_gui():
    root = tk.Tk()
    root.title("Server Control Panel")
    root.geometry("800x600")

    def switch_to_camera_view():
        frame_camera.tkraise()
        stop_event.clear()
        threading.Thread(
            target=handle_video_stream, args=(label_camera, stop_event)
        ).start()

    def switch_to_map_view():
        frame_map.tkraise()
        stop_event.set()

    def switch_to_home():
        frame_home.tkraise()
        stop_event.set()

    def adjust_quality_low():
        send_message("reduce_quality")

    def adjust_quality_high():
        send_message("high_quality")

    def select_camera(event):
        global client_ip
        selected_camera = camera_select.get()
        client_ip = camera_ips[selected_camera]
        print(f"Selected camera: {selected_camera}, IP: {client_ip}")
        if(selected_camera=="Cam1"):
            send_message("cam1")
        elif(selected_camera=="Cam2"):
            send_message("cam2")
        if(selected_camera=="Cam3"):
            send_message("cam3")            

    # Home screen frame
    frame_home = tk.Frame(root)
    frame_home.grid(row=0, column=0, sticky="nsew")

    logo = Image.open(
        "/home/casr-3/Pictures/Screenshots/logo.png"
    )  # Update with the path to your logo
    logo = logo.resize((200, 200), Image.LANCZOS)
    logo = ImageTk.PhotoImage(logo)

    logo_label = tk.Label(frame_home, image=logo)
    logo_label.image = logo
    logo_label.pack(pady=20)

    # Dropdown menu for camera selection
    camera_select = ttk.Combobox(
        frame_home, values=list(camera_ips.keys()), state="readonly"
    )
    camera_select.set("Cam1")  # Default selection
    camera_select.bind("<<ComboboxSelected>>", select_camera)
    camera_select.pack(pady=10)

    btn_select_camera = tk.Button(
        frame_home, text="Select Camera", command=switch_to_camera_view
    )
    btn_select_camera.pack(pady=10)

    btn_view_map = tk.Button(frame_home, text="View Map", command=switch_to_map_view)
    btn_view_map.pack(pady=10)

    btn_exit = tk.Button(frame_home, text="Exit", command=root.quit)
    btn_exit.pack(pady=10)

    # Camera view frame
    frame_camera = tk.Frame(root)
    frame_camera.grid(row=0, column=1, sticky="nsew")

    label_camera = tk.Label(frame_camera)
    label_camera.pack(fill="both", expand=True)

    btn_quality_low = tk.Button(
        frame_camera, text="Low Quality", command=adjust_quality_low
    )
    btn_quality_low.pack(side="left", padx=10, pady=10)

    btn_quality_high = tk.Button(
        frame_camera, text="High Quality", command=adjust_quality_high
    )
    btn_quality_high.pack(side="left", padx=10, pady=10)

    btn_back_home = tk.Button(frame_camera, text="Home", command=switch_to_home)
    btn_back_home.pack(side="left", padx=10, pady=10)

    # Map view frame
    frame_map = tk.Frame(root)
    frame_map.grid(row=0, column=1, sticky="nsew")

    map_label = tk.Label(frame_map, text="Map View (to be implemented)")
    map_label.pack(pady=20)

    btn_back_home_map = tk.Button(frame_map, text="Home", command=switch_to_home)
    btn_back_home_map.pack(pady=10)

    # Gimbal control frame
    frame_gimbal = tk.Frame(frame_camera)
    frame_gimbal.pack(side="right", padx=20, pady=20)

    btn_gimbal_up = tk.Button(
        frame_gimbal, text="Up", command=lambda: control_gimbal("up")
    )
    btn_gimbal_up.grid(row=0, column=1)

    btn_gimbal_down = tk.Button(
        frame_gimbal, text="Down", command=lambda: control_gimbal("down")
    )
    btn_gimbal_down.grid(row=2, column=1)

    btn_gimbal_left = tk.Button(
        frame_gimbal, text="Left", command=lambda: control_gimbal("left")
    )
    btn_gimbal_left.grid(row=1, column=0)

    btn_gimbal_right = tk.Button(
        frame_gimbal, text="Right", command=lambda: control_gimbal("right")
    )
    btn_gimbal_right.grid(row=1, column=2)

    btn_gimbal_home = tk.Button(
        frame_gimbal, text="Home", command=lambda: control_gimbal("home")
    )
    btn_gimbal_home.grid(row=1, column=1)

    frame_home.tkraise()

    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))

    root.mainloop()


def on_closing(root):
    stop_event.set()
    root.destroy()


if __name__ == "__main__":
    stop_event = threading.Event()
    create_gui()
