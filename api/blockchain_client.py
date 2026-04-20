"""
Blockchain API client.

Provides helper functions to fetch blockchain data from public APIs.
"""

import requests

BASE_URL = "https://blockchain.info"


def get_latest_block() -> dict:
    """Return the latest block summary."""
    response = requests.get(f"{BASE_URL}/latestblock", timeout=10)
    response.raise_for_status()
    return response.json()


def get_block(block_hash: str) -> dict:
    """Return full details for a block identified by *block_hash*."""
    response = requests.get(f"{BASE_URL}/rawblock/{block_hash}", timeout=10)
    response.raise_for_status()
    return response.json()


def get_difficulty_history(n_points: int = 100) -> list[dict]:
    """Return the last *n_points* difficulty values as a list of dicts."""
    response = requests.get(
        f"{BASE_URL}/charts/difficulty",
        params={"timespan": "1year", "format": "json", "sampled": "true"},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    return data.get("values", [])[-n_points:]


if __name__ == "__main__":
    latest = get_latest_block()
    block = get_block(latest["hash"])

    print("Height:", block["height"])
    print("Hash:", block["hash"])
    print("Difficulty:", block.get("difficulty", "Not available in this endpoint"))
    print("Bits:", block["bits"])
    print("Nonce:", block["nonce"])
    print("Transactions:", block["n_tx"])

    # The block hash usually starts with leading zeros because Proof of Work
    # requires the hash to be below a target threshold.
    # The bits field is the compact representation of that target.