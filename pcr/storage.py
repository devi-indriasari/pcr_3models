"""Penyimpanan lokal transaksional untuk review dan anotasi prototipe."""
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import sqlite3
import uuid

from .rubrics import LABELS, RUBRICS

ROOT = Path(__file__).resolve().parents[1]


def now():
    return datetime.now(timezone.utc).isoformat()


def stable_hash(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


@contextmanager
def connection():
    path = Path(os.environ.get("PCR_DB_PATH", str(ROOT / "runtime/pcr.sqlite3")))
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path, timeout=20) as db:
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("CREATE TABLE IF NOT EXISTS reviews (id TEXT PRIMARY KEY, created TEXT NOT NULL, student TEXT NOT NULL, code_id TEXT NOT NULL, payload TEXT NOT NULL)")
        db.execute("CREATE TABLE IF NOT EXISTS annotation_sets (id TEXT PRIMARY KEY, teacher TEXT NOT NULL, dataset_hash TEXT NOT NULL, created TEXT NOT NULL, updated TEXT NOT NULL, payload TEXT NOT NULL)")
        yield db


def save_review(review_id, student, code_id, payload):
    if not student.strip():
        raise ValueError("Kode mahasiswa wajib diisi.")
    if set(payload.get("comments", {})) != set(RUBRICS):
        raise ValueError("Review harus memuat enam rubrik.")
    if any(not value.strip() for value in payload["comments"].values()):
        raise ValueError("Seluruh komentar wajib diisi.")
    payload = {**payload, "student_id": student.strip(), "code_id": code_id,
               "review_id": review_id, "created_at_utc": now(), "data_origin": "student_submission"}
    with connection() as db:
        db.execute("INSERT INTO reviews VALUES (?,?,?,?,?)", (review_id, payload["created_at_utc"], student.strip(), code_id, json.dumps(payload, ensure_ascii=False)))
    return payload


def submitted_rows():
    rows = []
    with connection() as db:
        reviews = db.execute("SELECT payload FROM reviews ORDER BY created").fetchall()
    for (text,) in reviews:
        p = json.loads(text)
        for i, rubric in enumerate(RUBRICS, 1):
            rows.append({"comment_id": f"{p['review_id']}-{i}", "student_id": p["student_id"],
                         "code_id": p["code_id"], "comment": p["comments"][rubric],
                         "data_origin": "student_submission"})
    return rows


def open_annotation(teacher, rows, source):
    if not teacher.strip() or not rows:
        raise ValueError("Kode dosen dan dataset wajib tersedia.")
    fingerprint = stable_hash(rows)
    with connection() as db:
        existing = db.execute("SELECT payload FROM annotation_sets WHERE teacher=? AND dataset_hash=? ORDER BY updated DESC LIMIT 1", (teacher.strip(), fingerprint)).fetchone()
        if existing:
            return json.loads(existing[0])
        timestamp = now()
        value = {"id": uuid.uuid4().hex, "teacher": teacher.strip(), "dataset_hash": fingerprint,
                 "source": source, "rows": rows, "labels": {}, "notes": {}, "locked": False,
                 "created": timestamp, "updated": timestamp, "adjudication": {}}
        db.execute("INSERT INTO annotation_sets VALUES (?,?,?,?,?,?)", (value["id"], teacher.strip(), fingerprint, timestamp, timestamp, json.dumps(value, ensure_ascii=False)))
    return value


def get_annotation(set_id):
    with connection() as db:
        row = db.execute("SELECT payload FROM annotation_sets WHERE id=?", (set_id,)).fetchone()
    if row is None:
        raise ValueError("Anotasi tidak ditemukan.")
    return json.loads(row[0])


def save_label(set_id, comment_id, label, note=""):
    if label not in LABELS:
        raise ValueError("Pilih satu label yang valid.")
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        data = json.loads(db.execute("SELECT payload FROM annotation_sets WHERE id=?", (set_id,)).fetchone()[0])
        if data["locked"]:
            raise ValueError("Anotasi awal sudah dikunci; gunakan kolom adjudikasi.")
        if comment_id not in {r["comment_id"] for r in data["rows"]}:
            raise ValueError("ID komentar tidak ditemukan.")
        data["labels"][comment_id] = label
        data["notes"][comment_id] = note.strip()
        data["updated"] = now()
        db.execute("UPDATE annotation_sets SET payload=?,updated=? WHERE id=?", (json.dumps(data, ensure_ascii=False), data["updated"], set_id))
    return data


def lock_annotation(set_id, predictions, model_hash):
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        data = json.loads(db.execute("SELECT payload FROM annotation_sets WHERE id=?", (set_id,)).fetchone()[0])
        if data["locked"]:
            return data
        ids = [r["comment_id"] for r in data["rows"]]
        if any(data["labels"].get(i) not in LABELS for i in ids):
            raise ValueError("Lengkapi semua label sebelum membandingkan dengan model.")
        if len(predictions) != len(ids):
            raise ValueError("Jumlah prediksi berbeda dari jumlah komentar.")
        if any(p["label"] not in LABELS or p["text"] != r["comment"] for p, r in zip(predictions, data["rows"])):
            raise ValueError("Prediksi tidak cocok dengan urutan atau isi dataset.")
        data.update(locked=True, predictions=predictions, model_hash=model_hash,
                    revealed_at_utc=now(), updated=now())
        db.execute("UPDATE annotation_sets SET payload=?,updated=? WHERE id=?", (json.dumps(data, ensure_ascii=False), data["updated"], set_id))
    return data


def save_adjudication(set_id, comment_id, label, note=""):
    if label not in LABELS:
        raise ValueError("Label adjudikasi tidak valid.")
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        data = json.loads(db.execute("SELECT payload FROM annotation_sets WHERE id=?", (set_id,)).fetchone()[0])
        if not data["locked"] or comment_id not in data["labels"]:
            raise ValueError("Adjudikasi memerlukan anotasi awal yang sudah dikunci.")
        data["adjudication"][comment_id] = {"label": label, "note": note.strip(), "time_utc": now(), "after_model_exposure": True}
        data["updated"] = now()
        db.execute("UPDATE annotation_sets SET payload=?,updated=? WHERE id=?", (json.dumps(data, ensure_ascii=False), data["updated"], set_id))
    return data
