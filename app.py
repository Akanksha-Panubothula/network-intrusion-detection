import os
from pathlib import Path
import pickle
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# ============================================================
# PAGE SETUP
# ============================================================
st.set_page_config(
    page_title="Network Intrusion and Anomaly Detection System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# ROBUST HTML RENDERER
# Uses st.html when available so HTML/CSS is never shown as raw text.
# Falls back to st.markdown for older Streamlit versions.
# ============================================================
def render(content, *args, **kwargs):
    unsafe = kwargs.pop("unsafe_allow_html", False)
    if unsafe and hasattr(st, "html"):
        return st.html(content)
    return st.markdown(content, *args, **kwargs)

# ============================================================
# PROJECT PATH DISCOVERY
# ============================================================
BASE = Path(__file__).resolve().parent

def find_file(names):
    """Find a file in the app folder/project tree."""
    for name in names:
        direct = BASE / name
        if direct.exists():
            return direct
    for name in names:
        matches = list(BASE.rglob(name))
        if matches:
            return matches[0]
    return None

RF_PATH = find_file([
    "random_forest_model.pkl",
    "random_forest.pkl",
    "rf_model.pkl",
    "random_forest_model.sav",
])

ENCODER_PATH = find_file([
    "label_encoder.pkl",
    "label_encoder.sav",
    "encoder.pkl",
])

DATASET_PATH = find_file([
    "clean_dataset.csv",
    "final_clean_dataset.csv",
    "processed_dataset.csv",
])

FEATURE_PATH = find_file([
    "feature_names.pkl",
    "features.pkl",
    "model_features.pkl",
])

# ============================================================
# THEME
# ============================================================
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark"

with st.sidebar:
    render("### 🎨 Theme Customization")
    theme_choice = st.radio(
        "Select Portal Theme:",
        ["🌙 Deep Dark Cyber", "☀️ Modern Light Theme"],
        index=0 if st.session_state.theme_mode == "Dark" else 1,
    )
    st.session_state.theme_mode = (
        "Dark" if theme_choice.startswith("🌙") else "Light"
    )

    render("---")
    render(
        """
        <div class="security-visual">
            <div class="visual-grid"></div>
            <div class="visual-orbit orbit-a"></div>
            <div class="visual-orbit orbit-b"></div>
            <div class="visual-node n1"></div>
            <div class="visual-node n2"></div>
            <div class="visual-node n3"></div>
            <div class="visual-node n4"></div>
            <div class="shield-mark">
                <svg viewBox="0 0 100 115" aria-hidden="true">
                    <defs>
                        <linearGradient id="shieldGrad" x1="0" y1="0" x2="1" y2="1">
                            <stop offset="0%" stop-color="#22D3EE"/>
                            <stop offset="52%" stop-color="#6366F1"/>
                            <stop offset="100%" stop-color="#A855F7"/>
                        </linearGradient>
                    </defs>
                    <path d="M50 5 L88 20 V51 C88 78 72 98 50 109 C28 98 12 78 12 51 V20 Z"
                          fill="none" stroke="url(#shieldGrad)" stroke-width="5"/>
                    <path d="M31 56 L44 69 L70 40"
                          fill="none" stroke="#34D399" stroke-width="7"
                          stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </div>
            <div class="visual-caption">NIDS • AI SECURITY</div>
            <div class="visual-subcaption">LIVE TELEMETRY MONITOR</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render(
        """
        <div class="sidebar-status">
            <span class="status-dot"></span>
            <div>
                <b>Inference Core Online</b>
                <small>Random Forest telemetry ready</small>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

is_dark = st.session_state.theme_mode == "Dark"
bg_app = "#090D16" if is_dark else "#F8FAFC"
bg_sidebar = "#0F172A" if is_dark else "#FFFFFF"
bg_card = "#111827" if is_dark else "#FFFFFF"
text_main = "#FFFFFF" if is_dark else "#0F172A"
text_sub = "#CBD5E1" if is_dark else "#475569"
border_color = "#334155" if is_dark else "#94A3B8"
chart_text_color = "#FFFFFF" if is_dark else "#0F172A"
chart_grid_color = (
    "rgba(255,255,255,.18)" if is_dark else "rgba(15,23,42,.12)"
)
hero_bg = (
    "linear-gradient(135deg, rgba(8,15,28,.98), rgba(20,18,45,.96) 58%, rgba(8,30,38,.96))"
    if is_dark
    else "linear-gradient(135deg, #FFFFFF 0%, #F5F3FF 52%, #ECFEFF 100%)"
)
hero_border = "rgba(34,211,238,.28)" if is_dark else "rgba(99,102,241,.22)"
hero_sub = "#AAB8CB" if is_dark else "#475569"

# ============================================================
# CSS
# ============================================================
render(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {{ font-family: Inter, sans-serif !important; }}

.stApp {{
    background:
        radial-gradient(circle at 8% 8%, rgba(34,211,238,.10), transparent 24%),
        radial-gradient(circle at 92% 12%, rgba(168,85,247,.10), transparent 25%),
        radial-gradient(circle at 50% 100%, rgba(52,211,153,.06), transparent 28%),
        {bg_app} !important;
    color:{text_main} !important;
    animation: appFade .7s ease-out both;
}}

.stApp::before {{
    content:"";
    position:fixed;
    inset:0;
    pointer-events:none;
    z-index:0;
    opacity:{" .18" if is_dark else ".10"};
    background-image:
        linear-gradient(rgba(99,102,241,.12) 1px, transparent 1px),
        linear-gradient(90deg, rgba(34,211,238,.10) 1px, transparent 1px);
    background-size:48px 48px;
    mask-image:linear-gradient(to bottom, black, transparent 92%);
    animation:gridDrift 18s linear infinite;
}}

.block-container {{ position:relative; z-index:1; animation:contentRise .65s ease-out both; }}

h1,h2,h3,h4,h5,h6,p,label,span {{ color:{text_main} !important; }}

section[data-testid="stSidebar"] {{
    background:
        radial-gradient(circle at 20% 10%, rgba(34,211,238,.09), transparent 30%),
        radial-gradient(circle at 80% 80%, rgba(168,85,247,.08), transparent 30%),
        {bg_sidebar} !important;
    border-right:1px solid {border_color} !important;
    transition:background .35s ease, border-color .35s ease;
}}
section[data-testid="stSidebar"] * {{ color:{text_main} !important; }}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {{
    background:{"#111827" if is_dark else "#FFFFFF"} !important;
    border:2px solid {"#334155" if is_dark else "#CBD5E1"} !important;
    border-radius:10px !important;
    transition:all .25s ease !important;
}}
div[data-baseweb="select"] > div:hover,
div[data-baseweb="input"] > div:focus-within {{
    border-color:#6366F1 !important;
    box-shadow:0 0 0 4px rgba(99,102,241,.10), 0 7px 20px rgba(99,102,241,.10) !important;
    transform:translateY(-1px);
}}
div[data-baseweb="select"] *, div[data-baseweb="input"] input {{
    color:{"#F8FAFC" if is_dark else "#0F172A"} !important; font-weight:700 !important;
}}

[data-testid="stFileUploader"] section {{
    background:{bg_card} !important; border:2px dashed #64748B !important; border-radius:14px !important; padding:20px !important;
}}
[data-testid="stFileUploader"] section * {{ color:{text_main} !important; font-weight:600 !important; }}
[data-testid="stFileUploader"] section button {{ background:#E2E8F0 !important; border:1px solid #94A3B8 !important; border-radius:8px !important; }}
[data-testid="stFileUploader"] section button * {{ color:#0F172A !important; }}
[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] {{ background:#1E293B !important; border:1px solid #64748B !important; border-radius:9px !important; padding:7px 10px !important; }}
[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] * {{ color:#FFFFFF !important; fill:#FFFFFF !important; font-weight:700 !important; }}

div.stButton > button {{
    background:linear-gradient(100deg,#2563EB,#6366F1 48%,#A855F7) !important; color:#FFFFFF !important;
    border:none !important; border-radius:12px !important; font-weight:900 !important; min-height:50px !important;
    letter-spacing:.2px !important; box-shadow:0 9px 28px rgba(79,70,229,.28) !important;
    transition:transform .22s ease, box-shadow .22s ease, filter .22s ease !important; animation:buttonGlow 3s ease-in-out infinite;
}}
div.stButton > button:hover {{ transform:translateY(-3px) scale(1.01) !important; filter:saturate(1.15) brightness(1.05) !important; box-shadow:0 14px 34px rgba(99,102,241,.38) !important; }}

.metric-symbol-card {{
    background:{bg_card}; border:1px solid {border_color}; border-radius:15px; padding:17px; text-align:center;
    box-shadow:0 8px 24px rgba(0,0,0,.10); transition:transform .25s ease, box-shadow .25s ease, border-color .25s ease;
}}
.metric-symbol-card:hover {{ transform:translateY(-4px); border-color:#6366F1; box-shadow:0 13px 30px rgba(99,102,241,.15); }}
.metric-symbol-card h4 {{ color:{text_sub} !important; font-size:.78rem; margin:0 0 7px 0; text-transform:uppercase; letter-spacing:.6px; }}
.metric-symbol-card div {{ color:{text_main} !important; font-size:1.45rem; font-weight:800; }}

.hero {{
    position:relative; overflow:hidden; padding:30px 34px; border-radius:24px;
    border:1px solid {hero_border}; background:{hero_bg}; box-shadow:0 20px 55px rgba(0,0,0,.15);
    transition:all .35s ease; animation:heroIn .8s cubic-bezier(.2,.8,.2,1) both;
}}
.hero::before {{
    content:""; position:absolute; width:280px; height:280px; right:-100px; top:-150px; border-radius:50%;
    background:radial-gradient(circle, rgba(34,211,238,.22), transparent 68%); animation:heroOrb 7s ease-in-out infinite;
}}
.hero::after {{
    content:""; position:absolute; width:240px; height:2px; right:-30px; bottom:28px;
    background:linear-gradient(90deg, transparent, #22D3EE, #A855F7, transparent); animation:scanLine 3.8s linear infinite;
}}
.hero h1 {{
    position:relative; z-index:2; background:linear-gradient(90deg,#22D3EE 0%,#6366F1 42%,#A855F7 70%,#F59E0B 100%);
    -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent;
}}
.hero p {{ color:{hero_sub} !important; }}

.security-visual {{
    position:relative; height:205px; margin:8px 2px 16px; overflow:hidden; border-radius:22px;
    border:1px solid rgba(99,102,241,.24);
    background:radial-gradient(circle at 50% 45%, rgba(34,211,238,.18), transparent 24%),
               linear-gradient(145deg, rgba(34,211,238,.07), rgba(99,102,241,.08), rgba(168,85,247,.09));
    box-shadow:inset 0 0 35px rgba(34,211,238,.05), 0 10px 28px rgba(0,0,0,.10);
}}
.visual-grid {{
    position:absolute; inset:0; opacity:.28;
    background-image:linear-gradient(rgba(34,211,238,.18) 1px, transparent 1px),
                     linear-gradient(90deg, rgba(99,102,241,.18) 1px, transparent 1px);
    background-size:24px 24px; transform:perspective(260px) rotateX(58deg) scale(1.35);
    transform-origin:center bottom; animation:gridMove 8s linear infinite;
}}
.shield-mark {{
    position:absolute; left:50%; top:42%; width:70px; height:82px; transform:translate(-50%,-50%);
    filter:drop-shadow(0 0 18px rgba(34,211,238,.38)); animation:shieldFloat 3.2s ease-in-out infinite; z-index:3;
}}
.shield-mark svg {{ width:100%; height:100%; }}
.visual-orbit {{ position:absolute; left:50%; top:42%; border:1px solid rgba(34,211,238,.38); border-radius:50%; transform:translate(-50%,-50%); }}
.orbit-a {{ width:120px; height:120px; animation:orbitSpin 7s linear infinite; }}
.orbit-b {{ width:170px; height:72px; animation:orbitTilt 5s linear infinite; }}
.visual-node {{ position:absolute; width:7px; height:7px; border-radius:50%; background:#22D3EE; box-shadow:0 0 12px rgba(34,211,238,.85); animation:nodePulse 2.2s ease-in-out infinite; }}
.n1 {{left:12%;top:28%;}} .n2 {{right:13%;top:25%;animation-delay:.5s;background:#A855F7;}}
.n3 {{left:19%;bottom:24%;animation-delay:1s;background:#34D399;}} .n4 {{right:18%;bottom:21%;animation-delay:1.5s;background:#F59E0B;}}
.visual-caption {{ position:absolute; left:0; right:0; bottom:25px; text-align:center; font-size:.72rem; letter-spacing:2px; font-weight:900; color:{text_main}; }}
.visual-subcaption {{ position:absolute; left:0; right:0; bottom:9px; text-align:center; font-size:.57rem; letter-spacing:1.2px; color:{text_sub}; }}

.sidebar-status {{
    display:flex; align-items:center; gap:10px; padding:12px 13px; border-radius:13px;
    border:1px solid rgba(52,211,153,.22); background:rgba(52,211,153,.06); margin-top:8px;
}}
.sidebar-status b {{ display:block; font-size:.76rem; }}
.sidebar-status small {{ display:block; margin-top:3px; color:{text_sub} !important; font-size:.64rem; }}
.status-dot {{ width:9px; height:9px; border-radius:50%; background:#34D399; box-shadow:0 0 0 0 rgba(52,211,153,.6); animation:statusPulse 1.8s infinite; flex:0 0 auto; }}

.input-panel {{
    padding:24px; border-radius:20px; background:{bg_card}; border:1px solid {border_color};
    box-shadow:0 10px 30px rgba(0,0,0,.07); animation:panelIn .55s ease both;
}}
.result-card {{
    position:relative; overflow:hidden; padding:25px; border-radius:20px; margin-top:20px;
    box-shadow:0 14px 38px rgba(0,0,0,.12); animation:resultIn .7s cubic-bezier(.2,.8,.2,1) both;
}}
.result-card::before {{
    content:""; position:absolute; left:0; top:0; bottom:0; width:5px;
    background:linear-gradient(180deg,#22D3EE,#6366F1,#A855F7); animation:resultScan 2.5s ease-in-out infinite;
}}
.small-note {{ color:{text_sub} !important; font-size:.84rem; }}
[data-testid="stMetric"] {{ background:{bg_card}; border:1px solid {border_color}; border-radius:14px; padding:10px; transition:transform .2s ease, border-color .2s ease; }}
[data-testid="stMetric"]:hover {{ transform:translateY(-3px); border-color:#6366F1; }}
div[data-testid="stTabs"] button {{ transition:all .25s ease !important; }}
div[data-testid="stTabs"] button:hover {{ color:#6366F1 !important; transform:translateY(-1px); }}

@keyframes appFade {{ from {{opacity:0;}} to {{opacity:1;}} }}
@keyframes contentRise {{ from {{opacity:0;transform:translateY(12px);}} to {{opacity:1;transform:translateY(0);}} }}
@keyframes heroIn {{ from {{opacity:0;transform:translateY(-14px) scale(.985);}} to {{opacity:1;transform:translateY(0) scale(1);}} }}
@keyframes panelIn {{ from {{opacity:0;transform:translateY(10px);}} to {{opacity:1;transform:translateY(0);}} }}
@keyframes resultIn {{ from {{opacity:0;transform:translateY(18px) scale(.98);}} to {{opacity:1;transform:translateY(0) scale(1);}} }}
@keyframes gridDrift {{ from {{background-position:0 0,0 0;}} to {{background-position:48px 48px,-48px 48px;}} }}
@keyframes gridMove {{ from {{background-position:0 0,0 0;}} to {{background-position:0 48px,48px 0;}} }}
@keyframes heroOrb {{ 0%,100% {{transform:translate(0,0) scale(1);opacity:.7;}} 50% {{transform:translate(-70px,70px) scale(1.3);opacity:1;}} }}
@keyframes scanLine {{ 0% {{transform:translateX(180px);opacity:0;}} 15% {{opacity:1;}} 85% {{opacity:1;}} 100% {{transform:translateX(-380px);opacity:0;}} }}
@keyframes shieldFloat {{ 0%,100% {{transform:translate(-50%,-50%) translateY(0);}} 50% {{transform:translate(-50%,-50%) translateY(-7px);}} }}
@keyframes orbitSpin {{ from {{transform:translate(-50%,-50%) rotate(0deg);}} to {{transform:translate(-50%,-50%) rotate(360deg);}} }}
@keyframes orbitTilt {{ from {{transform:translate(-50%,-50%) rotateX(62deg) rotateZ(0deg);}} to {{transform:translate(-50%,-50%) rotateX(62deg) rotateZ(360deg);}} }}
@keyframes nodePulse {{ 0%,100% {{transform:scale(1);opacity:.55;}} 50% {{transform:scale(1.8);opacity:1;}} }}
@keyframes statusPulse {{ 0% {{box-shadow:0 0 0 0 rgba(52,211,153,.55);}} 70% {{box-shadow:0 0 0 8px rgba(52,211,153,0);}} 100% {{box-shadow:0 0 0 0 rgba(52,211,153,0);}} }}
@keyframes buttonGlow {{ 0%,100% {{box-shadow:0 9px 28px rgba(79,70,229,.24);}} 50% {{box-shadow:0 12px 34px rgba(168,85,247,.34);}} }}
@keyframes resultScan {{ 0%,100% {{opacity:.7;}} 50% {{opacity:1;filter:brightness(1.4);}} }}
@media (prefers-reduced-motion: reduce) {{ *, *::before, *::after {{ animation-duration:.01ms !important; animation-iteration-count:1 !important; scroll-behavior:auto !important; }} }}
</style>
""",
    unsafe_allow_html=True,
)
# ============================================================
# ORIGINAL 79-FEATURE MODEL
# ============================================================
@st.cache_resource
def load_original_model():
    if RF_PATH is None:
        return None, None, None

    with open(RF_PATH, "rb") as f:
        model = pickle.load(f)

    encoder = None
    if ENCODER_PATH is not None:
        with open(ENCODER_PATH, "rb") as f:
            encoder = pickle.load(f)

    features = None

    if hasattr(model, "feature_names_in_"):
        features = [str(x) for x in model.feature_names_in_]

    if features is None and FEATURE_PATH is not None:
        with open(FEATURE_PATH, "rb") as f:
            features = list(pickle.load(f))

    return model, encoder, features

original_model, original_encoder, original_features = load_original_model()

if original_model is not None:
    try:
        ORIGINAL_FEATURE_COUNT = int(original_model.n_features_in_)
    except Exception:
        ORIGINAL_FEATURE_COUNT = len(original_features or [])
else:
    ORIGINAL_FEATURE_COUNT = 79

# ============================================================
# 15 FEATURE LIVE MODEL
#
# This is a SECOND model for the simplified live/external
# pathway. The original 79-feature model is NOT changed.
# ============================================================
LIVE_FEATURES = [
    "Protocol",
    "Destination Port",
    "Flow Duration",
    "Total Fwd Packets",
    "Total Backward Packets",
    "Total Length of Fwd Packets",
    "Total Length of Bwd Packets",
    "Flow Bytes/s",
    "Flow Packets/s",
    "Fwd Packet Length Mean",
    "Bwd Packet Length Mean",
    "Packet Length Mean",
    "Packet Length Std",
    "SYN Flag Count",
    "ACK Flag Count",
]

LIVE_ALIASES = {
    "Protocol": ["protocol", "proto", "protocol_type"],
    "Destination Port": [
        "destination port", "dest port", "dst port",
        "destination_port", "dst_port", "dport"
    ],
    "Flow Duration": [
        "flow duration", "duration", "flow_duration", "dur"
    ],
    "Total Fwd Packets": [
        "total fwd packets", "fwd packets", "total_fwd_packets",
        "tot_fwd_pkts", "fwd_pkts"
    ],
    "Total Backward Packets": [
        "total backward packets", "bwd packets",
        "total_bwd_packets", "tot_bwd_pkts", "bwd_pkts"
    ],
    "Total Length of Fwd Packets": [
        "total length of fwd packets", "fwd bytes",
        "total_fwd_bytes", "totlen_fwd_pkts"
    ],
    "Total Length of Bwd Packets": [
        "total length of bwd packets", "bwd bytes",
        "total_bwd_bytes", "totlen_bwd_pkts"
    ],
    "Flow Bytes/s": [
        "flow bytes/s", "flow bytes per second",
        "bytes/s", "bytes_per_sec", "flow_bytes_s"
    ],
    "Flow Packets/s": [
        "flow packets/s", "flow packets per second",
        "packets/s", "packets_per_sec", "flow_packets_s"
    ],
    "Fwd Packet Length Mean": [
        "fwd packet length mean", "fwd_pkt_len_mean",
        "forward packet length mean"
    ],
    "Bwd Packet Length Mean": [
        "bwd packet length mean", "bwd_pkt_len_mean",
        "backward packet length mean"
    ],
    "Packet Length Mean": [
        "packet length mean", "pkt_len_mean",
        "packet_mean", "mean_packet_length"
    ],
    "Packet Length Std": [
        "packet length std", "pkt_len_std",
        "packet_std", "packet_length_std"
    ],
    "SYN Flag Count": [
        "syn flag count", "syn_count", "syn flags",
        "syn_flag_count", "syn"
    ],
    "ACK Flag Count": [
        "ack flag count", "ack_count", "ack flags",
        "ack_flag_count", "ack"
    ],
}

def canonical(s):
    return (
        str(s).strip().lower()
        .replace(" ", "")
        .replace("_", "")
        .replace("-", "")
        .replace("/", "")
        .replace(":", "")
    )

def find_matching_column(columns, aliases):
    cmap = {canonical(c): c for c in columns}
    for alias in aliases:
        if canonical(alias) in cmap:
            return cmap[canonical(alias)]
    return None

def find_label_column(columns):
    candidates = [
        "label", "attack", "attack_cat", "attack category",
        "target", "class", "category", "classification"
    ]
    return find_matching_column(columns, candidates)

def protocol_to_number(value):
    if pd.isna(value):
        return 0
    s = str(value).strip().lower()
    mapping = {
        "tcp": 6, "tcp stream": 6,
        "udp": 17, "udp datagram": 17,
        "icmp": 1, "icmp ping": 1,
        "6": 6, "17": 17, "1": 1
    }
    if s in mapping:
        return mapping[s]
    try:
        return float(value)
    except Exception:
        return 0.0

def numeric_series(series, feature_name):
    if feature_name == "Protocol":
        return series.apply(protocol_to_number).astype(float)

    return pd.to_numeric(
        series.astype(str).str.replace(",", "", regex=False),
        errors="coerce"
    ).replace([np.inf, -np.inf], np.nan).fillna(0)

@st.cache_resource(show_spinner="Preparing the 15-feature live Random Forest...")
def train_live_model(dataset_path):
    """
    Train a separate 15-feature Random Forest from the project's
    existing labeled CIC-IDS2017 clean dataset.

    This does NOT modify the original 79-feature model or the
    Model Evaluation page.
    """
    if dataset_path is None or not Path(dataset_path).exists():
        return None, None, None

    df = pd.read_csv(dataset_path, low_memory=False)

    label_col = find_label_column(df.columns)
    if label_col is None:
        return None, None, None

    matched = {}
    missing = []

    for feature in LIVE_FEATURES:
        col = find_matching_column(
            df.columns,
            [feature] + LIVE_ALIASES.get(feature, [])
        )
        if col is None:
            missing.append(feature)
        else:
            matched[feature] = col

    if missing:
        return None, None, None

    work = pd.DataFrame(index=df.index)

    for feature in LIVE_FEATURES:
        work[feature] = numeric_series(
            df[matched[feature]],
            feature
        )

    y = df[label_col].astype(str).str.strip()

    valid = y.ne("") & y.notna()
    work = work.loc[valid]
    y = y.loc[valid]

    # Remove unusable rows.
    work = work.replace([np.inf, -np.inf], np.nan).fillna(0)

    # Balanced sampling keeps app startup practical on the huge
    # CIC-IDS2017 dataset while preserving all classes.
    tmp = work.copy()
    tmp["_target_"] = y.values

    max_per_class = 6000
    parts = []

    for _, group in tmp.groupby("_target_", sort=False):
        if len(group) > max_per_class:
            group = group.sample(
                n=max_per_class,
                random_state=42
            )
        parts.append(group)

    train_df = pd.concat(parts, ignore_index=True)

    X = train_df[LIVE_FEATURES].astype(np.float32)
    y = train_df["_target_"].astype(str)

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    rf = RandomForestClassifier(
        n_estimators=180,
        max_depth=22,
        min_samples_leaf=1,
        class_weight="balanced_subsample",
        random_state=42,
        n_jobs=-1
    )

    rf.fit(X, y_encoded)

    return rf, le, LIVE_FEATURES

live_model, live_encoder, _ = train_live_model(
    str(DATASET_PATH) if DATASET_PATH else None
)

# ============================================================
# HELPERS
# ============================================================
CLASS_COLORS = {
    "BENIGN": "#22C55E",
    "PortScan": "#38BDF8",
    "DoS Hulk": "#EF4444",
    "DDoS": "#F97316",
    "DoS GoldenEye": "#F59E0B",
    "FTP-Patator": "#A855F7",
    "SSH-Patator": "#8B5CF6",
    "DoS slowloris": "#14B8A6",
    "DoS Slowhttptest": "#FB7185",
    "Bot": "#06B6D4",
    "Infiltration": "#EAB308",
    "Web Attack - Brute Force": "#EC4899",
    "Web Attack - XSS": "#F43F5E",
    "Web Attack - Sql Injection": "#84CC16",
    "Heartbleed": "#6366F1",
}

DEFAULT_COLORS = [
    "#22C55E", "#38BDF8", "#EF4444", "#F97316",
    "#A855F7", "#14B8A6", "#EAB308", "#EC4899",
    "#6366F1", "#06B6D4", "#F43F5E", "#84CC16"
]

def pretty_label(label):
    return str(label)

def color_for_label(label, index=0):
    s = str(label)
    if s in CLASS_COLORS:
        return CLASS_COLORS[s]
    if s.upper() == "BENIGN":
        return "#22C55E"
    return DEFAULT_COLORS[index % len(DEFAULT_COLORS)]

def decode_prediction(model, encoder, pred):
    try:
        if encoder is not None:
            return str(encoder.inverse_transform([pred])[0])
    except Exception:
        pass
    return str(pred)

def make_original_input(df):
    if original_model is None:
        raise RuntimeError(
            "The original Random Forest model file was not found."
        )

    expected = ORIGINAL_FEATURE_COUNT

    if original_features is None:
        raise RuntimeError(
            "The Random Forest was found, but its 79 feature names "
            "could not be determined. Place feature_names.pkl beside "
            "app.py or ensure the model contains feature_names_in_."
        )

    if len(original_features) != expected:
        raise RuntimeError(
            f"Feature-name count mismatch: model expects {expected}, "
            f"but feature_names contains {len(original_features)}."
        )

    out = pd.DataFrame(index=df.index)

    for feature in original_features:
        col = find_matching_column(
            df.columns,
            [feature]
        )
        if col is None:
            raise KeyError(feature)

        out[feature] = numeric_series(
            df[col],
            feature
        )

    return out.astype(np.float32)

def build_live_external_frame(df, mapping):
    out = pd.DataFrame(index=df.index)

    for feature in LIVE_FEATURES:
        selected = mapping.get(feature)
        if selected is None or selected == "— Not mapped —":
            raise ValueError(
                f"'{feature}' has not been mapped."
            )
        out[feature] = numeric_series(
            df[selected],
            feature
        )

    return out.astype(np.float32)

def auto_mapping(df):
    mapping = {}
    for feature in LIVE_FEATURES:
        mapping[feature] = find_matching_column(
            df.columns,
            [feature] + LIVE_ALIASES.get(feature, [])
        )
    return mapping

def run_live_prediction(X):
    if live_model is None or live_encoder is None:
        raise RuntimeError(
            "The 15-feature live model is unavailable. "
            "Make sure clean_dataset.csv is available in the project."
        )

    pred = live_model.predict(X)
    labels = [
        decode_prediction(live_model, live_encoder, p)
        for p in pred
    ]

    probs = None
    if hasattr(live_model, "predict_proba"):
        probs = live_model.predict_proba(X)

    return labels, probs

# ============================================================
# HERO
# ============================================================
render(
    f"""
    <div class="hero">
        <div style="position:relative;z-index:2;display:flex;align-items:center;gap:16px;">
            <div style="
                width:58px;height:58px;border-radius:17px;display:flex;align-items:center;justify-content:center;
                background:linear-gradient(135deg,rgba(34,211,238,.16),rgba(99,102,241,.18),rgba(168,85,247,.16));
                border:1px solid rgba(99,102,241,.28);box-shadow:0 0 28px rgba(34,211,238,.12);
                animation:shieldFloat 3s ease-in-out infinite;">
                <span style="font-size:31px;line-height:1;">🛡️</span>
            </div>
            <div>
                <div style="color:#22D3EE;font-size:.76rem;font-weight:900;letter-spacing:2.2px;">
                    AI • NETWORK SECURITY • TRAFFIC INTELLIGENCE
                </div>
                <div style="color:{text_sub};font-size:.68rem;font-weight:800;letter-spacing:1.4px;margin-top:4px;">
                    REAL-TIME THREAT TELEMETRY
                </div>
            </div>
        </div>
        <h1 style="position:relative;z-index:2;font-size:2.45rem;font-weight:900;margin:14px 0 6px 0;">
            Network Intrusion & Anomaly Detection System
        </h1>
        <p style="position:relative;z-index:2;margin:0;max-width:930px;line-height:1.65;">
            An intelligent network-flow monitoring portal powered by a dedicated 15-feature
            Random Forest inference engine for real-time traffic classification.
        </p>
        <div style="
            position:relative;z-index:2;display:inline-flex;align-items:center;gap:8px;margin-top:15px;
            padding:8px 14px;border-radius:999px;background:rgba(52,211,153,.08);
            border:1px solid rgba(52,211,153,.25);color:#34D399;font-size:.78rem;font-weight:900;letter-spacing:.6px;">
            <span class="status-dot"></span> ML INFERENCE SYSTEM ONLINE
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# NAVIGATION
# ============================================================
# NAVIGATION
# ============================================================
tab_live, tab_metrics = st.tabs(
    [
        "⚡ Real-Time Predictor",
        "📈 ML Evaluation Benchmarks",
    ]
)

# ============================================================
# TAB 1 — REAL TIME
# ============================================================
with tab_live:

    render(
        f"""
        <h3 style="margin-top:22px;font-weight:800;">
            Feature Telemetry Inputs
        </h3>
        <p class="small-note">
            Enter measurable network-flow values. These 15 inputs are
            processed by the dedicated live Random Forest pathway.
        </p>
        """,
        unsafe_allow_html=True,
    )

    if live_model is None:
        st.warning(
            "⚠️ Live model is not currently available. "
            "Keep your processed clean_dataset.csv in the project folder."
        )

    render('<div class="input-panel">', unsafe_allow_html=True)

    # Layer 3/4
    render(
        f"<h4 style='color:{text_main};'>🌐 Connection & Protocol</h4>",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        src_ip = st.text_input(
            "Source IP Address",
            "192.168.1.105"
        )

    with c2:
        dst_ip = st.text_input(
            "Destination IP Address",
            "192.168.1.1"
        )

    with c3:
        protocol = st.selectbox(
            "Protocol Type",
            ["TCP Stream", "UDP Datagram", "ICMP Ping"]
        )

    c1, c2, c3 = st.columns(3)

    with c1:
        destination_port = st.number_input(
            "Destination Port",
            min_value=0,
            max_value=65535,
            value=80
        )

    with c2:
        flow_duration = st.number_input(
            "Flow Duration (µs)",
            min_value=0.0,
            value=2500000.0,
            step=10000.0
        )

    with c3:
        total_fwd_packets = st.number_input(
            "Total Forward Packets",
            min_value=0.0,
            value=120.0,
            step=1.0
        )

    render(
        f"<h4 style='color:{text_main};margin-top:20px;'>📊 Traffic Volume</h4>",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        total_bwd_packets = st.number_input(
            "Total Backward Packets",
            min_value=0.0,
            value=90.0,
            step=1.0
        )

    with c2:
        total_fwd_bytes = st.number_input(
            "Total Forward Bytes",
            min_value=0.0,
            value=180000.0,
            step=1000.0
        )

    with c3:
        total_bwd_bytes = st.number_input(
            "Total Backward Bytes",
            min_value=0.0,
            value=120000.0,
            step=1000.0
        )

    c1, c2, c3 = st.columns(3)

    with c1:
        flow_bytes_sec = st.number_input(
            "Flow Bytes / Second",
            min_value=0.0,
            value=120000.0,
            step=1000.0
        )

    with c2:
        flow_packets_sec = st.number_input(
            "Flow Packets / Second",
            min_value=0.0,
            value=84.0,
            step=1.0
        )

    with c3:
        fwd_mean = st.number_input(
            "Fwd Packet Length Mean",
            min_value=0.0,
            value=1500.0,
            step=10.0
        )

    render(
        f"<h4 style='color:{text_main};margin-top:20px;'>📦 Packet Behaviour</h4>",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        bwd_mean = st.number_input(
            "Bwd Packet Length Mean",
            min_value=0.0,
            value=1333.0,
            step=10.0
        )

    with c2:
        packet_mean = st.number_input(
            "Packet Length Mean",
            min_value=0.0,
            value=1420.0,
            step=10.0
        )

    with c3:
        packet_std = st.number_input(
            "Packet Length Std",
            min_value=0.0,
            value=300.0,
            step=10.0
        )

    c1, c2 = st.columns(2)

    with c1:
        syn_count = st.number_input(
            "SYN Flag Count",
            min_value=0.0,
            value=2.0,
            step=1.0
        )

    with c2:
        ack_count = st.number_input(
            "ACK Flag Count",
            min_value=0.0,
            value=100.0,
            step=1.0
        )

    render("</div>", unsafe_allow_html=True)

    render("<br>", unsafe_allow_html=True)

    predict_live = st.button(
        "🛡️ RUN LIVE RANDOM FOREST INFERENCE →",
        use_container_width=True,
        key="live_predict"
    )

    if predict_live:

        live_values = {
            "Protocol": protocol_to_number(protocol),
            "Destination Port": destination_port,
            "Flow Duration": flow_duration,
            "Total Fwd Packets": total_fwd_packets,
            "Total Backward Packets": total_bwd_packets,
            "Total Length of Fwd Packets": total_fwd_bytes,
            "Total Length of Bwd Packets": total_bwd_bytes,
            "Flow Bytes/s": flow_bytes_sec,
            "Flow Packets/s": flow_packets_sec,
            "Fwd Packet Length Mean": fwd_mean,
            "Bwd Packet Length Mean": bwd_mean,
            "Packet Length Mean": packet_mean,
            "Packet Length Std": packet_std,
            "SYN Flag Count": syn_count,
            "ACK Flag Count": ack_count,
        }

        X_live = pd.DataFrame(
            [live_values],
            columns=LIVE_FEATURES
        ).astype(np.float32)

        try:
            labels, probs = run_live_prediction(X_live)
            label = labels[0]

            confidence = (
                float(np.max(probs[0]))
                if probs is not None
                else None
            )

            is_benign = str(label).strip().upper() == "BENIGN"
            result_color = "#22C55E" if is_benign else "#EF4444"

            title = (
                "🟢 BENIGN TRAFFIC"
                if is_benign
                else "🔴 ATTACK DETECTED"
            )

            description = (
                "The live Random Forest classified the supplied "
                "network-flow telemetry as benign traffic."
                if is_benign
                else f"The live Random Forest classified the supplied "
                     f"network-flow telemetry as {label}."
            )

            render(
                f"""
                <div class="result-card"
                     style="
                        background:{result_color}12;
                        border:2px solid {result_color};
                     ">

                    <div style="
                        color:{result_color};
                        font-weight:800;
                        letter-spacing:1.4px;
                        font-size:.78rem;
                    ">
                        LIVE INFERENCE RESULT
                    </div>

                    <h2 style="margin:8px 0;">
                        {title}
                    </h2>

                    <p style="
                        color:#AAB8CB !important;
                        margin:0;
                        line-height:1.6;
                    ">
                        {description}
                    </p>

                    <p style="
                        color:#CBD5E1 !important;
                        margin-top:10px;
                    ">
                        <b>Source:</b> {src_ip}
                        &nbsp; → &nbsp;
                        <b>Destination:</b> {dst_ip}
                        &nbsp; | &nbsp;
                        <b>Protocol:</b> {protocol}
                    </p>

                </div>
                """,
                unsafe_allow_html=True,
            )

            m1, m2, m3, m4 = st.columns(4)

            with m1:
                st.metric("Predicted Class", label)

            with m2:
                st.metric(
                    "RF Confidence",
                    f"{confidence*100:.2f}%"
                    if confidence is not None
                    else "N/A"
                )

            with m3:
                st.metric(
                    "Flow Rate",
                    f"{flow_packets_sec:,.1f}/s"
                )

            with m4:
                st.metric(
                    "Traffic Volume",
                    f"{total_fwd_bytes+total_bwd_bytes:,.0f} B"
                )

            if probs is not None:

                render(
                    f"<h4 style='margin-top:25px;'>🎯 Class Probability</h4>",
                    unsafe_allow_html=True
                )

                prob_df = pd.DataFrame({
                    "Class": live_encoder.classes_,
                    "Probability": probs[0] * 100
                }).sort_values(
                    "Probability",
                    ascending=False
                )

                fig_prob = px.bar(
                    prob_df,
                    x="Class",
                    y="Probability",
                    color="Class",
                    color_discrete_map={
                        str(c): color_for_label(c, i)
                        for i, c in enumerate(live_encoder.classes_)
                    },
                    text="Probability"
                )

                fig_prob.update_traces(
                    texttemplate="%{text:.1f}%",
                    textposition="outside",
                    cliponaxis=False
                )

                fig_prob.update_layout(
                    height=390,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font={"color": chart_text_color},
                    xaxis=dict(
                        color=chart_text_color,
                        tickangle=-35,
                        gridcolor=chart_grid_color
                    ),
                    yaxis=dict(
                        title="Probability (%)",
                        color=chart_text_color,
                        gridcolor=chart_grid_color,
                        range=[0, max(105, float(prob_df["Probability"].max())+10)]
                    ),
                    showlegend=False,
                    margin=dict(l=30,r=20,t=30,b=100)
                )

                st.plotly_chart(
                    fig_prob,
                    use_container_width=True
                )

        except Exception as e:
            st.error("❌ Live Random Forest prediction failed.")
            st.code(str(e))

# ============================================================
# TAB 2 — EVALUATION PAGE
# KEEPING YOUR EXISTING VALUES / STRUCTURE UNCHANGED
# ============================================================
with tab_metrics:

    render(
        f"""
        <h3 style="
            color:{text_main};
            font-weight:800;
        ">
            📈 ML Classifier Model Evaluation Benchmarks
        </h3>

        <p>
            Empirical performance benchmarks evaluated across trained algorithms.
        </p>
        """,
        unsafe_allow_html=True
    )

    metrics_data = {
        "Model": [
            "Logistic Regression",
            "Decision Tree",
            "Random Forest",
            "KNN"
        ],
        "Accuracy": [
            96.00, 99.19, 99.27, 98.40
        ],
        "Precision": [
            95.69, 99.20, 99.26, 98.43
        ],
        "Recall": [
            96.00, 99.19, 99.27, 98.40
        ],
        "F1 Score": [
            95.64, 99.19, 99.26, 98.40
        ],
    }

    df_metrics = pd.DataFrame(metrics_data)

    e1, e2, e3, e4 = st.columns(4)

    e1.metric(
        "Top Algorithm",
        "Random Forest 🤖"
    )

    e2.metric(
        "Best Accuracy",
        "99.27%"
    )

    e3.metric(
        "Best Precision",
        "99.26%"
    )

    e4.metric(
        "Best F1 Score",
        "99.26%"
    )

    render("<br>", unsafe_allow_html=True)

    col_chart, col_tbl = st.columns([1.3, 1.1])

    with col_chart:

        render(
            f"""
            <h5 style="
                color:{text_main};
                font-weight:700;
            ">
                📊 Classifier Metric Comparison
            </h5>
            """,
            unsafe_allow_html=True
        )

        df_melted = df_metrics.melt(
            id_vars="Model",
            var_name="Metric",
            value_name="Score"
        )

        fig_models = px.bar(
            df_melted,
            x="Model",
            y="Score",
            color="Metric",
            barmode="group",
            color_discrete_sequence=[
                "#38BDF8",
                "#818CF8",
                "#A855F7",
                "#34D399"
            ],
        )

        fig_models.update_traces(
            width=.18
        )

        fig_models.update_layout(
            height=340,
            margin=dict(
                l=60,r=20,t=30,b=80
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={
                "color": chart_text_color,
                "family": "Inter"
            },
            yaxis=dict(
                title_text="Score (%)",
                range=[90,100],
                gridcolor=chart_grid_color,
                color=chart_text_color,
                showticklabels=True
            ),
            xaxis=dict(
                title_text="Model Type",
                gridcolor=chart_grid_color,
                color=chart_text_color,
                showticklabels=True
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(
                    color=chart_text_color
                )
            )
        )

        st.plotly_chart(
            fig_models,
            use_container_width=True
        )

    with col_tbl:

        render(
            f"""
            <h5 style="
                color:{text_main};
                font-weight:700;
            ">
                📋 Evaluation Summary Table
            </h5>
            """,
            unsafe_allow_html=True
        )

        formatted_df = df_metrics.copy()

        for col in [
            "Accuracy",
            "Precision",
            "Recall",
            "F1 Score"
        ]:
            formatted_df[col] = formatted_df[col].apply(
                lambda x: f"{x:.2f}%"
            )

        st.dataframe(
            formatted_df,
            use_container_width=True,
            hide_index=True
        )

# ============================================================
# FOOTER
# ============================================================
render(
    """
<div style="
    text-align:center;
    margin:42px 0 8px;
    color:#64748B;
    font-size:.76rem;
">
    🛡️ Network Intrusion & Anomaly Detection System
    &nbsp; • &nbsp;
    CIC-IDS2017
    &nbsp; • &nbsp;
    Multi-Class Random Forest Inference
</div>
""",
    unsafe_allow_html=True
)
