"""
Blockchain API client.

Provides helper functions to fetch blockchain data from public APIs.
"""

import requests
import hashlib
import struct

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

def estimate_hashrate(bits: int) -> float:
    """Estimate Bitcoin network hashrate in hashes per second."""
    difficulty = bits_to_difficulty(bits)
    return difficulty * (2**32) / 600

def get_block_header_fields(block_hash: str) -> dict:
    """Return key block header fields from Blockstream API."""
    response = requests.get(f"{BLOCKSTREAM_URL}/block/{block_hash}", timeout=10)
    response.raise_for_status()
    block = response.json()

    return {
        "version": block["version"],
        "previousblockhash": block["previousblockhash"],
        "merkleroot": block["merkle_root"],
        "timestamp": block["timestamp"],
        "bits": block["bits"],
        "nonce": block["nonce"],
        "height": block["height"],
        "hash": block["id"],
    }


def count_leading_zero_hex(block_hash: str) -> int:
    """Count leading zero hexadecimal characters in a block hash."""
    count = 0
    for char in block_hash:
        if char == "0":
            count += 1
        else:
            break
    return count


def is_pow_valid(block_hash: str, bits: int) -> bool:
    """Check whether block hash is below the target encoded by bits."""
    target = bits_to_target(bits)
    block_hash_int = int(block_hash, 16)
    return block_hash_int < target

def reverse_hex_bytes(hex_string: str) -> bytes:
    """Convert hex string to bytes and reverse byte order."""
    return bytes.fromhex(hex_string)[::-1]


def serialize_block_header(header: dict) -> bytes:
    """Serialize the 80-byte Bitcoin block header in little-endian format."""
    version = struct.pack("<I", header["version"])
    prev_hash = reverse_hex_bytes(header["previousblockhash"])
    merkle_root = reverse_hex_bytes(header["merkleroot"])
    timestamp = struct.pack("<I", header["timestamp"])
    bits = struct.pack("<I", header["bits"])
    nonce = struct.pack("<I", header["nonce"])

    return version + prev_hash + merkle_root + timestamp + bits + nonce


def double_sha256(data: bytes) -> bytes:
    """Return SHA256(SHA256(data))."""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def compute_block_hash_from_header(header: dict) -> str:
    """Compute Bitcoin block hash from serialized header."""
    header_bytes = serialize_block_header(header)
    hashed = double_sha256(header_bytes)
    return hashed[::-1].hex()


def count_leading_zero_bits(block_hash: str) -> int:
    """Count leading zero bits in a block hash."""
    binary = bin(int(block_hash, 16))[2:].zfill(256)
    count = 0
    for bit in binary:
        if bit == "0":
            count += 1
        else:
            break
    return count

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