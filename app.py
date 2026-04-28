import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime

from api.blockchain_client import (
    bits_to_difficulty,
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
    is_pow_valid,
    serialize_block_header,
)

st.set_page_config(
    page_title="CryptoChain Analyzer Dashboard",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_custom_css():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(180deg, #f8fbff 0%, #f3f6fb 100%);
        }

        .block-container {
            padding-top: 1.4rem;
            padding-bottom: 2rem;
            max-width: 1320px;
        }

        section[data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid #e9eef6;
        }

        .hero {
            background: linear-gradient(135deg, #ffffff 0%, #f7fbff 100%);
            border: 1px solid #e6eef8;
            border-radius: 22px;
            padding: 1.6rem 1.8rem;
            box-shadow: 0 8px 26px rgba(18, 38, 63, 0.06);
            margin-bottom: 1.2rem;
        }

        .hero-title {
            font-size: 2.4rem;
            font-weight: 800;
            color: #14213d;
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
            background: #eef5ff;
            color: #2563eb;
            border: 1px solid #dbeafe;
            padding: 0.35rem 0.7rem;
            border-radius: 999px;
            font-size: 0.88rem;
            font-weight: 600;
        }

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
n_blocks = st.sidebar.slider("Recent blocks for M1 / M4", 10, 50, 20, 5)
history_points = st.sidebar.slider("Difficulty history points", 30, 150, 100, 10)

st.sidebar.markdown("---")
st.sidebar.markdown("### Visible sections")
st.sidebar.caption("This version keeps the required project structure and modules.")
st.sidebar.markdown(
    """
- Live Bitcoin Overview  
- M1 · Proof of Work Monitor  
- M2 · Block Header Analyzer  
- M3 · Difficulty History  
- M4 · AI Component Preview
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
            difficulty evolution, and a first anomaly detection preview using real blockchain data.
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

    interval_df = pd.DataFrame(
        {
            "Block index": list(range(1, len(intervals) + 1)),
            "Seconds": intervals,
        }
    )

    interval_df["Anomaly"] = interval_df["Seconds"].apply(
        lambda x: "Anomalous" if x < 300 or x > 1200 else "Normal"
    )

    target = bits_to_target(header["bits"])
    pow_valid = is_pow_valid(header["hash"], header["bits"])
    leading_zero_hex = count_leading_zero_hex(header["hash"])

    difficulty_values = get_difficulty_history_df(history_points)
    difficulty_df = pd.DataFrame(difficulty_values)
    difficulty_df["Date"] = difficulty_df["x"].apply(lambda ts: datetime.fromtimestamp(ts))
    difficulty_df["Difficulty"] = difficulty_df["y"]

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

    o1, o2, o3, o4 = st.columns(4)
    o5, o6, o7 = st.columns(3)

    o1.metric("Latest Block Height", block["height"])
    o2.metric("Current Difficulty", format_difficulty_short(difficulty))
    o3.metric("Bits", block["bits"])
    o4.metric("Estimated Hash Rate", format_hashrate(hashrate))
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

    # M1
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
    m1d.metric("Detected M4 Preview Anomalies", len(anomalous_blocks))

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

    st.markdown("---")

    # M2
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
    hf3.metric("Bits", header["bits"])
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

    st.markdown("---")

    # M3
    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">M3 · Difficulty History</div>
            <div class="section-subtitle">
                Historical evolution of Bitcoin mining difficulty across recent sampled periods.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    d1, d2, d3 = st.columns(3)
    d1.metric("Current Shown Difficulty", format_difficulty_short(difficulty_df["Difficulty"].iloc[-1]))
    d2.metric("Max in Period", format_difficulty_short(difficulty_df["Difficulty"].max()))
    d3.metric("Min in Period", format_difficulty_short(difficulty_df["Difficulty"].min()))

    difficulty_fig = px.line(
        difficulty_df,
        x="Date",
        y="Difficulty",
        title="Bitcoin Difficulty Over Time",
        markers=True,
    )
    difficulty_fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=55, b=20),
    )
    st.plotly_chart(difficulty_fig, width="stretch")

    st.info(
        "Difficulty changes in visible step-like adjustments rather than continuously. "
        "These adjustments help maintain the long-term average block interval near 600 seconds."
    )

    st.markdown("---")

    # M4
    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">M4 · AI Component Preview</div>
            <div class="section-subtitle">
                Initial anomaly detection preview on inter-block times using a rule-based heuristic.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write(
        "Chosen AI approach: anomaly detector for abnormal Bitcoin block times. "
        "This preview flags unusually fast or slow intervals and serves as a first step "
        "toward a more formal statistical or machine learning model."
    )

    a1, a2 = st.columns(2)
    a1.metric("Detected Anomalous Intervals", len(anomalous_blocks))
    a2.metric("Anomaly Rate", f"{(len(anomalous_blocks) / len(interval_df)) * 100:.1f}%")

    anomaly_fig = px.scatter(
        interval_df,
        x="Block index",
        y="Seconds",
        color="Anomaly",
        title="Preview of Potentially Anomalous Block Times",
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
    st.dataframe(anomalous_blocks, width="stretch")

    st.caption(
        "Current preview rule: intervals below 300 seconds or above 1200 seconds are flagged as anomalous."
    )

    st.markdown(
        '<div class="footer-note">CryptoChain Analyzer Dashboard · Educational use · Bitcoin public API data</div>',
        unsafe_allow_html=True,
    )

except Exception as error:
    st.error(f"Error while loading blockchain data: {error}")