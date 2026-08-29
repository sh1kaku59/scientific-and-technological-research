# V-Scribe: Structured Transcription of Vietnamese Speech for Digital Knowledge Management

[![Conference](https://img.shields.io/badge/FDSE-2025-blue.svg)](https://link.springer.com/chapter/10.1007/978-981-95-4721-0_23)
[![Publisher](https://img.shields.io/badge/Springer-CCIS_Vol_2708-orange.svg)](https://link.springer.com/book/9789819547203)
[![DOI](https://img.shields.io/badge/DOI-10.1007%2F978--981--95--4721--0__23-green.svg)](https://doi.org/10.1007/978-981-95-4721-0_23)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/PyTorch-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![ASR Model](https://img.shields.io/badge/PhoWhisper-Large-yellow.svg)](https://huggingface.co/vinai/PhoWhisper-large)
[![Database](https://img.shields.io/badge/Supabase-pgvector-3ECF8E?logo=supabase&logoColor=white)](https://supabase.com/)

---

## 📌 Abstract & Research Overview

This repository contains the official implementation of the research paper: **"V-Scribe: Structured Transcription of Vietnamese Speech for Digital Knowledge Management"**, presented at the **12th International Conference on Future Data and Security Engineering (FDSE 2025)** and published in the **Springer Communications in Computer and Information Science (CCIS, volume 2708)** series.

**V-Scribe** provides an automated, end-to-end framework tailored for conversational Vietnamese meeting intelligence. The system overcomes the challenges of low-resource tonal language processing, overlapping dialogue, and speaker attribution by decomposing the task into a multi-stage modular pipeline:

1. **Voice Separation & Diarization:** Segmenting multi-speaker audio streams into homogeneous speaker-attributed chunks using neural sequence models.
2. **Speaker Recognition & Profiling:** Building L2-normalized acoustic speaker embeddings and performing cosine similarity matching against reference prototypes.
3. **Vietnamese Speech-to-Text (ASR):** High-precision transcription using fine-tuned transformer architectures (`PhoWhisper-large`).
4. **Cloud Persistence & Knowledge Retrieval:** Synchronizing transcripts and segmented metadata to Supabase Cloud for vector semantic indexing and multi-criteria desktop querying.

---

## 🏗️ System Architecture

```text
[ Multi-Speaker Audio (.wav / .mp3) + Config JSON ]
                        │
                        ▼ (30s Polling Loop)
┌─────────────────────────────────────────────────────────┐
│ Module 1: Diarization & Speaker Profiling               │
│ • Pyannote Diarization 3.1 (VAD, SCD, OSD, VBx Cluster) │
│ • ECAPA-TDNN Embedding & Cosine Similarity Matching     │
│ • Intra-segment refinement (min_silence_len = 185ms)    │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│ Module 2: Automatic Speech Recognition (ASR)            │
│ • vinai/PhoWhisper-large (FP16 GPU / CPU batch infer)   │
│ • Text post-processing: casing, diacritic normalization │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│ Module 3: Cloud Persistence & Data Structuring          │
│ • Supabase Storage: Segmented Audio Files (.wav)        │
│ • Relational DB: `transcripts` & `transcript_segments`  │
│ • Local export: transcript.txt / JSON / DOCX            │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│ Module 4: Desktop Search Engine & Log Viewer            │
│ • Meeting ID, Date, and Speaker-based filtering         │
│ • Interactive playback synchronization with transcript  │
└─────────────────────────────────────────────────────────┘
```

---

## ✨ Core Components & Methodology

* **Speaker Profiling & Diarization (`pyannote/speaker-diarization-3.1`):** Audio is normalized to 16 kHz mono. Energy-based silence detection filters non-speech regions (`min_silence_len=150ms`, `silence_thresh=-40dBFS`). Speaker prototypes are built via mean-pooled L2-normalized embedding vectors.
* **Vietnamese ASR (`vinai/PhoWhisper-large`):** Leverages an encoder-decoder Transformer fine-tuned on 844 hours of Vietnamese speech across diverse regional accents. Processes 80-channel log-mel spectrograms with batch chunk inference.
* **Serverless Polling Architecture:** Operates on an automated loop polling Supabase buckets for `*.config.json` session files, providing a decoupled execution workflow.
* **Desktop Workstation UI:** Tkinter-based interactive GUI featuring file upload, batch session processing, synchronized audio playback, system log auditing, and transcript export (TXT, JSON, DOCX).

---

## 📊 Experimental Results

The framework was evaluated on both controlled conversational datasets (collected via Microsoft Teams) and real-world YouTube discussion recordings using NIST standard metrics:

* **Diarization Error Rate (DER):** **15.8%** (Speaker Confusion: 3.8s, Missed Speech: 2.0s, False Alarms: 2.7s across 53.9s benchmark).
* **Word Error Rate (WER):** **46.2%** on unconstrained conversational Vietnamese meetings (characterizing typical challenges in informal particles, overlap, and regional tone preservation).

---

## 📂 Project Structure

```text
├── Audio Mind.py                  # Main application entry point & GUI coordinator
├── upload_file_window.py          # Audio upload & session config (.json) generator
├── transcript_result_window.py   # Interactive transcript viewer & audio playback
├── search_window.py               # Meeting search engine (Session ID, Date, Speaker)
├── system_log.py                  # System execution logger & audit trail viewer
├── ui_kit.py                      # Reusable Tkinter UI widgets and styling
├── requirements.txt               # Dependencies (PyTorch, Transformers, Pyannote, Supabase)
└── README.md                      # Academic documentation & reproduction guide
```

---

## 🚀 Getting Started

### Prerequisites

- Python `>= 3.10`
- NVIDIA GPU with CUDA support (recommended for accelerated PhoWhisper & Pyannote inference)
- Supabase project credentials (URL & Service Key)

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/sh1kaku59/scientific-and-technological-research.git](https://github.com/sh1kaku59/scientific-and-technological-research.git)
   cd scientific-and-technological-research
   ```

2. **Create and activate virtual environment:**
   ```bash
   # Windows:
   python -m venv venv
   venv\Scripts\activate

   # Linux / macOS:
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

Launch the desktop workflow and transcription interface:
```bash
python "Audio Mind.py"
```

---

## 📖 Citation

If you use this research or codebase in your academic work, please cite our Springer publication:

```bibtex
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
```

---

## 👥 Authors & Affiliation

- **Authors:** Huu Nghia Huynh, Minh Duc Nhan, Van Bao Phan, Vu Huy Nguyen, **Ngoc Minh Vu (Co-Author)**[cite: 6].
- **Contact:** [wanbitido090@gmail.com](mailto:wanbitido090@gmail.com) | [LinkedIn Profile](https://linkedin.com/in/vungocminh9702)[cite: 4]
- **Affiliation:** Faculty of Information Technology & Faculty of Mechanical - Electrical and Computer Engineering, Van Lang University, Ho Chi Minh City, Vietnam[cite: 6].
