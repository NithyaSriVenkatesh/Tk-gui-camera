**Tk-GUI-Camera**

A Tkinter-based graphical user interface (GUI) for live-streaming video feeds from multiple cameras, typically used with UAVs (Unmanned Aerial Vehicles). This application supports viewing multiple camera streams simultaneously and allows users to switch to a single-camera view. It uses RTSP streaming and GStreamer for better video quality and performance. Additionally, a terminal interface is provided to receive and display responses from the camera.

**Features**

Multi-Camera View: View multiple camera streams at once in a grid layout.
Single Camera View: Switch to full-screen mode to view a single camera stream.
RTSP Streaming: Streams video from cameras using the RTSP protocol.
GStreamer Support: Utilizes GStreamer for improved video quality and performance.
Terminal Output: Integrated terminal to display responses from the camera or device for debugging and control.

**Requirements**

Before running the application, make sure you have the following dependencies installed:
Python

Python 3.x (preferably 3.6+)

**Required Python Libraries**

tkinter (for GUI)
opencv-python (for handling video streams)
gstreamer (for enhanced video streaming capabilities)
subprocess (for terminal interaction)

**Installation Guide for Tk-GUI-Camera**

Follow these steps to set up the necessary dependencies for the Tk-GUI-Camera application, which includes setting up OpenCV with GStreamer support for handling video streaming.
**Step 1:** Update and Install Basic Dependencies - Update your system:

    sudo apt update
    sudo apt upgrade

Install GStreamer libraries: These packages are necessary for video streaming with GStreamer:

    sudo apt-get install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
    libgstreamer-plugins-bad1.0-dev gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-tools \
    gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 \
    gstreamer1.0-qt5 gstreamer1.0-pulseaudio

Install additional dependencies for OpenCV: These are necessary for building OpenCV from source:

    sudo apt-get install cmake git libgtk2.0-dev pkg-config \
    libavcodec-dev libavformat-dev libswscale-dev python3-dev \
    python3-numpy libtbb2 libtbb-dev libjpeg-dev libpng-dev \
    libtiff-dev

**Step 2:** Download and Build OpenCV with GStreamer Support
Download OpenCV from GitHub: Go to the OpenCV GitHub Releases page and download the required version of OpenCV (e.g., the latest stable version). You can also clone the repository directly:

    git clone https://github.com/opencv/opencv.git
    cd opencv

Create a build directory: Inside the OpenCV directory, create a new build folder:

    mkdir build
    cd build

Configure OpenCV build options using CMake: Run the cmake command to configure the build. Ensure that GStreamer support is enabled:

    cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/home/yourusername/opencv_install \
    -DINSTALL_PYTHON_EXAMPLES=ON \
    -D INSTALL_C_EXAMPLES=ON \
    -D PYTHON_EXECUTABLE=/home/yourusername/.local/bin/python3.8 \
    -D BUILD_EXAMPLES=ON \
    -D WITH_GTK=ON \
    -D WITH_GSTREAMER=ON \
    -D WITH_FFMPEG=OFF \
    -D WITH_QT=OFF ..

Adjust /home/yourusername/.local/bin/python3.8 to the actual path of your Python executable (check with which python3).
You can change /home/yourusername/opencv_install to any directory where you want to install OpenCV.

Build OpenCV: Use make to start building OpenCV. The -j$(nproc) flag speeds up the process by utilizing multiple CPU cores.

    make -j$(nproc)

Install OpenCV: Once the build is complete, install OpenCV to your specified installation directory:

    sudo make install

**Step 3:** Install Python Bindings for OpenCV

Navigate to the Python bindings directory:

    cd ~/opencv/python_loader

Install Python bindings: Install the OpenCV Python bindings using setup.py:

    sudo python3.x setup.py install

Replace python3.x with your actual Python version (e.g., python3.8).

Install Tkinter: If Tkinter is not already installed, you can install it via your package manager:

    sudo apt-get install python3-tk

**Step 4:** Verify Installation

Once everything is installed, you can verify that GStreamer and OpenCV with GStreamer support are working by running a simple Python script:

    import cv2
    print(cv2.getBuildInformation())

Look for GStreamer in the output to ensure it is enabled.

**Usage**

Launching the GUI:
When you launch the program, a Tkinter window will open displaying multiple camera feeds in a grid format.

Switching to Single Camera View:
To switch to a full-screen view of a single camera feed, simply click on the desired camera window. The feed will switch to the larger view.

Camera Terminal Output:
The terminal window shows responses from the camera, such as error messages, status updates, or command outputs. This allows users to interact with the camera in real-time for diagnostics or control.
