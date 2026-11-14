from pathlib import Path
import json
import pandas as pd

from .preprocessing import clean_text

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ["comment_id", "student_id", "comment"]
DEFAULT_DEMO_FILENAME = "review_multibahasa_112.csv"


def java_catalog():
    return json.loads((ROOT / "java_examples/catalog.json").read_text(encoding="utf-8"))


def java_source(code_id):
    item = next((c for c in java_catalog() if c["id"] == code_id), None)
    if item is None:
        return None
    return (ROOT / "java_examples" / item["file"]).read_text(encoding="utf-8")


def validate_frame(frame, origin="uploaded"):
    missing = [c for c in REQUIRED if c not in frame.columns]
    if missing:
        raise ValueError("Kolom wajib: comment_id, student_id, comment. Kolom code_id bersifat opsional.")
    if frame.empty or len(frame) > 5000:
        raise ValueError("Dataset harus berisi 1–5.000 komentar.")
    result = frame.copy().fillna("")
    for column in REQUIRED + ["code_id"]:
        if column not in result:
            result[column] = ""
        result[column] = result[column].astype(str).str.strip()
    if any(result[c].eq("").any() for c in REQUIRED):
        raise ValueError("ID komentar, kode mahasiswa, dan komentar tidak boleh kosong.")
    if result["comment_id"].duplicated().any():
        raise ValueError("comment_id harus unik.")
    if result["comment"].map(len).gt(3000).any():
        raise ValueError("Panjang komentar maksimal 3.000 karakter.")
    if not result["comment"].map(clean_text).map(bool).all():
        raise ValueError("Ada komentar kosong setelah preprocessing.")
    # Jangan membawa target generasi, prediksi, atau anotasi dari unggahan ke tampilan buta.
    return [{**row, "data_origin": origin} for row in result[REQUIRED + ["code_id"]].to_dict("records")]


def demo_rows():
    path = ROOT / "data" / DEFAULT_DEMO_FILENAME
    if not path.is_file():
        raise FileNotFoundError(
            f"File data bawaan {DEFAULT_DEMO_FILENAME} tidak ditemukan. "
            f"Letakkan file tersebut di folder data: {path}"
        )
    rows = validate_frame(pd.read_csv(path, dtype=str, keep_default_na=False), "synthetic_demo")
    if len({r["student_id"] for r in rows}) != len(rows):
        raise ValueError("Setiap komentar simulasi harus memiliki kode mahasiswa fiktif yang berbeda.")
    return rows


def csv_bytes(frame):
    # Escape pemicu formula untuk ekspor yang mungkin dibuka dengan spreadsheet.
    output = frame.copy()
    for col in output.select_dtypes(include=["object", "string"]).columns:
        output[col] = output[col].map(lambda x: "'" + x if isinstance(x, str) and x.lstrip().startswith(("=", "+", "-", "@")) else x)
    return output.to_csv(index=False).encode("utf-8-sig")
