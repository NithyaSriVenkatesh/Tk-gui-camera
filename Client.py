import asyncio
import cv2
import numpy as np
from av import VideoFrame
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer

class VideoCapture(MediaStreamTrack):
    """
    A video stream track that returns frames from a VideoCapture object.
    """

    def __init__(self, cap):
        super().__init__()
        self.cap = cap

    async def recv(self):
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to capture frame")
            return None

        # Convert the frame to RGB format
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Create an av.VideoFrame from the frame
        new_frame = VideoFrame.from_ndarray(frame, format="rgb24")
        new_frame.pts = self.cap.get(cv2.CAP_PROP_POS_MSEC) * 1000
        new_frame.time_base = 1 / self.cap.get(cv2.CAP_PROP_FPS)

        return new_frame

    async def recv_bye():
        print("Shutting down video capture")
        self.cap.release()

async def start_client():
    pc = RTCPeerConnection()

    @pc.on("datachannel")
    def on_datachannel(channel):
        print(f"Received data channel: {channel.label}")

    # Open the webcam
    cap = cv2.VideoCapture(0)

    # Create a video track from the webcam
    local_video = VideoCapture(cap)
    pc.addTrack(local_video)

    # Get the server's offer
    offer = RTCSessionDescription(sdp="SERVER_OFFER_SDP", type="offer")

    # Set the remote description
    await pc.setRemoteDescription(offer)

    # Create an answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    print("Client Answer: ", pc.localDescription.sdp)

    # Wait for a while to send frames
    await asyncio.sleep(10)

    # Clean up
    await pc.close()
    cap.release()

asyncio.run(start_client())
