
import cv2
import socket
import pickle
import struct
import select
import errno
# Define server IP and port
server_ip = "192.168.1.104"  # Update with your server IP
server_port = 5600

# Maximum size for UDP datagram
MAX_DGRAM = 65507

def send_frame_in_chunks(sock, data, addr):
    """
    Send frame data in chunks using UDP.
    """
    size = len(data)
    chunks = [data[i:i+MAX_DGRAM] for i in range(0, size, MAX_DGRAM)]
    for chunk in chunks:
        print(addr)
        sock.sendto(chunk, addr)

def receive_message(sock):
    """
    Receive messages from the server.
    """
    try:
        ready_to_read, _, _ = select.select([sock], [], [], 0)
        for sock in ready_to_read:
            message, _ = sock.recvfrom(1024)
            return message.decode()
    except socket.error as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            # A real error occurred
            print("Socket error:", e)
        return None

def main():
    # Open camera capture
    #gst_str = "rtspsrc location=rtsp://192.168.6.121:8554/main.264 latency=0 ! decodebin ! videoconvert ! appsink"
    cap = cv2.VideoCapture(0, cv2.CAP_GSTREAMER)  # Adjust camera index or URL as needed
    
    # Create UDP socket for sending
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Create UDP socket for receiving
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    recv_sock.bind(('0.0.0.0', server_port))

    # Initial quality
    current_quality = 50  

    while True:
        # Read frame from camera
        ret, frame = cap.read()
        if not ret:
            break

        # Resize frame
        frame = cv2.resize(frame, (640, 480))

        # Adjust quality based on received message
        
        message = receive_message(recv_sock)
        if message == "reduce_quality":
            current_quality = max(10, current_quality - 10)  # Ensure quality doesn't go below 10
            print("LOWWWW !!!!!!!!",current_quality)
        elif message == "high_quality":
            current_quality = min(100, current_quality + 10)  # Ensure quality doesn't exceed 100
            print("HIGH !!!!!!!!",current_quality)
        
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), current_quality])
        data = pickle.dumps(buffer)
    
        # Send frame data in chunks
        send_frame_in_chunks(send_sock, data, (server_ip, server_port))

        # Display frame
        cv2.imshow('Client', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    send_sock.close()
    recv_sock.close()

if __name__ == "__main__":
    main()
'''


import cv2
import socket
import pickle
import struct
import select
import errno

server_ip = "192.168.51.214"  # Update with your server IP
server_port = 5600
MAX_DGRAM = 65507

def send_frame_in_chunks(sock, data, addr):
    size = len(data)
    chunks = [data[i:i+MAX_DGRAM] for i in range(0, size, MAX_DGRAM)]
    for chunk in chunks:
        sock.sendto(chunk, addr)

def receive_message(sock):
    try:
        ready_to_read, _, _ = select.select([sock], [], [], 0)
        for s in ready_to_read:
            message, _ = s.recvfrom(1024)
            return message.decode()
    except socket.error as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            # A real error occurred
            print("Socket error:", e)
        return None
    
cap = cv2.VideoCapture("rtspsrc location=rtsp://192.168.6.121:8554/main.264 latency=0 ! decodebin ! videoconvert ! appsink",cv2.CAP_GSTREAMER)
#cap = cv2.VideoCapture(0,cv2.CAP_GSTREAMER)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('0.0.0.0', server_port))

if __name__ == "__main__":
    
    
    # Create UDP socket for receiving
    #recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setblocking(False)
    
    
    # Initial quality
    current_quality = 50 
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (640, 480))
        
        message = receive_message(s)
        if message == "reduce_quality":
            current_quality = max(10, current_quality - 10)  # Ensure quality doesn't go below 10
            print("LOWWWW !!!!!!!!",current_quality)
        elif message == "high_quality":
            current_quality = min(100, current_quality + 10)  # Ensure quality doesn't exceed 100
            print("HIGH !!!!!!!!",current_quality)
            
        ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
        data = pickle.dumps(buffer)
    
        # Send frame data in chunks
        send_frame_in_chunks(s, data, (server_ip, server_port))

        cv2.imshow('Client', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    s.close()
    
'''
