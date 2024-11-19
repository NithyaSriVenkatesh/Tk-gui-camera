from flask import Flask, Response
import cv2, time
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
flag = 0
# cap = cv2.VideoCapture("rtsp://192.168.5.122:8554/main.264", cv2.CAP_FFMPEG)


# Function to generate video frames
def generate_frames(url):
    print("Runningggggggggg")
    cap = cv2.VideoCapture(url)
    flag = 0
    # cap = cv2.VideoCapture("rtsp://192.168.5.122:8554/main.264", cv2.CAP_FFMPEG)
    if not cap.isOpened():
        raise Exception("Error opening video file")
    while True:
        ret, frame = cap.read()
        if flag:
            break
        if not ret:
            print("Frame lost in read")
            continue
        # frame = cv2.resize(frame, (640, 480))
        ret, buffer = cv2.imencode(".jpg", frame)
        if not ret:
            print("frame lost in buffer")
            continue
        frame = buffer.tobytes()
        yield (b"--frame\r\n" b"Content-Type: image/jpg\r\n\r\n" + frame + b"\r\n\r\n")


@app.route("/")
def index():
    return "RTSP Stream Server"


@app.route("/video_1")
def video_1():
    # global flag
    # try:
    #     flag = 1
    #     time.sleep(0.1)
    return Response(
        # generate_frames("rtsp://192.168.6.161:8554/main.264"),
        generate_frames(0),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )
    # except Exception as e:
    #     print("Errorrr")
    #     return str(e)


@app.route("/video_2")
def video_2():
    global flag
    try:
        flag = 1
        time.sleep(0.1)
        return Response(
            generate_frames("rtsp://192.168.6.141:8554/main.264"),
            # generate_frames(0),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )
    except Exception as e:
        return str(e)


# @app.route("/video_3")
# def video_3():
#     try:
#         flag = 1
#         return Response(
#             generate_frames("rtsp://192.168.6.124:8554/main.264"),
#             # generate_frames(0),
#             mimetype="multipart/x-mixed-replace; boundary=frame",
#         )
#     except Exception as e:
#         return str(e)


if __name__ == "__main__":
    # app.run(host="192.168.0.104", port=int(8000), ssl_context="adhoc")
    app.run(host="192.168.6.21", port=int(8000), debug=True)
