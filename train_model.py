import os
import sys
import time
import json
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report, confusion_matrix

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

def train_activity_and_fall_model():
    print("=================================================================")
    print("        Post-Operative Activity & Fall Classifier Training       ")
    print("=================================================================")
    
    data_path = Path("dataset/CompleteDataSet.csv")
    if not data_path.exists():
        print(f"Error: Dataset not found at {data_path}")
        return

    print(f"\n[1/5] Loading Dataset from '{data_path}'...")
    t0 = time.time()
    
    # Read headers
    with open(data_path, "r") as f:
        h1 = f.readline().strip().split(",")
        h2 = f.readline().strip().split(",")

    cols = []
    cur = ""
    for i, (name, unit) in enumerate(zip(h1, h2)):
        if name:
            cur = name
        suffix = f"_{unit}" if unit else ""
        cols.append(f"{cur}_{i}{suffix}")

    cols[-4] = "Subject"
    cols[-3] = "Activity"
    cols[-2] = "Trial"
    cols[-1] = "Tag"

    df = pd.read_csv(data_path, skiprows=2, header=None, names=cols, low_memory=False)
    print(f"Loaded {len(df):,} rows and {len(df.columns)} columns in {time.time() - t0:.2f}s")

    # Sensor feature columns
    feature_cols = [c for c in cols if c not in ["TimeStamps_0", "Subject", "Activity", "Trial", "Tag"]]
    print(f"Features: {len(feature_cols)} sensor channels (Ankle, Pocket, Belt, Neck, Wrist Accelerometers/Gyros/IR)")

    for c in feature_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    clean_df = df.dropna(subset=feature_cols + ["Activity"])
    X = clean_df[feature_cols].values
    y = clean_df["Activity"].values.astype(int)

    classes = np.unique(y)
    print(f"Target Classes ({len(classes)} activities): {classes.tolist()}")

    print("\n[2/5] Splitting Train / Test (80% Train, 20% Test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"Training Samples: {len(X_train):,} | Test Samples: {len(X_test):,}")

    print("\n[3/5] Training HistGradientBoosting Classifier (150 trees)...")
    t_train = time.time()
    
    clf = HistGradientBoostingClassifier(
        max_iter=150,
        learning_rate=0.1,
        max_leaf_nodes=31,
        random_state=42
    )
    clf.fit(X_train, y_train)
    train_time = time.time() - t_train
    print(f"Model Training Completed in {train_time:.2f}s")

    print("\n[4/5] Evaluating Model on Test Dataset...")
    y_pred = clf.predict(X_test)

    # Accuracy Metrics
    test_accuracy = accuracy_score(y_test, y_pred)
    train_accuracy = clf.score(X_train, y_train)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="weighted")

    print("\n-----------------------------------------------------------------")
    print(f">> TEST SET ACCURACY:      {test_accuracy * 100:.2f}%")
    print(f">> TRAIN SET ACCURACY:     {train_accuracy * 100:.2f}%")
    print(f">> WEIGHTED PRECISION:     {precision * 100:.2f}%")
    print(f">> WEIGHTED RECALL:        {recall * 100:.2f}%")
    print(f">> WEIGHTED F1-SCORE:      {f1 * 100:.2f}%")
    print("-----------------------------------------------------------------")

    print("\nDetailed Per-Activity Classification Report:")
    report = classification_report(y_test, y_pred, digits=4)
    print(report)

    # Binary Fall Detection Accuracy (Activities 1-5 = Falls, 6-11 = Normal Activities)
    y_test_binary = np.isin(y_test, [1, 2, 3, 4, 5]).astype(int)
    y_pred_binary = np.isin(y_pred, [1, 2, 3, 4, 5]).astype(int)
    fall_accuracy = accuracy_score(y_test_binary, y_pred_binary)
    fall_p, fall_r, fall_f1, _ = precision_recall_fscore_support(y_test_binary, y_pred_binary, average="binary")
    
    print("-----------------------------------------------------------------")
    print("FALL DETECTION (Fall vs Normal Activities) METRICS:")
    print(f"   * Binary Fall Accuracy:      {fall_accuracy * 100:.2f}%")
    print(f"   * Fall Precision:            {fall_p * 100:.2f}%")
    print(f"   * Fall Recall (Sensitivity): {fall_r * 100:.2f}%")
    print(f"   * Fall F1-Score:             {fall_f1 * 100:.2f}%")
    print("-----------------------------------------------------------------")

    # [5/5] Save Model Artifacts
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    model_path = models_dir / "activity_fall_classifier.joblib"
    metrics_path = models_dir / "model_metrics.json"
    
    joblib.dump({
        "model": clf,
        "feature_cols": feature_cols,
        "classes": classes.tolist(),
        "accuracy": float(test_accuracy),
        "fall_accuracy": float(fall_accuracy)
    }, model_path)
    
    metrics = {
        "dataset_rows": len(df),
        "feature_count": len(feature_cols),
        "test_accuracy_pct": round(float(test_accuracy) * 100, 2),
        "train_accuracy_pct": round(float(train_accuracy) * 100, 2),
        "precision_pct": round(float(precision) * 100, 2),
        "recall_pct": round(float(recall) * 100, 2),
        "f1_score_pct": round(float(f1) * 100, 2),
        "fall_accuracy_pct": round(float(fall_accuracy) * 100, 2),
        "fall_recall_pct": round(float(fall_r) * 100, 2),
        "fall_precision_pct": round(float(fall_p) * 100, 2),
        "model_type": "HistGradientBoostingClassifier",
        "training_time_seconds": round(train_time, 2)
    }
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[5/5] Saved trained model to '{model_path}'")
    print(f"Saved metrics summary to '{metrics_path}'")
    print("=================================================================\n")

if __name__ == "__main__":
    train_activity_and_fall_model()
