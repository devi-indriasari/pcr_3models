"""Streamlit: satu halaman, dua peran, menggunakan model unggahan tanpa retraining."""
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import json
import random
import uuid

import pandas as pd
import streamlit as st

from pcr.datasets import (DEFAULT_DEMO_FILENAME, csv_bytes, demo_rows, java_catalog, java_source, validate_frame)
from pcr.feedback import coaching, disagreement_text
from pcr.metrics import agreement_report
from pcr.multi_model import ThreeModelService
from pcr.annotation_import import parse_progress_csv, restore_progress
from pcr.preprocessing import clean_text
from pcr.rubrics import BOUNDARIES, DEFINITIONS, LABELS, PLACEHOLDERS, PROMPTS, RUBRICS, slug
from pcr.storage import (get_annotation, lock_annotation, open_annotation, save_adjudication,
                         save_label, save_review, stable_hash, submitted_rows)

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="PCR · Code Quality Alignment", page_icon="📘", layout="wide")
st.markdown("""<style>
.block-container {max-width: 1220px; padding-top: 2rem; padding-bottom: 3rem;}
[data-testid="stMetricValue"] {font-size: 1.8rem;}
.rubric-anchor {scroll-margin-top: 90px;}
</style>""", unsafe_allow_html=True)


@st.cache_resource
def model_service():
    return ThreeModelService()


def json_bytes(value):
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False).encode("utf-8")


def score_table(prediction):
    return pd.DataFrame([{"Kategori": k, "Skor keputusan": v} for k, v in prediction["scores"].items()]).sort_values("Skor keputusan", ascending=False)


def display_xai(service, text, against=None):
    ex = service.explain(text, against=against)
    st.caption(f"Perbandingan: {ex['label']} terhadap {ex['against']}. Skor bukan probabilitas.")
    left, right = st.columns([1, 1.25])
    with left:
        st.dataframe(score_table(ex), hide_index=True, width="stretch",
                     column_config={"Skor keputusan": st.column_config.NumberColumn(format="%.4f")})
    with right:
        rows = ex["positive"][:6] + ex["negative"][:4]
        if rows:
            table = pd.DataFrame([{"Fragmen karakter": repr(r["fragment"]), "Kontribusi selisih": r["difference"]} for r in rows])
            st.dataframe(table, hide_index=True, width="stretch",
                         column_config={"Kontribusi selisih": st.column_config.NumberColumn(format="%+.5f")})
        else:
            st.info("Tidak ada fitur teks yang dikenali. Skor terutama berasal dari bias model.")
    st.caption("Kontribusi positif mendorong kelas prediksi; negatif mendorong kelas pembanding. Fragmen 2–5 karakter dapat tumpang tindih dan bukan penilaian semantik atas seluruh kalimat.")
    st.caption(f"Jumlah kontribusi seluruh fitur {ex['contribution_sum']:.5f} + selisih bias {ex['intercept_difference']:.5f} = selisih skor {ex['score_difference']:.5f}.")
    with st.expander("Teks yang diproses model"):
        st.text(ex["cleaned"])
        st.caption("Preprocessing mengikuti Notebook 3. Kode Java ditampilkan sebagai konteks bagi reviewer; model mengklasifikasikan teks komentar.")
    return ex


def new_student_draft(preserve_student=""):
    catalog = java_catalog()
    return {"id": uuid.uuid4().hex, "student": preserve_student,
            "code_id": random.choice(catalog)["id"], "comments": {r: "" for r in RUBRICS},
            "analysis": None, "analysis_hash": None, "history": [], "submitted": None}


def reset_student_widgets():
    for key in list(st.session_state):
        if key.startswith("student_"):
            del st.session_state[key]


def start_new_review():
    previous = st.session_state["draft"].get("student", "")
    reset_student_widgets()
    st.session_state["draft"] = new_student_draft(previous)


def invalidate_analysis():
    draft = st.session_state["draft"]
    draft["analysis"] = None
    draft["analysis_hash"] = None
    st.session_state["student_override"] = False
    st.session_state["student_override_reason"] = ""
    st.session_state["student_confirm"] = False


def update_comment(label):
    st.session_state["draft"]["comments"][label] = st.session_state[f"student_text_{slug(label)}"]
    invalidate_analysis()


def update_student_id():
    st.session_state["draft"]["student"] = st.session_state["student_identifier"]


def change_code():
    draft = st.session_state["draft"]
    draft["code_id"] = st.session_state["student_code"]
    draft["comments"] = {r: "" for r in RUBRICS}
    for label in RUBRICS:
        st.session_state[f"student_text_{slug(label)}"] = ""
    invalidate_analysis()


