import asyncio
import cv2
import numpy as np
from av import VideoFrame
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer

class VideoTransformTrack(MediaStreamTrack):
    """
    A video stream track that transforms frames from an another track.
    """

    def __init__(self, track):
        super().__init__()
        self.track = track

    async def recv(self):
        frame = await self.track.recv()
        img = frame.to_ndarray(format="bgr24")
        new_frame = VideoFrame.from_ndarray(img, format="bgr24")
        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base
        return new_frame

async def start_server():
    pc = RTCPeerConnection()
    pctx = pc.createDataChannel("chat")

    @pc.on("datachannel")
    def on_datachannel(channel):
        print(f"Received data channel: {channel.label}")

    @pc.on("track")
    def on_track(track):
        print("Received video track")
        local_video = VideoTransformTrack(track)
        pc.addTrack(local_video)

        @track.on("ended")
        async def on_ended():
            print("Video track ended")
            await pc.close()

    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)

    print("Server Offer: ", pc.localDescription.sdp)

    await asyncio.sleep(10)

asyncio.run(start_server())
