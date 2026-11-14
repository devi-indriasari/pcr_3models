# Tambahan 3-model untuk Streamlit PCR yang lama

## Kode lama TIDAK ditimpa

- `app.py` tetap kode aplikasi semula.
- `app_3models.py` adalah salinan aplikasi lama yang menambah prediksi dari S1/S2/S3 dan upload progres anotasi.
- `pcr/model.py`, `pcr/storage.py`, `pcr/datasets.py`, `pcr/feedback.py`, `pcr/rubrics.py`, `pcr/preprocessing.py` tetap dari aplikasi lama.
- Dua file tambahan: `pcr/multi_model.py` dan `pcr/annotation_import.py`.
- Data simulasi, source Java, database `runtime/pcr.sqlite3` (jika ada), dan audit lama tidak diubah/dihapus.

## Cara menjalankan

1. Backup folder Streamlit aktif, termasuk `runtime/pcr.sqlite3` jika ada. Ekstrak ZIP ini ke folder **baru**.
2. Masukkan **ketiga** file hasil Notebook 3 dalam satu folder yang sama. Paket mendukung dua lokasi:
   - `pcr_streamlit/models/` (struktur ZIP aplikasi lama) atau
   - `pcr_streamlit/app/models/` (struktur versi revisi yang pernah dipakai).
3. Nama file resmi Anda didukung tanpa rename:
   - `best_model_S1.joblib`, `best_model_S2.joblib`, `best_model_S3.joblib`.
   - Nama alternatif `champion_S1.joblib`, `champion_S2.joblib`, `champion_S3.joblib` juga didukung.
   - Metadata masing-masing `best_model_S1_metadata.json` dll disarankan disalin bersama model.
   - File `three_scenario_models_manifest.json` boleh tetap berada di folder yang sama; tidak perlu diubah.
4. Gunakan environment Python dengan versi dependency sesuai metadata model. Instal dependency `pip install -r requirements.txt`.
5. Jalankan dari folder `pcr_streamlit/`:

   ```bash
   streamlit run app_3models.py
   ```

6. **Jangan menjalankan `app.py`** jika ingin fitur 3 model, karena itu aplikasi asli tanpa penambahan.

## Fitur dipertahankan

Mahasiswa: contoh Java, enam rubrik, saran revisi, XAI (S1), simpan review, unduh bukti, review untuk dosen. Kini ada tabel hasil prediksi S1/S2/S3.

Dosen: 100 contoh simulasi, review mahasiswa terkirim, unggah dataset CSV, anotasi buta, penyimpanan progress pada SQLite, kunci anotasi, kesepakatan dan kappa, confusion matrix, adjudikasi, XAI (S1), unduh CSV dan audit JSON. Kini ada tabel dan metrics perbandingan ketiga model serta pilihan upload progres anotasi CSV.

## Upload progres anotasi dosen

1. Pilih peran Dosen.
2. Pilih radio `Upload progres anotasi (lanjutkan)`.
3. Isi kode dosen, misalnya `DOSEN01-DEV`.
4. Upload file `progres_anotasi_dev.csv` dari app lama (kolom `ID,Mahasiswa,Komentar,Label dosen`).
5. Klik `Pulihkan dan lanjutkan anotasi`.
6. Jika ada baris belum dilabeli, lanjutkan dari anotasi buta. Jika semua sudah dilabeli, klik `Kunci anotasi & bandingkan dengan model` untuk menampilkan perbandingan.

Import mempertahankan label yang sudah ada dan menolak konflik dengan data SQLite sebelumnya. Upload file tidak mengubah model dan tidak melatih ulang model. Prediksi tidak ditampilkan sebelum anotasi dikunci.

CSV progres yang diberikan pada percakapan berisi 100 komentar dan **100 label dosen**, sehingga setelah dipulihkan sudah lengkap dan langsung dapat dikunci untuk evaluasi.

## Peran model S1 dalam fitur lama

Agar seluruh fitur pedagogis lama, penjelasan XAI, serta format audit yang pernah diekspor tidak rusak, fitur coaching/XAI dan blok audit lama tetap menggunakan S1. Prediksi S1, S2, S3 dipresentasikan dalam tabel tambahan. Pada tab dosen, metrik untuk ketiga model dihitung ulang dari label awal dosen yang sama, bukan dari prediksi tersimpan aplikasi lama.

Catatan metodologis: Label dosen tunggal adalah pembanding sementara, bukan consensus expert ground truth. CSV 100 komentar tersebut adalah `synthetic_demo`.

## Uji yang dijalankan

- Validasi CSV 100 komentar; kesesuaian dengan demo awal.
- Restore penuh 100 label dan parsial 99 label tanpa overwrite; conflict protection.
- Smoke test inferensi dari tiga model dan XAI S1 menggunakan **model buatan sementara untuk uji**, bukan model penelitian Anda.
- Pemeriksaan sintaks seluruh file Python.

Tidak dilakukan end-to-end UI Streamlit langsung dalam lingkungan pembuatan ini karena Streamlit tidak tersedia. Model joblib resmi Anda tidak disertakan dalam ZIP.
