[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/N3kLi3ZO)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=23640602&assignment_repo_type=AssignmentRepo)

# CryptoChain Analyzer Dashboard

Real-time Bitcoin dashboard for the Cryptography project at Universidad Alfonso X el Sabio.

The dashboard connects to public Bitcoin APIs and displays live cryptographic metrics related to Proof of Work, block headers, mining difficulty, inter-block times, and mempool activity. It also includes an AI-based anomaly detection component for abnormal Bitcoin block intervals.

---

## Student Information

| Field | Value |
|---|---|
| Student Name | Marta Pamies Merino |
| GitHub Username | mpamimer |
| Project Title | CryptoChain Analyzer Dashboard |
| Chosen AI Approach | Anomaly detector for abnormal Bitcoin block times |

---

## Project Summary

This project applies cryptographic concepts studied in the course to real Bitcoin data.

The dashboard focuses on:

- SHA-256 and double SHA-256 block hashing.
- Bitcoin Proof of Work validation.
- Compact target representation through the `bits` field.
- Mining difficulty and estimated hash rate.
- Inter-block time analysis.
- Difficulty history using public API data.
- AI anomaly detection based on an exponential baseline.
- Extra mempool and fee market overview.

The application is built with Streamlit and updates automatically using a configurable refresh interval.

---

## Module Tracking

| Module | What it includes | Status |
|---|---|---|
| M1 | Proof of Work Monitor: current difficulty, estimated hash rate, block time intervals, histogram, and 600-second target comparison | Done |
| M2 | Block Header Analyzer: six block header fields, 80-byte serialization, double SHA-256 recomputation, `bits` to target conversion, and Proof of Work verification | Done |
| M3 | Difficulty History: historical difficulty chart using public API sampled data, significant variation detection, and approximate block time ratio | Done |
| M4 | AI Component: anomaly detector for abnormal Bitcoin inter-block times using an exponential baseline and tail probability threshold | Done |
| Extra | Mempool overview: pending transactions, mempool size, recommended fees, and fee rate distribution | Done |

---

## Current Progress

- GitHub Classroom repository accepted and original project structure preserved.
- Streamlit dashboard implemented with visible integration of M1, M2, M3, and M4.
- Live Bitcoin data is retrieved from public APIs including Blockchain.com, Blockstream, and Mempool.space.
- M1 displays current mining conditions, recent block intervals, and the expected 600-second target.
- M2 locally reconstructs the Bitcoin block header and verifies Proof of Work using `hashlib`.
- M3 shows recent difficulty evolution and highlights significant visible variations in sampled public API data.
- M4 implements a statistical anomaly detector for abnormal Bitcoin block times.
- Extra mempool section added to show current transaction pressure and fee recommendations.
- Final report added in PDF format under the `report/` folder.

---

## AI Component

The selected AI approach is an anomaly detector for abnormal Bitcoin block times.

Bitcoin mining can be modelled as a probabilistic process. The expected average time between blocks is approximately 600 seconds, and inter-block times can be compared against an exponential baseline.

The model:

- Collects recent real Bitcoin block timestamps.
- Computes positive inter-block intervals.
- Uses an exponential distribution with expected mean 600 seconds.
- Calculates lower-tail and upper-tail probabilities.
- Flags very short or very long intervals as potential anomalies when their tail probability is below the selected threshold.

The dashboard reports:

- Total anomalies.
- Anomaly rate.
- Fast anomalies.
- Slow anomalies.
- Expected mean interval.
- Current threshold.
- Table of detected anomalous intervals.

Since there is no labelled ground truth for anomalous blocks, the evaluation is based on statistical consistency with the exponential baseline and on the percentage of intervals falling in the extreme tails.

---

## Cryptographic Correctness

The dashboard verifies the latest Bitcoin block using the actual block header fields:

1. Version.
2. Previous block hash.
3. Merkle root.
4. Timestamp.
5. Bits.
6. Nonce.

The 80-byte block header is serialized in little-endian format where required. The application then computes:

```text
SHA256(SHA256(block_header))
```

The computed hash is compared with the hash returned by the API. The dashboard also converts the compact `bits` representation into the full mining target and verifies that:

```text
block_hash <= target
```

This demonstrates the Proof of Work condition directly with real Bitcoin data.

---

## APIs Used

| API | Purpose |
|---|---|
| Blockchain.com API | Latest block, full block data, and difficulty chart |
| Blockstream API | Block header fields and recent blocks |
| Mempool.space API | Mempool status, recommended fees, and recent mempool transactions |

---

## How to Run

Install the dependencies:

```bash
pip install -r requirements.txt
```

Run the dashboard:

```bash
streamlit run app.py
```

The dashboard should open automatically in the browser. If it does not, copy the local URL shown in the terminal.

---

## Required Dependencies

The project requires the following main Python packages:

```text
streamlit
streamlit-autorefresh
pandas
plotly
requests
```

---

## Project Structure

```bash
blockchain-dashboard-mpamimer/
|-- README.md
|-- requirements.txt
|-- .gitignore
|-- app.py
|-- api/
|   |-- __init__.py
|   `-- blockchain_client.py
|-- modules/
|   |-- m1_pow_monitor.py
|   |-- m2_block_header.py
|   |-- m3_difficulty_history.py
|   `-- m4_ai_component.py
`-- report/
    `-- final_report.pdf
```

---

## Final Report

The final report is included in:

```text
report/final_report.pdf
```

It explains:

1. The cryptographic metrics displayed in the dashboard and their meaning.
2. The chosen AI model, why it was selected, and how it is evaluated.
3. External references used for Bitcoin, Proof of Work, block headers, and public API documentation.

---

## References

- Nakamoto, S. (2008). *Bitcoin: A Peer-to-Peer Electronic Cash System*.
- Bitcoin Developer Reference.
- Blockstream API documentation.
- Blockchain.com API documentation.
- Mempool.space API documentation.

<!-- student-repo-auditor:teacher-feedback:start -->
## Teacher Feedback

### Kick-off Review

Review time: 2026-04-29 20:31 CEST
Status: Amber

Strength:
- M1 already shows visible progress beyond the initial template.

Improve now:
- I do not yet see a clear dashboard integration for M1, M2, M3, and M4 in app.py.

Next step:
- Make sure app.py visibly integrates M1, M2, M3, and M4 in the dashboard navigation.
<!-- student-repo-auditor:teacher-feedback:end -->
