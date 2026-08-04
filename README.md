<div align="center">

# 🌊 Wave Sense
### Smart Marine Boat Tracking & Safety Assistance System

**AI that watches the water — so fishermen don't have to gamble with it.**

[![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Scikit--Learn-green?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](#-license)

[Overview](#-overview) • [Features](#-features) • [Architecture](#%EF%B8%8F-project-architecture) • [Install](#-installation) • [Roadmap](#-future-enhancements)

</div>

---

## ⚓ Why Wave Sense?

Every year, fishermen head out to sea with nothing but instinct and hope that the weather holds. A sudden storm, a misjudged swell, an unseen risk — and a routine trip turns into a tragedy.

**Wave Sense exists to close that gap.**

It's an AI-powered marine safety platform that helps fishermen and marine authorities monitor boat activity, predict dangerous weather conditions *before* they hit, and make one simple question answerable in seconds:

> *"Is it safe to go out today?"*

---

## 📖 Overview

Wave Sense combines **Machine Learning**, **weather prediction**, and **real-time monitoring** into a single, easy-to-use safety system. Instead of guessing, fishermen get a data-backed risk assessment — powered by a trained model that learns from real marine weather patterns — delivered through a clean, interactive dashboard.

At its core, the project answers one critical question before every voyage: **is the sea safe today?**

---

## ✨ Features

| | Feature | What it does |
|---|---------|---------------|
| 🚤 | **Boat Tracking Dashboard** | Central view of boat activity and status |
| 🌦️ | **Weather Safety Prediction (ML)** | Predicts safe vs. risky conditions using a trained model |
| ⚠️ | **Instant Weather Risk Alerts** | Flags dangerous conditions before departure |
| 📊 | **Interactive Streamlit Dashboard** | Clean, visual, no-code-required interface |
| 🔐 | **Secure User Authentication** | Keeps access controlled and safe |
| 📈 | **Data Visualization** | Turns raw marine data into readable insight |
| ⚡ | **FastAPI Backend** | Fast, lightweight, production-ready API layer |
| 💾 | **Trained ML Model Integration** | Pre-trained `.pkl` models ready to serve predictions |
| 📱 | **User-Friendly Interface** | Built for real users, not just developers |

---

## 🏗️ Project Architecture

```
                Marine Weather Dataset
                         │
                         ▼
               Data Preprocessing
                         │
                         ▼
            Machine Learning Model
                         │
         ┌───────────────┴───────────────┐
         ▼                               ▼
 Weather Safety Prediction        Model Storage
         │                               │
         └───────────────┬───────────────┘
                          ▼
                  FastAPI Backend
                         │
                         ▼
               Streamlit Dashboard
                         │
                         ▼
                     End User
```

Raw marine data flows in, gets cleaned and modeled, and comes out the other end as a clear, human-readable safety signal — right on the dashboard.

---

## 📂 Project Structure

```
Wave-Sense/
│
├── dashboard/
│   └── Streamlit Dashboard
│
├── data/
│   ├── sonar.csv
│   ├── sst_easy.csv
│   └── weather dataset
│
├── models/
│   ├── fish_presence_model.pkl
│   └── weather_alert_model.pkl
│
├── src/
│   ├── preprocessing.py
│   ├── training.py
│   ├── prediction.py
│   └── utils.py
│
├── app.py
├── requirements.txt
└── README.md
```

---

## 🧠 Machine Learning Workflow

```
1. Collect marine weather datasets
2. Clean and preprocess data
3. Train Machine Learning models
4. Evaluate model performance
5. Save trained models
6. Deploy with FastAPI
7. Build interactive dashboard using Streamlit
```

Each stage feeds the next — from raw, messy marine data to a live, queryable safety prediction.

---

## 🛠️ Tech Stack

| Category | Technologies |
|----------|--------------|
| 🐍 Programming | Python |
| 🤖 Machine Learning | Scikit-Learn |
| 🧹 Data Processing | Pandas, NumPy |
| 📊 Visualization | Matplotlib |
| ⚡ Backend | FastAPI |
| 🎨 Frontend | Streamlit |
| 💾 Model Storage | Joblib |
| 🗂️ Version Control | Git & GitHub |

---

## 📊 Dataset

Wave Sense is trained on real marine-related data:

- 🔊 **Sonar Dataset** — underwater signal readings
- 🌡️ **Sea Surface Temperature Dataset** — ocean temperature trends
- ☁️ **Weather Dataset** — atmospheric and marine conditions

All datasets are cleaned, processed, and fed into the prediction pipeline to power accurate weather-safety classification.

---

## 🚀 Installation

**1. Clone the repository**
```bash
git clone https://github.com/abbascse2023/wave-sense-project.git
```

**2. Move into the project**
```bash
cd wave-sense-project
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Run the FastAPI backend**
```bash
uvicorn app:app --reload
```

**5. Run the Streamlit dashboard**
```bash
streamlit run dashboard/app.py
```

That's it — you're up and running. 🎉

---

## 📈 Model Performance

The Weather Alert Prediction model was trained using supervised Machine Learning techniques, with a focus on real-world reliability rather than just benchmark scores.

**Performance highlights:**
- ✅ High prediction accuracy
- ⚡ Fast inference time
- 🎯 Reliable weather risk classification
- 🔧 Optimized preprocessing pipeline

---

## 📸 Screenshots

### 🖥️ Command Center — Home Dashboard
The mission control view: live system status, last risk level, and quick access to every module.

![Command Center](screenshots/01-command-center.png)

---

### 🌦️ Weather Safety Prediction — Inputs
Feed in live or manual sensor readings (temperature, wind, dew point, visibility, pressure, etc.) to generate a prediction.

![Weather Safety Inputs](screenshots/02-weather-inputs.png)

### ⚠️ Weather Safety Prediction — Result
The model returns a clear verdict, a confidence score, a risk meter, and an emergency checklist when conditions turn dangerous.

![Weather Safety Result](screenshots/03-weather-result.png)

---

### 🎯 Fishing Hotspot Zone
Uses Sea Surface Temperature (SST) to estimate fishing potential and pairs it with decision-support guidance.

![Fishing Hotspot Zone](screenshots/04-hotspot-zone.png)

### 📊 Hotspot Zone Meter — Result
A simple zone meter and suggested action, so users know exactly where and when to fish.

![Hotspot Zone Result](screenshots/05-hotspot-result.png)

---

### 🛰️ Boat Tracking — Live Map
Real-time GPS position on an interactive map, with geofence status to confirm the boat is within a safe boundary.

![Boat Tracking](screenshots/06-boat-tracking.png)

### 🆘 SOS / Share GPS
One-tap emergency sharing — broadcasts live coordinates to the shore team and logs the SOS event with timestamp and reason.

![SOS Share GPS](screenshots/07-sos-share.png)

---

## 🎯 Future Enhancements

- [ ] 🌍 Live GPS Boat Tracking
- [ ] 📡 Real-Time Weather API Integration
- [ ] ☁️ Cloud Deployment
- [ ] 📱 Mobile Application
- [ ] 🛰️ Satellite Weather Support
- [ ] 🔔 SMS & Email Alert System

---

## 👨‍💻 Author

**Abbas**
Computer Science Engineering Student

[![GitHub](https://img.shields.io/badge/GitHub-abbascse2023-181717?style=flat-square&logo=github)](https://github.com/abbascse2023)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Add%20Profile-0A66C2?style=flat-square&logo=linkedin)](#)

---

## ⭐ Support This Project

If Wave Sense helped you, sparked an idea, or you just believe in tech that keeps fishermen safer — consider giving it a ⭐ on GitHub.

It costs nothing and means everything for a student building real-world AI projects. 🙏

---

## 📄 License

This project is licensed under the **MIT License**.

<div align="center">

**Built with 🌊 and 🤖 to make the sea a little safer.**

</div>
