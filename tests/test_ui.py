from pathlib import Path
from streamlit.testing.v1 import AppTest

from pcr.rubrics import RUBRICS, slug
from pcr.storage import get_annotation, save_label, submitted_rows

APP = str(Path(__file__).resolve().parents[1] / 'app.py')
TEXTS = {
    'Variable': 'Nama variabel h kurang jelas; ganti menjadi hargaSatuan agar maksud datanya terlihat.',
    'Expression': 'Perhitungan 10 / 100 memakai integer sehingga diskon selalu nol. Gunakan 0.10 untuk mendapatkan pecahan.',
    'Control Flow': 'Tambahkan percabangan untuk menolak jumlah barang negatif sebelum loop dijalankan.',
    'Comment': 'Komentar di dalam kode menyebut pajak tetapi dokumentasinya tidak sesuai karena tidak ada perhitungan pajak.',
    'Layout and Formatting': 'Indentasi loop pencetakan tidak konsisten dan spasi di sekitar operator perlu dirapikan.',
    'Decomposition': 'Pisahkan perhitungan total dan pencetakan struk ke method berbeda agar setiap method memiliki tanggung jawab jelas.',
}


def app():
    value = AppTest.from_file(APP, default_timeout=30).run()
    assert not value.exception
    return value


def fill_student(at):
    at.text_input(key='student_identifier').set_value('MHS999').run()
    at.selectbox(key='student_code').select('JAVA01').run()
    for label in RUBRICS:
        at.text_area(key=f'student_text_{slug(label)}').set_value(TEXTS[label])
    at.run()
    at.button(key='student_check').click().run()
    assert not at.exception


def authorize_human_review(at):
    flagged = [r for r, value in at.session_state['draft']['analysis'].items() if value['coaching']['needs_review']]
    if flagged:
        at.checkbox(key='student_override').check()
        at.text_area(key='student_override_reason').set_value('Saya telah membaca kode dan menilai bukti teknis sesuai dengan masing-masing rubrik.')
    at.checkbox(key='student_confirm').check().run()


def test_student_recheck_and_final_submission():
    at = app()
    assert len(at.text_area) == 6
    assert at.button(key='student_submit').disabled
    fill_student(at)
    draft = at.session_state['draft']
    for label in RUBRICS:
        assert draft['analysis'][label]['prediction']['text'] == TEXTS[label]
    authorize_human_review(at)
    assert not at.button(key='student_submit').disabled
    # Perubahan satu karakter harus menghapus hasil pemeriksaan lama.
    at.text_area(key='student_text_variable').set_value(TEXTS['Variable'] + ' Harap diperbaiki.').run()
    assert at.session_state['draft']['analysis'] is None
    assert at.button(key='student_submit').disabled
    at.button(key='student_check').click().run()
    authorize_human_review(at)
    at.button(key='student_submit').click().run()
    assert not at.exception
    assert any('Review berhasil dikirim' in x.value for x in at.success)
    assert len(submitted_rows()) == 6
    at.run()
    assert len(submitted_rows()) == 6  # Rerun tidak mengirim duplikat.


def test_role_switch_preserves_comments_and_code_change_resets():
    at = app()
    at.text_area(key='student_text_variable').set_value('Nama hargaSatuan sudah jelas.').run()
    at.radio(key='role').set_value('Dosen').run()
    assert not at.exception
    at.radio(key='role').set_value('Mahasiswa').run()
    assert at.text_area(key='student_text_variable').value == 'Nama hargaSatuan sudah jelas.'
    code = 'JAVA02' if at.selectbox(key='student_code').value != 'JAVA02' else 'JAVA03'
    at.selectbox(key='student_code').select(code).run()
    assert all(x.value=='' for x in at.text_area)
    assert at.session_state['draft']['analysis'] is None


def test_teacher_blind_annotation_lock_compare_and_resume():
    at = app()
    at.radio(key='role').set_value('Dosen').run()
    next(b for b in at.button if b.label=='Mulai / lanjutkan anotasi').click().run()
    assert not at.exception
    set_id = at.session_state['active_annotation']
    data = get_annotation(set_id)
    assert len(data['rows']) == 100
    assert not data['locked'] and 'predictions' not in data
    assert not at.metric
    assert at.button(key='teacher_compare').disabled
    label_widget = next(x for x in at.selectbox if x.label=='Label dosen')
    label_widget.select('Variable')
    next(b for b in at.button if b.label=='Simpan label & berikutnya').click().run()
    assert not at.exception
    data = get_annotation(set_id)
    assert len(data['labels']) == 1
    # Lengkapi entri lain lewat penyimpanan yang sama tanpa membuka prediksi.
    for row in data['rows']:
        if row['comment_id'] not in data['labels']:
            save_label(set_id, row['comment_id'], 'General', 'Anotasi uji, bukan label pakar.')
    at.run()
    assert not at.button(key='teacher_compare').disabled
    at.button(key='teacher_compare').click().run()
    assert not at.exception
    assert get_annotation(set_id)['locked']
    assert len(at.metric) == 4
    assert any(x.label=='Cohen’s κ' for x in at.metric)
    # Sesi baru dapat membuka anotasi tersimpan menggunakan dosen dan dataset yang sama.
    other = app()
    other.radio(key='role').set_value('Dosen').run()
    next(b for b in other.button if b.label=='Mulai / lanjutkan anotasi').click().run()
    assert not other.exception
    assert other.session_state['active_annotation'] == set_id
    assert len(other.metric) == 4
