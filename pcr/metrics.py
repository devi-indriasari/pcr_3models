"""Kesepakatan nominal 7 kelas. Tidak memakai pembobotan ordinal."""
import numpy as np
from sklearn.metrics import confusion_matrix
from .rubrics import LABELS


def agreement_report(human, model):
    if len(human) != len(model) or len(human) == 0:
        raise ValueError("Pasangan label harus sama panjang dan tidak kosong.")
    if any(x not in LABELS for x in list(human) + list(model)):
        raise ValueError("Ada label kosong atau tidak valid; hanya pasangan lengkap boleh dihitung.")
    cm = confusion_matrix(human, model, labels=LABELS)
    n = int(cm.sum())
    observed = float(np.trace(cm) / n)
    human_counts = cm.sum(axis=1)
    model_counts = cm.sum(axis=0)
    expected = float(np.dot(human_counts / n, model_counts / n))
    kappa = None if np.isclose(1 - expected, 0) else float((observed - expected) / (1 - expected))
    return {"n": n, "agree": int(np.trace(cm)), "disagree": int(n - np.trace(cm)),
            "p_o": observed, "p_e": expected, "kappa": kappa,
            "confusion_matrix": cm.tolist(), "human_counts": human_counts.tolist(),
            "model_counts": model_counts.tolist()}
