import sys
import threading
import time
import socket
import struct
import binascii
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QPushButton, QVBoxLayout, QWidget, QLabel

class GimbalControlApp(QMainWindow):
    def _init_(self):
        super()._init_()
        self.initUI()
        self.s6 = None
        self.current_host = None
        self.PORT = 37260  # The port used by the server

    def initUI(self):
        self.setWindowTitle('Gimbal Control')
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        self.host_label = QLabel("Select Host:")
        layout.addWidget(self.host_label)

        self.host_combo = QComboBox(self)
        self.host_combo.addItems(["192.168.6.125", "192.168.6.128", "192.168.6.131","192.168.6.135"])  # Add your hosts here
        layout.addWidget(self.host_combo)

        self.connect_button = QPushButton("Connect", self)
        self.connect_button.clicked.connect(self.connect_to_gimbal)
        layout.addWidget(self.connect_button)

        self.send_gimbal_rotation_button = QPushButton("Send Gimbal Rotation Command", self)
        self.send_gimbal_rotation_button.clicked.connect(self.send_gimbal_rotation_command)
        layout.addWidget(self.send_gimbal_rotation_button)
        
        self.send_center_button = QPushButton("Send Center Command", self)
        self.send_center_button.clicked.connect(self.send_center_command)
        layout.addWidget(self.send_center_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def is_connected(self, sock):
        try:
            sock.send(b'')
        except socket.error:
            return False
        return True

    def connect_to_gimbal(self):
        self.current_host = self.host_combo.currentText()
        if self.s6:
            self.s6.close()
        self.s6 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.s6.connect((self.current_host, self.PORT))
            time.sleep(2)
            print(f"Connected to gimbal at {self.current_host}")
        except socket.error as e:
            print(f"Connection failed: {e}")

    def send_gimbal_rotation_command(self):
        gimbal_rotation_90_90 = [0x55, 0x66, 0x01, 0x04, 0x00, 0x00, 0x00, 0x0e, 0x00, 0x00, 0xff, 0xa6, 0x3b, 0x11]
        self.connect_to_gimbal()
        self.send_command(gimbal_rotation_90_90)

    def send_center_command(self):
        center_command = [0x55, 0x66, 0x01, 0x01, 0x00, 0x00, 0x00, 0x08, 0x01, 0xd1, 0x12]
        self.connect_to_gimbal()
        self.send_command(center_command)

    def send_command(self, command):
        if not self.is_connected(self.s6):
            print("Gimbal is disconnected")
            self.connect_to_gimbal()
        try:
            packet = bytearray(command)
            bytePacket = bytes(packet)
            self.s6.sendall(bytePacket)
            print("Sent packet to gimbal: " + " ".join(f"{b:02x}" for b in command))
        except socket.error as e:
            print(f"Error sending packet: {e}")
            self.s6.close()
            time.sleep(5)
            self.connect_to_gimbal()

def main():
    app = QApplication(sys.argv)
    ex = GimbalControlApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
