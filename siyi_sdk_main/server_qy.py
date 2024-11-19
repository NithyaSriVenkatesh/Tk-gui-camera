import tkinter as tk
from tkinter import messagebox, ttk
import socket
import pickle
import threading
from PIL import Image, ImageTk
import cv2
import time

# Define server IP and port
server_ip = "192.168.6.203"  # Update with your server IP
server_port = 5600
gimbal_server_port = 5700
# Maximum size for UDP datagram
MAX_DGRAM = 65507
selected_camera = ""
# Define client IPs for different cameras
camera_ips = {
    "cam1": "192.168.6.151",  # Update with your Cam1 IP
    "cam2": "192.168.6.152",  # Update with your Cam2 IP
    "cam3": "192.168.6.153",  # Update with your Cam3 IP
}

client_ip = ""  # Default client IP

# Function to send messages to client
def send_message(message):
    global selected_camera
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_ip=camera_ips[selected_camera]
    print("client_ip",client_ip,server_port)
    s_add = (client_ip, server_port)
    s.sendto(message.encode(), s_add)
    s.close()

def switch_cam_message(message):
    global selected_camera
    for i,x in enumerate(camera_ips):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_ip=camera_ips[x]
        print("client_ip",client_ip,server_port,message)
        s_add = (client_ip, server_port)
        s.sendto(message.encode(), s_add)
        s.close()
    
def gimbal_ctrl_message(message):
    global selected_camera
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_ip=camera_ips[selected_camera]
    print("client_ip",client_ip,gimbal_server_port)
    s_add = (client_ip, gimbal_server_port)
    s.sendto(message.encode(), s_add)
    s.close()

# Function to handle gimbal control
def control_gimbal(direction):
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
            label.after(0, update_image, label, imgtk)
        except Exception as e:
            print(f"Error receiving frame: {e}")

def update_image(label, imgtk):
    label.imgtk = imgtk
    label.configure(image=imgtk)

