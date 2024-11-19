import cv2
import socket
import pickle
import struct
import select
import errno,threading,time
#ser = serial.Serial('COM3', 115200, timeout=0.1)
import binascii
import socket
import struct
import sys
import time
from modules.utils import *
from siyi_sdk_main import siyi_sdk

# Define server IP and port
server_ip = "192.168.1.104"  # Update with your server IP
server_port = 5600
all_cam_port= 5601
# Maximum size for UDP datagram
MAX_DGRAM = 65507
recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
recv_sock.bind(('', server_port))
index=""

cam_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

HOST = '192.168.1.104'  # The server's hostname or IP address
PORT = 37260        # The port used by the server
try:
	cam_sock.connect((HOST, PORT))
	time.sleep(2)
except:
	pass
	
def send_frame_in_chunks(sock, data, addr):
    """
    Send frame data in chunks using UDP.
    """
    size = len(data)
    chunks = [data[i:i+MAX_DGRAM] for i in range(0, size, MAX_DGRAM)]
    for chunk in chunks:
        #print("addr")
        sock.sendto(chunk, addr)

def receive_message():
    """
    Receive messages from the server.
    """
    global recv_sock,index
    while True:
        try:
            #ready_to_read, _, _ = select.select([sock], [], [], 0)
            #for sock in ready_to_read:
            print("GGGGGGG")
            message, _ = recv_sock.recvfrom(1024)
            print("message",message)
            index= message.decode()
            print("Received message :",type(index), index == "cam1" )
        except socket.error as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                # A real error occurred
                print("Socket error:", e)
        #return None
t = threading.Thread(target=receive_message)
t.daemon=True
t.start()

def main():
    lock_mode = [0x55 ,0x66 ,0x01 ,0x01 ,0x00 ,0x00 ,0x00 ,0x0c ,0x03 ,0x57 ,0xfe]
    follow_mode = [0x55 ,0x66 ,0x01 ,0x01 ,0x00 ,0x00 ,0x00 ,0x0c ,0x04 ,0xb0 ,0x8e]
    zoom_in = [0x55 ,0x66 ,0x01 ,0x01 ,0x00 ,0x00 ,0x00 ,0x05 ,0x01 ,0x8d ,0x64]#zoom=1
    zoom_out = [0x55 ,0x66 ,0x01 ,0x01 ,0x00 ,0x00 ,0x00 ,0x05 ,0xFF ,0x5c ,0x6a]#zoom =-1
    absolute_zoom=[0x55 ,0x66 ,0x01 ,0x02 ,0x00 ,0x10 ,0x00 ,0x0f ,0x04 ,0x05 ,0x6b ,0x15]#4.5x
    ##gimbal_rotation = [ 0x55 ,0x66 ,0x01 ,0x02 ,0x00 ,0x00 ,0x00 ,0x07 ,0x64 ,0x64 ,0x3d ,0xcf]##gimbal_rotation 100 100
    gimbal_rotation = [0x55 ,0x66 ,0x01 ,0x04 ,0x00 ,0x00 ,0x00 ,0x0e ,0x00 ,0x00 ,0xff ,0xa6 ,0x3b ,0x11]###-90,0
    attitude_data=[0x55 ,0x66 ,0x01 ,0x00 ,0x00 ,0x00 ,0x00 ,0x0d ,0xe8 ,0x05]
    center = [0x55 ,0x66 ,0x01 ,0x01 ,0x00 ,0x00 ,0x00 ,0x08 ,0x01 ,0xd1 ,0x12]
    # Open camera capture
    global index
    #gst_str = "rtspsrc location=rtsp://192.168.6.121:8554/main.264 latency=0 ! decodebin ! videoconvert ! appsink"
    #gst_str = "rtsp://192.168.6.131:8554/main.264"
    cap = cv2.VideoCapture(0, cv2.CAP_GSTREAMER)  # Adjust camera index or URL as needed
    
    # Create UDP socket for sending
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Create UDP socket for receiving
    
    # Initial quality
    current_quality = 50  
    send_frame_flag=False
    all_cam_send_flag=False
    while True:
        # Read frame from camera
        ret, frame = cap.read()
        if not ret:
            break

        # Resize frame
        frame = cv2.resize(frame, (640, 480))
        '''
        ########
        cam=siyi_sdk.SIYISDK(server_ip="192.168.6.121", port=37260, debug=False)

        if not cam.connect():
            exit(1)
        cam.requestGimbalAttitude()
        print("Attitude: ", cam.getAttitude()) ###get yaw,pitch,roll
        #########
        '''
        if index == "cam1_360p":
            current_quality = 10
            print("360p !!!!!!!!",current_quality)
	
        elif index == "cam1_SD":
            current_quality = 30
            print("sd !!!!!!!!",current_quality)
	
        elif index == "cam1_HD":
            current_quality = 50
            print("hd !!!!!!!!",current_quality)
	
        elif index == "cam1_Full_HD":
            current_quality = 90
            print("fullhd !!!!!!!!",current_quality)
	
        elif index == "cam1_lock_mode":
            packet = bytearray(lock_mode)
            bytePacket = bytes(packet)
            cam_sock.sendall(bytePacket)
            time.sleep(0.2)
           
        elif index == "cam1_follow_mode":
            packet = bytearray(follow_mode)
            bytePacket = bytes(packet)
            cam_sock.sendall(bytePacket)
            time.sleep(0.2)
         
        elif index == "cam1_zoom_in":
            packet = bytearray(zoom_in)
            bytePacket = bytes(packet)
            cam_sock.sendall(bytePacket)
            time.sleep(0.2)
		    
        elif index == "cam1_zoom_out":
            packet = bytearray(zoom_out)
            bytePacket = bytes(packet)
            cam_sock.sendall(bytePacket)
            time.sleep(0.2)
		    
        elif index == "cam1_absolute_zoom":
            packet = bytearray(absolute_zoom)
            bytePacket = bytes(packet)
            cam_sock.sendall(bytePacket)
            time.sleep(0.2)
		    
        elif index == "cam1_gimbal_rotation":
            packet = bytearray(absolute_zoom)
            bytePacket = bytes(packet)
            cam_sock.sendall(bytePacket)
            time.sleep(0.2)
		    
        elif index == "cam1_center":
            packet = bytearray(absolute_zoom)
            bytePacket = bytes(packet)
            cam_sock.sendall(bytePacket)
            time.sleep(0.2)
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), current_quality])
        data = pickle.dumps(buffer)
    
        if index=="All_Camera":
            all_cam_send_flag=True
        else:
            all_cam_send_flag=False
        # Send frame data in chunks
        if index.startswith("cam1"): 
            #print("JJJJJ")
            send_frame_flag=True
            #print("@@@",send_frame_flag)
        else:
            send_frame_flag=False
            
        if(send_frame_flag):
           # print("JJJJ")
            send_frame_in_chunks(send_sock, data, (server_ip, server_port))
        if(all_cam_send_flag):
            send_frame_in_chunks(send_sock, data, (server_ip, all_cam_port))

        cv2.imshow('Client', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    send_sock.close()
    #recv_sock.close()

if __name__ == "__main__":
    main()
