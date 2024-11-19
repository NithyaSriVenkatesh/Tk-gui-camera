from flask import Flask, Response
import cv2, time
from flask_cors import CORS
import pickle
import socket

app = Flask(_name_)
CORS(app)
flag = 0
# cap = cv2.VideoCapture("rtsp://192.168.5.122:8554/main.264", cv2.CAP_FFMPEG)
#############################
server_ip = "192.168.6.203"  # Update with your server IP
server_port = 5600

# Maximum size for UDP datagram
MAX_DGRAM = 65507
selected_camera = ""
# Define client IPs for different cameras
camera_ips = {
    "cam1": "192.168.6.137",  # Update with your Cam1 IP
    "cam2": "192.168.6.214",  # Update with your Cam2 IP
    "cam3": "192.168.6.153",  # Update with your Cam3 IP
}
quality_array = ["360p", "SD", "HD", "Full_HD"]
quality = ""
client_ip = ""  # Default client IP
    
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


########################################
# Function to generate video frames
def generate_frames():
    print("Runningggggggggg")
    while True:
        frame = receive_frame()
        yield (b"--frame\r\n" b"Content-Type: image/jpg\r\n\r\n" + frame + b"\r\n\r\n")


@app.route("/")
def index():
    return "RTSP Stream Server"


@app.route("/video_1")
def video_1():
    # global flag
    # try:
    #     flag = 1
    #     time.sleep(0.1)
    switch_cam_message("cam1")
    return Response(
        # generate_frames("rtsp://192.168.6.161:8554/main.264"),
        generate_frames(),
        
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )
    # except Exception as e:
    #     print("Errorrr")
    #     return str(e)


@app.route("/video_2")
def video_2():
    switch_cam_message("cam2")
    
    return Response(
        generate_frames(),
        # generate_frames(0),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )
   


# @app.route("/video_3")
# def video_3():
#     try:
#         flag = 1
#         return Response(
#             generate_frames("rtsp://192.168.6.124:8554/main.264"),
#             # generate_frames(0),
#             mimetype="multipart/x-mixed-replace; boundary=frame",
#         )
#     except Exception as e:
#         return str(e)


if _name_ == "_main_":
    # app.run(host="192.168.0.104", port=int(8000), ssl_context="adhoc")
    app.run(host="192.168.6.21", port=int(8000), debug=True)
