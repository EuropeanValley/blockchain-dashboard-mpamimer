import math
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime

from api.blockchain_client import (
    bits_to_difficulty,
    bits_to_hex,
    bits_to_target,
    compute_block_hash_from_header,
    count_leading_zero_bits,
    count_leading_zero_hex,
    estimate_hashrate,
    get_block,
    get_block_header_fields,
    get_block_intervals,
    get_difficulty_history_df,
    get_latest_block,
    get_mempool_info,
    get_recommended_fees,
    get_recent_mempool_txs,
    is_pow_valid,
    serialize_block_header,
)

st.set_page_config(
    page_title="CryptoChain Analyzer Dashboard",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="expanded",
)

st_autorefresh = None

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

refresh_seconds = st.sidebar.slider("Auto-refresh interval (seconds)", 30, 120, 60, 10)

if st_autorefresh is not None:
    st_autorefresh(interval=refresh_seconds * 1000, key="bitcoin_autorefresh")
else:
    st.sidebar.warning(
        "Auto-refresh package not installed. Install streamlit-autorefresh to enable automatic updates."
    )
        
def inject_custom_css():
    st.markdown(
        """
        <style>
        /* ------------------------------
           Global app layout
        ------------------------------ */
        .stApp {
            background: linear-gradient(180deg, #f8fbff 0%, #f3f6fb 100%);
        }

        header[data-testid="stHeader"] {
            height: 0rem !important;
            background: transparent !important;
        }

        div[data-testid="stToolbar"] {
            display: none !important;
        }

        .block-container {
            padding-top: 0.4rem !important;
            padding-bottom: 2rem;
            max-width: 1320px;
        }

        /* ------------------------------
           Sidebar
        ------------------------------ */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #ffffff 0%, #f7faff 55%, #f8efff 100%);
            border-right: 1px solid #e5eaf5;
            box-shadow: 4px 0 18px rgba(18, 38, 63, 0.05);
        }

        section[data-testid="stSidebar"] > div {
            padding-top: 1rem;
        }

        section[data-testid="stSidebar"] h1 {
            color: #0f1f3d;
            font-weight: 850;
            font-size: 1.6rem;
            letter-spacing: -0.02em;
        }

        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: #163153;
            font-weight: 800;
        }

        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] li,
        section[data-testid="stSidebar"] label {
            color: #4d607d;
        }

        section[data-testid="stSidebar"] hr {
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, #d9e3f2, transparent);
            margin: 1.1rem 0;
        }

        section[data-testid="stSidebar"] .stSlider {
            background: rgba(255, 255, 255, 0.78);
            border: 1px solid #e8eef7;
            border-radius: 18px;
            padding: 0.85rem 0.95rem 0.55rem 0.95rem;
            margin-bottom: 0.9rem;
            box-shadow: 0 5px 16px rgba(18, 38, 63, 0.045);
        }

        section[data-testid="stSidebar"] div[data-testid="stAlert"] {
            border-radius: 18px;
            border: 1px solid #d8f3df;
            box-shadow: 0 5px 16px rgba(18, 38, 63, 0.045);
        }

        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] ul {
            background: rgba(255, 255, 255, 0.60);
            border: 1px solid #e8eef7;
            border-radius: 16px;
            padding: 0.85rem 1rem 0.85rem 1.35rem;
            box-shadow: 0 4px 14px rgba(18, 38, 63, 0.035);
        }

        /* ------------------------------
        Sidebar slider color: blue
        ------------------------------ */

        section[data-testid="stSidebar"] div[data-baseweb="slider"] div {
            color: #3b82f6 !important;
        }

        section[data-testid="stSidebar"] div[data-baseweb="slider"] div[style*="background: linear-gradient"],
        section[data-testid="stSidebar"] div[data-baseweb="slider"] div[style*="background-color"] {
            background: #3b82f6 !important;
            background-color: #3b82f6 !important;
        }

        section[data-testid="stSidebar"] div[data-baseweb="slider"] > div > div {
            background: #dbeafe !important;
        }

        section[data-testid="stSidebar"] div[data-baseweb="slider"] div[role="slider"] {
            background-color: #3b82f6 !important;
            border-color: #3b82f6 !important;
            box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.18) !important;
        }

        section[data-testid="stSidebar"] div[data-baseweb="slider"] div[role="slider"]:hover,
        section[data-testid="stSidebar"] div[data-baseweb="slider"] div[role="slider"]:focus,
        section[data-testid="stSidebar"] div[data-baseweb="slider"] div[role="slider"]:active {
            background-color: #2563eb !important;
            border-color: #2563eb !important;
            box-shadow: 0 0 0 5px rgba(59, 130, 246, 0.20) !important;
        }

        section[data-testid="stSidebar"] div[data-baseweb="slider"] span {
            color: #334155 !important;
            background: transparent !important;
        }

        section[data-testid="stSidebar"] .stSlider p {
            color: #334155 !important;
        }

        
        /* ------------------------------
           Optional custom sidebar cards
        ------------------------------ */
        .sidebar-title-card {
            background: linear-gradient(135deg, #eef5ff 0%, #f7edff 100%);
            border: 1px solid #e0e8ff;
            border-radius: 20px;
            padding: 1rem 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 6px 18px rgba(18, 38, 63, 0.055);
        }

        .sidebar-title-main {
            font-size: 1.25rem;
            font-weight: 850;
            color: #0f1f3d;
            margin-bottom: 0.25rem;
        }

        .sidebar-title-sub {
            font-size: 0.82rem;
            color: #5a6f91;
            line-height: 1.35;
        }

        .sidebar-pill {
            display: inline-block;
            margin-top: 0.55rem;
            background: #ffffff;
            color: #2457d6;
            border: 1px solid #dbeafe;
            padding: 0.28rem 0.58rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 750;
        }

        .sidebar-section-card {
            background: rgba(255, 255, 255, 0.72);
            border: 1px solid #e8eef7;
            border-radius: 18px;
            padding: 0.9rem 0.95rem;
            margin: 0.85rem 0;
            box-shadow: 0 4px 14px rgba(18, 38, 63, 0.035);
        }

        .sidebar-section-title {
            font-size: 0.93rem;
            font-weight: 850;
            color: #163153;
            margin-bottom: 0.45rem;
        }

        .sidebar-small {
            font-size: 0.82rem;
            color: #637894;
            line-height: 1.4;
        }

        /* ------------------------------
           Hero
        ------------------------------ */
        .hero {
            background: linear-gradient(135deg, #ffffff 0%, #eef5ff 55%, #f8efff 100%);
            border: 1px solid #e6eef8;
            border-radius: 22px;
            padding: 1.6rem 1.8rem;
            box-shadow: 0 8px 26px rgba(18, 38, 63, 0.06);
            margin-bottom: 1.2rem;
        }

        .hero-title {
            font-size: 2.4rem;
            font-weight: 800;
            color: #0f1f3d;
            margin-bottom: 0.25rem;
        }

        .hero-subtitle {
            font-size: 1.02rem;
            color: #4b5d79;
            line-height: 1.55;
        }

        .hero-tag {
            display: inline-block;
            margin-top: 0.7rem;
            background: linear-gradient(135deg, #eef5ff 0%, #f4ecff 100%);
            color: #2457d6;
            border: 1px solid #dbeafe;
            padding: 0.35rem 0.7rem;
            border-radius: 999px;
            font-size: 0.88rem;
            font-weight: 700;
        }

        /* ------------------------------
           Cards and sections
        ------------------------------ */
        .section-card {
            background: #ffffff;
            border: 1px solid #e8eef7;
            border-radius: 22px;
            padding: 1.15rem 1.2rem 1rem 1.2rem;
            box-shadow: 0 6px 22px rgba(18, 38, 63, 0.05);
            margin-top: 1rem;
            margin-bottom: 1rem;
        }

        .section-title {
            font-size: 1.4rem;
            font-weight: 800;
            color: #163153;
            margin-bottom: 0.3rem;
        }

        .section-subtitle {
            color: #58708f;
            font-size: 0.97rem;
            line-height: 1.5;
        }

        .mini-card {
            background: #ffffff;
            border: 1px solid #e8eef7;
            border-radius: 18px;
            padding: 1rem;
            box-shadow: 0 4px 16px rgba(18, 38, 63, 0.04);
        }

        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e8eef7;
            border-radius: 18px;
            padding: 14px 16px;
            box-shadow: 0 4px 16px rgba(18, 38, 63, 0.04);
        }

        div[data-testid="stMetricLabel"] {
            font-weight: 700;
            color: #50627f;
        }

        div[data-testid="stCodeBlock"] {
            border-radius: 14px;
            border: 1px solid #e8eef7;
        }

        .small-note {
            color: #6b7f99;
            font-size: 0.92rem;
        }

        .footer-note {
            text-align: center;
            color: #7a8da8;
            font-size: 0.85rem;
            margin-top: 1.2rem;
            margin-bottom: 0.5rem;
        }

        /* FINAL OVERRIDE - force sliders to purple */

        /* Slider active track: overrides Streamlit red/orange inline style */
        section[data-testid="stSidebar"] div[data-baseweb="slider"] div[style*="rgb(255, 75, 75)"],
        section[data-testid="stSidebar"] div[data-baseweb="slider"] div[style*="#ff4b4b"],
        section[data-testid="stSidebar"] div[data-baseweb="slider"] div[style*="background"] {
            background: #8b5cf6 !important;
            background-color: #8b5cf6 !important;
        }

        /* Slider inactive rail */
        section[data-testid="stSidebar"] div[data-baseweb="slider"] > div > div:first-child {
            background: #e9d5ff !important;
        }

        /* Slider thumb */
        section[data-testid="stSidebar"] div[data-baseweb="slider"] div[role="slider"] {
            background: #8b5cf6 !important;
            background-color: #8b5cf6 !important;
            border-color: #8b5cf6 !important;
            box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.22) !important;
        }

        /* Hover/focus thumb */
        section[data-testid="stSidebar"] div[data-baseweb="slider"] div[role="slider"]:hover,
        section[data-testid="stSidebar"] div[data-baseweb="slider"] div[role="slider"]:focus,
        section[data-testid="stSidebar"] div[data-baseweb="slider"] div[role="slider"]:active {
            background: #7c3aed !important;
            background-color: #7c3aed !important;
            border-color: #7c3aed !important;
            box-shadow: 0 0 0 5px rgba(124, 58, 237, 0.25) !important;
        }

        /* Slider labels */
        section[data-testid="stSidebar"] div[data-baseweb="slider"] span,
        section[data-testid="stSidebar"] .stSlider p {
            color: #334155 !important;
            background: transparent !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def format_hashrate(value: float) -> str:
    if value >= 1e18:
        return f"{value / 1e18:,.2f} EH/s"
    if value >= 1e15:
        return f"{value / 1e15:,.2f} PH/s"
    if value >= 1e12:
        return f"{value / 1e12:,.2f} TH/s"
    if value >= 1e9:
        return f"{value / 1e9:,.2f} GH/s"
    return f"{value:,.2f} H/s"


def format_difficulty_short(value: float) -> str:
    if value >= 1e12:
        return f"{value / 1e12:,.2f} T"
    if value >= 1e9:
        return f"{value / 1e9:,.2f} B"
    if value >= 1e6:
        return f"{value / 1e6:,.2f} M"
    return f"{value:,.2f}"


inject_custom_css()

st.sidebar.title("Navigation")
st.sidebar.markdown("### Dashboard Controls")
n_blocks = st.sidebar.slider("Recent blocks for M1 / M4", 10, 50, 50, 5)
history_points = st.sidebar.slider("Difficulty history points", 30, 150, 100, 10)

anomaly_threshold = st.sidebar.slider(
    "M4 anomaly threshold",
    0.01,
    0.10,
    0.10,
    0.01,
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Visible sections")
st.sidebar.caption("This dashboard integrates the four required modules directly in app.py.")
st.sidebar.markdown(
    """
- Live Bitcoin Overview  
- M1 · Proof of Work Monitor  
- M2 · Block Header Analyzer  
- M3 · Difficulty History  
- M4 · AI Anomaly Detection
"""
)

st.sidebar.markdown("---")
st.sidebar.success("Live Bitcoin data loaded from public blockchain APIs.")

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">CryptoChain Analyzer Dashboard</div>
        <div class="hero-subtitle">
            Cryptography project dashboard focused on Bitcoin Proof of Work, block timing,
            difficulty evolution, and AI-based anomaly detection using real blockchain data.
        </div>
        <div class="hero-tag">Hash Functions and Blockchain · Universidad Alfonso X el Sabio</div>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    latest = get_latest_block()
    block = get_block(latest["hash"])
    header = get_block_header_fields(latest["hash"])

    difficulty = bits_to_difficulty(block["bits"])
    hashrate = estimate_hashrate(block["bits"])
    header_bytes = serialize_block_header(header)
    computed_hash = compute_block_hash_from_header(header)
    hash_matches_api = computed_hash == header["hash"]
    leading_zero_bits = count_leading_zero_bits(header["hash"])

    intervals = get_block_intervals(n_blocks)
    average_interval = sum(intervals) / len(intervals)

    mempool_info = get_mempool_info()
    fee_info = get_recommended_fees()
    recent_mempool_txs = get_recent_mempool_txs()

    interval_df = pd.DataFrame(
        {
            "Block index": list(range(1, len(intervals) + 1)),
            "Seconds": intervals,
        }
    )

    interval_df = interval_df[interval_df["Seconds"] > 0].copy()
    interval_df.reset_index(drop=True, inplace=True)
    interval_df["Block index"] = range(1, len(interval_df) + 1)

    observed_mean_interval = interval_df["Seconds"].mean()
    expected_mean_interval = 600

    def lower_tail_probability(x: float, mean_value: float) -> float:
        return 1 - math.exp(-x / mean_value)

    def upper_tail_probability(x: float, mean_value: float) -> float:
        return math.exp(-x / mean_value)

    interval_df["Lower tail p"] = interval_df["Seconds"].apply(
    lambda x: lower_tail_probability(x, expected_mean_interval)
    )
    interval_df["Upper tail p"] = interval_df["Seconds"].apply(
        lambda x: upper_tail_probability(x, expected_mean_interval)
    )

    interval_df["Tail probability"] = interval_df.apply(
        lambda row: min(row["Lower tail p"], row["Upper tail p"]),
        axis=1,
    )

    interval_df["Anomaly"] = interval_df["Tail probability"].apply(
        lambda p: "Anomalous" if p < anomaly_threshold else "Normal"
    )

    anomalous_blocks = interval_df[interval_df["Anomaly"] == "Anomalous"].copy()
    fast_anomalies = anomalous_blocks[
        anomalous_blocks["Seconds"] < expected_mean_interval
    ].copy()

    slow_anomalies = anomalous_blocks[
        anomalous_blocks["Seconds"] > expected_mean_interval
    ].copy()

    target = bits_to_target(header["bits"])
    pow_valid = is_pow_valid(header["hash"], header["bits"])
    leading_zero_hex = count_leading_zero_hex(header["hash"])

    difficulty_values = get_difficulty_history_df(history_points)
    difficulty_df = pd.DataFrame(difficulty_values)
    difficulty_df["Date"] = difficulty_df["x"].apply(lambda ts: datetime.fromtimestamp(ts))
    difficulty_df["Difficulty"] = difficulty_df["y"]

    difficulty_df["Previous Difficulty"] = difficulty_df["Difficulty"].shift(1)
    difficulty_df["Change %"] = (
        (difficulty_df["Difficulty"] / difficulty_df["Previous Difficulty"] - 1) * 100
    )

    difficulty_df["Difficulty Change"] = (
        difficulty_df["Difficulty"] - difficulty_df["Previous Difficulty"]
    )

    difficulty_df["Significant Variation"] = difficulty_df["Change %"].apply(
        lambda x: "Yes" if pd.notna(x) and abs(x) > 0.5 else "No"
    )

    difficulty_df["Block Time Ratio Approx"] = (
        difficulty_df["Previous Difficulty"] / difficulty_df["Difficulty"]
    )

    significant_variations = difficulty_df[
        difficulty_df["Significant Variation"] == "Yes"
    ].copy()

    anomalous_blocks = interval_df[interval_df["Anomaly"] == "Anomalous"]
    

    # OVERVIEW
    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">Live Bitcoin Overview</div>
            <div class="section-subtitle">
                Real-time summary of the latest Bitcoin block and current mining conditions.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        "Interactive dashboard with live Bitcoin data, Proof of Work verification, difficulty history, and AI anomaly detection."
    )

    o1, o2, o3, o4 = st.columns(4)
    o5, o6, o7 = st.columns(3)

    o1.metric("Latest Block Height", block["height"])
    o2.metric("Current Difficulty", format_difficulty_short(difficulty))
    o3.metric("Bits", block["bits"])
    o4.metric("Theoretical Hash Rate Estimate", format_hashrate(hashrate))
    o5.metric("Nonce", block["nonce"])
    o6.metric("Transactions", block["n_tx"])
    o7.metric("Block Size", f"{block['size']:,} B")

    top_left, top_right = st.columns([2.2, 1])
    with top_left:
        st.subheader("Latest Block Hash")
        st.code(block["hash"], language="text")
        st.caption(
            "The leading zeros in the hash are a visible consequence of the Proof of Work target."
        )

    with top_right:
        st.markdown(
            """
            <div class="mini-card">
                <div style="font-weight:800; color:#163153; font-size:1.05rem; margin-bottom:0.35rem;">
                    Proof of Work meaning
                </div>
                <div class="small-note">
                    Bitcoin miners must find a block hash that is numerically lower than the
                    threshold encoded by the <b>bits</b> field. That is why valid hashes tend
                    to begin with several zeros.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    tab_m1, tab_m2, tab_m3, tab_m4, tab_extra = st.tabs(
        [
            "M1 · Proof of Work Monitor",
            "M2 · Block Header Analyzer",
            "M3 · Difficulty History",
            "M4 · AI Anomaly Detection",
            "Extra · Mempool Overview",
        ]
    )

    with tab_m1:
        st.markdown(
            """
            <div class="section-card">
                <div class="section-title">M1 · Proof of Work Monitor</div>
                <div class="section-subtitle">
                    Analysis of recent block intervals, expected 600-second target, and estimated mining rate.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        m1a, m1b, m1c, m1d = st.columns(4)
        m1a.metric("Average Block Time", f"{average_interval:.2f} s")
        m1b.metric("Target", "600 s")
        m1c.metric("Intervals Below 600 s", int((interval_df["Seconds"] < 600).sum()))
        m1d.metric("Detected M4 Anomalies", len(anomalous_blocks))

        st.caption(
            "Hash rate is estimated from difficulty using the expected 600-second block interval. "
            "It is not a direct measurement of miners' hardware."
        )

        m1_left, m1_right = st.columns([2.2, 1.15])

        with m1_left:
            line_fig = px.line(
                interval_df,
                x="Block index",
                y="Seconds",
                markers=True,
                title="Time Between Latest Bitcoin Blocks",
            )
            line_fig.add_hline(y=600, line_dash="dash", annotation_text="Target: 600s")
            line_fig.update_layout(
                plot_bgcolor="white",
                paper_bgcolor="white",
                margin=dict(l=20, r=20, t=55, b=20),
            )
            st.plotly_chart(line_fig, width="stretch")

        with m1_right:
            hist_fig = px.histogram(
                interval_df,
                x="Seconds",
                nbins=12,
                title=f"Distribution of Time Between Last {len(intervals)} Blocks",
            )
            hist_fig.add_vline(x=600, line_dash="dash", annotation_text="Target: 600s")
            hist_fig.update_layout(
                plot_bgcolor="white",
                paper_bgcolor="white",
                margin=dict(l=20, r=20, t=55, b=20),
            )
            st.plotly_chart(hist_fig, width="stretch")

        if average_interval > 650:
            st.info("Recent average block time is above the 600-second target, suggesting a slower recent pace.")
        elif average_interval < 550:
            st.info("Recent average block time is below the 600-second target, suggesting a faster recent pace.")
        else:
            st.info("Recent average block time is close to the 600-second target expected in Bitcoin.")

    with tab_m2:
        st.markdown(
            """
            <div class="section-card">
                <div class="section-title">M2 · Block Header Analyzer</div>
                <div class="section-subtitle">
                    Bitcoin block header fields, local double SHA-256 recomputation, and Proof of Work verification.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        hf1, hf2, hf3, hf4, hf5, hf6 = st.columns(6)
        hf1.metric("Version", header["version"])
        hf2.metric("Timestamp", header["timestamp"])
        hf3.metric("Bits", f"{header['bits']} / 0x{bits_to_hex(header['bits'])}")
        hf4.metric("Nonce", header["nonce"])
        hf5.metric("Leading Zero Hex", leading_zero_hex)
        hf6.metric("Leading Zero Bits", leading_zero_bits)

        st.subheader("Header Fields")
        f1, f2, f3 = st.columns(3)
        with f1:
            st.code(f"Previous Block Hash\n{header['previousblockhash']}", language="text")
        with f2:
            st.code(f"Merkle Root\n{header['merkleroot']}", language="text")
        with f3:
            st.code(f"Serialized Header (80 bytes, hex)\n{header_bytes.hex()}", language="text")

        st.subheader("Proof of Work Verification")
        v1, v2 = st.columns([2.2, 1])

        with v1:
            st.code(f"Block Hash (API)\n{header['hash']}", language="text")
            st.code(f"Computed Double SHA-256 Hash\n{computed_hash}", language="text")
            st.code(f"Target (decimal)\n{target}", language="text")

        with v2:
            st.metric("Hash matches API", str(hash_matches_api))
            st.metric("PoW Valid", str(pow_valid))
            st.markdown(
                """
                <div class="mini-card">
                    <div style="font-weight:800; color:#163153; margin-bottom:0.35rem;">
                        Verification Flow
                    </div>
                    <div class="small-note">
                        80-byte Header → SHA256 → SHA256 → 256-bit Hash → compare with target
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.caption(
            "A Bitcoin block is valid only if its hash is numerically lower than the target encoded by the bits field."
        )

    with tab_m3:
        st.markdown(
            """
            <div class="section-card">
                <div class="section-title">M3 · Difficulty History</div>
                <div class="section-subtitle">
                    Historical evolution of Bitcoin mining difficulty using public API sampled data.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Current Shown Difficulty", format_difficulty_short(difficulty_df["Difficulty"].iloc[-1]))
        d2.metric("Max in Period", format_difficulty_short(difficulty_df["Difficulty"].max()))
        d3.metric("Min in Period", format_difficulty_short(difficulty_df["Difficulty"].min()))
        d4.metric("Significant Variations", len(significant_variations))

        difficulty_fig = px.line(
            difficulty_df,
            x="Date",
            y="Difficulty",
            title="Bitcoin Difficulty Over Time",
            markers=False,
        )

        if not significant_variations.empty:
            difficulty_fig.add_scatter(
                x=significant_variations["Date"],
                y=significant_variations["Difficulty"],
                mode="markers",
                name="Significant Variation",
                marker=dict(size=9),
            )

        difficulty_fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=20, r=20, t=55, b=20),
        )

        st.plotly_chart(difficulty_fig, width="stretch")

        st.subheader("Recent significant difficulty variations")

        recent_adjustments = significant_variations[
            ["Date", "Difficulty", "Change %", "Block Time Ratio Approx"]
        ].copy()

        recent_adjustments["Difficulty"] = recent_adjustments["Difficulty"].round(2)
        recent_adjustments["Change %"] = recent_adjustments["Change %"].round(2)
        recent_adjustments["Block Time Ratio Approx"] = recent_adjustments[
            "Block Time Ratio Approx"
        ].round(3)

        st.dataframe(recent_adjustments.tail(8), width="stretch")

        st.info(
            "The chart uses sampled public API difficulty data. Points above 0.5% change are highlighted "
            "as significant visible variations, not as a full reconstruction of every 2016-block adjustment boundary."
        )

    with tab_m4:
        st.markdown(
            """
            <div class="section-card">
                <div class="section-title">M4 · AI Anomaly Detection</div>
                <div class="section-subtitle">
                    Statistical anomaly detection on Bitcoin inter-block times using an exponential baseline.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write(
            "Chosen AI approach: anomaly detector for abnormal Bitcoin block times. "
            "Bitcoin mining can be modelled as a probabilistic process, where inter-block "
            "times are expected to follow an exponential baseline with an average target "
            "of 600 seconds. The model analyses positive block intervals and flags as "
            "potentially anomalous those with very low tail probability under this baseline."
        )

        a1, a2, a3, a4, a5, a6 = st.columns(6)
        a1.metric("Total Anomalies", len(anomalous_blocks))
        a2.metric("Anomaly Rate", f"{(len(anomalous_blocks) / len(interval_df)) * 100:.1f}%")
        a3.metric("Fast Anomalies", len(fast_anomalies))
        a4.metric("Slow Anomalies", len(slow_anomalies))
        a5.metric("Expected Mean", "600 s")
        a6.metric("Threshold", f"{anomaly_threshold:.2f}")

        st.caption(
            f"Observed mean interval in the selected sample: {observed_mean_interval:.2f} seconds."
        )

        hist_ai_fig = px.histogram(
            interval_df,
            x="Seconds",
            nbins=12,
            title="Observed Inter-Block Times Compared with Exponential Baseline",
            histnorm="probability density",
        )

        hist_ai_fig.add_vline(
            x=600,
            line_dash="dash",
            annotation_text="Expected mean: 600s",
        )

        hist_ai_fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=20, r=20, t=55, b=20),
        )

        st.plotly_chart(hist_ai_fig, width="stretch")

        anomaly_fig = px.scatter(
            interval_df,
            x="Block index",
            y="Seconds",
            color="Anomaly",
            title="Detected Anomalous Bitcoin Block Intervals",
            color_discrete_map={"Normal": "#4f8cff", "Anomalous": "#9b6dff"},
        )
        anomaly_fig.add_hline(y=600, line_dash="dash", annotation_text="Target: 600s")
        anomaly_fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=20, r=20, t=55, b=20),
        )
        st.plotly_chart(anomaly_fig, width="stretch")

        st.subheader("Potential anomalies detected")

        if anomalous_blocks.empty:
            st.info(
                "No anomalous intervals were detected with the current threshold. "
                "This is possible because Bitcoin block discovery is random, and the selected sample "
                "may not contain extremely short or extremely long intervals."
            )
        else:
            st.dataframe(
                anomalous_blocks[
                    ["Block index", "Seconds", "Tail probability", "Anomaly"]
                ],
                width="stretch",
            )

        st.caption(
            f"Anomalies are flagged using an exponential baseline with expected mean 600 seconds. "
            f"Very short or very long intervals receive low tail probability. "
            f"The current anomaly threshold is {anomaly_threshold:.2f}."
        )

        with tab_extra:
            st.markdown(
                """
                <div class="section-card">
                    <div class="section-title">Extra · Mempool Overview</div>
                    <div class="section-subtitle">
                        Real-time view of pending Bitcoin transactions and current recommended fees.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.write(
                "This extra section extends the dashboard beyond block headers and difficulty. "
                "It shows current mempool pressure and fee recommendations for new transactions."
            )

            e1, e2, e3, e4 = st.columns(4)
            e1.metric("Mempool Transactions", f"{mempool_info['count']:,}")
            e2.metric("Mempool Size", f"{mempool_info['vsize']:,} vB")
            e3.metric("High Priority Fee", f"{fee_info['fastestFee']} sat/vB")
            e4.metric("Economy Fee", f"{fee_info['economyFee']} sat/vB")

            recent_df = pd.DataFrame(recent_mempool_txs)

            if not recent_df.empty:
                recent_df["fee_per_vsize"] = recent_df["fee"] / recent_df["vsize"]

                fee_fig = px.histogram(
                    recent_df,
                    x="fee_per_vsize",
                    nbins=20,
                    title="Recent Mempool Transactions: Fee Rate Distribution",
                )
                fee_fig.update_layout(
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    margin=dict(l=20, r=20, t=55, b=20),
                )
                st.plotly_chart(fee_fig, width="stretch")

                st.subheader("Recent mempool transactions")
                st.dataframe(
                    recent_df[["txid", "fee", "vsize", "fee_per_vsize"]].head(10),
                    width="stretch",
                )

            st.info(
                "When the mempool becomes more congested, recommended fees tend to increase. "
                "This helps explain how transaction demand affects inclusion priority."
            )

        st.markdown(
            '<div class="footer-note">CryptoChain Analyzer Dashboard · Educational use · Bitcoin public API data</div>',
            unsafe_allow_html=True,
        )

except Exception as error:
    st.error(f"Error while loading blockchain data: {error}")