def shuffle_code():
    current = st.session_state["draft"]["code_id"]
    others = [c["id"] for c in java_catalog() if c["id"] != current]
    st.session_state["student_code"] = random.choice(others)
    change_code()


def submit_student_review(model_hash, model_name):
    """Callback berjalan sebelum tampilan berikutnya; pengiriman hanya satu kali."""
    draft = st.session_state["draft"]
    if draft["submitted"]:
        return
    current_hash = stable_hash({"code_id": draft["code_id"], "comments": draft["comments"]})
    analysis = draft.get("analysis")
    if not analysis or current_hash != draft["analysis_hash"] or not st.session_state.get("student_confirm"):
        st.session_state["submission_error"] = "Periksa komentar terbaru dan konfirmasikan review terlebih dahulu."
        return
    flagged = [r for r in RUBRICS if analysis[r]["coaching"]["needs_review"]]
    reason = st.session_state.get("student_override_reason", "") if flagged else ""
    if flagged and (not st.session_state.get("student_override") or len(reason.strip()) < 15):
        st.session_state["submission_error"] = "Perbaiki komentar yang ditandai atau jelaskan alasan mempertahankannya."
        return
    try:
        draft["submitted"] = save_review(draft["id"], draft["student"], draft["code_id"], {
            "comments": dict(draft["comments"]), "analysis": analysis,
            "model_sha256": model_hash, "model_name": model_name,
            "history": draft["history"], "override": {"rubrics": flagged, "reason": reason},
        })
    except (OSError, ValueError) as error:
        st.session_state["submission_error"] = f"Review belum terkirim: {error}"


