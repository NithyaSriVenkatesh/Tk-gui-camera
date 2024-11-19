import socket
import threading
import time
from siyi_sdk import SIYISDK

# Define the UDP socket for receiving data
receiver_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiver_sock.bind(('', 12009))  # Receiver address

class GimbalControl:
    def __init__(self):
        self.cam = SIYISDK(server_ip="192.168.6.141", port=37260)
        self.connected = False
        self.connect_to_gimbal()

    def connect_to_gimbal(self):
        if self.cam.connect():
            self.connected = True
            print("Connected to gimbal")
        else:
            print("Failed to connect to gimbal")

    def set_gimbal_rotation(self, yaw, pitch):
        if self.connected:
            retry_attempts = 3
            while retry_attempts > 0:
                result = self.cam.setGimbalRotation(yaw, pitch)
                if result:
                    print(f"Updated Gimbal Rotation to (Yaw: {yaw}, Pitch: {pitch})")
                    break
                else:
                    print(f"Failed to set gimbal rotation, retrying... ({3 - retry_attempts + 1})")
                    retry_attempts -= 1
                    time.sleep(0.1)
            if retry_attempts == 0:
                print("Failed to set gimbal rotation after several attempts.")
        else:
            print("Gimbal not connected")

    def receive_gimbal_commands(self):
        while True:
            try:
                data, _ = receiver_sock.recvfrom(1024)
                yaw, pitch = map(int, data.decode().split(','))
                self.set_gimbal_rotation(yaw, pitch)
            except Exception as e:
                print(f"Error receiving data: {e}")

if __name__ == "__main__":
    gimbal_control = GimbalControl()

    receiver_thread = threading.Thread(target=gimbal_control.receive_gimbal_commands, daemon=True)
    receiver_thread.start()

    try:
        receiver_thread.join()
    except KeyboardInterrupt:
        print("Receiver interrupted")

