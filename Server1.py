import asyncio
import tkinter as tk
import cv2
from PIL import Image, ImageTk
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
import websockets
import json

class VideoReceiver(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Video Receiver")
        self.pack()
        self.label = tk.Label(self)
        self.label.pack()

        SERVER_IP = '192.168.6.203'
        SERVER_PORT = 8766  # Use the same port as the video sender

        asyncio.get_event_loop().run_until_complete(self.start_server(SERVER_IP, SERVER_PORT))

    async def start_server(self, server_ip, server_port):
        pc = RTCPeerConnection()

        @pc.on("track")
        def on_track(track):
            if track.kind == "video":
                self.video_track = VideoTrack(track, self.label)
                pc.addTrack(self.video_track)

        async def signaling_handler(websocket, path):
            async for message in websocket:
                data = json.loads(message)
                if "sdp" in data:
                    offer = RTCSessionDescription(data["sdp"], data["type"])
                    await pc.setRemoteDescription(offer)
                    answer = await pc.createAnswer()
                    await pc.setLocalDescription(answer)
                    await websocket.send(json.dumps({"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}))

        start_server = websockets.serve(signaling_handler, server_ip, server_port)
        await start_server
        print(f"Server listening on {server_ip}:{server_port}")

        async def run_server():
            while True:
                await asyncio.sleep(1)

        asyncio.create_task(run_server())

class VideoTrack(VideoStreamTrack):
    def __init__(self, track, label):
        super().__init__()
        self.track = track
        self.label = label
        self.frame_task = None

    async def recv(self):
        frame = await self.track.recv()
        img = frame.to_ndarray(format="bgr24")
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        self.label.imgtk = imgtk
        self.label.configure(image=imgtk)

        if self.frame_task is not None:
            self.frame_task.cancel()
        self.frame_task = self.label.after(10, lambda: asyncio.create_task(self.recv()))

        # Print frame dimensions for verification
        print(f"Received frame: {img.size}")

root = tk.Tk()
app = VideoReceiver(master=root)
app.mainloop()

