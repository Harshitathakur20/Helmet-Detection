import streamlit as st
import cv2
import time
import numpy as np
from ultralytics import YOLO
from datetime import datetime
from PIL import Image
import io

# ═══════════════════════════════════════════════
#  PAGE CONFIG
# ═══════════════════════════════════════════════
st.set_page_config(
    page_title="HelmetGuard · Real-Time Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════
#  CYBERPUNK-BLUE THEME CSS
# ═══════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --bg-base:      #020812;
    --bg-card:      #060e1f;
    --bg-card2:     #0a1628;
    --border:       #0d2545;
    --border-bright:#1a4a8a;
    --cyan:         #00d4ff;
    --cyan-dim:     #0088aa;
    --blue:         #0066ff;
    --blue-bright:  #3399ff;
    --green:        #00ff88;
    --green-dim:    #00aa55;
    --red:          #ff3355;
    --red-dim:      #aa1133;
    --amber:        #ffaa00;
    --amber-dim:    #aa6600;
    --text-primary: #e0f0ff;
    --text-secondary:#7090b0;
    --text-muted:   #304060;
    --glow-cyan:    0 0 20px rgba(0,212,255,0.4);
    --glow-blue:    0 0 20px rgba(0,102,255,0.4);
    --glow-red:     0 0 20px rgba(255,51,85,0.5);
    --glow-green:   0 0 20px rgba(0,255,136,0.4);
}

/* ── BASE ── */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg-base) !important;
    color: var(--text-primary);
    font-family: 'Exo 2', sans-serif;
}

/* animated grid background */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(0,102,255,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,102,255,0.04) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #030c1a !important;
    border-right: 1px solid var(--border-bright) !important;
}
[data-testid="stSidebar"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--cyan), var(--blue), transparent);
}
[data-testid="stSidebar"] * { font-family: 'Exo 2', sans-serif !important; }

/* ── HEADER ── */
.hg-header {
    position: relative;
    padding: 24px 0 20px 0;
    margin-bottom: 28px;
    text-align: center;
}
.hg-header::after {
    content: '';
    position: absolute;
    bottom: 0; left: 10%; right: 10%;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--cyan), var(--blue), transparent);
}
.hg-logo-line {
    font-family: 'Orbitron', monospace;
    font-size: 2.2rem;
    font-weight: 900;
    letter-spacing: 6px;
    text-transform: uppercase;
    color: var(--text-primary);
    text-shadow: var(--glow-cyan);
}
.hg-logo-line span.accent { color: var(--cyan); }
.hg-subtitle {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 3px;
    color: var(--text-secondary);
    margin-top: 6px;
    text-transform: uppercase;
}
.hg-pill {
    display: inline-block;
    background: linear-gradient(135deg, var(--blue), var(--cyan));
    color: var(--bg-base);
    font-family: 'Orbitron', monospace;
    font-size: 0.55rem;
    font-weight: 700;
    letter-spacing: 2px;
    padding: 3px 10px;
    border-radius: 20px;
    margin-top: 10px;
}

/* ── STAT CARDS ── */
.sc-wrap {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
    margin-bottom: 16px;
}
.sc {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 12px;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s;
}
.sc::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    border-radius: 10px 10px 0 0;
}
.sc.cyan::before  { background: linear-gradient(90deg, var(--cyan), var(--blue)); }
.sc.green::before { background: linear-gradient(90deg, var(--green), var(--green-dim)); }
.sc.red::before   { background: linear-gradient(90deg, var(--red), var(--red-dim)); }
.sc.amber::before { background: linear-gradient(90deg, var(--amber), var(--amber-dim)); }

.sc-num {
    font-family: 'Orbitron', monospace;
    font-size: 2rem;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 4px;
}
.sc.cyan  .sc-num { color: var(--cyan);  text-shadow: var(--glow-cyan); }
.sc.green .sc-num { color: var(--green); text-shadow: var(--glow-green);}
.sc.red   .sc-num { color: var(--red);   text-shadow: var(--glow-red);  }
.sc.amber .sc-num { color: var(--amber); }
.sc-label {
    font-size: 0.65rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--text-secondary);
}

