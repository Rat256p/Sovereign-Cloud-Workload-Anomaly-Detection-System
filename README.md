# ☁️ Sovereign Cloud Workload Anomaly Detection System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red.svg)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.3+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**Simulating CrowdStrike Falcon's Cloud Workload Protection for India's Sovereign Cloud Security**

[Report Bug](https://github.com/Rat256p/sovereign-cloud-anomaly-detection/issues) · [Request Feature](https://github.com/Rat256p/sovereign-cloud-anomaly-detection/issues)

</div>

---

## 📌 Overview

This project implements a **production-grade sovereign cloud workload anomaly detection system** that simulates CrowdStrike Falcon's cloud workload protection capabilities. It detects security threats including data exfiltration, unauthorized access, and geo-fencing violations while mapping detections to India's sovereign compliance requirements for regulated sectors (BFSI, Government).

### 🎯 Why This Project?

| Challenge | Solution |
|-----------|----------|
| Legacy on-prem security can't detect cloud-native threats | ML-based anomaly detection for distributed cloud workloads |
| Data residency violations are hard to monitor | Automated geo-fencing & region compliance mapping |
| Manual compliance reporting is slow | Real-time violation detection with severity classification |
| Single-model detection has high false positives | Ensemble approach (Isolation Forest + Autoencoder) |

---

──┘


---

## 🚀 Key Results

| Metric | Value |
|--------|-------|
| **Total Events Processed** | 10,000+ |
| **Ensemble Detection Accuracy** | 76.32% |
| **Compliance Violations Identified** | 4,499+ |
| **Affected Workloads** | 3,546 |
| **Inference Latency** | <100ms per event |
| **Autoencoder Final Loss** | 0.0124 |

### Anomaly Distribution

| Anomaly Type | Count | Percentage |
|--------------|-------|------------|
| Data Exfiltration | 1,200 | 40% |
| Unauthorized Access | 1,000 | 33.3% |
| Geo-fencing Violation | 800 | 26.7% |

### Compliance Violations Breakdown

| Violation Type | Count | Severity |
|----------------|-------|----------|
| RBAC Violation | 2,632 | HIGH |
| ML Anomaly Detected | 2,500 | HIGH |
| Data Residency Violation | 800 | HIGH |
| Geo-fencing Violation | 800 | HIGH |
| Data Exfiltration Alert | 476 | HIGH |

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Machine Learning** | Scikit-learn (Isolation Forest), PyTorch (Autoencoder) |
| **Data Processing** | Pandas, NumPy |
| **Visualization** | Matplotlib, Seaborn |
| **Language** | Python 3.8+ |

---

## 📁 Project Structure
sovereign-cloud-anomaly-detection/
│
├── 📄 main_pipeline.py # Main execution pipeline
├── 📄 workload_generator.py # Synthetic workload event generator
├── 📄 anomaly_detector.py # Isolation Forest + Autoencoder models
├── 📄 compliance_mapper.py # Sovereign compliance mapping
├── 📄 requirements.txt # Dependencies
│
├── 📊 Outputs/
│ ├── sovereign_cloud_security_report.png # Visualization
│ ├── sovereign_cloud_detection_results.csv # Detection results
│ └── compliance_violations_report.csv # Compliance report
│
└── 📖 README.md # This file


---

## ⚡ Quick Start

### Prerequisites

```bash
Python 3.8 or higher
pip package manager

# Clone the repository
git clone https://github.com/Rat256p/sovereign-cloud-anomaly-detection.git
cd sovereign-cloud-anomaly-detection

# Install dependencies
pip install -r requirements.txt
