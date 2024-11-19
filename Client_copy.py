import asyncio
import cv2
import numpy as np
from av import VideoFrame
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription

class VideoCapture(MediaStreamTrack):
    """
    A video stream track that returns frames from a VideoCapture object.
    """
    kind = "video"

    def __init__(self, cap):
        super().__init__()
        self.cap = cap
        self.frame_counter = 0  # Initialize frame counter

    async def recv(self):
        try:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to capture frame")
                return None
            # Convert the frame to RGB format
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Create an av.VideoFrame from the frame
            new_frame = VideoFrame.from_ndarray(frame, format="rgb24")
            new_frame.pts = self.frame_counter * (1 / self.cap.get(cv2.CAP_PROP_FPS)) * 1000
            self.frame_counter += 1  # Increment counter after setting pts
            return new_frame
        except Exception as e:
            print(f"Error capturing frame: {e}")
            return None

    async def recv_bye(self):
        print("Shutting down video capture")
        self.cap.release()

async def start_client(server_ip, server_port):
    pc = RTCPeerConnection()

    @pc.on("datachannel")
    def on_datachannel(channel):
        print(f"Received data channel: {channel.label}")

    # Open the webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open video device.")
        return

    # Create a video track from the webcam
    local_video = VideoCapture(cap)
    pc.addTrack(local_video)

    # Create an offer
    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)
    print(f"Client Offer: {pc.localDescription.sdp}")

    # Connect to the server
    await pc.connect(f"stun:{server_ip}:{server_port}")

    # Wait for a while to send frames
    await asyncio.sleep(10)

    # Clean up
    await pc.close()
    cap.release()

if __name__ == "__main__":
    # Get the server's IP address and port
    server_ip = '192.168.6.203'
    server_port = 8000
    asyncio.run(start_client(server_ip, server_port))

