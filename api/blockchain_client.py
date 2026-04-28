"""
Blockchain API client.

Provides helper functions to fetch blockchain data from public APIs.
"""

import requests

BASE_URL = "https://blockchain.info"
BLOCKSTREAM_URL = "https://blockstream.info/api"


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


def bits_to_target(bits: int) -> int:
    """Convert compact bits representation to full mining target."""
    exponent = bits >> 24
    coefficient = bits & 0xFFFFFF
    return coefficient * (1 << (8 * (exponent - 3)))


def bits_to_difficulty(bits: int) -> float:
    """Compute Bitcoin difficulty from compact bits."""
    max_target = 0x00FFFF * (1 << (8 * (0x1D - 3)))
    current_target = bits_to_target(bits)
    return max_target / current_target

def get_latest_blocks(n_blocks: int = 20) -> list[dict]:
    """Return the latest *n_blocks* blocks using Blockstream API."""
    blocks = []
    response = requests.get(f"{BLOCKSTREAM_URL}/blocks", timeout=10)
    response.raise_for_status()
    blocks.extend(response.json())

    while len(blocks) < n_blocks:
        last_height = blocks[-1]["height"]
        response = requests.get(f"{BLOCKSTREAM_URL}/blocks/{last_height}", timeout=10)
        response.raise_for_status()
        new_blocks = response.json()

        if not new_blocks:
            break

        blocks.extend(new_blocks)

    return blocks[:n_blocks]


def get_block_intervals(n_blocks: int = 20) -> list[int]:
    """Return time intervals in seconds between consecutive latest blocks."""
    blocks = get_latest_blocks(n_blocks)
    intervals = []

    for i in range(len(blocks) - 1):
        current_time = blocks[i]["timestamp"]
        next_time = blocks[i + 1]["timestamp"]
        intervals.append(current_time - next_time)

    return intervals

if __name__ == "__main__":
    try:
        latest = get_latest_block()
        block = get_block(latest["hash"])
        difficulty = bits_to_difficulty(block["bits"])

        print("Height:", block["height"])
        print("Hash:", block["hash"])
        print("Difficulty:", round(difficulty, 2))
        print("Bits (compact target):", block["bits"])
        print("Nonce:", block["nonce"])
        print("Transactions:", block["n_tx"])

        # The block hash starts with leading zeros because Bitcoin uses Proof of Work.
        # A valid block hash must be lower than a target value.
        # The bits field stores that target in compact format.
        # The nonce is changed by miners to search for a valid hash.

    except requests.RequestException as error:
        print("API request failed:", error)