# 🛡️ HelmetGuard – Real-Time Helmet Detection System

HelmetGuard is a computer vision-based safety monitoring application that detects whether people are wearing helmets in real time.

The system uses a YOLO-based object detection model with OpenCV and provides an interactive Streamlit dashboard for monitoring helmet compliance, detecting violations, triggering alerts, and maintaining an event log.

---

## 📌 Project Overview

In workplaces and other safety-critical environments, manually monitoring helmet compliance can be difficult and time-consuming.

HelmetGuard automates this process by analyzing live camera feeds, uploaded videos, and images to detect heads and helmets and identify potential helmet violations.

The application provides a visual dashboard where users can monitor detection results, adjust detection parameters, view statistics, and track safety events.

---

## ✨ Features

- 🎥 Real-time webcam monitoring
- 📹 Video file analysis
- 🖼️ Image upload and analysis
- 📡 RTSP stream support
- 🤖 YOLO-based object detection
- 🎯 Adjustable confidence threshold
- 🎯 Adjustable IoU threshold
- 🚨 Real-time violation alerts
- 🔔 Configurable alarm with cooldown
- 📊 Live detection statistics
- 📝 Event and violation log
- ⚡ FPS monitoring
- 👷 Head and helmet counting
- 📈 Helmet compliance monitoring
- 🌐 Interactive Streamlit dashboard

⚙️ Installation
1. Clone the repository
git clone https://github.com/Harshitathakur20/Helmet-Detection.git
2. Open the project directory
cd Helmet-Detection
3. Install the required libraries
pip install streamlit ultralytics opencv-python numpy pillow
4. Run the application
streamlit run app.py

The Streamlit application will open in your browser.


---

## 🧠 How It Works

The system follows these basic steps:

```text

Input Source
     ↓
Webcam / Video / Image / RTSP
     ↓
Frame Processing
     ↓
YOLO Object Detection
     ↓
Head & Helmet Detection
     ↓
Violation Analysis
     ↓
Alert + Statistics + Event Log
     ↓
Dashboard Display