class Joystick(tk.Canvas):
    def __init__(self, parent, width=200, height=200):
        super().__init__(parent, width=width, height=height, bg="white")
        self.center = (width // 2, height // 2)
        self.outer_circle_radius = min(self.center) - 10
        self.inner_circle_radius = self.outer_circle_radius // 3
        self.inner_circle_position = self.center
        self.create_oval(self.get_outer_circle_pos(), outline="#000080", width=2)
        self.inner_circle = self.create_oval(self.get_inner_circle_pos(), fill="#0000FF")
        self.bind("<B1-Motion>", self.on_touch_move)

    def get_outer_circle_pos(self):
        return (
            self.center[0] - self.outer_circle_radius,
            self.center[1] - self.outer_circle_radius,
            self.center[0] + self.outer_circle_radius,
            self.center[1] + self.outer_circle_radius,
        )

    def get_inner_circle_pos(self):
        return (
            self.inner_circle_position[0] - self.inner_circle_radius,
            self.inner_circle_position[1] - self.inner_circle_radius,
            self.inner_circle_position[0] + self.inner_circle_radius,
            self.inner_circle_position[1] + self.inner_circle_radius,
        )

    def on_touch_move(self, event):
        distance = ((self.center[0] - event.x) ** 2 + (self.center[1] - event.y) ** 2) ** 0.5
        if distance <= self.outer_circle_radius:
            self.inner_circle_position = (event.x, event.y)
            self.coords(self.inner_circle, self.get_inner_circle_pos())

class GimbalControlApp:
    def __init__(self, joystick):
        print("LLLLLL")
        self.joystick = joystick

        # Initial yaw and pitch
        self.yaw = 0
        self.pitch = 0

        # Start updating gimbal in a separate thread
        self.stop_event = threading.Event()
        self.gimbal_thread = threading.Thread(target=self.gimbal_control_loop, daemon=True)
        self.gimbal_thread.start()

    def gimbal_control_loop(self):
        global selected_camera
        while not self.stop_event.is_set():
            #print("KK")
            dx = (self.joystick.inner_circle_position[0] - self.joystick.center[0]) / self.joystick.outer_circle_radius
            dy = (self.joystick.inner_circle_position[1] - self.joystick.center[1]) / self.joystick.outer_circle_radius

            # Invert the controls
            self.yaw = int(-45 * dx)
            self.pitch = int(-90 * dy)  # Adjusted for correct pitch down movement
            msg = f"rotation,{self.yaw},{self.pitch}"
            print("msg",msg)    
            if selected_camera!="":
                #gimbal_ctrl_message(msg)
                pass
            #print(f"Sent Gimbal Rotation (Yaw: {self.yaw}, Pitch: {self.pitch})")
            time.sleep(0.1)  # Update every 100ms

    def stop(self):
        self.stop_event.set()
        self.gimbal_thread.join()

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
        #frame_home.tkraise()
        #stop_event.set()
        print("home")

    def adjust_quality_low():
        global selected_camera
        msg = f'{selected_camera}_reduce_quality'
        print("msg",msg)
        send_message(msg)

    def adjust_quality_high():
        global selected_camera
        msg = f'{selected_camera}_high_quality'
        print("msg",msg)
        send_message(msg)
    
    def zoom_in():
        global selected_camera
        msg = 'zoom_in'
        print("msg",msg)
        gimbal_ctrl_message(msg)
    
    def zoom_out():
        global selected_camera
        msg = 'zoom_out'
        print("msg",msg)
        gimbal_ctrl_message(msg)

    def record():
        global selected_camera
        msg = 'record'
        print("msg",msg)
        gimbal_ctrl_message(msg)
            
    def select_camera(event):
        global client_ip, selected_camera
        selected_camera = camera_select.get()
        client_ip = camera_ips[selected_camera]
        print("@@@@@@@@@@@client_ip",client_ip)
        switch_cam_message(selected_camera)
        
    frame_home = tk.Frame(root)
    frame_home.grid(row=0, column=0, sticky="nsew")
    print("client_ip",client_ip)
    logo = Image.open("/home/casr-3/Pictures/Screenshots/logo.png")  # Update with the path to your logo
    logo = logo.resize((200, 200), Image.LANCZOS)
    logo = ImageTk.PhotoImage(logo)

    logo_label = tk.Label(frame_home, image=logo)
    logo_label.image = logo
    logo_label.pack(pady=20)

    camera_select = ttk.Combobox(
        frame_home, values=list(camera_ips.keys()), state="readonly"
    )
    camera_select.set("cam1")  # Default selection
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
 
    # camera ....
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

    btn_zoom_in = tk.Button(frame_camera, text="Zoom In", command=zoom_in)
    btn_zoom_in.pack(side="left", padx=10, pady=10)

    btn_zoom_out = tk.Button(frame_camera, text="Zoom Out", command=zoom_out)
    btn_zoom_out.pack(side="left", padx=10, pady=10)

    btn_record = tk.Button(frame_camera, text="Record", command=record)
    btn_record.pack(side="left", padx=10, pady=10)
    
    btn_back_home = tk.Button(frame_camera, text="Home", command=switch_to_home)
    btn_back_home.pack(side="left", padx=10, pady=10)

    frame_map = tk.Frame(root)
    frame_map.grid(row=0, column=1, sticky="nsew")

    map_label = tk.Label(frame_map, text="Map View (to be implemented)")
    map_label.pack(pady=20)

    btn_back_home_map = tk.Button(frame_map, text="Home", command=switch_to_home)
    btn_back_home_map.pack(pady=10)

    # Gimbal control frame
    canva_gimbal = tk.Canvas(frame_camera)
    canva_gimbal.pack(padx=20, pady=20)

    # Add the Joystick
    joystick = Joystick(frame_camera)
    joystick.pack(pady=20)

    # Initialize GimbalControlApp with the joystick
    gimbal_app = GimbalControlApp(joystick)

    frame_home.tkraise()

    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root, gimbal_app))
    root.mainloop()

def on_closing(root, gimbal_app):
    gimbal_app.stop()
    stop_event.set()
    root.destroy()

if __name__ == "__main__":
    stop_event = threading.Event()
    create_gui()