/* ── STATUS BANNERS ── */
.banner-safe {
    background: linear-gradient(90deg, rgba(0,255,136,0.08) 0%, rgba(6,14,31,0) 100%);
    border: 1px solid var(--green-dim);
    border-left: 3px solid var(--green);
    border-radius: 8px;
    padding: 12px 18px;
    font-family: 'Orbitron', monospace;
    font-size: 0.8rem;
    letter-spacing: 2px;
    color: var(--green);
    text-shadow: var(--glow-green);
    text-transform: uppercase;
    margin-bottom: 10px;
}
.banner-danger {
    background: linear-gradient(90deg, rgba(255,51,85,0.12) 0%, rgba(6,14,31,0) 100%);
    border: 1px solid var(--red-dim);
    border-left: 3px solid var(--red);
    border-radius: 8px;
    padding: 12px 18px;
    font-family: 'Orbitron', monospace;
    font-size: 0.8rem;
    letter-spacing: 2px;
    color: var(--red);
    text-shadow: var(--glow-red);
    text-transform: uppercase;
    margin-bottom: 10px;
    animation: danger-pulse 0.9s infinite;
}
@keyframes danger-pulse {
    0%,100% { border-left-color: var(--red); }
    50%      { border-left-color: #ff8899; box-shadow: var(--glow-red); }
}

/* ── PHOTO RESULT BOX ── */
.photo-meta {
    background: var(--bg-card2);
    border: 1px solid var(--border-bright);
    border-radius: 10px;
    padding: 16px 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: var(--text-primary);
    margin-top: 12px;
}
.photo-meta .row { display:flex; justify-content:space-between; margin-bottom:6px; }
.photo-meta .key { color: var(--text-secondary); }
.photo-meta .val-ok  { color: var(--green); }
.photo-meta .val-bad { color: var(--red); }
.photo-meta .val-info{ color: var(--cyan); }

/* ── ALERT LOG ── */
.alog {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px;
    max-height: 280px;
    overflow-y: auto;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
}
.alog::-webkit-scrollbar { width: 4px; }
.alog::-webkit-scrollbar-track { background: var(--bg-base); }
.alog::-webkit-scrollbar-thumb { background: var(--blue); border-radius:4px; }
.alog-row {
    display: flex; gap: 12px; align-items: flex-start;
    padding: 5px 8px; border-radius: 5px; margin-bottom: 3px;
}
.alog-row.v { background: rgba(255,51,85,0.08); border-left: 2px solid var(--red); color: var(--red); }
.alog-row.s { background: rgba(0,255,136,0.06); border-left: 2px solid var(--green); color: var(--green); }
.alog-row.p { background: rgba(0,212,255,0.06); border-left: 2px solid var(--cyan); color: var(--cyan); }
.alog-time  { color: var(--text-muted); min-width: 72px; }

/* ── SECTION HEADER ── */
.sec-hdr {
    font-family: 'Orbitron', monospace;
    font-size: 0.62rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--cyan-dim);
    margin: 18px 0 10px 0;
    display: flex; align-items: center; gap: 10px;
}
.sec-hdr::after { content:''; flex:1; height:1px; background: linear-gradient(90deg, var(--border-bright), transparent); }

