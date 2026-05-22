# Technical Report: Raffinerie IoT - Predictive Intelligence Pipeline
## Project Evolution & Engineering Journey (May 2026)

### 1. Architectural Overview
The goal of this project was to build a complete industrial IoT pipeline capable of simulating refinery sensors, processing massive data streams in real-time, and using Artificial Intelligence to anticipate equipment failure.

**The Stack:**
*   **Ingestion:** Python Simulator -> MQTT (Mosquitto) -> Kafka.
*   **Processing:** Apache Spark Structured Streaming (Real-time filtering & KPI calculation).
*   **Storage:** TimescaleDB (Structured/Relational) & MinIO (Object/Raw Data Lake).
*   **Visualization:** Grafana & Custom HTML/JS Dashboard.
*   **Control Center:** FastAPI Backend.

---

### 2. Phase 1: Pipeline Construction & The "Automation Fix"
Initially, the pipeline was constructed as separate blocks. We encountered a major synchronization hurdle: **Spark-Job execution.**

*   **The Problem:** Running the Spark processing script manually in a terminal was error-prone and caused data gaps. Furthermore, data wasn't appearing in Grafana because the manual bridge between Kafka and the Database was unstable.
*   **The Fix (Docker Integration):** We refactored the architecture to include the `spark-job` directly in the `docker-compose.yml`. 
    *   **How we did it:** We created a custom Dockerfile for Spark that pre-installs the necessary JARs (`spark-sql-kafka`, `postgresql-driver`, `hadoop-aws`). We then added a service to the Compose file that automatically runs `spark-submit` on container startup.
    *   **Result:** The pipeline became "Zero-Touch." Running `docker-compose up` now starts the entire brain of the system automatically, ensuring consistent data flow to TimescaleDB and Grafana.

---

### 3. Phase 2: The ML Journey – From Prediction to Detection

#### Initial Approach: The Stacked LSTM
We originally chose a **Stacked LSTM (Long Short-Term Memory)** neural network. LSTMs are designed for **temporal sequences**, where the goal is to predict the next value based on past patterns.

*   **Why it didn't work:** Although our data has a temporal timestamp, the **Simulator** generates values using `random.uniform()`. In mathematics, this is "High Entropy" data—it has no repeating pattern or trend to learn. 
*   **The Difficulty:** The LSTM tried to find a pattern where none existed. It eventually "gave up" and started predicting the mathematical mean (a flat line). This made it useless for detecting anomalies because every real fluctuation was treated as a "prediction error."

#### The Pivot: Isolation Forest (The Definitive Model)
To solve this, we moved from "Sequence Prediction" to **"Spatial Outlier Detection."** We chose the **Isolation Forest** as our definitive model.

*   **Why Isolation Forest?** Instead of guessing what happens next, it looks at the current state (Temperature + Vibration) and asks: *"How easy is it to isolate this point from the thousands of normal points I've seen?"* 
*   **Multi-Variate Integration:** We trained the model on **36,221 paired records** (Temp + Vib) from a 1-hour high-volume data run. The AI now understands the relationship between layers: it knows that high vibration is only "normal" at specific temperature ranges.
*   **Efficiency:** It is computationally lightweight, executes in milliseconds, and is incredibly robust against the random noise of our simulator.

---

### 4. Phase 3: The Control Center & Web UI
We built a custom Web Dashboard to bridge the gap between the complex backend and a human operator.

#### Functionality:
*   **Real-Time Visualization:** Two charts using **Dual Y-Axes**. This allows us to show Temperature (0-200), Vibration (0-6), and the AI Anomaly Score (-1 to 1) on the same screen without losing scale detail.
*   **Live Alert Console:** A scrolling log that translates raw AI scores into human-readable warnings: `Score: -0.084 | T: 195.2 V: 4.85`.
*   **AI Safety Reference:** A panel that displays the "Normal" operating boundaries (derived from our 125k-point training run) so the user knows exactly why an alert was triggered.

#### Real-Time Configuration:
The UI features a "Command" panel that allows the user to:
1.  **Scale the Network:** Dynamically change the number of machines being simulated.
2.  **Tune the AI:** Adjust the `ml_threshold`. This acts as a "Sensitivity Knob," allowing the operator to make the AI more or less "suspicious" of fluctuations in real-time via a `config.json` bridge.

---

### 5. Conclusion
The project has evolved from a basic data pipeline into a sophisticated **Explainable AI system.** By pivoting from the predictive LSTM to the multi-variate Isolation Forest, we successfully built a system that handles high-entropy industrial data with professional accuracy and provides an intuitive interface for real-world refinery management.
