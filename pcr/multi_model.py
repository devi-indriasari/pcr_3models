"""Three frozen Notebook 3 scenarios; does not train or modify existing artefacts."""
from pathlib import Path
import json
import hashlib
import warnings
import joblib
import numpy as np
import sklearn
from sklearn.exceptions import InconsistentVersionWarning
from .preprocessing import clean_text
from .rubrics import LABELS

ROOT = Path(__file__).resolve().parents[1]
MODEL_ALIASES = {
    "S1": ["best_model_S1.joblib", "champion_S1.joblib"],
    "S2": ["best_model_S2.joblib", "champion_S2.joblib"],
    "S3": ["best_model_S3.joblib", "champion_S3.joblib"],
}


def locate_models(root=ROOT):
    root = Path(root)
    # Existing old folder layout root/models; also accept earlier app/models layout.
    candidates = [root / "models", root / "app" / "models"]
    for directory in candidates:
        paths = {s: next((directory / name for name in names if (directory / name).is_file()), None)
                 for s, names in MODEL_ALIASES.items()}
        if all(paths.values()):
            return directory, paths
    status = "; ".join(f"{d}: " + ", ".join(p.name for p in d.glob("*.joblib")) for d in candidates)
    raise FileNotFoundError("Tiga model S1/S2/S3 belum ditemukan pada folder yang sama. "
                            "Nama yang didukung: best_model_S1/S2/S3.joblib atau champion_S1/S2/S3.joblib. "
                            + status)


class ScenarioModel:
    def __init__(self, key, path, directory):
        self.key = key
        self.path = Path(path)
        self.fingerprint = hashlib.sha256(self.path.read_bytes()).hexdigest()
        candidates = [directory / f"best_model_{key}_metadata.json", directory / f"champion_{key}_metadata.json"]
        meta = next((x for x in candidates if x.exists()), None)
        self.metadata = json.loads(meta.read_text(encoding="utf-8")) if meta else {}
        expected = self.metadata.get("scikit_learn_version") or self.metadata.get("sklearn_version")
        if expected and sklearn.__version__ != str(expected):
            raise RuntimeError(f"Model {key} memerlukan scikit-learn {expected}; versi terpasang {sklearn.__version__}.")
        with warnings.catch_warnings():
            warnings.simplefilter("error", InconsistentVersionWarning)
            self.pipeline = joblib.load(self.path)
        if hasattr(self.pipeline, "memory"):
            self.pipeline.memory = None
        self.vectorizer = self.pipeline.named_steps["vectorizer"]
        self.classifier = self.pipeline.named_steps["classifier"]
        self.classes = [str(x) for x in self.classifier.classes_]
        if set(self.classes) != set(LABELS):
            raise ValueError(f"Label {key} tidak cocok dengan tujuh rubrik: {self.classes}")
        self.features = self.vectorizer.get_feature_names_out()

    def predict(self, texts):
        cleaned = [clean_text(x) for x in texts]
        if not cleaned or not all(cleaned):
            raise ValueError("Komentar harus terisi setelah preprocessing")
        x = self.vectorizer.transform(cleaned)
        scores = np.asarray(self.classifier.decision_function(x))
        labels = self.pipeline.predict(cleaned)
        result = []
        for i,(raw,text,label) in enumerate(zip(texts, cleaned, labels)):
            rank=np.argsort(-scores[i],kind="stable")
            result.append({"text":raw,"cleaned":text,"label":str(label),
                "scores":{c:float(z) for c,z in zip(self.classes,scores[i])},
                "runner_up":self.classes[int(rank[1])],
                "gap":float(scores[i,rank[0]]-scores[i,rank[1]]),
                "known_features":int(x[i].nnz)})
        return result

    def explain(self,text,against=None,top_k=8):
        pred=self.predict([text])[0]
        winner=pred["label"]
        rival=against if against and against != winner else pred["runner_up"]
        if rival not in self.classes:
            raise ValueError("Label pembanding tidak dikenal")
        wi,ri=self.classes.index(winner),self.classes.index(rival)
        x=self.vectorizer.transform([pred["cleaned"]]).tocsr()
        idx,values=x.indices,x.data
        weights=self.classifier.coef_
        contrast=values*(weights[wi,idx]-weights[ri,idx])
        rows=[{"fragment":str(self.features[j]),"tfidf":float(v),
            "winner_contribution":float(v*weights[wi,j]),
            "rival_contribution":float(v*weights[ri,j]),
            "difference":float(d)} for j,v,d in zip(idx,values,contrast)]
        positive=sorted((r for r in rows if r["difference"]>0),key=lambda r:-r["difference"])[:top_k]
        negative=sorted((r for r in rows if r["difference"]<0),key=lambda r:r["difference"])[:top_k]
        intercept=float(self.classifier.intercept_[wi]-self.classifier.intercept_[ri])
        gap=pred["scores"][winner]-pred["scores"][rival]
        reconstructed=float(contrast.sum()+intercept)
        if not np.isclose(gap,reconstructed,rtol=1e-7,atol=1e-7):
            raise ArithmeticError("Skor XAI tidak sama dengan model")
        return {**pred,"against":rival,"positive":positive,"negative":negative,
            "intercept_difference":intercept,"contribution_sum":float(contrast.sum()),
            "score_difference":float(gap),"reconstructed":reconstructed,
            "other_contribution":float(contrast.sum()-sum(r["difference"] for r in positive+negative))}


class ThreeModelService:
    """Backward-compatible S1 interface plus explicit predict_three()."""
    def __init__(self, root=ROOT):
        directory,paths=locate_models(root)
        self.model_directory=directory
        self.models={s:ScenarioModel(s,paths[s],directory) for s in ("S1","S2","S3")}
        self.fingerprint=self.models["S1"].fingerprint
        self.metadata={"best_model_name":"S1 LinearSVC (SVM) + TF-IDF char; plus S2/S3", "scenario_hashes":self.hashes}

    @property
    def hashes(self):
        return {s:model.fingerprint for s,model in self.models.items()}

    def predict(self,texts):
        return self.models["S1"].predict(texts)

    def explain(self,text,against=None):
        return self.models["S1"].explain(text,against=against)

    def predict_three(self,texts):
        return {s:self.models[s].predict(texts) for s in ("S1","S2","S3")}
