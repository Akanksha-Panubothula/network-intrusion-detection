import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Network Intrusion & Anomaly Detection System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

.stApp {
    background: linear-gradient(180deg,#F0F4FF 0%,#F8FAFC 100%);
    font-family:'Plus Jakarta Sans',sans-serif;
    color:#0F172A;
}

.hero {
    background:linear-gradient(135deg,#EEF2FF,#E0E7FF);
    border:1px solid #C7D2FE;
    border-radius:18px;
    padding:25px;
    margin-bottom:20px;
    box-shadow:0 5px 20px rgba(79,70,229,.08);
}

.hero-title {
    font-size:32px;
    font-weight:800;
    color:#1E1B4B;
}

.hero-sub {
    color:#475569;
    font-size:15px;
}

.status {
    background:#DCFCE7;
    color:#15803D;
    padding:10px 18px;
    border-radius:20px;
    font-weight:700;
    text-align:center;
}

.metric-card {
    background:white;
    border-radius:14px;
    padding:18px;
    border-left:5px solid #4F46E5;
    box-shadow:0 4px 15px rgba(0,0,0,.05);
}

.metric-card.red {
    border-left-color:#EF4444;
}

.metric-card.green {
    border-left-color:#10B981;
}

.metric-card.orange {
    border-left-color:#F59E0B;
}

.metric-label {
    font-size:12px;
    font-weight:700;
    color:#64748B;
    text-transform:uppercase;
}

.metric-value {
    font-size:27px;
    font-weight:800;
    color:#0F172A;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================

c1, c2 = st.columns([4,1])

with c1:
    st.markdown("""
    <div class="hero">
        <div class="hero-title">
            🛡️ Network Intrusion & Anomaly Detection System
        </div>
        <div class="hero-sub">
            AI-powered network traffic classification and
            cybersecurity threat intelligence dashboard
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.write("")
    st.markdown(
        '<div class="status">🟢 SYSTEM ACTIVE</div>',
        unsafe_allow_html=True
    )

# =========================================================
# PROJECT OVERVIEW
# =========================================================

st.subheader("📊 Security Intelligence Overview")

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Dataset Records</div>
        <div class="metric-value">2,813,701</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown("""
    <div class="metric-card red">
        <div class="metric-label">Attack Classes</div>
        <div class="metric-value">14</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown("""
    <div class="metric-card green">
        <div class="metric-label">Features</div>
        <div class="metric-value">79</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown("""
    <div class="metric-card orange">
        <div class="metric-label">Best Accuracy</div>
        <div class="metric-value">99.27%</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# =========================================================
# DATASET DISTRIBUTION
# =========================================================

st.subheader("🚨 Network Traffic Classification")

attack_data = pd.DataFrame({
    "Attack Type": [
        "BENIGN",
        "DoS Hulk",
        "PortScan",
        "DDoS",
        "DoS GoldenEye",
        "FTP-Patator",
        "SSH-Patator",
        "DoS slowloris",
        "DoS Slowhttptest",
        "Bot",
        "Web Attack - Brute Force",
        "Web Attack - XSS",
        "Infiltration",
        "Web Attack - Sql Injection",
        "Heartbleed"
    ],
    "Records": [
        2263667,
        223488,
        158930,
        128027,
        10293,
        7938,
        5897,
        5769,
        5499,
        1966,
        1507,
        652,
        36,
        21,
        11
    ]
})

col1, col2 = st.columns([1.6, 1])

with col1:

    fig = px.bar(
        attack_data,
        x="Attack Type",
        y="Records",
        title="CIC-IDS2017 Class Distribution",
        text="Records"
    )

    fig.update_layout(
        template="plotly_white",
        height=450,
        xaxis_tickangle=-45
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    fig2 = px.pie(
        attack_data,
        names="Attack Type",
        values="Records",
        hole=0.55,
        title="Traffic Distribution",
        color="Attack Type",
        color_discrete_map={
            "BENIGN": "#22C55E",
            "DoS Hulk": "#EF4444",
            "DDoS": "#DC2626",
            "PortScan": "#F97316",
            "DoS GoldenEye": "#F59E0B",
            "DoS slowloris": "#E11D48",
            "DoS Slowhttptest": "#FB7185",
            "FTP-Patator": "#8B5CF6",
            "SSH-Patator": "#6366F1",
            "Bot": "#14B8A6",
            "Web Attack - Brute Force": "#EC4899",
            "Web Attack - XSS": "#D946EF",
            "Web Attack - Sql Injection": "#A855F7",
            "Infiltration": "#06B6D4",
            "Heartbleed": "#0EA5E9"
        }
    )

    fig2.update_traces(
        textposition="inside",
        textinfo="percent",
        textfont_size=10,
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Records: %{value:,}<br>"
            "Percentage: %{percent}"
            "<extra></extra>"
        )
    )

    fig2.update_layout(
        height=380,
        margin=dict(l=5, r=5, t=50, b=5),
        paper_bgcolor="white",
        plot_bgcolor="white",

        # IMPORTANT: legend shows attack + corresponding color
        showlegend=True,
        legend=dict(
            orientation="v",
            x=1.02,
            y=0.5,
            xanchor="left",
            yanchor="middle",
            font=dict(size=9)
        ),

        title=dict(
            font=dict(size=16)
        )
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )
# ================= MODEL COMPARISON =================

st.markdown("### 📊 Model Accuracy Comparison")

model_df = pd.DataFrame({
    "Model": [
        "Logistic Regression",
        "Decision Tree",
        "Random Forest",
        "KNN"
    ],
    "Accuracy": [
        96.00,
        99.19,
        99.27,
        98.40
    ]
})

model_colors = {
    "Logistic Regression": "#6366F1",
    "Decision Tree": "#F59E0B",
    "Random Forest": "#10B981",
    "KNN": "#EF4444"
}

fig_model = px.bar(
    model_df,
    x="Model",
    y="Accuracy",
    color="Model",
    color_discrete_map=model_colors,
    text="Accuracy"
)

fig_model.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside",
    width=0.35,                 # ⭐ THIN BARS
    marker_line_width=0
)

fig_model.update_layout(
    height=350,
    showlegend=False,

    # Keep bars thin
    bargap=0.65,

    # Clean background
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",

    # Font
    font=dict(
        family="Plus Jakarta Sans",
        size=12,
        color="#334155"
    ),

    xaxis=dict(
        title=None,
        showgrid=False,
        tickfont=dict(size=12)
    ),

    yaxis=dict(
        title="Accuracy (%)",
        range=[90, 101],
        showgrid=True,
        gridcolor="#E2E8F0",
        zeroline=False
    ),

    margin=dict(
        l=40,
        r=20,
        t=25,
        b=45
    )
)

st.plotly_chart(
    fig_model,
    use_container_width=True
)
# =========================================================
# BEST MODEL
# =========================================================

st.success(
    "🏆 Random Forest achieved the highest performance "
    "with 99.27% accuracy and was selected as the final model."
)



# =========================================================
# DATASET INFORMATION
# =========================================================

st.subheader("📁 Dataset Information")

info1, info2, info3 = st.columns(3)

with info1:
    st.info("""
    **Dataset**

    CIC-IDS2017

    2,813,701 records
    """)

with info2:
    st.info("""
    **Features**

    79 numerical features

    Missing values: 0
    """)

with info3:
    st.info("""
    **Classes**

    15 total classes

    1 BENIGN + 14 attacks
    """)



# ================= ATTACK TYPES =================

st.markdown("### 🛡️ Detected Traffic Classes")

attack_colors = {
    "BENIGN": "#22C55E",
    "DoS Hulk": "#EF4444",
    "DDoS": "#DC2626",
    "PortScan": "#F97316",
    "DoS GoldenEye": "#F59E0B",
    "DoS slowloris": "#E11D48",
    "DoS Slowhttptest": "#FB7185",
    "FTP-Patator": "#8B5CF6",
    "SSH-Patator": "#6366F1",
    "Bot": "#14B8A6",
    "Web Attack - Brute Force": "#EC4899",
    "Web Attack - XSS": "#D946EF",
    "Web Attack - SQL Injection": "#A855F7",
    "Infiltration": "#06B6D4",
    "Heartbleed": "#0EA5E9"
}

# Show classes in 3 columns
classes = list(attack_colors.keys())

col1, col2, col3 = st.columns(3)

for i, attack in enumerate(classes):

    if i % 3 == 0:
        with col1:
            st.markdown(
                f"""
                <div style="
                    display:flex;
                    align-items:center;
                    gap:10px;
                    margin:10px 0;
                    font-weight:600;
                    color:#0F172A;
                ">
                    <span style="
                        width:19px;
                        height:19px;
                        border-radius:50%;
                        background:{attack_colors[attack]};
                        display:inline-block;
                        box-shadow:0 2px 6px {attack_colors[attack]}55;
                    "></span>
                    {attack}
                </div>
                """,
                unsafe_allow_html=True
            )

    elif i % 3 == 1:
        with col2:
            st.markdown(
                f"""
                <div style="
                    display:flex;
                    align-items:center;
                    gap:10px;
                    margin:10px 0;
                    font-weight:600;
                    color:#0F172A;
                ">
                    <span style="
                        width:19px;
                        height:19px;
                        border-radius:50%;
                        background:{attack_colors[attack]};
                        display:inline-block;
                        box-shadow:0 2px 6px {attack_colors[attack]}55;
                    "></span>
                    {attack}
                </div>
                """,
                unsafe_allow_html=True
            )

    else:
        with col3:
            st.markdown(
                f"""
                <div style="
                    display:flex;
                    align-items:center;
                    gap:10px;
                    margin:10px 0;
                    font-weight:600;
                    color:#0F172A;
                ">
                    <span style="
                        width:19px;
                        height:19px;
                        border-radius:50%;
                        background:{attack_colors[attack]};
                        display:inline-block;
                        box-shadow:0 2px 6px {attack_colors[attack]}55;
                    "></span>
                    {attack}
                </div>
                """,
                unsafe_allow_html=True
            )
# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "🛡️ Network Intrusion & Anomaly Detection System "
    "| CIC-IDS2017 | Machine Learning | Random Forest"
)