# 🛡️ Security Flow Agent

A lightweight backend service that analyzes Windows event logs, detects suspicious patterns, and produces both structured summaries and human-readable security insights.  
Built with **FastAPI**, **Python**, and an extensible **AI-ready agent** layer.

---

## 🔍 Features

| Feature             | Description                                                     |
|---------------------|-----------------------------------------------------------------|
| **Log Ingestion**    | Converts structured Windows logs (CSV) into normalized JSON.    |
| **Rule-Based Analysis** | Extracts top Event IDs, frequency patterns, and anomalies.     |
| **Incident Detection Engine** | Flags issues like event dominance, unknown sources, or abnormal patterns. |
| **LLM-Ready Explanation Layer** | Generates natural-language summaries (with fallback if no API key). |
| **FastAPI Backend**  | Fully documented API with interactive Swagger UI.               |

---

## 🔌 API Endpoints

| Endpoint                             | Method | Description                                         |
|--------------------------------------|--------|-----------------------------------------------------|
| `/health`                             | GET    | Service status check.                               |
| `/logs/sample?limit=50`              | GET    | Preview log entries from the dataset.               |
| `/analyze?limit=200`                 | POST   | Runs full analysis: summary, incidents, AI explanation. |
| `/event/template/{event_id}`         | GET    | Returns template text for a specific EventId (e.g., `E36`). |

---

## 📚 Dataset Source (Required Citation)

This project uses the **Windows 2k** log dataset provided by **LogPai / LogHub**,  
a widely-used benchmark for system log parsing and anomaly detection.

**LogHub Repository:**  
https://github.com/logpai/loghub

### Dataset files used
- `Windows_2k.log_structured.csv`  
- `Windows_2k.log_templates.csv`

### 📄 Citation
He et al., *“LogHub: A Large Collection of System Log Datasets for AI-driven Log Analytics,”* 2020.  
https://github.com/logpai/loghub


