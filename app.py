import streamlit as st
import cv2
import time
from ultralytics import YOLO
import numpy as np

# ===============================
# Page Config
# ===============================
st.set_page_config(page_title="Safety Monitoring System", layout="wide")

st.title("🚧 Real-Time Safety Monitoring System")
st.markdown("### 🧠 AI-powered Helmet Detection")

# ===============================
# Load Model
# ===============================
@st.cache_resource
def load_model():
    return YOLO(r"C:\Users\welcome\Downloads\actual project\actual project\best.pt")

model = load_model()

# ===============================
# Sidebar Controls
# ===============================
st.sidebar.header("Settings")

source = st.sidebar.radio("Select Input Source", ["Webcam", "Upload Video", "RTSP Stream"])
confidence = st.sidebar.slider("Confidence Threshold", 0.1, 1.0, 0.6)
rtsp_url = None
if source == "RTSP Stream":
    rtsp_url = st.sidebar.text_input("Enter RTSP URL")
# ===============================
# Display Area
# ===============================
frame_placeholder = st.empty()
fps_placeholder = st.empty()
violation_placeholder = st.empty()
status_placeholder = st.empty()

# ===============================
# IOU FUNCTION
# ===============================
def calculate_iou(box1, box2):
    x1, y1, x2, y2 = box1
    x1_p, y1_p, x2_p, y2_p = box2

    xi1 = max(x1, x1_p)
    yi1 = max(y1, y1_p)
    xi2 = min(x2, x2_p)
    yi2 = min(y2, y2_p)

    inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)

    box1_area = (x2 - x1) * (y2 - y1)
    box2_area = (x2_p - x1_p) * (y2_p - y1_p)

    union_area = box1_area + box2_area - inter_area

    return inter_area / union_area if union_area != 0 else 0

# ===============================
# Detection Logic
# ===============================
def process_frame(frame):
    results = model(frame, conf=confidence)[0]

    helmets = []
    heads = []

    for box in results.boxes:
        cls = int(box.cls[0])
        label = model.names[cls]
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        if label == "helmet":
            helmets.append((x1, y1, x2, y2))
        elif label == "head":
            heads.append((x1, y1, x2, y2))

    violations = 0

    for hx1, hy1, hx2, hy2 in heads:
        has_helmet = False

        for px1, py1, px2, py2 in helmets:
            iou = calculate_iou(
                (hx1, hy1, hx2, hy2),
                (px1, py1, px2, py2)
            )

            if iou > 0.3:  # 🔥 stricter matching
                has_helmet = True
                break

        if not has_helmet:
            violations += 1

    frame = results.plot()
    return frame, violations, len(heads), len(helmets)

# ===============================
# Webcam Mode
# ===============================
if source == "Webcam":
    run = st.checkbox("Start Webcam")

    if run:
        cap = cv2.VideoCapture(0)
        prev_time = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                st.error("Failed to access webcam")
                break

            frame = cv2.resize(frame, (640, 480))

            frame, violations, head_count, helmet_count = process_frame(frame)

            # FPS
            curr_time = time.time()
            fps = 1 / (curr_time - prev_time) if prev_time else 0
            prev_time = curr_time

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            frame_placeholder.image(frame_rgb, channels="RGB")
            fps_placeholder.markdown(f"### FPS: {int(fps)}")
            violation_placeholder.markdown(
                f"### Violations: {violations} | Heads: {head_count} | Helmets: {helmet_count}"
            )

            # Status display
            if violations > 0:
                status_placeholder.error(f"⚠️ {violations} Safety Violations Detected")
            else:
                status_placeholder.success("✅ All Safe")

        cap.release()

# ===============================
# Video Upload Mode
# ===============================
elif source == "Upload Video":
    uploaded_file = st.file_uploader("Upload Video", type=["mp4", "avi", "mov"])

    if uploaded_file is not None:
        with open("temp.mp4", "wb") as f:
            f.write(uploaded_file.read())

        cap = cv2.VideoCapture("temp.mp4")
        prev_time = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (640, 480))

            frame, violations, head_count, helmet_count = process_frame(frame)

            curr_time = time.time()
            fps = 1 / (curr_time - prev_time) if prev_time else 0
            prev_time = curr_time

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            frame_placeholder.image(frame_rgb, channels="RGB")
            fps_placeholder.markdown(f"### FPS: {int(fps)}")
            violation_placeholder.markdown(
                f"### Violations: {violations} | Heads: {head_count} | Helmets: {helmet_count}"
            )

            if violations > 0:
                status_placeholder.error(f"⚠️ {violations} Safety Violations Detected")
            else:
                status_placeholder.success("✅ All Safe")

        cap.release()
        
        
# ===============================
# RTSP processing block
# ===============================
# ===============================
# RTSP processing block (FIXED)
# ===============================
elif source == "RTSP Stream":

    start = st.button("Start Stream")

    if start and rtsp_url:

        cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)

        if not cap.isOpened():
            st.error("❌ Cannot open stream. Check URL or network.")
        else:
            st.success("✅ Stream started")

            prev_time = 0

            for _ in range(10000):  # controlled loop (important)

                ret, frame = cap.read()

                if not ret:
                    st.warning("⚠️ Stream disconnected")
                    break

                frame = cv2.resize(frame, (640, 480))

                frame, violations, head_count, helmet_count = process_frame(frame)

                # FPS calculation
                curr_time = time.time()
                fps = 1 / (curr_time - prev_time) if prev_time else 0
                prev_time = curr_time

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                frame_placeholder.image(frame_rgb)

                fps_placeholder.markdown(f"### FPS: {int(fps)}")
                violation_placeholder.markdown(
                    f"### Violations: {violations} | Heads: {head_count} | Helmets: {helmet_count}"
                )

                if violations > 0:
                    status_placeholder.error(f"⚠️ {violations} Violations")
                else:
                    status_placeholder.success("✅ Safe")

            cap.release()