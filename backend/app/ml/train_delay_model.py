"""
XGBoost Delay Prediction Model Training Script
==============================================
Trains an XGBoost regression pipeline to predict Indian Railways arrival delays.

Features Used:
  - train_type: RAJDHANI, VANDE_BHARAT, SUPERFAST, EXPRESS, etc.
  - railway_zone: NR, NCR, WR, CR, SR, ER, etc.
  - month: 1-12 (Captures winter fog in North & monsoon rain in West)
  - day_of_week: 0-6
  - scheduled_hour: 0-23
  - distance_km: Distance traveled from source station
  - halt_minutes: Scheduled halt time at station

Outputs:
  - app/ml/models/delay_predictor.joblib (Trained scikit-learn Pipeline)

Usage:
  python -m app.ml.train_delay_model
"""

import os
import random
from datetime import date, timedelta
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBRegressor

from app.config import get_settings

settings = get_settings()

RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

TRAIN_TYPES = [
    "RAJDHANI", "VANDE_BHARAT", "SHATABDI", "DURONTO",
    "SUPERFAST", "EXPRESS", "MAIL", "PASSENGER"
]

RAILWAY_ZONES = [
    "NR", "NCR", "NER", "NWR", "ER", "ECR", "ECoR",
    "SER", "SECR", "WR", "WCR", "CR", "SR", "SCR", "SWR", "NFR", "KR"
]

DELAY_PROFILES = {
    "RAJDHANI":     {"mean": 8,  "std": 6},
    "VANDE_BHARAT": {"mean": 5,  "std": 4},
    "SHATABDI":     {"mean": 10, "std": 7},
    "DURONTO":      {"mean": 12, "std": 8},
    "SUPERFAST":    {"mean": 15, "std": 12},
    "EXPRESS":      {"mean": 25, "std": 18},
    "MAIL":         {"mean": 30, "std": 20},
    "PASSENGER":    {"mean": 40, "std": 25},
}

HOLIDAYS = {
    (1, 26), (3, 8), (8, 15), (10, 2), (11, 1), (11, 14), (12, 25),
    (1, 1), (1, 14), (3, 29), (4, 14), (5, 1), (10, 24), (10, 31),
}


def generate_training_data(num_samples: int = 50000) -> pd.DataFrame:
    """
    Generate a high-fidelity synthetic dataset matching Indian Railways operational
    delays across different seasons, zones, and train categories.
    """
    records = []
    today = date.today()

    train_weights = [0.08, 0.07, 0.08, 0.06, 0.30, 0.31, 0.06, 0.04]
    zone_weights = [
        0.18, 0.12, 0.06, 0.05, 0.08, 0.06, 0.04,
        0.04, 0.03, 0.12, 0.04, 0.08, 0.06, 0.05, 0.04, 0.03, 0.02
    ]

    for _ in range(num_samples):
        train_type = random.choices(TRAIN_TYPES, weights=train_weights, k=1)[0]
        zone = random.choices(RAILWAY_ZONES, weights=zone_weights, k=1)[0]

        days_ago = random.randint(1, 365)
        record_date = today - timedelta(days=days_ago)
        month = record_date.month
        day_of_week = record_date.weekday()

        scheduled_hour = random.randint(0, 23)
        halt_minutes = random.choice([2, 3, 5, 10, 15, 20])
        distance_km = random.randint(50, 2400)

        profile = DELAY_PROFILES[train_type]
        base_delay = random.gauss(profile["mean"], profile["std"])

        # Distance accumulation effect (longer distance trains accumulate slight variance)
        distance_factor = 1.0 + (distance_km / 3000.0) * 0.25

        # Seasonal multiplier (fog in winter North, rain in monsoon West/South)
        seasonal_multiplier = 1.0
        if month in (12, 1) and zone in ("NR", "NCR", "NER", "NWR"):
            seasonal_multiplier = 1.45  # Winter fog
        elif month in (7, 8, 9) and zone in ("WR", "CR", "SR", "KR"):
            seasonal_multiplier = 1.30  # Monsoon
        elif month in (4, 5) and zone in ("NR", "NCR", "WR"):
            seasonal_multiplier = 1.10  # Summer heat

        # Peak hours congestion (08:00-11:00 and 17:00-21:00)
        time_factor = 1.0
        if scheduled_hour in (8, 9, 10, 17, 18, 19, 20):
            time_factor = 1.15

        # Holiday multiplier
        if (month, record_date.day) in HOLIDAYS:
            seasonal_multiplier *= 1.15

        calculated_delay = base_delay * distance_factor * seasonal_multiplier * time_factor
        delay = int(round(calculated_delay))
        delay = max(-5, delay)  # Max 5 min early arrival

        records.append({
            "train_type": train_type,
            "railway_zone": zone,
            "month": month,
            "day_of_week": day_of_week,
            "scheduled_hour": scheduled_hour,
            "distance_km": distance_km,
            "halt_minutes": halt_minutes,
            "delay_minutes": delay,
        })

    return pd.DataFrame(records)


