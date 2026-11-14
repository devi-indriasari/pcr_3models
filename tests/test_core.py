import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import cohen_kappa_score

from pcr.datasets import csv_bytes, demo_rows, java_catalog, java_source, validate_frame
from pcr.feedback import coaching
from pcr.metrics import agreement_report
from pcr.preprocessing import clean_text
from pcr.rubrics import LABELS, RUBRICS
from pcr.storage import (get_annotation, lock_annotation, open_annotation, save_adjudication,
                         save_label, save_review, submitted_rows)


def test_training_preprocessing_policy():
    assert clean_text('NAMA\n<b>saldo</b> &amp; TOTAL 😀 https://contoh.id') == 'Nama saldo & Total'
    assert clean_text('  nilaiRataRata / 2.0;\n\tbaik  ') == 'nilaiRataRata / 2.0; baik'
    # Tidak menghilangkan stopword Indonesia atau menambahkan stemming.
    assert clean_text('yang tidak konsisten dan kurang jelas') == 'yang tidak konsisten dan kurang jelas'


def test_attached_pipeline_is_the_predictor(service):
    texts = [r['comment'] for r in demo_rows()]
    results = service.predict(texts)
    assert [r['label'] for r in results] == service.pipeline.predict([clean_text(x) for x in texts]).tolist()
    assert set(service.classes) == set(LABELS)
    assert service.fingerprint == 'f53bc15f425166545b16e30f8afdb488e758106d6051c79db904429feea6e565'
    assert service.vectorizer.ngram_range == (2, 5)


@pytest.mark.parametrize('against', LABELS)
def test_xai_is_exact_not_keyword_rationale(service, against):
    ex = service.explain('Nama totalBelanja jelas, tetapi rumus 10 / 100 menghasilkan diskon nol.', against)
    assert np.isclose(ex['reconstructed'], ex['score_difference'], atol=1e-10)
    shown_sum = sum(r['difference'] for r in ex['positive'] + ex['negative'])
    assert np.isclose(shown_sum + ex['other_contribution'], ex['contribution_sum'])
    assert ex['against'] != ex['label']
    assert all(r['fragment'] in ex['cleaned'].lower() for r in ex['positive'] + ex['negative'])


def test_no_known_features_and_empty_input(service):
    pred = service.predict(['q'])[0]
    assert pred['known_features'] == 0
    assert coaching(pred, 'Variable')['needs_review']
    ex = service.explain('q')
    assert ex['contribution_sum'] == 0
    assert ex['reconstructed'] == ex['intercept_difference']
    with pytest.raises(ValueError):
        service.predict(['https://contoh.id 😀'])


@pytest.mark.parametrize('human,model', [
    (['Variable','Variable','Comment','Comment'], ['Variable','Comment','Variable','Comment']),
    (LABELS * 3, LABELS * 3),
    (LABELS * 2, LABELS[::-1] * 2),
])
def test_kappa_matches_independent_sklearn(human, model):
    report = agreement_report(human, model)
    assert np.isclose(report['kappa'], cohen_kappa_score(human, model, labels=LABELS))
    assert report['agree'] + report['disagree'] == len(human)


def test_kappa_empty_invalid_and_degenerate():
    assert agreement_report(['General'] * 4, ['General'] * 4)['kappa'] is None
    with pytest.raises(ValueError):
        agreement_report([], [])
    with pytest.raises(ValueError):
        agreement_report([''], ['General'])
    with pytest.raises(ValueError):
        agreement_report(['General'], LABELS)


def test_demo_is_100_fictional_students_and_10_codes():
    rows = demo_rows()
    assert len(rows) == len({r['comment_id'] for r in rows}) == len({r['student_id'] for r in rows}) == 100
    assert len({r['comment'] for r in rows}) == 100
    assert len(java_catalog()) == 10
    assert all(java_source(r['code_id']) for r in rows)
    assert all('label' not in k.lower() and 'prediction' not in k.lower() for r in rows for k in r)


def test_uploaded_labels_are_not_leaked_and_invalid_rows_rejected():
    frame = pd.DataFrame([{'comment_id':'C1','student_id':'M1','comment':'Sudah cukup baik.', 'Label_Target_LLM':'General'}])
    assert 'Label_Target_LLM' not in validate_frame(frame)[0]
    with pytest.raises(ValueError):
        validate_frame(pd.concat([frame,frame]))
    with pytest.raises(ValueError):
        validate_frame(frame.assign(comment=''))
    with pytest.raises(ValueError):
        validate_frame(frame.assign(comment='www.example.com'))


def test_csv_export_escapes_formulas():
    output = csv_bytes(pd.DataFrame({'comment':['=1+1','  @value','Normal']})).decode('utf-8-sig')
    assert "'=1+1" in output and "'  @value" in output


def test_submission_and_blind_annotation_are_persisted(service):
    payload = save_review('R1', 'M1', 'JAVA01', {'comments':{r:f'Komentar untuk {r}' for r in RUBRICS}})
    rows = submitted_rows()
    assert len(rows) == 6 and payload['review_id'] == 'R1'
    assert all(r['data_origin']=='student_submission' for r in rows)
    data = open_annotation('D1', rows, 'student_submission')
    assert open_annotation('D1', rows, 'student_submission')['id'] == data['id']
    predictions = service.predict([r['comment'] for r in rows])
    with pytest.raises(ValueError, match='Lengkapi'):
        lock_annotation(data['id'], predictions, service.fingerprint)
    for i, row in enumerate(rows):
        save_label(data['id'], row['comment_id'], LABELS[i])
    # Urutan komentar salah tidak boleh dikunci.
    with pytest.raises(ValueError, match='urutan'):
        lock_annotation(data['id'], predictions[::-1], service.fingerprint)
    locked = lock_annotation(data['id'], predictions, service.fingerprint)
    first_labels = dict(locked['labels'])
    with pytest.raises(ValueError, match='dikunci'):
        save_label(data['id'], rows[0]['comment_id'], 'General')
    save_adjudication(data['id'], rows[0]['comment_id'], 'General', 'Ditinjau setelah model dibuka')
    final = get_annotation(data['id'])
    assert final['labels'] == first_labels
    assert final['adjudication'][rows[0]['comment_id']]['after_model_exposure']
