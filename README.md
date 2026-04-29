[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/N3kLi3ZO)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=23640602&assignment_repo_type=AssignmentRepo)
# Blockchain Dashboard Project

Use this repository to build your blockchain dashboard project.
Update this README every week.

## Student Information

| Field | Value |
|---|---|
| Student Name | Marta Pamies Merino |
| GitHub Username | mpamimer |
| Project Title | CryptoChain Analyzer Dashboard |
| Chosen AI Approach | Anomaly detector for abnormal Bitcoin block times |

## Module Tracking

Use one of these values: `Not started`, `In progress`, `Done`

| Module | What it should include | Status |
|---|---|---|
| M1 | Proof of Work Monitor | In progress |
| M2 | Block Header Analyzer | In progress |
| M3 | Difficulty History | In progress |
| M4 | AI Component | In progress |

## Current Progress

Write 3 to 5 short lines about what you have already done.

- GitHub Classroom repository accepted and initial project structure preserved.
- Streamlit dashboard created and connected to real Bitcoin blockchain APIs.
- M1 implemented with live block metrics, estimated hash rate, and block time analysis charts.
- M2 implemented with block header fields, target calculation, local header serialization, and double SHA-256 verification.
- M3 started with a difficulty history chart and M4 preview added with anomaly detection on inter-block times.

## Next Step

Write the next small step you will do before the next class.

- Improve the dashboard layout and refine the anomaly detection approach.

## Main Problem or Blocker

Write here if you are stuck with something.

- The AI component is still a preview and needs a more formal statistical or machine learning model.

## How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
```
## Project Structure
```bash
template-blockchain-dashboard/
|-- README.md
|-- requirements.txt
|-- .gitignore
|-- app.py
|-- api/
|   `-- blockchain_client.py
`-- modules/
    |-- m1_pow_monitor.py
    |-- m2_block_header.py
    |-- m3_difficulty_history.py
    `-- m4_ai_component.py
```

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
