# run command : python -m streamlit run app.py

import streamlit as st
import pickle
import pandas as pd
import numpy as np
import time
import warnings
warnings.filterwarnings('ignore')

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="CardioScan AI",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Load model & encoders ─────────────────────────────────────
@st.cache_resource
def load_model():
    with open('model.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('encoders.pkl', 'rb') as f:
        encoders = pickle.load(f)
    return model, encoders

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:wght@300;400;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #010812 !important;
    color: #c8e6ff !important;
    font-family: 'Exo 2', sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 50% at 50% -20%, rgba(0,180,255,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 80%, rgba(0,255,180,0.07) 0%, transparent 50%),
        #010812 !important;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { background: #020f1e !important; }

/* Hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem !important; max-width: 1400px !important; }

/* ── HERO HEADER ── */
.hero {
    text-align: center;
    padding: 3rem 0 2rem;
    position: relative;
}
.hero::before {
    content: '';
    position: absolute;
    top: 0; left: 50%;
    transform: translateX(-50%);
    width: 600px; height: 2px;
    background: linear-gradient(90deg, transparent, #00b4ff, #00ffb4, transparent);
    animation: scanline 3s ease-in-out infinite;
}
@keyframes scanline {
    0%, 100% { opacity: 0.3; width: 200px; }
    50% { opacity: 1; width: 600px; }
}
.hero-title {
    font-family: 'Orbitron', monospace;
    font-size: 3.2rem;
    font-weight: 900;
    letter-spacing: 0.15em;
    background: linear-gradient(135deg, #00b4ff 0%, #00ffb4 50%, #00b4ff 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmer 4s linear infinite;
}
@keyframes shimmer {
    0% { background-position: 0% center; }
    100% { background-position: 200% center; }
}
.hero-sub {
    font-family: 'Exo 2', sans-serif;
    font-size: 0.85rem;
    letter-spacing: 0.4em;
    color: #3a7a9c;
    margin-top: 0.5rem;
    text-transform: uppercase;
}
.hero-line {
    width: 100%;
    height: 1px;
    background: linear-gradient(90deg, transparent, #00b4ff33, #00ffb455, #00b4ff33, transparent);
    margin: 1.5rem 0;
}

/* ── CARDS ── */
.card {
    background: linear-gradient(135deg, rgba(0,20,40,0.9), rgba(0,10,25,0.95));
    border: 1px solid rgba(0,180,255,0.2);
    border-radius: 16px;
    padding: 1.8rem;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(10px);
    box-shadow: 0 0 40px rgba(0,0,0,0.5), inset 0 1px 0 rgba(0,180,255,0.1);
}
.card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, #00b4ff, transparent);
}
.card-title {
    font-family: 'Orbitron', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.3em;
    color: #00b4ff;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ── METRIC BOXES ── */
.metric-box {
    background: rgba(0,180,255,0.05);
    border: 1px solid rgba(0,180,255,0.15);
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.metric-box::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00b4ff, transparent);
    animation: pulse-bar 2s ease-in-out infinite;
}
@keyframes pulse-bar {
    0%, 100% { opacity: 0.3; }
    50% { opacity: 1; }
}
.metric-icon { font-size: 1.8rem; margin-bottom: 0.4rem; }
.metric-label {
    font-size: 0.65rem;
    letter-spacing: 0.25em;
    color: #3a7a9c;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
}
.metric-value {
    font-family: 'Orbitron', monospace;
    font-size: 2.2rem;
    font-weight: 700;
    color: #00ffb4;
    line-height: 1;
}
.metric-value.hr { color: #ff4d6d; }
.metric-value.spo2 { color: #00ffb4; }

/* ── SENSOR STATUS ── */
.sensor-status {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(0,255,180,0.08);
    border: 1px solid rgba(0,255,180,0.2);
    border-radius: 999px;
    padding: 0.4rem 1rem;
    font-size: 0.75rem;
    letter-spacing: 0.15em;
    color: #00ffb4;
    margin-bottom: 1rem;
}
.dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #00ffb4;
    box-shadow: 0 0 8px #00ffb4;
    animation: blink 1.2s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }

/* ── PROGRESS BAR ── */
.prog-track {
    background: rgba(0,180,255,0.08);
    border: 1px solid rgba(0,180,255,0.15);
    border-radius: 999px;
    height: 8px;
    overflow: hidden;
    margin: 0.5rem 0;
}
.prog-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #00b4ff, #00ffb4);
    transition: width 0.4s ease;
    box-shadow: 0 0 10px rgba(0,255,180,0.5);
}

/* ── RISK RESULT ── */
.result-box {
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.result-box.low {
    background: rgba(0,255,100,0.06);
    border: 2px solid rgba(0,255,100,0.3);
    box-shadow: 0 0 60px rgba(0,255,100,0.1);
}
.result-box.medium {
    background: rgba(255,170,0,0.06);
    border: 2px solid rgba(255,170,0,0.3);
    box-shadow: 0 0 60px rgba(255,170,0,0.1);
}
.result-box.high {
    background: rgba(255,50,50,0.06);
    border: 2px solid rgba(255,50,50,0.3);
    box-shadow: 0 0 60px rgba(255,50,50,0.1);
}
.result-label {
    font-family: 'Orbitron', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.4em;
    color: #3a7a9c;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.result-value {
    font-family: 'Orbitron', monospace;
    font-size: 2rem;
    font-weight: 900;
    letter-spacing: 0.1em;
}
.result-value.low  { color: #00ff64; text-shadow: 0 0 30px rgba(0,255,100,0.5); }
.result-value.medium { color: #ffaa00; text-shadow: 0 0 30px rgba(255,170,0,0.5); }
.result-value.high { color: #ff3232; text-shadow: 0 0 30px rgba(255,50,50,0.5); }

/* ── PROB BARS ── */
.prob-row {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 0.8rem;
}
.prob-name {
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    color: #3a7a9c;
    width: 120px;
    flex-shrink: 0;
}
.prob-track {
    flex: 1;
    background: rgba(0,180,255,0.08);
    border-radius: 999px;
    height: 6px;
    overflow: hidden;
}
.prob-fill {
    height: 100%;
    border-radius: 999px;
}
.prob-pct {
    font-family: 'Orbitron', monospace;
    font-size: 0.75rem;
    color: #c8e6ff;
    width: 45px;
    text-align: right;
    flex-shrink: 0;
}

/* ── INPUTS ── */
.stTextInput input, .stNumberInput input, .stSelectbox select {
    background: rgba(0,20,40,0.8) !important;
    border: 1px solid rgba(0,180,255,0.25) !important;
    border-radius: 8px !important;
    color: #c8e6ff !important;
    font-family: 'Exo 2', sans-serif !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: #00b4ff !important;
    box-shadow: 0 0 0 2px rgba(0,180,255,0.15) !important;
}
label { color: #3a7a9c !important; font-size: 0.78rem !important; letter-spacing: 0.15em !important; text-transform: uppercase !important; }

/* ── BUTTON ── */
.stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, rgba(0,180,255,0.15), rgba(0,255,180,0.1)) !important;
    border: 1px solid rgba(0,180,255,0.4) !important;
    border-radius: 10px !important;
    color: #00ffb4 !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.25em !important;
    padding: 0.8rem 1.5rem !important;
    transition: all 0.3s ease !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, rgba(0,180,255,0.25), rgba(0,255,180,0.2)) !important;
    border-color: #00ffb4 !important;
    box-shadow: 0 0 20px rgba(0,255,180,0.2) !important;
    transform: translateY(-1px) !important;
}

/* ── SELECTBOX ── */
[data-baseweb="select"] > div {
    background: rgba(0,20,40,0.8) !important;
    border: 1px solid rgba(0,180,255,0.25) !important;
    border-radius: 8px !important;
    color: #c8e6ff !important;
}

/* ── DIVIDER ── */
hr { border-color: rgba(0,180,255,0.1) !important; }

/* ── SPINNER ── */
.stSpinner > div { border-top-color: #00b4ff !important; }

/* ── ALERT ── */
.stAlert { background: rgba(0,20,40,0.8) !important; border-radius: 10px !important; }

/* ── GRID corner decorations ── */
.corner-deco {
    position: absolute;
    width: 12px; height: 12px;
}
.corner-deco.tl { top: 8px; left: 8px; border-top: 1px solid #00b4ff; border-left: 1px solid #00b4ff; }
.corner-deco.tr { top: 8px; right: 8px; border-top: 1px solid #00b4ff; border-right: 1px solid #00b4ff; }
.corner-deco.bl { bottom: 8px; left: 8px; border-bottom: 1px solid #00b4ff; border-left: 1px solid #00b4ff; }
.corner-deco.br { bottom: 8px; right: 8px; border-bottom: 1px solid #00b4ff; border-right: 1px solid #00b4ff; }

/* ── ECG line animation ── */
.ecg-container {
    width: 100%;
    height: 50px;
    overflow: hidden;
    position: relative;
    margin: 1rem 0;
}
.ecg-svg { width: 200%; animation: ecg-scroll 3s linear infinite; }
@keyframes ecg-scroll { from { transform: translateX(0); } to { transform: translateX(-50%); } }

/* ── NUMBER INPUT arrows hide ── */
input[type=number]::-webkit-inner-spin-button,
input[type=number]::-webkit-outer-spin-button { -webkit-appearance: none; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────
if 'sensor_hr'   not in st.session_state: st.session_state.sensor_hr   = None
if 'sensor_spo2' not in st.session_state: st.session_state.sensor_spo2 = None
if 'result'      not in st.session_state: st.session_state.result       = None
if 'probs'       not in st.session_state: st.session_state.probs        = None

# ── Helper ────────────────────────────────────────────────────
def risk_class(label):
    l = label.lower()
    if 'low'    in l: return 'low'
    if 'medium' in l or 'moderate' in l: return 'medium'
    return 'high'

def prob_color(i, total):
    colors = ['#00ff64', '#ffaa00', '#ff3232', '#00b4ff', '#bf00ff']
    return colors[i % len(colors)]

def ecg_svg():
    return """
    <div class="ecg-container">
      <svg class="ecg-svg" viewBox="0 0 800 50" xmlns="http://www.w3.org/2000/svg">
        <polyline points="
          0,25 60,25 70,25 80,5 90,45 100,25 120,25
          180,25 190,25 200,5 210,45 220,25 240,25
          300,25 310,25 320,5 330,45 340,25 360,25
          420,25 430,25 440,5 450,45 460,25 480,25
          540,25 550,25 560,5 570,45 580,25 600,25
          660,25 670,25 680,5 690,45 700,25 720,25
          780,25 790,25 800,25
        "
        fill="none" stroke="#ff4d6d" stroke-width="1.5"
        stroke-linecap="round" stroke-linejoin="round"
        filter="url(#glow)"/>
        <defs>
          <filter id="glow">
            <feGaussianBlur stdDeviation="1.5" result="blur"/>
            <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
        </defs>
      </svg>
    </div>
    """

# ── HERO ──────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-title">🫀 CARDIOSCAN AI</div>
  <div class="hero-sub">Advanced Cardiac Risk Assessment System · v2.0</div>
  <div class="hero-line"></div>
</div>
""", unsafe_allow_html=True)

# ── LAYOUT ───────────────────────────────────────────────────
col_left, col_right = st.columns([1, 1.2], gap="large")

# ════════════════════════════════════════════════════════
# LEFT COLUMN — Sensor + Inputs
# ════════════════════════════════════════════════════════
with col_left:

    # ── SENSOR PANEL ──────────────────────────────────
    st.markdown("""
    <div class="card">
      <div class="corner-deco tl"></div><div class="corner-deco tr"></div>
      <div class="corner-deco bl"></div><div class="corner-deco br"></div>
      <div class="card-title">⬡ &nbsp;BIOSENSOR INPUT</div>
    </div>
    """, unsafe_allow_html=True)

    # ECG animation
    st.markdown(ecg_svg(), unsafe_allow_html=True)

    # Sensor readings display
    m1, m2 = st.columns(2)
    with m1:
        hr_val = str(st.session_state.sensor_hr) if st.session_state.sensor_hr else "--"
        st.markdown(f"""
        <div class="metric-box">
          <div class="metric-icon">❤️</div>
          <div class="metric-label">Heart Rate</div>
          <div class="metric-value hr">{hr_val}</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        spo2_val = str(st.session_state.sensor_spo2) if st.session_state.sensor_spo2 else "--"
        st.markdown(f"""
        <div class="metric-box">
          <div class="metric-icon">🩸</div>
          <div class="metric-label">SpO2</div>
          <div class="metric-value spo2">{spo2_val}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Sensor scan button
    if st.button("⬡  SCAN FROM SENSOR", key="scan_btn"):
        with st.spinner("Connecting to MAX30100 sensor..."):
            try:
                from sensor_reader import read_sensor_data
                progress_placeholder = st.empty()
                progress_placeholder.markdown("""
                <div style="text-align:center; color:#00b4ff; font-family:'Orbitron',monospace;
                            font-size:0.8rem; letter-spacing:0.2em; padding:1rem;">
                  ⬡ &nbsp; READING BIOSIGNALS...
                </div>
                """, unsafe_allow_html=True)
                hr, spo2 = read_sensor_data()
                progress_placeholder.empty()
                if hr and spo2:
                    st.session_state.sensor_hr   = hr
                    st.session_state.sensor_spo2 = spo2
                    st.success(f"✅ Sensor capture complete — HR: {hr} | SpO2: {spo2}")
                    st.rerun()
                else:
                    st.error("❌ Sensor read failed. Check ESP32 connection.")
            except Exception as e:
                st.error(f"❌ Sensor error: {e}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── MANUAL OVERRIDE ───────────────────────────────
    st.markdown("""
    <div class="card-title" style="font-family:'Orbitron',monospace; font-size:0.65rem;
         letter-spacing:0.3em; color:#3a7a9c; text-transform:uppercase;">
      ◈ &nbsp; MANUAL OVERRIDE
    </div>
    """, unsafe_allow_html=True)

    mc1, mc2 = st.columns(2)
    with mc1:
        manual_hr = st.number_input(
            "Heart Rate", min_value=30, max_value=200,
            value=int(st.session_state.sensor_hr) if st.session_state.sensor_hr else 72,
            step=1
        )
    with mc2:
        manual_spo2 = st.number_input(
            "Oxygen Saturation", min_value=70, max_value=100,
            value=int(st.session_state.sensor_spo2) if st.session_state.sensor_spo2 else 98,
            step=1
        )

    # Use sensor values if available, else manual
    final_hr   = st.session_state.sensor_hr   if st.session_state.sensor_hr   else manual_hr
    final_spo2 = st.session_state.sensor_spo2 if st.session_state.sensor_spo2 else manual_spo2

    st.markdown("<br>", unsafe_allow_html=True)

    # ── PATIENT DATA ──────────────────────────────────
    st.markdown("""
    <div class="card-title" style="font-family:'Orbitron',monospace; font-size:0.65rem;
         letter-spacing:0.3em; color:#3a7a9c; text-transform:uppercase;">
      ◈ &nbsp; PATIENT PARAMETERS
    </div>
    """, unsafe_allow_html=True)

    age    = st.number_input("Age", min_value=1, max_value=120, value=45, step=1)
    gender = st.selectbox("Gender", ["Male", "Female"])

    wc, hc = st.columns(2)
    with wc:
        weight = st.number_input("Weight (kg)", min_value=10.0, max_value=300.0, value=70.0, step=0.5)
    with hc:
        height = st.number_input("Height (m)", min_value=0.5, max_value=2.5, value=1.70, step=0.01)

    bmi = weight / (height ** 2) if height > 0 else 0
    st.markdown(f"""
    <div style="text-align:right; font-family:'Orbitron',monospace; font-size:0.7rem;
                color:#3a7a9c; letter-spacing:0.15em; margin-top:0.3rem;">
      BMI &nbsp;<span style="color:#00b4ff;">{bmi:.1f}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ANALYSE BUTTON ────────────────────────────────
    if st.button("⬡  RUN CARDIAC ANALYSIS", key="predict_btn"):
        try:
            model, encoders = load_model()
            gender_enc = encoders['Gender'].transform([gender.lower().capitalize()])[0]

            input_df = pd.DataFrame([[
                final_hr, final_spo2, age, gender_enc, weight, height, bmi
            ]], columns=[
                'Heart Rate', 'Oxygen Saturation', 'Age', 'Gender',
                'Weight (kg)', 'Height (m)', 'Derived_BMI'
            ])

            with st.spinner("Analysing cardiac biomarkers..."):
                time.sleep(1.2)  # dramatic effect
                probs      = model.predict_proba(input_df)[0]
                pred_idx   = model.predict(input_df)[0]
                pred_label = encoders['Risk Category'].inverse_transform([pred_idx])[0]
                categories = encoders['Risk Category'].classes_

            st.session_state.result = pred_label
            st.session_state.probs  = list(zip(categories, probs))
            st.rerun()

        except FileNotFoundError:
            st.error("❌ model.pkl / encoders.pkl not found in working directory.")
        except Exception as e:
            st.error(f"❌ Analysis error: {e}")

    # Clear sensor button
    if st.session_state.sensor_hr:
        if st.button("↺  CLEAR SENSOR DATA", key="clear_btn"):
            st.session_state.sensor_hr   = None
            st.session_state.sensor_spo2 = None
            st.rerun()


# ════════════════════════════════════════════════════════
# RIGHT COLUMN — Results
# ════════════════════════════════════════════════════════
with col_right:

    if st.session_state.result is None:

        # ── IDLE STATE ────────────────────────────────
        st.markdown("""
        <div class="card" style="min-height:520px; display:flex; flex-direction:column;
             align-items:center; justify-content:center; text-align:center;">
          <div class="corner-deco tl"></div><div class="corner-deco tr"></div>
          <div class="corner-deco bl"></div><div class="corner-deco br"></div>
          <div style="font-size:4rem; margin-bottom:1.5rem; opacity:0.3;">🫀</div>
          <div style="font-family:'Orbitron',monospace; font-size:0.75rem;
                      letter-spacing:0.3em; color:#1a3a5c; text-transform:uppercase;">
            AWAITING ANALYSIS
          </div>
          <div style="font-size:0.8rem; color:#1a3050; margin-top:0.8rem;
                      max-width:260px; line-height:1.7;">
            Scan biosensor or enter patient parameters,<br>then run cardiac analysis
          </div>
          <div style="margin-top:2rem; width:80px; height:1px;
                      background:linear-gradient(90deg,transparent,#00b4ff33,transparent);">
          </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        result    = st.session_state.result
        probs     = st.session_state.probs
        rc        = risk_class(result)

        # ── RESULT CARD ───────────────────────────────
        st.markdown(f"""
        <div class="card">
          <div class="corner-deco tl"></div><div class="corner-deco tr"></div>
          <div class="corner-deco bl"></div><div class="corner-deco br"></div>
          <div class="card-title">⬡ &nbsp;ANALYSIS COMPLETE</div>

          <div class="result-box {rc}">
            <div class="result-label">CARDIAC RISK CLASSIFICATION</div>
            <div class="result-value {rc}">{result.upper()}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── PROBABILITY BREAKDOWN ─────────────────────
        # FIX: Use individual st.markdown calls per row instead of
        # concatenating HTML strings, which causes Streamlit to
        # escape the tags and render raw HTML code on screen.
        st.markdown("""
        <div class="card-title" style="font-family:'Orbitron',monospace; font-size:0.65rem;
             letter-spacing:0.3em; color:#3a7a9c; text-transform:uppercase;">
          ◈ &nbsp; PROBABILITY DISTRIBUTION
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="padding:0.5rem 0;">', unsafe_allow_html=True)

        for i, (cat, prob) in enumerate(probs):
            pct   = round(prob * 100, 1)
            color = prob_color(i, len(probs))
            st.markdown(f"""
            <div class="prob-row">
              <div class="prob-name">{cat}</div>
              <div class="prob-track">
                <div class="prob-fill" style="width:{pct}%; background:{color};
                     box-shadow:0 0 8px {color}66;"></div>
              </div>
              <div class="prob-pct">{pct}%</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── VITALS SUMMARY ────────────────────────────
        st.markdown("""
        <div class="card-title" style="font-family:'Orbitron',monospace; font-size:0.65rem;
             letter-spacing:0.3em; color:#3a7a9c; text-transform:uppercase;">
          ◈ &nbsp; VITALS SNAPSHOT
        </div>
        """, unsafe_allow_html=True)

        v1, v2, v3, v4 = st.columns(4)
        vitals = [
            ("❤️", "HR", f"{final_hr}"),
            ("🩸", "SpO2", f"{final_spo2}"),
            ("📅", "Age", f"{age}"),
            ("⚖️", "BMI", f"{bmi:.1f}"),
        ]
        for col, (icon, label, val) in zip([v1,v2,v3,v4], vitals):
            with col:
                st.markdown(f"""
                <div class="metric-box" style="padding:0.8rem;">
                  <div class="metric-icon" style="font-size:1.2rem;">{icon}</div>
                  <div class="metric-label">{label}</div>
                  <div style="font-family:'Orbitron',monospace; font-size:1.1rem;
                              font-weight:700; color:#c8e6ff;">{val}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── RECOMMENDATION ────────────────────────────
        recs = {
            'low':    ("✅", "#00ff64", "LOW RISK DETECTED",
                       "Cardiac biomarkers within normal range. Continue routine monitoring and maintain healthy lifestyle practices."),
            'medium': ("⚠️", "#ffaa00", "MODERATE RISK DETECTED",
                       "Elevated cardiac indicators observed. Recommend consultation with a cardiologist and lifestyle modifications."),
            'high':   ("🚨", "#ff3232", "HIGH RISK DETECTED",
                       "Critical cardiac risk indicators present. Immediate medical consultation strongly recommended."),
        }
        icon, color, title, msg = recs[rc]
        st.markdown(f"""
        <div style="background:rgba(0,20,40,0.6); border:1px solid {color}33;
                    border-left:3px solid {color}; border-radius:10px;
                    padding:1.2rem 1.5rem;">
          <div style="font-family:'Orbitron',monospace; font-size:0.7rem;
                      letter-spacing:0.2em; color:{color}; margin-bottom:0.5rem;">
            {icon} &nbsp; {title}
          </div>
          <div style="font-size:0.85rem; color:#7aabcc; line-height:1.7;">{msg}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── RESET ─────────────────────────────────────
        if st.button("⬡  NEW ASSESSMENT", key="reset_btn"):
            st.session_state.result      = None
            st.session_state.probs       = None
            st.session_state.sensor_hr   = None
            st.session_state.sensor_spo2 = None
            st.rerun()

# ── FOOTER ────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; margin-top:3rem; padding-top:1.5rem;
            border-top:1px solid rgba(0,180,255,0.08);">
  <div style="font-family:'Orbitron',monospace; font-size:0.6rem;
              letter-spacing:0.4em; color:#1a3050;">
    CARDIOSCAN AI &nbsp;·&nbsp; MAX30100 BIOSENSOR &nbsp;·&nbsp; ESP32 &nbsp;·&nbsp;
    FOR RESEARCH USE ONLY
  </div>
</div>
""", unsafe_allow_html=True)