import sys
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def train_model() -> Pipeline:
    """
    Train and evaluate the XGBoost delay regression pipeline.
    """
    print("=" * 60)
    print("SmartRail -- Training XGBoost Delay Prediction Model")
    print("=" * 60)

    print("\n1. Generating training dataset (~50,000 records)...")
    df = generate_training_data(50000)
    print(f"   [OK] Generated {len(df):,} samples across {len(TRAIN_TYPES)} train types and {len(RAILWAY_ZONES)} zones.")

    categorical_features = ["train_type", "railway_zone"]
    numerical_features = ["month", "day_of_week", "scheduled_hour", "distance_km", "halt_minutes"]

    X = df[categorical_features + numerical_features]
    y = df["delay_minutes"]

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_SEED
    )

    print("\n2. Building Feature Transformation & XGBoost Pipeline...")
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features),
            ("num", StandardScaler(), numerical_features),
        ]
    )

    model = XGBRegressor(
        n_estimators=180,
        max_depth=5,
        learning_rate=0.08,
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=RANDOM_SEED,
        n_jobs=-1,
    )

    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("regressor", model),
    ])

    print("3. Fitting XGBoost Regressor...")
    pipeline.fit(X_train, y_train)

    print("\n4. Evaluating Model Performance...")
    y_pred_train = pipeline.predict(X_train)
    y_pred_val = pipeline.predict(X_val)

    train_mae = mean_absolute_error(y_train, y_pred_train)
    val_mae = mean_absolute_error(y_val, y_pred_val)
    val_rmse = np.sqrt(mean_squared_error(y_val, y_pred_val))
    val_r2 = r2_score(y_val, y_pred_val)

    print(f"   Train MAE: {train_mae:.2f} minutes")
    print(f"   Val MAE:   {val_mae:.2f} minutes")
    print(f"   Val RMSE:  {val_rmse:.2f} minutes")
    print(f"   Val R2:    {val_r2:.4f}")

    # Output artifact directory
    output_dir = Path("app/ml/models")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "delay_predictor.joblib"

    print(f"\n5. Saving trained model artifact to: {output_path}")
    joblib.dump(pipeline, output_path)
    print(f"   [OK] Model successfully saved ({os.path.getsize(output_path) / 1024:.1f} KB)")

    # Test sample predictions
    print("\n6. Sample Test Predictions:")
    sample_tests = [
        {"train_type": "RAJDHANI", "railway_zone": "NR", "month": 12, "day_of_week": 0, "scheduled_hour": 9, "distance_km": 1400, "halt_minutes": 10},
        {"train_type": "EXPRESS", "railway_zone": "NR", "month": 12, "day_of_week": 0, "scheduled_hour": 9, "distance_km": 1400, "halt_minutes": 10},
        {"train_type": "VANDE_BHARAT", "railway_zone": "SR", "month": 6, "day_of_week": 2, "scheduled_hour": 14, "distance_km": 500, "halt_minutes": 3},
        {"train_type": "PASSENGER", "railway_zone": "CR", "month": 8, "day_of_week": 5, "scheduled_hour": 18, "distance_km": 150, "halt_minutes": 2},
    ]

    sample_df = pd.DataFrame(sample_tests)
    preds = pipeline.predict(sample_df)
    for sample, pred in zip(sample_tests, preds):
        print(f"   * {sample['train_type']:<13} ({sample['railway_zone']}, Month {sample['month']}) -> Predicted Delay: {int(round(pred)):>2} mins")

    print("\n[SUCCESS] Training Complete!")
    return pipeline


if __name__ == "__main__":
    train_model()