/* ── SIDEBAR BRAND ── */
.sb-brand {
    background: linear-gradient(135deg, #0a1628, #060e1f);
    border: 1px solid var(--border-bright);
    border-radius: 10px;
    padding: 12px 16px;
    text-align: center;
    margin-bottom: 16px;
}
.sb-brand-title {
    font-family: 'Orbitron', monospace;
    font-size: 1rem;
    font-weight: 700;
    color: var(--cyan);
    letter-spacing: 3px;
    text-shadow: var(--glow-cyan);
}
.sb-brand-sub {
    font-size: 0.65rem;
    color: var(--text-secondary);
    letter-spacing: 1.5px;
    margin-top: 3px;
}

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #003399, #0055cc) !important;
    color: var(--cyan) !important;
    border: 1px solid var(--border-bright) !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    border-radius: 8px !important;
    padding: 10px 22px !important;
    transition: all 0.2s !important;
    box-shadow: var(--glow-blue) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #0044cc, #0088ff) !important;
    box-shadow: 0 0 30px rgba(0,136,255,0.6) !important;
    transform: translateY(-2px) !important;
}

/* ── CHECKBOX / TOGGLE ── */
.stCheckbox label { font-weight: 600; letter-spacing: 1px; color: var(--text-primary) !important; }

/* ── IMAGE ── */
[data-testid="stImage"] img {
    border-radius: 10px;
    border: 1px solid var(--border-bright);
    box-shadow: 0 0 24px rgba(0,100,255,0.2);
}

/* ── SCAN LINE OVERLAY ── */
.scanline {
    pointer-events: none;
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 3px,
        rgba(0,212,255,0.012) 3px,
        rgba(0,212,255,0.012) 4px
    );
    z-index: 9999;
}

/* ── RADIO ── */
.stRadio label { font-family: 'Exo 2', sans-serif !important; color: var(--text-primary) !important; }

/* ── DIVIDER ── */
hr { border-color: var(--border) !important; }

/* ── SESSION TIMER ── */
.session-timer {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: var(--cyan-dim);
    text-align: center;
    letter-spacing: 2px;
    padding: 8px;
    border: 1px solid var(--border);
    border-radius: 6px;
    background: var(--bg-card);
    margin-top: 10px;
}

/* ── RTSP GUIDE ── */
.rtsp-step {
    background: var(--bg-card2);
    border: 1px solid var(--border);
    border-left: 3px solid var(--blue-bright);
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 8px;
    font-size: 0.82rem;
    color: var(--text-primary);
}
.rtsp-step .snum {
    font-family: 'Orbitron', monospace;
    color: var(--cyan);
    font-size: 0.65rem;
    margin-bottom: 3px;
    letter-spacing: 1px;
}
.rtsp-step code {
    background: rgba(0,100,255,0.15);
    color: var(--cyan);
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
}
</style>
<div class="scanline"></div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
#  ALARM JS
# ═══════════════════════════════════════════════
ALARM_JS = """
<script>
(function(){
    if(window._hgAlarmActive) return;
    window._hgAlarmActive = true;
    const AC = window.AudioContext || window.webkitAudioContext;
    if(!AC) return;
    const ctx = new AC();
    const schedule = [[880,0,0.15],[660,0.18,0.12],[880,0.33,0.15],[1100,0.50,0.22]];
    schedule.forEach(([f,t,d])=>{
        const o=ctx.createOscillator(), g=ctx.createGain();
        o.connect(g); g.connect(ctx.destination);
        o.type='square'; o.frequency.value=f;
        const st=ctx.currentTime+t;
        g.gain.setValueAtTime(0.3,st);
        g.gain.exponentialRampToValueAtTime(0.001,st+d);
        o.start(st); o.stop(st+d+0.05);
    });
    setTimeout(()=>{ window._hgAlarmActive=false; },900);
})();
</script>
"""
ALARM_CLEAR = "<script>window._hgAlarmActive=false;</script>"

def trigger_alarm():
    st.components.v1.html(ALARM_JS, height=0)

def clear_alarm():
    st.components.v1.html(ALARM_CLEAR, height=0)

