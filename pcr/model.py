"""Inferensi model asli dan XAI aditif/kontrastif yang eksak untuk LinearSVC."""
from pathlib import Path
import hashlib
import json
import warnings

import joblib
import numpy as np
import sklearn
from sklearn.exceptions import InconsistentVersionWarning
from sklearn.svm import LinearSVC

from .preprocessing import clean_text
from .rubrics import LABELS

ROOT = Path(__file__).resolve().parents[1]


class ModelService:
    def __init__(self, root=ROOT):
        root = Path(root)
        self.metadata = json.loads((root / "models/best_model_metadata.json").read_text())
        expected = self.metadata["scikit_learn_version"]
        if sklearn.__version__ != expected:
            raise RuntimeError(f"Model memerlukan scikit-learn {expected}; terpasang {sklearn.__version__}. Jalankan pip install -r requirements.txt.")
        model_path = root / "models/best_model.joblib"
        self.fingerprint = hashlib.sha256(model_path.read_bytes()).hexdigest()
        with warnings.catch_warnings():
            warnings.simplefilter("error", InconsistentVersionWarning)
            self.pipeline = joblib.load(model_path)
        # Artefak pelatihan memakai lokasi cache notebook; inferensi tidak memerlukannya.
        self.pipeline.memory = None
        self.vectorizer = self.pipeline.named_steps["vectorizer"]
        self.classifier = self.pipeline.named_steps["classifier"]
        if not isinstance(self.classifier, LinearSVC) or self.vectorizer.analyzer != "char":
            raise ValueError("Penjelasan aplikasi ini memerlukan LinearSVC dengan fitur karakter.")
        self.classes = [str(x) for x in self.classifier.classes_]
        if set(self.classes) != set(LABELS):
            raise ValueError("Label model tidak cocok dengan tujuh label rubrik.")
        self.features = self.vectorizer.get_feature_names_out()

    def predict(self, texts):
        cleaned = [clean_text(t) for t in texts]
        if not cleaned or any(not t for t in cleaned):
            raise ValueError("Komentar harus berisi teks setelah preprocessing.")
        x = self.vectorizer.transform(cleaned)
        scores = np.asarray(self.classifier.decision_function(x))
        labels = self.pipeline.predict(cleaned)
        output = []
        for i, (raw, text, label) in enumerate(zip(texts, cleaned, labels)):
            rank = np.argsort(-scores[i], kind="stable")
            output.append({
                "text": raw, "cleaned": text, "label": str(label),
                "scores": {c: float(s) for c, s in zip(self.classes, scores[i])},
                "runner_up": self.classes[int(rank[1])],
                "gap": float(scores[i, rank[0]] - scores[i, rank[1]]),
                "known_features": int(x[i].nnz),
            })
        return output

    def explain(self, text, against=None, top_k=8):
        pred = self.predict([text])[0]
        winner = pred["label"]
        # Jika label pembanding sama, jelaskan terhadap kelas peringkat kedua.
        rival = against if against and against != winner else pred["runner_up"]
        if rival not in self.classes:
            raise ValueError("Label pembanding tidak dikenal.")
        wi, ri = self.classes.index(winner), self.classes.index(rival)
        x = self.vectorizer.transform([pred["cleaned"]]).tocsr()
        idx, values = x.indices, x.data
        weights = self.classifier.coef_
        predicted_contrib = values * weights[wi, idx]
        rival_contrib = values * weights[ri, idx]
        contrast = predicted_contrib - rival_contrib
        rows = [{"fragment": str(self.features[j]), "tfidf": float(v),
                 "winner_contribution": float(a), "rival_contribution": float(b),
                 "difference": float(d)}
                for j, v, a, b, d in zip(idx, values, predicted_contrib, rival_contrib, contrast)]
        positive = sorted((r for r in rows if r["difference"] > 0), key=lambda r: -r["difference"])[:top_k]
        negative = sorted((r for r in rows if r["difference"] < 0), key=lambda r: r["difference"])[:top_k]
        intercept = float(self.classifier.intercept_[wi] - self.classifier.intercept_[ri])
        score_gap = pred["scores"][winner] - pred["scores"][rival]
        reconstructed = float(contrast.sum() + intercept)
        if not np.isclose(score_gap, reconstructed, rtol=1e-9, atol=1e-9):
            raise ArithmeticError("Penjelasan tidak merekonstruksi skor model.")
        return {**pred, "against": rival, "positive": positive, "negative": negative,
                "intercept_difference": intercept, "contribution_sum": float(contrast.sum()),
                "score_difference": float(score_gap), "reconstructed": reconstructed,
                "other_contribution": float(contrast.sum() - sum(r["difference"] for r in positive + negative))}