def student_view(service):
    if "draft" not in st.session_state:
        st.session_state["draft"] = new_student_draft()
    draft = st.session_state["draft"]
    st.subheader("Review kode sebagai mahasiswa")
    if "submission_error" in st.session_state:
        st.error(st.session_state.pop("submission_error"))
    if draft["submitted"]:
        payload = draft["submitted"]
        sent_time = datetime.fromisoformat(payload["created_at_utc"]).astimezone(ZoneInfo("Asia/Jakarta"))
        st.success("Review berhasil dikirim dan disimpan. Keenam komentar sudah masuk ke daftar review untuk dosen.")
        st.caption(f"ID review: {payload['review_id']} · {sent_time:%d-%m-%Y %H:%M} WIB")
        st.dataframe(pd.DataFrame([{"Rubrik": r, "Komentar terkirim": t} for r, t in payload["comments"].items()]), hide_index=True, width="stretch")
        st.download_button("Unduh bukti review (JSON)", json_bytes(payload), file_name=f"review_{payload['review_id'][:8]}.json", mime="application/json")
        st.button("Buat review baru", on_click=start_new_review)
        return

    if "student_identifier" not in st.session_state:
        st.session_state["student_identifier"] = draft["student"]
    st.text_input("Kode mahasiswa", key="student_identifier", placeholder="Contoh: MHS101", max_chars=50, on_change=update_student_id)
    st.caption("Baca kode → tulis enam komentar → periksa dan revisi → kirim review akhir.")
    catalog = java_catalog()
    lookup = {c["id"]: c for c in catalog}
    if "student_code" not in st.session_state:
        st.session_state["student_code"] = draft["code_id"]
    code_col, form_col = st.columns([1, 1.15], gap="large")
    with code_col:
        st.markdown("**1. Baca kode Java**")
        st.selectbox("Contoh kode", list(lookup), format_func=lambda x: f"{x} · {lookup[x]['title']}", key="student_code", on_change=change_code)
        st.button("Acak kode", on_click=shuffle_code, help="Mengganti kode dan mengosongkan komentar saat ini.")
        item = lookup[draft["code_id"]]
        st.info(item["task"])
        source = java_source(draft["code_id"])
        with st.container(height=570, border=True):
            st.code(source, language="java", line_numbers=True)
        st.download_button("Unduh kode Java", source, file_name=item["file"], mime="text/plain")
        st.caption("Contoh latihan sengaja memuat bagian yang dapat dikritisi. Nilai aspek yang benar-benar terlihat pada kode.")
    with form_col:
        st.markdown("**2. Tulis komentar berdasarkan enam rubrik**")
        st.caption("Satu fokus dominan per kolom. General tetap menjadi keluaran model, tetapi bukan rubrik isian.")
        for label in RUBRICS:
            st.markdown(f'<div id="rubrik-{slug(label)}" class="rubric-anchor"></div>', unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown(f"**{label}**")
                st.caption(DEFINITIONS[label])
                st.caption(BOUNDARIES[label])
                key = f"student_text_{slug(label)}"
                if key not in st.session_state:
                    st.session_state[key] = draft["comments"][label]
                st.text_area(f"Komentar untuk {label}", key=key, placeholder=PLACEHOLDERS[label],
                             height=100, max_chars=3000, label_visibility="collapsed", on_change=update_comment, args=(label,))

    st.markdown("**3. Periksa dan perbaiki komentar**")
    if st.button("Periksa komentar", type="primary", key="student_check"):
        missing = [r for r in RUBRICS if not clean_text(draft["comments"][r])]
        if missing:
            st.error("Lengkapi komentar yang bermakna pada: " + ", ".join(missing))
        else:
            predictions = service.predict([draft["comments"][r] for r in RUBRICS])
            draft["analysis"] = {r: {"prediction": p, "coaching": coaching(p, r)} for r, p in zip(RUBRICS, predictions)}
            draft["analysis_hash"] = stable_hash({"code_id": draft["code_id"], "comments": draft["comments"]})
            draft["history"].append({"code_id": draft["code_id"], "comments": dict(draft["comments"]), "analysis": draft["analysis"], "hash": draft["analysis_hash"]})
            st.session_state["student_override"] = False
            st.session_state["student_confirm"] = False

    analysis = draft["analysis"]
    if analysis is not None and draft.get("analysis_hash") == stable_hash({"code_id": draft["code_id"], "comments": draft["comments"]}):
        st.markdown("**Perbandingan tiga model terbaik pada keenam komentar**")
        three = service.predict_three([draft["comments"][r] for r in RUBRICS])
        comp = pd.DataFrame([{"Rubrik":r, "S1 (Original)":three["S1"][i]["label"],
            "S2 (+783)":three["S2"][i]["label"], "S3 (+1050)":three["S3"][i]["label"]}
            for i,r in enumerate(RUBRICS)])
        st.dataframe(comp, hide_index=True, width="stretch")
        st.caption("S1 tetap digunakan sebagai acuan coaching dan XAI bawaan aplikasi lama; S2/S3 ditampilkan sebagai prediksi pembanding. Tidak ada training ulang.")
    current_hash = stable_hash({"code_id": draft["code_id"], "comments": draft["comments"]})
    fresh = analysis is not None and current_hash == draft["analysis_hash"]
    flagged = []
    if fresh:
        for label in RUBRICS:
            result = analysis[label]
            pred, coach = result["prediction"], result["coaching"]
            if coach["needs_review"]:
                flagged.append(label)
            status = "Tinjau kembali" if coach["needs_review"] else "Prediksi selaras"
            with st.expander(f"{label} → {pred['label']} · {status}", expanded=coach["needs_review"]):
                st.markdown("**Komentar yang Anda masukkan**")
                st.write(draft["comments"][label])
                if coach["needs_review"]:
                    st.warning(" · ".join(coach["flags"]))
                else:
                    st.success("Prediksi selaras dengan rubrik isian.")
                st.markdown("**Saran revisi berdasarkan rubrik**")
                for tip in coach["advice"]:
                    st.write("• " + tip)
                st.markdown(f"[Kembali ke kolom {label}](#rubrik-{slug(label)})")
                st.markdown("**Bukti dari model (XAI)**")
                display_xai(service, draft["comments"][label], against=label)
        st.caption("Saran revisi mengikuti definisi rubrik. XAI menjelaskan kontribusi fitur model; keduanya tidak memverifikasi kebenaran penilaian terhadap kode.")
    else:
        st.info("Periksa keenam komentar. Setelah mengubah komentar, lakukan pemeriksaan ulang agar hasil sesuai dengan teks terbaru.")

    st.markdown("**4. Kirim review akhir**")
    override_ok = False
    if flagged:
        st.warning("Perbaiki dan periksa ulang: " + ", ".join(flagged) + ".")
        with st.expander("Prediksi model menurut saya keliru"):
            st.caption("Anda dapat mempertahankan komentar yang sudah sesuai rubrik dengan memberikan alasan. Perbedaan prediksi tidak otomatis berarti komentar salah.")
            st.checkbox("Saya telah meninjau komentar yang ditandai dan mempertahankannya berdasarkan kode/rubrik.", key="student_override")
            reason = st.text_area("Alasan mempertahankan komentar", key="student_override_reason", max_chars=1000)
            override_ok = bool(st.session_state.get("student_override")) and len(reason.strip()) >= 15
    confirmed = st.checkbox("Saya sudah membaca kode dan memeriksa isi keenam komentar.", key="student_confirm")
    allowed = fresh and bool(draft["student"].strip()) and confirmed and (not flagged or override_ok)
    st.button("Kirim review akhir", key="student_submit", type="primary", disabled=not allowed,
              on_click=submit_student_review, args=(service.fingerprint, service.metadata["best_model_name"]))
    if not draft["student"].strip():
        st.caption("Isi kode mahasiswa agar review dapat dikirim.")


def annotation_overview(data):
    return pd.DataFrame([{"ID": r["comment_id"], "Mahasiswa": r["student_id"],
                          "Komentar": r["comment"], "Label dosen": data["labels"].get(r["comment_id"], "")}
                         for r in data["rows"]])


def start_teacher():
    st.session_state.pop("active_annotation", None)


def teacher_setup():
    st.caption("Labeli komentar secara mandiri. Prediksi dibuka setelah semua label disimpan dan anotasi awal dikunci.")
    teacher = st.text_input("Kode dosen", value="DOSEN01", max_chars=50, key="teacher_identifier")
    default_rows = []
    default_error = None
    try:
        default_rows = demo_rows()
    except (OSError, ValueError, UnicodeError, pd.errors.ParserError) as error:
        default_error = str(error)
    demo_label = f"{len(default_rows)} komentar simulasi" if default_rows else "Komentar simulasi bawaan"
    options = [demo_label, "Review mahasiswa terkirim", "Unggah CSV"]
    if st.session_state.get("teacher_dataset") not in (None, *options):
        st.session_state["teacher_dataset"] = demo_label
    source = st.radio("Sumber komentar", options, horizontal=True, key="teacher_dataset")
    rows = []
    if source == demo_label:
        if default_error:
            st.error(f"Data bawaan belum dapat dibaca: {default_error}")
        else:
            rows = default_rows
            students = len({r["student_id"] for r in rows})
            st.info(f"{len(rows)} komentar sintetis dari {students} mahasiswa fiktif. "
                    "Label akhir ditentukan pakar; target generasi tidak ditampilkan pada anotasi.")
    elif source == "Review mahasiswa terkirim":
        rows = submitted_rows()
        if not rows:
            st.info("Review mahasiswa yang dikirim melalui aplikasi akan muncul di sini.")
    else:
        st.caption("Kolom wajib: comment_id, student_id, comment. Kolom code_id opsional. Satu baris untuk satu komentar.")
        uploaded = st.file_uploader("File komentar CSV", type="csv")
        if uploaded:
            try:
                rows = validate_frame(pd.read_csv(uploaded, dtype=str, keep_default_na=False), "uploaded")
            except (ValueError, UnicodeError, pd.errors.ParserError) as error:
                st.error(f"CSV belum dapat dipakai: {error}")
    if default_rows:
        st.download_button("Unduh dataset bawaan (CSV)", csv_bytes(pd.DataFrame(default_rows).drop(columns="data_origin")),
                           file_name=DEFAULT_DEMO_FILENAME, mime="text/csv")
    if rows:
        st.caption(f"{len(rows)} komentar · {len({r['student_id'] for r in rows})} kode mahasiswa")
        with st.expander("Lihat daftar komentar"):
            st.dataframe(pd.DataFrame(rows).drop(columns="data_origin"), hide_index=True, width="stretch")
    if st.button("Mulai / lanjutkan anotasi", type="primary", disabled=not rows or not teacher.strip()):
        data = open_annotation(teacher, rows, source)
        st.session_state["active_annotation"] = data["id"]
        st.rerun()


def teacher_blind(data, service):
    rows = data["rows"]
    ids = [r["comment_id"] for r in rows]
    completed = len(data["labels"])
    st.progress(completed / len(rows), text=f"{completed} dari {len(rows)} komentar sudah dilabeli")
    pick_key = f"annotation_pick_{data['id']}"
    if pick_key not in st.session_state:
        st.session_state[pick_key] = next((i for i in ids if i not in data["labels"]), ids[0])
    selected = st.selectbox("Pilih komentar", ids, key=pick_key,
                            format_func=lambda x: f"{'✓' if x in data['labels'] else '○'} {x} · {next(r['student_id'] for r in rows if r['comment_id'] == x)}")
    row = next(r for r in rows if r["comment_id"] == selected)
    with st.container(border=True):
        st.caption(f"{row['student_id']} · {row['code_id'] or 'Kode tidak disertakan'}")
        st.write(row["comment"])
        source = java_source(row["code_id"])
        if source:
            with st.expander("Lihat kode yang direview"):
                st.code(source, language="java", line_numbers=True)
        label_key = f"annotation_label_{data['id']}_{selected}"
        note_key = f"annotation_note_{data['id']}_{selected}"
        existing = data["labels"].get(selected)
        with st.form(f"annotation_form_{data['id']}_{selected}"):
            label = st.selectbox("Label dosen", LABELS, index=LABELS.index(existing) if existing else None,
                                 placeholder="Pilih satu kategori", key=label_key)
            note = st.text_area("Alasan penilaian (opsional)", value=data["notes"].get(selected, ""), key=note_key, max_chars=1500)
            saved = st.form_submit_button("Simpan label & berikutnya", type="primary")
        if saved:
            if label is None:
                st.error("Pilih satu label terlebih dahulu.")
            else:
                data = save_label(data["id"], selected, label, note)
                remaining = [i for i in ids if i not in data["labels"]]
                # Widget yang sudah dibuat diperbarui pada run berikutnya.
                st.session_state["next_annotation_pick"] = (pick_key, remaining[0] if remaining else selected)
                st.session_state["annotation_saved_notice"] = selected
                st.rerun()
    with st.expander("Daftar komentar dan progres label"):
        st.dataframe(annotation_overview(data), hide_index=True, width="stretch")
    st.download_button("Unduh progres anotasi (CSV)", csv_bytes(annotation_overview(data)), file_name="progres_anotasi.csv", mime="text/csv")
    ready = len(data["labels"]) == len(rows)
    st.caption("Tombol berikut mengunci label awal dan membuka prediksi model. Label awal dipertahankan untuk perhitungan kesepakatan.")
    if st.button("Kunci anotasi & bandingkan dengan model", type="primary", disabled=not ready, key="teacher_compare"):
        predictions = service.predict([r["comment"] for r in rows])
        lock_annotation(data["id"], predictions, service.fingerprint)
        st.rerun()


def comparison_frame(data):
    rows = []
    for row, pred in zip(data["rows"], data["predictions"]):
        i = row["comment_id"]
        adj = data["adjudication"].get(i, {})
        rows.append({"ID": i, "Mahasiswa": row["student_id"], "Kode": row["code_id"], "Komentar": row["comment"],
                     "Label dosen awal": data["labels"][i], "Prediksi model": pred["label"],
                     "Sama": data["labels"][i] == pred["label"], "Selisih dua skor teratas": pred["gap"],
                     "Alasan dosen": data["notes"].get(i, ""), "Label adjudikasi": adj.get("label", ""),
                     "Alasan adjudikasi": adj.get("note", ""), "Asal data": row["data_origin"]})
    return pd.DataFrame(rows)


def teacher_comparison(data, service):
    """Evaluasi DOSEN vs 3 champion; hindari blok legacy yang hanya S1."""
    from sklearn.metrics import accuracy_score, balanced_accuracy_score, classification_report, f1_score

    frame = comparison_frame(data)
    # Prediksi yang tersimpan sebelumnya tidak dipakai untuk metrik baru.
    frame = frame.rename(columns={"Prediksi model": "Prediksi model lama (arsip)",
                                  "Sama": "Sama model lama (arsip)"})
    keys = ("S1", "S2", "S3")
    texts = [r["comment"] for r in data["rows"]]
    three = service.predict_three(texts)  # selalu prediksi ulang memakai tiga artefak aktif
    truth = frame["Label dosen awal"].tolist()  # label sebelum prediksi dibuka
    reports, per_class, metrics = {}, {}, []
    for key in keys:
        frame[f"Prediksi {key}"] = [p["label"] for p in three[key]]
        frame[f"Sama {key}"] = frame["Label dosen awal"] == frame[f"Prediksi {key}"]
        preds = frame[f"Prediksi {key}"].tolist()
        reports[key] = agreement_report(truth, preds)
        per_class[key] = classification_report(truth, preds, labels=LABELS,
                                               output_dict=True, zero_division=0)
        r = reports[key]
        metrics.append({"Model": key, "Jumlah komentar": r["n"],
                        "Label sama": r["agree"], "Label berbeda": r["disagree"],
                        "Accuracy": accuracy_score(truth, preds),
                        "Macro-F1": f1_score(truth, preds, labels=LABELS, average="macro", zero_division=0),
                        "Weighted-F1": f1_score(truth, preds, labels=LABELS, average="weighted", zero_division=0),
                        "Balanced Accuracy": balanced_accuracy_score(truth, preds),
                        "Cohen kappa": r["kappa"]})

    st.success("Anotasi awal telah dikunci. Perbandingan dengan tiga model S1, S2, dan S3 tersedia.")
    st.subheader("Hasil kesepakatan dosen dengan tiga model terbaik")
    st.caption("S1: original only; S2: original + 783; S3: original + 1.050. "
               "Semua skor dihitung dari label dosen SEBELUM prediksi dibuka. "
               "Cohen's kappa di sini mengukur kesesuaian satu dosen dengan model, bukan inter-rater reliability dua dosen.")
    for c, key in zip(st.columns(3), keys):
        r = reports[key]
        with c:
            st.markdown(f"**{key} — {['Original only','Original + 783','Original + 1.050'][keys.index(key)]}**")
            st.metric("Label sama", f"{r['agree']} / {r['n']} ({r['p_o']:.1%})")
            st.metric("Label berbeda", r["disagree"])
            st.metric("Cohen's kappa", "Tidak terdefinisi" if r["kappa"] is None else f"{r['kappa']:.4f}")
    st.markdown("**Ringkasan metrik per model**")
    metdf = pd.DataFrame(metrics)
    st.dataframe(metdf, hide_index=True, width="stretch",
                 column_config={k: st.column_config.NumberColumn(format="%.4f")
                                for k in ("Accuracy", "Macro-F1", "Weighted-F1", "Balanced Accuracy", "Cohen kappa")})
    st.caption("Macro-F1 memberi bobot sama pada tujuh label. Perbandingan di sini adalah evaluasi, "
               "bukan pemilihan ulang champion berdasarkan data dosen.")

    st.markdown("**Tabel prediksi untuk setiap komentar**")
    visible_cols = ["ID", "Mahasiswa", "Komentar", "Label dosen awal",
                    "Prediksi S1", "Sama S1", "Prediksi S2", "Sama S2", "Prediksi S3", "Sama S3"]
    selected_filter = st.selectbox("Filter tabel perbandingan", ["Semua komentar", "Berbeda dari S1",
        "Berbeda dari S2", "Berbeda dari S3", "Berbeda dari salah satu model", "Ketiga model berbeda dari dosen"],
        key=f"compare_filter_{data['id']}")
    if selected_filter.startswith("Berbeda dari S"):
        k = selected_filter[-2:]
        visible = frame.loc[~frame[f"Sama {k}"]]
    elif selected_filter == "Berbeda dari salah satu model":
        visible = frame.loc[~frame[[f"Sama {k}" for k in keys]].all(axis=1)]
    elif selected_filter == "Ketiga model berbeda dari dosen":
        visible = frame.loc[~frame[[f"Sama {k}" for k in keys]].any(axis=1)]
    else:
        visible = frame
    st.dataframe(visible[visible_cols], hide_index=True, width="stretch")
    if visible.empty:
        st.info("Tidak ada komentar pada filter ini.")
    st.download_button("Unduh perbandingan ketiga model (CSV)", csv_bytes(frame),
                       file_name="perbandingan_dosen_S1_S2_S3.csv", mime="text/csv",
                       key=f"download_compare3_{data['id']}")

    st.subheader("Detail hasil evaluasi per skenario")
    tabs = st.tabs([f"{key} — hasil lengkap" for key in keys])
    for tab, key in zip(tabs, keys):
        r = reports[key]
        with tab:
            st.markdown(f"**Dosen vs {key}**")
            cols = st.columns(4)
            cols[0].metric("Komentar", r["n"])
            cols[1].metric("Label sama", f"{r['p_o']:.1%}")
            cols[2].metric("Label berbeda", r["disagree"])
            cols[3].metric("Cohen's kappa", "N/A" if r["kappa"] is None else f"{r['kappa']:.4f}")
            with st.expander(f"Rumus dan perhitungan Cohen's kappa — {key}"):
                st.latex(r"P_o=\frac{\text{jumlah label sama}}{N},\quad P_e=\sum_{c=1}^{7}\frac{n_{d,c}}{N}\frac{n_{m,c}}{N},\quad\kappa=\frac{P_o-P_e}{1-P_e}")
                st.write(f"N={r['n']}; label sama={r['agree']}; Pₒ={r['p_o']:.6f}; Pₑ={r['p_e']:.6f}.")
                if r["kappa"] is None:
                    st.info("Kappa tidak terdefinisi apabila Pₑ = 1.")
                else:
                    st.write(f"κ=({r['p_o']:.6f} − {r['p_e']:.6f}) / (1 − {r['p_e']:.6f}) = {r['kappa']:.6f}.")
                st.dataframe(pd.DataFrame({"Kategori": LABELS, "Jumlah label dosen": r["human_counts"],
                                           f"Jumlah prediksi {key}": r["model_counts"]}), hide_index=True)
            st.markdown(f"**Confusion matrix dosen vs {key}**")
            cm = pd.DataFrame(r["confusion_matrix"], index=LABELS, columns=LABELS)
            st.caption("Baris: label dosen awal; kolom: prediksi model. Label dosen tunggal bukan consensus ground truth.")
            st.dataframe(cm.style.background_gradient(cmap="Blues", axis=None).format("{:d}"), width="stretch")
            st.markdown(f"**Precision, Recall, F1, dan support per label — {key}**")
            pc = per_class[key]
            detail = pd.DataFrame([{"Kategori": label,
                "Precision": pc[label]["precision"], "Recall": pc[label]["recall"],
                "F1": pc[label]["f1-score"], "Support": int(pc[label]["support"])} for label in LABELS])
            st.dataframe(detail, hide_index=True, width="stretch",
                column_config={k: st.column_config.NumberColumn(format="%.4f")
                               for k in ("Precision", "Recall", "F1")})
            st.download_button(f"Unduh confusion matrix {key} (CSV)",
                cm.to_csv(index=True).encode("utf-8-sig"),
                file_name=f"confusion_dosen_{key}.csv", mime="text/csv", key=f"cm_{data['id']}_{key}")

    st.subheader("Tinjau komentar, XAI, dan adjudikasi")
    review_key = st.selectbox("Model yang ingin ditinjau", keys,
                             key=f"review_model_{data['id']}")
    show_diff = st.checkbox(f"Tampilkan hanya komentar berbeda untuk {review_key}",
                            key=f"diff3_{data['id']}_{review_key}")
    subset = frame.loc[~frame[f"Sama {review_key}"]] if show_diff else frame
    if subset.empty:
        st.info(f"Tidak ada komentar pada filter {review_key}.")
    else:
        selected = st.selectbox("Pilih komentar untuk penjelasan", subset["ID"].tolist(),
                                key=f"explain3_{data['id']}_{review_key}")
        row = next(r for r in data["rows"] if r["comment_id"] == selected)
        human = data["labels"][selected]
        idx = [r["comment_id"] for r in data["rows"]].index(selected)
        st.markdown("**Komentar**")
        st.write(row["comment"])
        if data["notes"].get(selected):
            st.markdown("**Alasan dosen sebelum prediksi dibuka**")
            st.write(data["notes"][selected])
        st.markdown("**Prediksi ketiga model untuk komentar ini**")
        st.dataframe(pd.DataFrame([{"Model": key, "Label prediksi": three[key][idx]["label"],
                     "Sama dengan dosen": three[key][idx]["label"] == human,
                     "Selisih skor tertinggi": three[key][idx]["gap"]} for key in keys]),
                     hide_index=True, width="stretch")
        current_model = service.models[review_key]
        ex = current_model.explain(row["comment"], against=human)
        st.write(disagreement_text(ex, human))
        with st.expander(f"Bukti kontribusi fitur model {review_key}",
                         expanded=human != three[review_key][idx]["label"]):
            display_xai(current_model, row["comment"], against=human)
        with st.expander("Catat adjudikasi (opsional)"):
            st.caption("Label ini dicatat setelah prediksi dibuka. Tidak mengubah label dosen awal "
                       "dan seluruh metrik perbandingan tetap memakai label dosen awal.")
            existing = data["adjudication"].get(selected, {})
            with st.form(f"adjudication3_{data['id']}_{selected}"):
                label = st.selectbox("Label akhir hasil peninjauan", LABELS,
                    index=LABELS.index(existing.get("label", human)),
                    key=f"adj3_label_{data['id']}_{selected}")
                note = st.text_area("Catatan peninjauan", value=existing.get("note", ""), max_chars=1500)
                submit = st.form_submit_button("Simpan adjudikasi")
            if submit:
                save_adjudication(data["id"], selected, label, note)
                st.rerun()

    with st.expander("Audit anotasi dan model (JSON)"):
        hashes = getattr(service, "hashes", {})
        st.json({"annotation_locked": data["locked"], "model_sha256": hashes,
                 "kappa_uses": "original_blind_labels", "scenarios": list(keys)})
    st.download_button("Unduh audit dan perhitungan S1–S3 (JSON)",
        json_bytes({"labels_order": LABELS, "reports": reports, "metrics": metrics,
                    "model_sha256": getattr(service, "hashes", {}),
                    "annotation": data, "formula": "kappa=(P_o-P_e)/(1-P_e); P_e=sum(p_dosen_c*p_model_c)",
                    "scope": "teacher_model_agreement; initial labels before model exposure"}),
        file_name="audit_dosen_S1_S2_S3.json", mime="application/json",
        key=f"audit3_{data['id']}")


def teacher_view(service):
    st.subheader("Anotasi dan evaluasi sebagai dosen")
    if st.session_state.pop("pcr_resume_just_done", False):
        st.session_state["teacher_activity"] = "Anotasi / evaluasi seperti sebelumnya"
    mode=st.radio("Aktivitas dosen",["Anotasi / evaluasi seperti sebelumnya", "Upload progres anotasi (lanjutkan)"],
                  horizontal=True,key="teacher_activity")
    if mode == "Upload progres anotasi (lanjutkan)":
        st.markdown("**Pulihkan hasil anotasi CSV dari aplikasi sebelumnya**")
        st.caption("Kolom ID, Mahasiswa, Komentar, dan Label dosen dibaca. Label yang sudah ada tidak ditimpa; prediksi tetap disembunyikan sampai anotasi dikunci.")
        teacher=st.text_input("Kode dosen untuk progres",value="DOSEN01-DEV",key="resume_teacher")
        uploaded=st.file_uploader("Unggah progres_anotasi_dev.csv",type="csv",key="resume_csv")
        if uploaded is not None:
            try:
                rows,labels,source=parse_progress_csv(uploaded)
                st.info(f"{len(rows)} komentar; {len(labels)} sudah diberi label; {len(rows)-len(labels)} belum dilabeli.")
                if st.button("Pulihkan dan lanjutkan anotasi",type="primary",key="do_resume"):
                    data=restore_progress(teacher,rows,labels,source)
                    st.session_state["active_annotation"]=data["id"]
                    st.session_state["pcr_resume_just_done"] = True
                    st.rerun()
            except (ValueError,UnicodeError,pd.errors.ParserError) as error:
                st.error(f"CSV tidak dapat dipulihkan: {error}")
        return
    if "next_annotation_pick" in st.session_state:
        key, value = st.session_state.pop("next_annotation_pick")
        st.session_state[key] = value
    if "annotation_saved_notice" in st.session_state:
        st.success(f"Label {st.session_state.pop('annotation_saved_notice')} berhasil disimpan.")
    if "active_annotation" not in st.session_state:
        teacher_setup()
        return
    data = get_annotation(st.session_state["active_annotation"])
    st.caption(f"{data['teacher']} · {data['source']} · {len(data['rows'])} komentar")
    st.button("Pilih data / dosen lain", on_click=start_teacher)
    if data["locked"]:
        teacher_comparison(data, service)
    else:
        teacher_blind(data, service)


def main():
    st.title("PCR · Code Quality Alignment")
    st.caption("Komentar lebih terarah pada rubrik, dengan perbandingan prediksi S1, S2, S3 dan penjelasan model.")
    try:
        service = model_service()
    except Exception as error:
        st.error(f"Model belum dapat dimuat: {error}")
        st.stop()
    role = st.radio("Saya menggunakan aplikasi sebagai", ["Mahasiswa", "Dosen"], horizontal=True, key="role")
    with st.sidebar:
        st.markdown("**Panduan rubrik**")
        for label in LABELS:
            with st.expander(label):
                st.write(DEFINITIONS[label])
                st.caption(BOUNDARIES[label])
        with st.expander("Tentang model & penjelasan"):
            st.write("S1: LinearSVC (SVM) + TF-IDF char; S2: LinearSVC + TF-IDF char; S3: LinearSVC + TF-IDF word")
            st.caption("Tiga model terbaik dipilih berdasarkan fixed 5-fold CV; tidak dilatih ulang oleh aplikasi.")
            st.caption("XAI = kontribusi TF-IDF × selisih koefisien kelas. Skor keputusan bukan persentase keyakinan.")
            st.caption("Selisih dua skor <0,25 memunculkan ajakan meninjau. Ambang ini adalah aturan prototipe dan belum dikalibrasi.")
            st.caption("Model membaca komentar; keputusan akhir tetap pada reviewer dan dosen.")
    if role == "Mahasiswa":
        student_view(service)
    else:
        teacher_view(service)


main()
