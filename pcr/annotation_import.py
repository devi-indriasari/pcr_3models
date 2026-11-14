"""Import old progress CSV into the existing SQLite annotation workflow, never overwrite labels."""
import pandas as pd
import json
from .datasets import demo_rows, validate_frame
from .rubrics import LABELS
from .storage import open_annotation, connection, now


def parse_progress_csv(uploaded):
    frame=pd.read_csv(uploaded,dtype=str,keep_default_na=False,encoding="utf-8-sig")
    frame.columns=[str(c).strip() for c in frame.columns]
    if frame.empty or len(frame)>5000:
        raise ValueError("CSV harus memuat 1 sampai 5000 komentar.")
    def field(*aliases,mandatory=True):
        for alias in aliases:
            if alias in frame.columns:
                return alias
        if mandatory:
            raise ValueError("Kolom CSV tidak ditemukan: " + " / ".join(aliases))
    id_col=field("ID","comment_id","Comment_ID","Candidate_ID")
    comment_col=field("Komentar","comment","Komen Mahasiswa","komen mahasiswa")
    student_col=field("Mahasiswa","student_id","Student_ID",mandatory=False)
    label_col=field("Label dosen","Label dosen awal","label_dosen","Verified_Label",mandatory=False)
    code_col=field("Kode","code_id",mandatory=False)
    ids=frame[id_col].str.strip()
    if ids.eq("").any() or ids.duplicated().any():
        raise ValueError("ID komentar kosong atau duplikat")
    if frame[comment_col].str.strip().eq("").any():
        raise ValueError("Komentar kosong")
    invalid=set(frame[label_col].str.strip())-set(LABELS)-{""} if label_col else set()
    if invalid:
        raise ValueError("Label tidak dikenal: " + ", ".join(sorted(invalid)))
    # Matching built-in dataset: retain code_id/data_origin when restoring progress.
    # A missing optional default file must not block restoration of another valid CSV.
    try:
        demo=demo_rows()
    except (OSError,ValueError,UnicodeError,pd.errors.ParserError):
        demo=[]
    lookup={r["comment_id"]:r for r in demo}
    demo_exact=bool(demo) and len(frame)==len(demo) and all(i in lookup and lookup[i]["comment"].strip()==text.strip()
                          for i,text in zip(ids,frame[comment_col]))
    if demo_exact:
        rows=[lookup[i] for i in ids]
        source=f"{len(demo)} komentar simulasi"
    else:
        records=[]
        for i in range(len(frame)):
            records.append({"comment_id":ids.iloc[i],
                "student_id":str(frame[student_col].iloc[i]).strip() if student_col else f"MHS{i+1:03d}",
                "comment":str(frame[comment_col].iloc[i]).strip(),
                "code_id":str(frame[code_col].iloc[i]).strip() if code_col else ""})
        if any(not r["student_id"] for r in records):
            raise ValueError("Kode mahasiswa kosong")
        rows=validate_frame(pd.DataFrame(records),"uploaded_progress")
        source="Upload progres anotasi CSV"
    labels={i:str(v).strip() for i,v in zip(ids,frame[label_col]) if str(v).strip()} if label_col else {}
    return rows,labels,source


def restore_progress(teacher,rows,labels,source):
    if not teacher.strip():
        raise ValueError("Kode dosen harus diisi")
    data=open_annotation(teacher,rows,source)
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        row=db.execute("SELECT payload FROM annotation_sets WHERE id=?",(data["id"],)).fetchone()
        current=json.loads(row[0])
        if current["locked"]:
            # Avoid changing existing locked expert labels.
            conflicts=[i for i,label in labels.items() if current["labels"].get(i)!=label]
            if conflicts:
                raise ValueError("Anotasi sudah dikunci dan CSV berbeda: "+", ".join(conflicts[:5]))
            return current
        conflicts=[i for i,label in labels.items() if i in current["labels"] and current["labels"][i]!=label]
        if conflicts:
            raise ValueError("Label CSV berbeda dari progres yang sudah tersimpan pada ID: "+", ".join(conflicts[:10])+
                             ". Tidak ada label yang ditimpa.")
        allowed={r["comment_id"] for r in rows}
        if set(labels)-allowed:
            raise ValueError("Ada label di luar ID dataset")
        current["labels"].update(labels)
        current["updated"]=now()
        db.execute("UPDATE annotation_sets SET payload=?,updated=? WHERE id=?",
                   (json.dumps(current,ensure_ascii=False),current["updated"],current["id"]))
    return current
