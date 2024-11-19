import tkinter as tk
from tkinter import messagebox, ttk
import socket
import pickle
import threading
from PIL import Image, ImageTk
import cv2
import time
#from server_qy_all_camera import *
import server_qy_all_camera
from tkinter import scrolledtext
import subprocess
import threading

# Define server IP and port
server_ip = "192.168.16.220" #"192.168.6.203"  # Update with your server IP
server_port = 5600

# Maximum size for UDP datagram
MAX_DGRAM = 65507
selected_camera = ""
# Define client IPs for different cameras
camera_ips = {
    "cam1": "192.168.6.252",  # Update with your Cam1 IP
    "cam2": "192.168.6.138",  # Update with your Cam2 IP
    "cam3": "192.168.6.214",
    "cam3": "192.168.6.154"# Update with your Cam3 IP
}
quality_array = ["360p", "SD", "HD", "Full_HD"]
quality = ""
client_ip = ""  # Default client IP
entry=""
current_host = None
ping_thread = None

def ping(host,text_widget):
    # Start a ping process
    process = subprocess.Popen(
        ['ping', host],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    print("ping",process)
    # Read the output line by line
    for line in process.stdout:
        # Insert the line into the text widget
        text_widget.insert(tk.END, line)
        # Scroll to the end of the text widget
        text_widget.see(tk.END)
    
    process.stdout.close()
    process.wait()

def start_ping(entry,text_widget):
    host = entry.get()
    print(host)
    if host:
        # Clear previous text
        text_widget.delete(1.0, tk.END)
        # Start the ping in a new thread
        threading.Thread(target=ping, args=(host,text_widget,), daemon=True).start()

# def start_ping(entry, text_widget):
#     global current_host, ping_thread
#     host = entry.get()
#     print(host)
#     if host != current_host:
#         # Stop the current ping thread
#         if ping_thread is not None:
#             ping_thread.cancel()
#             ping_thread = None
#         # Start the ping in a new thread
#         ping_thread = threading.Thread(target=ping, args=(host, text_widget,), daemon=True)
#         ping_thread.start()
#         current_host = host

# def ping(host, text_widget):
#     while True:
#         try:
#             output = subprocess.check_output(["ping", "-c", "4", host]).decode("utf-8")
#             text_widget.insert(tk.END, output)
#             text_widget.see(tk.END)
#             time.sleep(1)
#         except subprocess.CalledProcessError:
#             text_widget.insert(tk.END, f"Ping to {host} failed\n")
#             text_widget.see(tk.END)
#             time.sleep(1)

# Function to send messages to client
def send_message(message):
    global selected_camera
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_ip=camera_ips[selected_camera]
    print("client_ip",client_ip,server_port,message)
    s_add = (client_ip, server_port)
    s.sendto(message.encode(), s_add)
    print("KKKK")
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
    
# def gimbal_ctrl_message(message):
#     global selected_camera
#     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     client_ip=camera_ips[selected_camera]
#     print("client_ip",client_ip,gimbal_server_port)
#     s_add = (client_ip, gimbal_server_port)
#     s.sendto(message.encode(), s_add)
#     s.close()

# # Function to handle gimbal control
# def control_gimbal(direction):
#     print(f"Gimbal move: {direction}")

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
            
            # Get label dimensions
            label_width = label.winfo_width()
            label_height = label.winfo_height()
            
            # Resize frame to fit label dimensions
            frame = cv2.resize(frame, (label_width, label_height))
            
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            label.after(0, update_image, label, imgtk)
        except Exception as e:
            print(f"Error receiving frame: {e}")

def update_image(label, imgtk):
    label.imgtk = imgtk
   
    label.configure(image=imgtk)

        
def on_closing(root):
    
    stop_event.set()
    root.destroy()
    
def create_gui():
    global entry
    root = tk.Tk()
    #root.attributes('-fullscreen', True)
    
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width}x{screen_height}")

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    #root.grid_columnconfigure(1, weight=1)
    root.configure(bg="#F5F5F5")
    root.title("Server Control Panel")
    #root['bg'] = '#ff2200'
    #root.geometry("800x600")
    
    

    def switch_to_camera_view():
        frame_camera.tkraise()
        stop_event.set()
        stop_event.clear()
        threading.Thread(
            target=handle_video_stream, args=(label_camera, stop_event)
        ).start()
        
    def switch_to_all_camera_view():
        global camera_ips
        frame_camera_1.tkraise()
        stop_event.clear()
        stop_event.set()
        switch_cam_message("All_Camera")
        selected_cameras = list(camera_ips.keys()) 
        server_qy_all_camera.create_camera_frames(frame_camera_1,selected_cameras)


    '''
    def switch_to_home():
        #frame_home.tkraise()
        #back to home ...
        print("back to home ...")
    
    '''   
    def change_quality(event=None):
        global quality, selected_camera
        quality = Quality.get()
        print("quality-------->",quality)
        msg = f'{selected_camera}_{quality}'
        print("msg",msg)
        send_message(msg)  
    '''
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
    '''      
    def select_camera(event):
        global client_ip, selected_camera
        selected_camera = camera_select.get()
        client_ip = camera_ips[selected_camera]
        print("@@@@@@@@@@@client_ip",client_ip)
        switch_cam_message(selected_camera)
        
        
    frame_home = tk.Frame(root,bg="#F5F5F5")
    frame_home.grid(row=1, column=0, sticky="nsew")
    print("cl   ient_ip",client_ip)

    style = ttk.Style()
    style.configure("TCombobox", fieldbackground="lightblue", background="#F5F5F5")


    camera_select = ttk.Combobox(
        frame_home, values=list(camera_ips.keys()), state="readonly", style="TCombobox"
    )
    camera_select.set("select_camera")  # Default selection
    camera_select.bind("<<ComboboxSelected>>", select_camera)
    camera_select.pack(side="left",padx=10,pady=10)
    
    Quality = ttk.Combobox(
        frame_home, values=quality_array, state="readonly", style="TCombobox"
    )
    Quality.set(quality_array[2])   # Default selection
    Quality.bind("<<ComboboxSelected>>", change_quality)
    Quality.pack(side="left",padx=10,pady=10)
    print("Quality",Quality)

    btn_select_camera = tk.Button(
        frame_home, text="Select Camera",bg="#F5F5F5", command=switch_to_camera_view
    )
    btn_select_camera.pack(side="left",padx=10,pady=10)
    
    btn_select_camera = tk.Button(
        frame_home, text="All Camera",bg="#F5F5F5", command=switch_to_all_camera_view
    )
    btn_select_camera.pack(side="left",padx=10,pady=10)

    frame_t = tk.Frame(root,bg="#F5F5F5")
    frame_t.grid(row=2, column=0, pady=10)  # Use grid instead of pack

    entry_label = tk.Label(frame_t, text="Enter host to ping:",bg="#F5F5F5")
    entry_label.grid(row=0, column=0, padx=5)

    entry = tk.Entry(frame_t,bg="#F5F5F5")
    entry.grid(row=0, column=1, padx=5)
    
    text_widget = scrolledtext.ScrolledText(root, width=40, height=20)
    text_widget.grid(row=0, column=1, sticky="nsew")

    ping_button = tk.Button(frame_t, text="Start Ping",bg="#F5F5F5", command=lambda:start_ping(entry,text_widget))
    ping_button.grid(row=0, column=2, padx=5)


    # camera ....
    frame_camera = tk.Frame(root,bg="#F5F5F5")
    frame_camera.grid(row=0, column=0, sticky="nsew")
    
    frame_camera_1 = tk.Frame(root,bg="#F5F5F5")
    frame_camera_1.grid(row=0, column=0, sticky="nsew")
    
    label_camera = tk.Label(frame_camera)
    label_camera.pack(fill="both", expand=True)
 
    

    btn_back_home = tk.Button(frame_home, text="Exit",bg="#F5F5F5", command=root.quit)
    btn_back_home.pack(side="left", padx=10, pady=10)



    frame_home.tkraise()
    root.protocol("WM_DELETE_WINDOW", on_closing)

    #root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root, gimbal_app))
    root.mainloop()



if __name__ == "__main__":
    stop_event = threading.Event()
    create_gui()

