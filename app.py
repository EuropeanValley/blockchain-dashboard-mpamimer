import streamlit as st

from api.blockchain_client import get_latest_block, get_block, bits_to_difficulty

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

except Exception as error:
    st.error(f"Error while loading blockchain data: {error}")
