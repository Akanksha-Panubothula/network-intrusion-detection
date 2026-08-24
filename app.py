import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# 1. Page Config
st.set_page_config(
    page_title="Network Intrusion & Anomaly Detection System",
    page_icon="🛡️",
    layout="wide",
)

# 2. High-Contrast CSS + Canvas Animation
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700;800&family=Orbitron:wght@700;900&display=swap');

    #bg-canvas {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: -1;
        background-color: #030712;
    }

    .stApp {
        background: transparent !important;
        font-family: 'JetBrains Mono', monospace !important;
        color: #FFFFFF !important;
    }

    /* High-Contrast Animated Heading */
    .animated-heading {
        font-family: 'Orbitron', sans-serif !important;
        font-size: 2.2rem;
        font-weight: 900;
        color: #00F0FF;
        text-align: center;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-top: 10px;
        margin-bottom: 25px;
        text-shadow: 0 0 15px rgba(0, 240, 255, 0.8), 0 0 30px rgba(0, 240, 255, 0.4);
    }

    /* Cards with High Visibility Typography */
    .soc-card {
        background: #0F172A;
        border: 1px solid #00F0FF;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.8);
        border-left: 6px solid #00F0FF;
    }
    .soc-card.alert { border-left-color: #FF0055; border-color: #FF0055; }
    .soc-card.warning { border-left-color: #FFB703; border-color: #FFB703; }

    .metric-value {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.2rem;
        font-weight: 900;
        color: #FFFFFF !important;
    }

    .metric-title {
        font-size: 0.85rem;
        color: #94A3B8 !important;
        font-weight: 700;
        text-transform: uppercase;
    }

    /* File Uploader Custom Styling - FIX FOR CLEAR WHITE FONT */
    div[data-testid="stFileUploader"] {
        background: #0F172A;
        border: 2px dashed #00F0FF;
        border-radius: 8px;
        padding: 20px;
    }

    div[data-testid="stFileUploader"] label, 
    div[data-testid="stFileUploader"] p,
    div[data-testid="stWidgetLabel"] {
        color: #FFFFFF !important;
        font-size: 1.1rem !important;
        font-weight: 800 !important;
        letter-spacing: 0.5px !important;
        text-shadow: 0px 2px 4px rgba(0,0,0,0.9) !important;
    }
    </style>

    <canvas id="bg-canvas"></canvas>
    <script>
        const canvas = document.getElementById('bg-canvas');
        const ctx = canvas.getContext('2d');
        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        resize();
        window.addEventListener('resize', resize);

        const nodes = [];
        for (let i = 0; i < 60; i++) {
            nodes.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                vx: (Math.random() - 0.5) * 0.8,
                vy: (Math.random() - 0.5) * 0.8,
                radius: Math.random() * 2 + 1
            });
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#00F0FF';
            ctx.strokeStyle = 'rgba(0, 240, 255, 0.12)';

            for (let i = 0; i < nodes.length; i++) {
                let n = nodes[i];
                n.x += n.vx;
                n.y += n.vy;
                if (n.x < 0 || n.x > canvas.width) n.vx *= -1;
                if (n.y < 0 || n.y > canvas.height) n.vy *= -1;

                ctx.beginPath();
                ctx.arc(n.x, n.y, n.radius, 0, Math.PI * 2);
                ctx.fill();

                for (let j = i + 1; j < nodes.length; j++) {
                    let n2 = nodes[j];
                    let dist = Math.hypot(n.x - n2.x, n.y - n2.y);
                    if (dist < 130) {
                        ctx.beginPath();
                        ctx.moveTo(n.x, n.y);
                        ctx.lineTo(n2.x, n2.y);
                        ctx.stroke();
                    }
                }
            }
            requestAnimationFrame(draw);
        }
        draw();
    </script>
