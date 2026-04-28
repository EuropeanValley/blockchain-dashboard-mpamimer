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

st.set_page_config(page_title="CryptoChain Analyzer Dashboard", layout="wide")

st.title("CryptoChain Analyzer Dashboard")
st.subheader("Live Bitcoin overview")

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

    col1, col2, col3, col4 = st.columns(4)
    col5, col6, col7 = st.columns(3)

    col1.metric("Block Height", block["height"])
    col2.metric("Difficulty", f"{difficulty:,.2f}")
    col3.metric("Bits", block["bits"])
    col4.metric("Estimated Hash Rate", format_hashrate(hashrate))
    col5.metric("Nonce", block["nonce"])
    col6.metric("Transactions", block["n_tx"])
    col7.metric("Block Size (bytes)", block["size"])

    st.markdown("### Latest Block Hash")
    st.code(block["hash"], language="text")

    st.markdown("### Proof of Work meaning")
    st.write(
        "The block hash starts with leading zeros because Bitcoin miners must find "
        "a hash that is lower than the target threshold. The bits field stores that "
        "target in compact format."
    )

    st.markdown("---")
    st.header("M1 · Proof of Work Monitor")

    intervals = get_block_intervals(20)
    average_interval = sum(intervals) / len(intervals)

    st.metric("Average time between latest blocks (seconds)", f"{average_interval:.2f}")

    interval_df = pd.DataFrame(
        {
            "Block index": list(range(1, len(intervals) + 1)),
            "Seconds": intervals,
        }
    )

    interval_df["Anomaly"] = interval_df["Seconds"].apply(
        lambda x: "Anomalous" if x < 300 or x > 1200 else "Normal"
    )

    line_fig = px.line(
        interval_df,
        x="Block index",
        y="Seconds",
        markers=True,
        title="Time Between Latest Bitcoin Blocks",
    )
    line_fig.add_hline(y=600, line_dash="dash", annotation_text="Target: 600s")
    st.plotly_chart(line_fig, use_container_width=True)

    hist_fig = px.histogram(
        interval_df,
        x="Seconds",
        nbins=10,
        title="Distribution of Time Between Latest Bitcoin Blocks",
    )
    hist_fig.add_vline(x=600, line_dash="dash", annotation_text="Target: 600s")
    st.plotly_chart(hist_fig, use_container_width=True)

    st.write(
        "Bitcoin is expected to produce one block roughly every 600 seconds on average. "
        "This chart helps compare recent block production against that target."
    )
    
    st.markdown("---")
    st.header("M2 · Block Header Analyzer")

    header = get_block_header_fields(latest["hash"])
    target = bits_to_target(header["bits"])
    pow_valid = is_pow_valid(header["hash"], header["bits"])
    leading_zero_hex = count_leading_zero_hex(header["hash"])

    st.subheader("Header fields")

    hcol1, hcol2 = st.columns(2)

    with hcol1:
        st.write("**Version:**", header["version"])
        st.write("**Previous Block Hash:**", header["previousblockhash"])
        st.write("**Merkle Root:**", header["merkleroot"])

    with hcol2:
        st.write("**Timestamp:**", header["timestamp"])
        st.write("**Bits:**", header["bits"])
        st.write("**Nonce:**", header["nonce"])

    st.subheader("Proof of Work verification")

    vcol1, vcol2 = st.columns(2)

    with vcol1:
        st.write("**Block Hash (API):**")
        st.code(header["hash"], language="text")

        st.write("**Computed Double SHA-256 Hash:**")
        st.code(computed_hash, language="text")

        st.write("**Target (decimal):**")
        st.code(str(target), language="text")

        st.write("**Serialized Header (80 bytes, hex):**")
        st.code(header_bytes.hex(), language="text")

    with vcol2:
        st.metric("Hash matches API", str(hash_matches_api))
        st.metric("PoW Valid", str(pow_valid))
        st.metric("Leading zero hex characters", leading_zero_hex)
        st.metric("Leading zero bits", leading_zero_bits)

    st.write(
        "A Bitcoin block is valid only if its hash is numerically lower than the "
        "target encoded by the bits field."
    )

    st.markdown("---")
    st.header("M3 · Difficulty History")

    difficulty_values = get_difficulty_history_df(100)

    difficulty_df = pd.DataFrame(difficulty_values)
    difficulty_df["Date"] = difficulty_df["x"].apply(
        lambda ts: datetime.fromtimestamp(ts)
    )
    difficulty_df["Difficulty"] = difficulty_df["y"]

    difficulty_fig = px.line(
        difficulty_df,
        x="Date",
        y="Difficulty",
        title="Bitcoin Difficulty Over Time",
    )
    st.plotly_chart(difficulty_fig, use_container_width=True)

    st.write(
        "This chart shows how Bitcoin mining difficulty changes over time. "
        "Difficulty adjusts to keep the average block production close to 600 seconds."
    )

    st.markdown("---")
    st.header("M4 · AI Component Preview")

    anomalous_blocks = interval_df[interval_df["Anomaly"] == "Anomalous"]

    st.write(
        "Chosen AI approach: anomaly detector for abnormal Bitcoin block times. "
        "This preview uses a simple heuristic to flag unusually fast or slow blocks. "
        "A more formal statistical or machine learning model will be added later."
    )

    st.metric("Detected anomalous intervals", len(anomalous_blocks))

    anomaly_fig = px.scatter(
        interval_df,
        x="Block index",
        y="Seconds",
        color="Anomaly",
        title="Preview of Potentially Anomalous Block Times",
    )
    anomaly_fig.add_hline(y=600, line_dash="dash", annotation_text="Target: 600s")
    st.plotly_chart(anomaly_fig, use_container_width=True)

    st.subheader("Potential anomalies detected")
    st.dataframe(anomalous_blocks, use_container_width=True)

except Exception as error:
    st.error(f"Error while loading blockchain data: {error}")
