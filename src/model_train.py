from __future__ import annotations

from pathlib import Path
from typing import Dict

import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

from src.feature_engine import FEATURE_COLUMNS


class ModelTrainer:
    def __init__(self, random_state: int = 42):
        self.model = LogisticRegression(max_iter=500, random_state=random_state, multi_class="multinomial")

    def train(self, df: pd.DataFrame) -> Dict[str, str]:
        split_idx = int(len(df) * 0.8)
        train = df.iloc[:split_idx]
        test = df.iloc[split_idx:]
        X_train = train[FEATURE_COLUMNS]
        y_train = train["label"]
        X_test = test[FEATURE_COLUMNS]
        y_test = test["label"]

        self.model.fit(X_train, y_train)
        pred = self.model.predict(X_test)
        report = classification_report(y_test, pred, output_dict=False)
        return {"classification_report": report}

    def save(self, path: str = "models/model.joblib") -> Path:
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, out)
        return out