# ═══════════════════════════════════════════════
#  SESSION STATE
# ═══════════════════════════════════════════════
defaults = {
    "total_violations": 0,
    "total_frames": 0,
    "total_photos": 0,
    "photo_violations": 0,
    "alert_log": [],
    "session_start": datetime.now(),
    "last_alarm": 0.0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ═══════════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════════
st.markdown("""
<div class="hg-header">
  <div class="hg-logo-line">🛡 <span class="accent">Helmet</span>Guard</div>
  <div class="hg-subtitle">Real-Time AI Detection System · v2.0</div>
  <div><span class="hg-pill">⬡ YOLO NEURAL ENGINE ACTIVE</span></div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
#  LOAD MODEL
# ═══════════════════════════════════════════════
@st.cache_resource
def load_model():
    return YOLO(r"C:\Users\welcome\Downloads\actual project\actual project\best.pt")

model = load_model()

# ═══════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sb-brand">
        <div class="sb-brand-title">⬡ HELMETGUARD</div>
        <div class="sb-brand-sub">DETECTION CONSOLE</div>
    </div>""", unsafe_allow_html=True)

    source = st.radio(
        "INPUT SOURCE",
        ["📷 Webcam", "🎞️ Upload Video", "🖼️ Upload Photo", "📡 RTSP Stream"],
    )
    src = source.split(" ", 1)[1]

    st.markdown('<div class="sec-hdr">⚙ Detection Params</div>', unsafe_allow_html=True)
    confidence = st.slider("Confidence", 0.10, 1.00, 0.60, 0.05)
    iou_thresh  = st.slider("IOU Threshold", 0.10, 0.90, 0.30, 0.05)

    st.markdown('<div class="sec-hdr">🔔 Alarm</div>', unsafe_allow_html=True)
    alarm_on       = st.toggle("Enable Alarm", value=True)
    alarm_cooldown = st.slider("Cooldown (sec)", 1, 10, 3)

    st.markdown('<div class="sec-hdr">🖥 Display</div>', unsafe_allow_html=True)
    show_stats = st.toggle("Stats Panel", value=True)
    show_log   = st.toggle("Alert Log",   value=True)

    if src == "RTSP Stream":
        st.markdown('<div class="sec-hdr">📡 RTSP Config</div>', unsafe_allow_html=True)
        rtsp_url = st.text_input("RTSP URL", placeholder="rtsp://user:pass@ip:554/stream")

    st.divider()
    if st.button("↺  Reset Session"):
        for k, v in defaults.items():
            if k != "session_start":
                st.session_state[k] = v
        st.session_state["session_start"] = datetime.now()
        st.rerun()

    elapsed = datetime.now() - st.session_state["session_start"]
    m, s = divmod(int(elapsed.total_seconds()), 60)
    h, m = divmod(m, 60)
    st.markdown(
        f'<div class="session-timer">⏱ SESSION &nbsp;{h:02d}:{m:02d}:{s:02d}</div>',
        unsafe_allow_html=True,
    )

# ═══════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════
def iou(b1, b2):
    xi1,yi1 = max(b1[0],b2[0]), max(b1[1],b2[1])
    xi2,yi2 = min(b1[2],b2[2]), min(b1[3],b2[3])
    inter = max(0,xi2-xi1)*max(0,yi2-yi1)
    u = (b1[2]-b1[0])*(b1[3]-b1[1])+(b2[2]-b2[0])*(b2[3]-b2[1])-inter
    return inter/u if u else 0

def process_frame(frame):
    res = model(frame, conf=confidence)[0]
    helmets, heads = [], []
    for box in res.boxes:
        lbl = model.names[int(box.cls[0])]
        c   = tuple(map(int, box.xyxy[0]))
        if lbl == "helmet": helmets.append(c)
        elif lbl == "head": heads.append(c)
    violations = sum(
        1 for h in heads
        if not any(iou(h, p) > iou_thresh for p in helmets)
    )
    return res.plot(), violations, len(heads), len(helmets)

def add_log(t, msg):
    st.session_state["alert_log"].append({
        "type": t,
        "time": datetime.now().strftime("%H:%M:%S"),
        "msg":  msg,
    })

def render_stats_panel(stat_slots, violations, heads, helmets):
    s1, s2, s3, s4 = stat_slots
    comp = round((1 - violations/max(heads,1))*100) if heads else 100
    col  = "green" if comp==100 else ("amber" if comp>=50 else "red")
    s1.markdown(f'<div class="sc {col}"><div class="sc-num">{comp}%</div><div class="sc-label">Compliance</div></div>', unsafe_allow_html=True)
    s2.markdown(f'<div class="sc red"><div class="sc-num">{st.session_state["total_violations"]}</div><div class="sc-label">Total Violations</div></div>', unsafe_allow_html=True)
    s3.markdown(f'<div class="sc cyan"><div class="sc-num">{st.session_state["total_frames"]}</div><div class="sc-label">Frames</div></div>', unsafe_allow_html=True)
    s4.markdown(f'<div class="sc amber"><div class="sc-num">{len(st.session_state["alert_log"])}</div><div class="sc-label">Events</div></div>', unsafe_allow_html=True)

def render_log_panel(slot):
    log = st.session_state["alert_log"]
    if not log:
        slot.markdown('<div class="alog" style="color:#304060;text-align:center;padding:24px 0">— No events recorded —</div>', unsafe_allow_html=True)
        return
    rows = ""
    for e in reversed(log[-40:]):
        cls  = {"violation":"v","safe":"s","photo":"p"}.get(e["type"],"p")
        icon = {"v":"⚠","s":"✓","p":"📷"}.get(cls,"•")
        rows += f'<div class="alog-row {cls}"><span class="alog-time">{e["time"]}</span><span>{icon} {e["msg"]}</span></div>'
    slot.markdown(f'<div class="alog">{rows}</div>', unsafe_allow_html=True)

def maybe_alarm(violations):
    if not alarm_on or violations == 0:
        clear_alarm()
        return
    now = time.time()
    if now - st.session_state["last_alarm"] > alarm_cooldown:
        trigger_alarm()
        st.session_state["last_alarm"] = now

# ═══════════════════════════════════════════════
#  LAYOUT: feed + right panel
# ═══════════════════════════════════════════════
col_feed, col_right = st.columns([3, 1.5], gap="large")

with col_feed:
    st.markdown('<div class="sec-hdr">📹 Detection Feed</div>', unsafe_allow_html=True)
    frame_slot  = st.empty()
    status_slot = st.empty()
    c1, c2, c3, c4 = st.columns(4)
    fps_slot    = c1.empty()
    head_slot   = c2.empty()
    helmet_slot = c3.empty()
    viol_slot   = c4.empty()

with col_right:
    if show_stats:
        st.markdown('<div class="sec-hdr">📊 Session Stats</div>', unsafe_allow_html=True)
        ss1 = st.empty()
        ss2 = st.empty()
        ss3 = st.empty()
        ss4 = st.empty()
        stat_slots = (ss1, ss2, ss3, ss4)
    if show_log:
        st.markdown('<div class="sec-hdr">🚨 Event Log</div>', unsafe_allow_html=True)
        log_slot = st.empty()

def inline_cards(fps, heads, helmets, violations):
    def card(num, label, color):
        return f'<div class="sc {color}" style="padding:10px 8px"><div class="sc-num" style="font-size:1.5rem">{num}</div><div class="sc-label">{label}</div></div>'
    fps_slot.markdown(card(int(fps),     "FPS",      "cyan"),  unsafe_allow_html=True)
    head_slot.markdown(card(heads,       "Heads",    "amber"), unsafe_allow_html=True)
    helmet_slot.markdown(card(helmets,   "Helmets",  "green"), unsafe_allow_html=True)
    viol_slot.markdown(card(violations,  "Violations","red"),  unsafe_allow_html=True)

# ═══════════════════════════════════════════════
#  STREAM LOOP
# ═══════════════════════════════════════════════
def run_stream(cap):
    prev_t = 0.0
    prev_vstate = False
    while True:
        ret, frame = cap.read()
        if not ret:
            status_slot.warning("⚠️ Stream ended.")
            break
        frame = cv2.resize(frame, (640, 480))
        ann, violations, heads, helmets = process_frame(frame)
        st.session_state["total_frames"] += 1
        if violations: st.session_state["total_violations"] += violations

        now = time.time()
        fps = 1/(now-prev_t) if prev_t else 0
        prev_t = now

        frame_slot.image(cv2.cvtColor(ann, cv2.COLOR_BGR2RGB), use_container_width=True)
        inline_cards(fps, heads, helmets, violations)

        if violations:
            status_slot.markdown(
                f'<div class="banner-danger">⚠ ALERT · {violations} HEAD{"S" if violations>1 else ""} WITHOUT HELMET DETECTED</div>',
                unsafe_allow_html=True)
            if not prev_vstate:
                add_log("violation", f"{violations} head(s) without helmet")
            prev_vstate = True
            maybe_alarm(violations)
        else:
            status_slot.markdown(
                '<div class="banner-safe">✔ ZONE CLEAR · ALL PERSONNEL COMPLIANT</div>',
                unsafe_allow_html=True)
            if prev_vstate:
                add_log("safe", "Zone cleared — helmets confirmed")
            prev_vstate = False
            clear_alarm()

        if show_stats: render_stats_panel(stat_slots, violations, heads, helmets)
        if show_log:   render_log_panel(log_slot)
    cap.release()

# ═══════════════════════════════════════════════
#  SOURCE: WEBCAM
# ═══════════════════════════════════════════════
if src == "Webcam":
    if st.checkbox("▶  Start Webcam", key="wc"):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("❌ Webcam not accessible.")
        else:
            run_stream(cap)

# ═══════════════════════════════════════════════
#  SOURCE: UPLOAD VIDEO  ← FIXED for Windows
# ═══════════════════════════════════════════════
elif src == "Upload Video":
    vid = st.file_uploader("Drop a video file", type=["mp4","avi","mov","mkv"])
    if vid:
        import tempfile
        import os
        # Preserve original extension so OpenCV picks the correct codec
        suffix = os.path.splitext(vid.name)[-1]
        # tempfile uses the OS-correct temp folder (works on Windows & Linux/Mac)
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(vid.read())
            tmp_path = tmp_file.name
        try:
            cap = cv2.VideoCapture(tmp_path)
            if not cap.isOpened():
                st.error("❌ Could not open video file. Please try a different file.")
            else:
                run_stream(cap)
        finally:
            # Always clean up the temp file after the stream ends
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

# ═══════════════════════════════════════════════
#  SOURCE: UPLOAD PHOTO
# ═══════════════════════════════════════════════
elif src == "Upload Photo":
    photos = st.file_uploader(
        "Upload one or more images",
        type=["jpg","jpeg","png","bmp","webp"],
        accept_multiple_files=True,
    )
    if photos:
        for photo in photos:
            img_pil  = Image.open(photo).convert("RGB")
            img_np   = np.array(img_pil)
            frame_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

            ann, violations, heads, helmets = process_frame(frame_bgr)
            st.session_state["total_photos"] += 1
            if violations: st.session_state["photo_violations"] += violations

            ann_rgb = cv2.cvtColor(ann, cv2.COLOR_BGR2RGB)
            comp = round((1 - violations/max(heads,1))*100) if heads else 100

            with col_feed:
                frame_slot.image(ann_rgb, caption=f"📷 {photo.name}", use_container_width=True)
                if violations:
                    status_slot.markdown(
                        f'<div class="banner-danger">⚠ {violations} VIOLATION{"S" if violations>1 else ""} DETECTED IN {photo.name.upper()}</div>',
                        unsafe_allow_html=True)
                    maybe_alarm(violations)
                else:
                    status_slot.markdown(
                        f'<div class="banner-safe">✔ COMPLIANT · NO VIOLATIONS IN {photo.name.upper()}</div>',
                        unsafe_allow_html=True)
                    clear_alarm()

                st.markdown(f"""
                <div class="photo-meta">
                  <div class="row"><span class="key">FILE</span><span class="val-info">{photo.name}</span></div>
                  <div class="row"><span class="key">HEADS DETECTED</span><span class="val-info">{heads}</span></div>
                  <div class="row"><span class="key">HELMETS DETECTED</span><span class="val-info">{helmets}</span></div>
                  <div class="row"><span class="key">VIOLATIONS</span><span class="{'val-bad' if violations else 'val-ok'}">{violations}</span></div>
                  <div class="row"><span class="key">COMPLIANCE</span><span class="{'val-ok' if comp==100 else 'val-bad'}">{comp}%</span></div>
                </div>
                """, unsafe_allow_html=True)

            log_type = "violation" if violations else "photo"
            add_log(log_type, f"{photo.name} → {heads} head(s), {violations} violation(s)")

        if show_stats: render_stats_panel(stat_slots, 0, 0, 0)
        if show_log:   render_log_panel(log_slot)

# ═══════════════════════════════════════════════
#  SOURCE: RTSP
# ═══════════════════════════════════════════════
elif src == "RTSP Stream":
    # Quick guide
    with st.expander("📖 How to use RTSP Stream — Step-by-step guide", expanded=False):
        st.markdown("""
<div class="rtsp-step"><div class="snum">STEP 01 · FIND YOUR CAMERA IP</div>
Check your IP camera's manual or admin panel. Typically accessed at <code>http://192.168.x.x</code>. Look for the <b>Network</b> or <b>Stream</b> settings page.</div>

<div class="rtsp-step"><div class="snum">STEP 02 · GET THE RTSP URL FORMAT</div>
Most cameras use one of these formats:<br>
<code>rtsp://username:password@192.168.1.100:554/stream1</code><br>
<code>rtsp://192.168.1.100:554/h264/ch01/main/av_stream</code><br>
<code>rtsp://admin:admin123@192.168.1.100:554/live</code><br>
Check your camera brand's documentation for the exact path.</div>

<div class="rtsp-step"><div class="snum">STEP 03 · COMMON BRAND FORMATS</div>
• <b>Hikvision:</b> <code>rtsp://admin:pass@IP:554/Streaming/Channels/101</code><br>
• <b>Dahua:</b> <code>rtsp://admin:pass@IP:554/cam/realmonitor?channel=1&subtype=0</code><br>
• <b>Reolink:</b> <code>rtsp://admin:pass@IP:554/h264Preview_01_main</code><br>
• <b>TP-Link Tapo:</b> <code>rtsp://user:pass@IP:554/stream1</code><br>
• <b>Generic:</b> <code>rtsp://IP:554/live/ch0</code></div>

<div class="rtsp-step"><div class="snum">STEP 04 · TEST IN VLC FIRST</div>
Open VLC → Media → Open Network Stream → paste your URL. If video plays in VLC, it will work here too.</div>

<div class="rtsp-step"><div class="snum">STEP 05 · ENTER URL AND START</div>
Paste your RTSP URL in the sidebar field, then click the <b>▶ Connect to Stream</b> button below. Make sure your PC and camera are on the <b>same network</b>.</div>

<div class="rtsp-step"><div class="snum">STEP 06 · PHONE AS IP CAMERA (FREE)</div>
Install <b>IP Webcam</b> (Android) or <b>EpocCam</b> (iOS) on your phone.<br>
Start the server — it shows a URL like <code>http://192.168.1.55:8080</code>.<br>
Your RTSP URL will be: <code>rtsp://192.168.1.55:8080/h264_ulaw.sdp</code></div>
""", unsafe_allow_html=True)

    if st.button("▶  Connect to Stream"):
        if not rtsp_url:
            st.error("Enter an RTSP URL in the sidebar first.")
        else:
            cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
            if not cap.isOpened():
                st.error("❌ Cannot open stream. Verify URL, credentials and network.")
            else:
                st.success("✅ Stream connected")
                run_stream(cap)