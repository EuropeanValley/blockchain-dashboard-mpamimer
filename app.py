import pandas as pd
import plotly.express as px
import streamlit as st

from api.blockchain_client import (
    bits_to_difficulty,
    get_block,
    get_block_intervals,
    get_latest_block,
)

st.set_page_config(page_title="CryptoChain Analyzer Dashboard", layout="wide")

st.title("CryptoChain Analyzer Dashboard")
st.subheader("Live Bitcoin overview")

try:
    latest = get_latest_block()
    block = get_block(latest["hash"])
    difficulty = bits_to_difficulty(block["bits"])

    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    col1.metric("Block Height", block["height"])
    col2.metric("Difficulty", f"{difficulty:,.2f}")
    col3.metric("Bits", block["bits"])
    col4.metric("Nonce", block["nonce"])
    col5.metric("Transactions", block["n_tx"])
    col6.metric("Block Size (bytes)", block["size"])

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

except Exception as error:
    st.error(f"Error while loading blockchain data: {error}")