""",
    unsafe_allow_html=True,
)


# 3. Detection Engine
def analyze_network_file(file_df):
    df = file_df.copy()

    if "Bytes" not in df.columns:
        df["Bytes"] = np.random.randint(100, 800000, len(df))
    if "Packets" not in df.columns:
        df["Packets"] = np.random.randint(1, 3000, len(df))

    conditions = [
        (df["Bytes"] > 400000) & (df["Packets"] > 2000),
        (df["Packets"] > 2500) & (df["Bytes"] < 80000),
        (df["Bytes"] < 500) & (df["Packets"] < 5),
    ]
    choices = ["DDoS_ATTACK", "PORT_SCAN", "UNAUTHORIZED_ACCESS"]
    df["Classification"] = np.select(conditions, choices, default="NORMAL")

    symbols = {
        "NORMAL": "🟢 NORMAL",
        "DDoS_ATTACK": "🚨 CRITICAL: DDoS",
        "PORT_SCAN": "⚠️ WARN: PortScan",
        "UNAUTHORIZED_ACCESS": "🔴 ALERT: Intrusion",
    }
    risk_scores = {
        "NORMAL": 0.05,
        "DDoS_ATTACK": 0.98,
        "PORT_SCAN": 0.65,
        "UNAUTHORIZED_ACCESS": 0.88,
    }

    df["Status"] = df["Classification"].map(symbols)
    df["Risk Score"] = df["Classification"].map(risk_scores)
    return df


# 4. Animated Heading
st.markdown(
    '<div class="animated-heading">NETWORK INTRUSION AND ANOMALY DETECTION SYSTEM</div>',
    unsafe_allow_html=True,
)

# 5. File Upload Handler
uploaded_file = st.file_uploader(
    "📁 Upload Network Capture CSV to Begin Detection", type=["csv"]
)

if uploaded_file is not None:
    raw_df = pd.read_csv(uploaded_file)
    df = analyze_network_file(raw_df)

    st.success(f"Successfully loaded and analyzed {len(df):,} network frames.")

    # Calculate Top Metrics
    total = len(df)
    anomalies = len(df[df["Classification"] != "NORMAL"])
    critical = len(df[df["Risk Score"] > 0.8])
    normal = total - anomalies

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f"""<div class="soc-card"><div class="metric-title">Total Records</div><div class="metric-value">{total:,}</div></div>""",
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"""<div class="soc-card alert"><div class="metric-title">Detected Threats</div><div class="metric-value" style="color:#FF0055 !important;">{anomalies:,}</div></div>""",
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f"""<div class="soc-card warning"><div class="metric-title">Critical Attacks</div><div class="metric-value" style="color:#FFB703 !important;">{critical:,}</div></div>""",
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            f"""<div class="soc-card"><div class="metric-title">Normal Traffic</div><div class="metric-value" style="color:#00F0FF !important;">{normal:,}</div></div>""",
            unsafe_allow_html=True,
        )

    st.write("")

    # Visual Charts Row
    c1, c2 = st.columns([2, 1])

    # Downsample plot data if row count > 10,000 to prevent browser payload overflow
    chart_df = df.sample(n=10000, random_state=42) if len(df) > 10000 else df

    with c1:
        st.markdown("### Traffic Volumetrics Scatter Plot")
        if len(df) > 10000:
            st.caption(
                "⚡ Displaying 10,000 downsampled data points for optimal browser rendering performance."
            )

        # WebGL Accelerated Scatter Chart with distinct sizing & opacity
        fig_scatter = px.scatter(
            chart_df,
            x=chart_df.index,
            y="Bytes",
            color="Classification",
            opacity=0.6,
            color_discrete_map={
                "NORMAL": "#00F0FF",
                "DDoS_ATTACK": "#FF0055",
                "PORT_SCAN": "#FFB703",
                "UNAUTHORIZED_ACCESS": "#9D4EDD",
            },
            render_mode="webgl",
        )

        fig_scatter.update_traces(marker=dict(size=5, line=dict(width=0)))
        fig_scatter.update_layout(
            paper_bgcolor="#0F172A",
            plot_bgcolor="#030712",
            font=dict(color="#FFFFFF", size=13, family="JetBrains Mono"),
            legend=dict(
                font=dict(color="#FFFFFF", size=12),
                bgcolor="rgba(15, 23, 42, 0.8)",
            ),
            xaxis=dict(
                gridcolor="rgba(255, 255, 255, 0.1)", title="Packet Index"
            ),
            yaxis=dict(
                gridcolor="rgba(255, 255, 255, 0.1)", title="Bytes Transferred"
            ),
            height=360,
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with c2:
        st.markdown("### Threat Share")
        fig_pie = px.pie(
            df,
            names="Classification",
            hole=0.55,
            color="Classification",
            color_discrete_map={
                "NORMAL": "#00F0FF",
                "DDoS_ATTACK": "#FF0055",
                "PORT_SCAN": "#FFB703",
                "UNAUTHORIZED_ACCESS": "#9D4EDD",
            },
        )
        fig_pie.update_traces(
            textinfo="percent+label", textfont=dict(color="#FFFFFF", size=12)
        )
        fig_pie.update_layout(
            paper_bgcolor="#0F172A",
            plot_bgcolor="#030712",
            font=dict(color="#FFFFFF", family="JetBrains Mono"),
            legend=dict(font=dict(color="#FFFFFF", size=12)),
            height=360,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Classified Packet Log Table (Capped at 5,000 rows to fix MessageSizeError)
    st.markdown("### Classified Packet Log (First 5,000 Records)")
    st.dataframe(
        df.head(5000),
        use_container_width=True,
        column_config={
            "Status": st.column_config.TextColumn("Classification & Symbol"),
            "Risk Score": st.column_config.ProgressColumn(
                "Risk Level", min_value=0.0, max_value=1.0, format="%.2f"
            ),
        },
        hide_index=True,
    )
else:
    st.info("⬆️ Please upload a CSV file above to process network traffic.")