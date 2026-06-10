import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler
import joblib
import os

# Configuration
MODEL_PATH = "ml/isolation_forest.joblib"
SCALER_PATH = "ml/scaler.gz"
DATA_PATH = "ml/historical_data.csv"
CONTAMINATION = 0.05

def train_model():
    print("--- Starting MULTI-VARIATE Anomaly Model Training (Temp + Vib) ---")
    
    if not os.path.exists(DATA_PATH):
        print(f"Error: {DATA_PATH} not found. Please run extract_minio.py first.")
        return

    # 1. Data Preparation
    df = pd.read_csv(DATA_PATH)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Pivot the data to have columns for each sensor type
    # We group by timestamp and machine_id to align Temp and Vib readings
    pivot_df = df.pivot_table(
        index=['timestamp', 'machine_id'], 
        columns='type_capteur', 
        values='valeur'
    ).reset_index()
    
    # Drop rows where we don't have both readings (alignment)
    pivot_df = pivot_df.dropna(subset=['temperature', 'vibration'])
    pivot_df = pivot_df.sort_values('timestamp')

    print(f"Aligned {len(pivot_df)} records with both Temperature and Vibration.")

    # 2. Feature Engineering: [Temp, Vib, Temp_Mean, Vib_Mean]
    # We capture the state of both sensors and their local averages
    pivot_df['temp_mean'] = pivot_df['temperature'].rolling(window=5).mean()
    pivot_df['vib_mean'] = pivot_df['vibration'].rolling(window=5).mean()
    pivot_df = pivot_df.dropna()

    features_cols = ['temperature', 'vibration', 'temp_mean', 'vib_mean']
    features = pivot_df[features_cols].values

    # 3. Scaling
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_features = scaler.fit_transform(features)
    joblib.dump(scaler, SCALER_PATH)
    print(f"Scaler saved to {SCALER_PATH}")

    # 4. Isolation Forest Training
    model = IsolationForest(
        n_estimators=100,
        contamination=CONTAMINATION,
        random_state=42,
        verbose=1
    )
    
    print(f"Fitting Isolation Forest on {features_cols}...")
    model.fit(scaled_features)

    # 5. Save Model
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

    # 6. Evaluation
    preds = model.predict(scaled_features)
    anomalies_count = (preds == -1).sum()
    print(f"Training Complete. Detected {anomalies_count} multi-variate anomalies ({anomalies_count/len(preds)*100:.2f}%).")

if __name__ == "__main__":
    train_model()
