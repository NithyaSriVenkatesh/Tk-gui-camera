import asyncio
import tkinter as tk
import cv2
import numpy as np
from PIL import Image, ImageTk
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
import websockets

class VideoReceiver(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Video Receiver")
        self.pack()

        # Create a label to display the video
        self.label = tk.Label(self)
        self.label.pack()

        # Set the server address and port
        SERVER_IP = '0.0.0.0'
        SERVER_PORT = 8000

        asyncio.run(self.start_server(SERVER_IP, SERVER_PORT))

    async def start_server(self, server_ip, server_port):
        pc = RTCPeerConnection()

        @pc.on("track")
        def on_track(track):
            print("Received video track")
            local_video = VideoTrack(track, self.label)
            pc.addTrack(local_video)

        async def signaling_handler(websocket, path):
            async for message in websocket:
                offer = RTCSessionDescription.from_json(message)
                await pc.setRemoteDescription(offer)
                answer = await pc.createAnswer()
                await pc.setLocalDescription(answer)
                await websocket.send(answer.to_json())

        start_server = websockets.serve(signaling_handler, server_ip, server_port)
        await start_server

        print(f"Server listening on {server_ip}:{server_port}")

        # Keep the server running
        async def run_server():
            while True:
                await asyncio.sleep(1)

        asyncio.create_task(run_server())

class VideoTrack(VideoStreamTrack):
    def __init__(self, track, label):
        super().__init__()
        self.track = track
        self.label = label

    async def recv(self):
        frame = await self.track.recv()
        img = frame.to_ndarray(format="bgr24")
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        self.label.imgtk = imgtk
        self.label.configure(image=imgtk)
        self.label.after(10, self.recv)

root = tk.Tk()
app = VideoReceiver(root)
app.mainloop()
