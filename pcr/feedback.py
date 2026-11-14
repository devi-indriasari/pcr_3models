"""Saran pedagogis berbasis rubrik; dipisah dari bukti kontribusi fitur model."""
from .rubrics import DEFINITIONS, PROMPTS


def coaching(prediction, intended):
    mismatch = prediction["label"] != intended
    general = prediction["label"] == "General"
    no_features = prediction["known_features"] == 0
    # Ambang kerja prototipe, bukan probabilitas atau ambang yang divalidasi.
    close = prediction["gap"] < 0.25
    flags, advice = [], []
    if general:
        flags.append("Terprediksi umum")
        advice.append("Model membaca komentar sebagai penilaian umum. Periksa apakah komentar sudah menyebut aspek teknis yang diminta dan bukti dari kode.")
    elif mismatch:
        flags.append("Prediksi berbeda dari rubrik")
        advice.append(f"Kolom ini membahas {intended}, sedangkan prediksi model adalah {prediction['label']}. Baca kembali fokus komentar dan definisi kedua kategori.")
    if no_features:
        flags.append("Fitur teks tidak dikenali")
        advice.append("Teks tidak memiliki fitur yang dikenali model. Tambahkan uraian yang bermakna tentang bagian kode yang dinilai.")
    if close:
        flags.append("Dua skor berdekatan")
        advice.append("Dua kategori teratas memiliki skor berdekatan. Periksa apakah komentar mencampurkan dua fokus yang sama kuat.")
    if not advice:
        advice.append("Prediksi selaras dengan rubrik. Tetap pastikan penilaian didukung oleh bagian kode yang Anda baca.")
    advice.append(PROMPTS[intended])
    return {"flags": flags, "needs_review": bool(flags), "advice": advice,
            "definition": DEFINITIONS[intended]}


def disagreement_text(explanation, human_label):
    model_label = explanation["label"]
    if human_label == model_label:
        return f"Label dosen dan model sama: {human_label}. Kesamaan ini tidak otomatis memverifikasi kebenaran label."
    pieces = [r["fragment"].replace(" ", "␠") for r in explanation["positive"][:4]]
    evidence = ", ".join(repr(p) for p in pieces) or "tidak ada fragmen dengan kontribusi positif"
    return (
        f"Dosen memilih {human_label}; model memilih {model_label}. "
        f"Dalam perbandingan kedua kelas, fragmen yang mendorong skor ke {model_label} antara lain {evidence}. "
        f"Fokus {human_label}: {DEFINITIONS[human_label]} "
        f"Fokus {model_label}: {DEFINITIONS[model_label]} "
        "Kontribusi fitur menjelaskan keputusan model, bukan alasan dosen. Perbedaan bisa berasal dari petunjuk teks yang dipelajari, ambiguitas komentar, atau kesalahan model. Tinjau konteks sebelum adjudikasi."
    )
