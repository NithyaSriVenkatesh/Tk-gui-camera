import asyncio
import cv2
from av import VideoFrame
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
import websockets
import json

class VideoCapture(MediaStreamTrack):
    kind = "video"

    def __init__(self, cap):
        super().__init__()
        self.cap = cap
        self.frame_counter = 0

    async def recv(self):
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to capture frame")
            return None
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        new_frame = VideoFrame.from_ndarray(frame, format="rgb24")
        new_frame.pts = self.frame_counter * (1 / self.cap.get(cv2.CAP_PROP_FPS)) * 1000
        self.frame_counter += 1
        return new_frame

async def send_offer(pc, websocket):
    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)
    await websocket.send(json.dumps({"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}))

async def receive_answer(pc, websocket):
    async for message in websocket:
        data = json.loads(message)
        if "sdp" in data:
            sdp = data["sdp"]
            sdp_type = data["type"]
            answer = RTCSessionDescription(sdp, sdp_type)
            await pc.setRemoteDescription(answer)
            break

async def start_client(server_ip, server_port):
    pc = RTCPeerConnection()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open video device.")
        return

    local_video = VideoCapture(cap)
    pc.addTrack(local_video)

    uri = f"ws://{server_ip}:{server_port}"
    async with websockets.connect(uri) as websocket:
        await send_offer(pc, websocket)
        await receive_answer(pc, websocket)
        await asyncio.sleep(10)
        print(f"Connecting to signaling server at {server_ip}:{server_port}")

    await pc.close()
    cap.release()

if __name__ == "__main__":
    server_ip = '192.168.6.203'
    server_port = 8766  # Ensure this matches the signaling server port
    asyncio.run(start_client(server_ip, server_port))

