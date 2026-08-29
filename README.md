# V-Scribe: Structured Transcription of Vietnamese Speech for Digital Knowledge Management

[![Conference](https://img.shields.io/badge/FDSE-2025-blue.svg)](https://link.springer.com/chapter/10.1007/978-981-95-4721-0_23)
[![Publisher](https://img.shields.io/badge/Springer-CCIS_Vol_2708-orange.svg)](https://link.springer.com/book/9789819547203)
[![DOI](https://img.shields.io/badge/DOI-10.1007%2F978--981--95--4721--0__23-green.svg)](https://doi.org/10.1007/978-981-95-4721-0_23)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/PyTorch-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![Database](https://img.shields.io/badge/Supabase-pgvector-3ECF8E?logo=supabase&logoColor=white)](https://supabase.com/)

---

## 📌 Abstract & Overview

This repository contains the official implementation of the research paper: **"V-Scribe: Structured Transcription of Vietnamese Speech for Digital Knowledge Management"**, presented at the **12th International Conference on Future Data and Security Engineering (FDSE 2025)** and published in the **Springer Communications in Computer and Information Science (CCIS, volume 2708)** series.

**V-Scribe** addresses the challenge of digitizing, diarizing, and structuring Vietnamese conversational audio from corporate and academic meetings. The system introduces an end-to-end automated pipeline comprising sequential modules:
1. **Audio Preprocessing & Separation:** Denoising and audio stream isolation.
2. **Speaker Diarization:** Segmenting and identifying individual speakers across continuous conversational audio.
3. **Automated Speech-to-Text (STT):** High-accuracy Vietnamese phonetic transcription.
4. **Structured Knowledge & Semantic Search:** Storing structured dialogue data and text embeddings in Supabase (PostgreSQL with `pgvector`) for contextual multi-dimensional retrieval.

---

## 🏗️ System Architecture & Pipeline
[ Input Meeting Audio (.wav / .mp3) ]
│
▼
┌───────────────────────┐
│  Speaker Diarization  │ ──► (Pyannote / PyTorch Pipeline)
└───────────────────────┘
│
▼
┌───────────────────────┐
│ Vietnamese Speech-2-Text│ ──► (Segmented Transcript Generation)
└───────────────────────┘
│
▼
┌───────────────────────┐
│ Structured Formatting │ ──► (Timeline, Speaker IDs, Metadata)
└───────────────────────┘
│
▼
┌───────────────────────┐
│  Supabase Cloud DB    │ ──► (PostgreSQL + pgvector Semantic Search)
└───────────────────────┘
---

## ✨ Key Features

- **Automated Vietnamese Transcription:** Optimized acoustic and language processing specifically tuned for Vietnamese speech characteristics and meeting dynamics.
- **Timeline-based Speaker Attribution:** Automatically separates dialogue turn-by-turn with timestamps and speaker labels.
- **Multi-Dimensional Semantic Search:** Integrates vector similarity retrieval enabling semantic querying beyond conventional keyword matching.
- **Serverless Cloud Integration:** Direct synchronization with Supabase for scalable structured storage, system logging, and session scanning.

---

## 📂 Project Structure

```bash
├── Audio Mind.py                  # Main application entry point
├── upload_file_window.py          # Audio upload & batch preprocessing module
├── transcript_result_window.py   # Diarization & transcription viewer UI
├── search_window.py               # Semantic and timeline search module
├── system_log.py                  # Audit trails and execution logger
├── ui_kit.py                      # UI components and styling utilities
├── requirements.txt               # Project dependencies and model packages
└── README.md                      # Academic documentation & reproduction guide
🚀 Getting Started
Prerequisites
Python >= 3.10

CUDA-compatible GPU recommended for accelerated PyTorch audio inferencing.

Supabase account with configured database credentials.

Installation
1. Clone the repository:
git clone [https://github.com/sh1kaku59/scientific-and-technological-research.git](https://github.com/sh1kaku59/scientific-and-technological-research.git)
cd scientific-and-technological-research
2. Create and activate a virtual environment:
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
3. Install dependencies:
pip install -r requirements.txt

Running the Application
Launch the desktop workflow and transcription interface:
python "Audio Mind.py"

📖 Citation
If you find this research or code useful in your academic work, please cite our paper published in Springer CCIS:
@inproceedings{vscribe_fdse2025,
  title={V-Scribe: Structured Transcription of Vietnamese Speech for Digital Knowledge Management},
  author={Huynh, Huu Nghia and Nhan, Minh Duc and Phan, Van Bao and Nguyen, Vu Huy and Vu, Ngoc Minh},
  booktitle={Future Data and Security Engineering (FDSE 2025)},
  series={Communications in Computer and Information Science},
  volume={2708},
  pages={340--354},
  year={2025},
  publisher={Springer Nature Singapore},
  doi={10.1007/978-981-95-4721-0_23}
}

👥 Authors & Contributions
Ngoc Minh Vu (Co-Author) – GitHub | LinkedIn | Email

Research Team: Huu Nghia Huynh, Minh Duc Nhan, Van Bao Phan, Vu Huy Nguyen.

Affiliation: Faculty of Information Technology, Van Lang University, Ho Chi Minh City, Vietnam.
