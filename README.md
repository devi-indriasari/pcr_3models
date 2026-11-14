# PCR · Code Quality Alignment

Aplikasi Streamlit dengan pilihan peran **Mahasiswa** dan **Dosen** untuk mendukung peer code review berdasarkan rubrik kualitas kode. Versi ini menggunakan **112 komentar sintetis berbahasa Indonesia**, **16 contoh kode dalam empat bahasa pemrograman**, dan **tiga model terbaik dari skenario S1, S2, dan S3**.

**File utama yang dijalankan adalah `app_3models_compare.py`.** Aplikasi memuat model yang sudah dilatih dan tidak melakukan pelatihan ulang.

## Ringkasan versi terbaru

| Komponen | Kondisi saat ini |
| --- | --- |
| Data bawaan dosen | `data/review_multibahasa_112.csv` |
| Jumlah komentar | 112 komentar, masing-masing menggunakan satu kode mahasiswa fiktif |
| Bahasa komentar | Bahasa Indonesia dengan gaya komentar mahasiswa |
| Bahasa kode yang direview | Java, C++, PHP, dan Python |
| Contoh kode | 16 file, yaitu 4 file per bahasa |
| Kategori klasifikasi | 7 kategori, satu label dominan per komentar |
| Isian rubrik mahasiswa | 6 kategori; General tidak menjadi kolom isian |
| Pemeriksaan komentar mahasiswa | Menggunakan model S1 dan penjelasan kontribusi fitur |
| Perbandingan oleh dosen | Label awal dosen dibandingkan dengan prediksi S1, S2, dan S3 pada komentar yang sama |

**112 kode mahasiswa pada tampilan berarti 112 pengenal mahasiswa fiktif, bukan 112 file source code.** Dataset ini menggunakan 16 contoh kode yang direview.

## Struktur file yang diperlukan

| File/folder | Fungsi |
| --- | --- |
| `app_3models_compare.py` | Aplikasi utama untuk mahasiswa dan perbandingan tiga model oleh dosen |
| `requirements.txt` | Dependensi Python beserta versi yang digunakan |
| `models/` | Ketiga model terlatih dan metadata pendukung |
| `pcr/` | Preprocessing, rubrik, prediksi, XAI, pembacaan data, penyimpanan, dan pemulihan anotasi |
| `data/review_multibahasa_112.csv` | Data bawaan 112 komentar untuk anotasi dosen |
| `java_examples/catalog.json` | Katalog 16 contoh kode beserta bahasa, judul, dan konteks tugas |
| `java_examples/` | File contoh kode Java, C++, PHP, dan Python |
| `.streamlit/config.toml` | Konfigurasi tampilan, jika disertakan dalam proyek |
| `runtime/pcr.sqlite3` | Database yang dibuat saat aplikasi menyimpan review atau anotasi |

Nama folder `java_examples/` dipertahankan agar sesuai dengan kode aplikasi, walaupun isinya mencakup empat bahasa pemrograman. Pertahankan nama file, ID kode, dan keterkaitan dalam `catalog.json`.

## Menjalankan aplikasi secara lokal

Gunakan **Python 3.12**. Ekstrak paket proyek, lalu buka terminal di folder yang memuat `app_3models_compare.py` dan `requirements.txt`.

Buat lingkungan virtual:

```bash
python -m venv .venv
```

Aktifkan lingkungan pada Windows melalui Command Prompt:

```bat
.venv\Scripts\activate.bat
```

Atau pada macOS/Linux:

```bash
source .venv/bin/activate
```

Pasang dependensi dan jalankan aplikasi:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app_3models_compare.py
```

Buka alamat yang muncul pada terminal, biasanya `http://localhost:8501`.

## Dataset 112 komentar multibahasa

Seluruh komentar merupakan data sintetis untuk bahan anotasi dan evaluasi eksploratif. Komentar tersebut bukan hasil pengumpulan dari 112 mahasiswa nyata.

| Bahasa kode | Contoh kode | Komentar | Target komentar per kategori |
| --- | ---: | ---: | ---: |
| Java | 4 | 28 | 4 |
| C++ | 4 | 28 | 4 |
| PHP | 4 | 28 | 4 |
| Python | 4 | 28 | 4 |
| **Total** | **16** | **112** | **16 per kategori** |

Distribusi kategori berikut adalah **rancangan target generasi**, bukan hasil anotasi pakar:

| Kategori | Target jumlah komentar |
| --- | ---: |
| Variable | 16 |
| Expression | 16 |
| Control Flow | 16 |
| Comment | 16 |
| Layout and Formatting | 16 |
| Decomposition | 16 |
| General | 16 |
| **Total** | **112** |

Setiap kombinasi bahasa–kategori ditargetkan berisi empat komentar. Distribusi label akhir dapat berubah setelah anotasi dan adjudikasi. Keseimbangan ini membantu perbandingan pada bahan yang sama, tetapi tidak menjamin kesetaraan tingkat kesulitan antarbahasa atau antarkategori.

CSV bawaan memiliki kolom:

| Kolom | Isi |
| --- | --- |
| `comment_id` | ID komentar yang unik |
| `student_id` | Kode mahasiswa fiktif |
| `code_id` | ID contoh kode yang cocok dengan katalog |
| `comment` | Teks komentar review dalam bahasa Indonesia |

Label target generasi tidak dimasukkan ke bahan anotasi. Arsip `PCR_Metadata_Target_Privat_112.zip`, jika tersedia, merupakan dokumentasi khusus pengelola dan **tidak diperlukan untuk menjalankan aplikasi**. Simpan terpisah dari repository aplikasi dan bahan yang diberikan kepada pakar sebelum anotasi independen dikunci. Target generasi tidak digunakan sebagai ground truth final.

## Enam belas contoh kode

Contoh kode sengaja menyediakan bagian yang dapat diapresiasi atau dikritisi. Gunakan kode dan konteks tugas untuk memeriksa ketepatan komentar. Menjalankan atau mengompilasi contoh kode tidak diperlukan untuk menjalankan Streamlit.

| ID | Bahasa | File | Konteks |
| --- | --- | --- | --- |
| ML_JAVA01 | Java | `TagihanKantin.java` | Pesanan kantin, diskon, dan struk |
| ML_JAVA02 | Java | `RekapPresensi.java` | Persentase kehadiran dan izin ujian |
| ML_JAVA03 | Java | `PeminjamanAlat.java` | Peminjaman, pengembalian, dan denda |
| ML_JAVA04 | Java | `PemesananLapangan.java` | Pemesanan dan pembatalan slot lapangan |
| ML_CPP01 | C++ | `parkir_kampus.cpp` | Durasi parkir dan perhitungan tarif |
| ML_CPP02 | C++ | `bank_sampah.cpp` | Berat setoran dan bukti penerimaan |
| ML_CPP03 | C++ | `antrian_cetak.cpp` | Antrean pekerjaan cetak dan biaya |
| ML_CPP04 | C++ | `kuota_internet.cpp` | Sisa kuota, peringatan, dan ringkasan pemakaian |
| ML_PHP01 | PHP | `pesanan_kopi.php` | Total pesanan dan bukti transaksi |
| ML_PHP02 | PHP | `pendaftaran_workshop.php` | Pendaftaran, pembatalan, dan biaya peserta |
| ML_PHP03 | PHP | `rekap_donasi.php` | Total donasi dan kemajuan target |
| ML_PHP04 | PHP | `katalog_buku.php` | Pencarian judul dan tahun terbit |
| ML_PY01 | Python | `ringkasan_cuaca.py` | Ringkasan suhu dan peringatan panas |
| ML_PY02 | Python | `daftar_belanja.py` | Daftar barang, penghapusan, dan diskon |
| ML_PY03 | Python | `pengeluaran_kos.py` | Pengeluaran, saldo, dan periode bulanan |
| ML_PY04 | Python | `jadwal_tugas.py` | Daftar tugas dan estimasi waktu |

Sebagian teks tombol dan penyorotan sintaks pada UI masih menyebut Java. Hal ini merupakan keterbatasan tampilan dari struktur aplikasi sebelumnya; bahasa setiap contoh dapat dilihat pada judul katalog dan ekstensi filenya.

## Untuk mahasiswa

1. Pilih **Mahasiswa** dan isi kode mahasiswa. Gunakan kode samaran untuk uji coba.
2. Baca contoh kode dan deskripsi tugasnya. Kode awal dipilih acak dan tetap selama interaksi. Tombol **Acak kode** mengganti kode dan mengosongkan isian komentar.
3. Isi enam komentar: **Variable, Expression, Control Flow, Comment, Layout and Formatting, Decomposition**. Panduan dan batas setiap kategori tersedia di samping isian. **General tidak menjadi kolom rubrik**, tetapi tetap dapat diprediksi model.
4. Klik **Periksa komentar**. Pemeriksaan mahasiswa menggunakan **model S1**. Setiap hasil menampilkan teks komentar yang masuk, prediksi, saran revisi, skor keputusan, dan kontribusi fitur.
5. Tinjau komentar yang berbeda fokus dari rubrik, terprediksi General, atau memiliki dua skor teratas yang berdekatan. Setelah mengedit, klik **Periksa komentar** lagi agar hasil sesuai dengan teks terbaru.
6. Jika prediksi menurut Anda keliru, gunakan bagian **Prediksi model menurut saya keliru** untuk mempertahankan komentar dengan alasan setelah meninjau kode dan rubrik. Perbedaan prediksi tidak otomatis berarti komentar mahasiswa salah.
7. Konfirmasikan pemeriksaan isi, lalu klik **Kirim review akhir**. Pesan berhasil, ID review, waktu WIB, dan unduhan bukti JSON ditampilkan. Review masuk ke sumber **Review mahasiswa terkirim** pada tampilan dosen.

Pemeriksaan awal tidak mengirim review. Tombol pengiriman akhir hanya aktif untuk enam komentar terbaru yang sudah diperiksa dan memenuhi konfirmasi yang diminta. Satu review menghasilkan enam komentar.

Kategori **Comment** membahas komentar atau dokumentasi di dalam source code, bukan kualitas kalimat peer review mahasiswa.

## Untuk dosen atau pakar

1. Pilih **Dosen**, lalu **Anotasi / evaluasi seperti sebelumnya** pada bagian **Aktivitas dosen**.
2. Isi kode dosen. Gunakan kode yang konsisten untuk pakar yang sama dan kode berbeda untuk pakar yang berbeda.
3. Pada **Sumber komentar**, pilih **112 komentar simulasi**. Pastikan tampilan menunjukkan **112 komentar · 112 kode mahasiswa**. Data bawaan dibaca langsung dari `data/review_multibahasa_112.csv`; tidak perlu mengunggah CSV secara manual.
4. Klik **Mulai / lanjutkan anotasi**. Baca komentar dan, jika diperlukan, buka **Lihat kode yang direview**.
5. Pilih satu dari tujuh kategori, tambahkan alasan jika diperlukan, lalu klik **Simpan label & berikutnya**. Memilih label tanpa menekan tombol simpan belum menyimpan anotasi.
6. Gunakan **Daftar komentar dan progres label** untuk meninjau pekerjaan. Unduh progres CSV secara berkala.
7. Setelah seluruh 112 komentar berlabel, klik **Kunci anotasi & bandingkan dengan model**. Prediksi disembunyikan sebelum penguncian agar tidak memengaruhi anotasi awal.
8. Lihat perbandingan label awal dosen dengan prediksi **S1, S2, dan S3**. Ketiga model dievaluasi pada komentar dan label dosen yang sama.
9. Gunakan filter perbedaan, tabel prediksi, confusion matrix, metrik per label, serta pilihan model untuk meninjau XAI per komentar.
10. Adjudikasi dapat dicatat pada kolom terpisah setelah peninjauan. Label awal dosen dan metrik yang memakai label awal tersebut dipertahankan.

Hasil yang tersedia mencakup jumlah label sama/berbeda, Accuracy, Macro-F1, Weighted-F1, Balanced Accuracy, Cohen’s kappa, serta Precision, Recall, F1, dan support per label. Unduhan mencakup `perbandingan_dosen_S1_S2_S3.csv`, confusion matrix tiap model, dan `audit_dosen_S1_S2_S3.json`.

Alasan dosen hanya ditampilkan jika ditulis oleh dosen. Aplikasi tidak menebak alasan pribadi dosen dari labelnya. XAI menjelaskan keluaran model yang dipilih.

### Sumber komentar lain

Selain data bawaan, dosen dapat memilih **Review mahasiswa terkirim** atau **Unggah CSV**. CSV komentar baru wajib memiliki kolom `comment_id`, `student_id`, dan `comment`; `code_id` bersifat opsional. Gunakan ID komentar unik dan satu baris untuk satu komentar. Agar kode dapat ditampilkan, nilai `code_id` harus cocok dengan ID pada katalog.

Gunakan **Unggah CSV** untuk memasukkan bahan komentar. Gunakan **Upload progres anotasi (lanjutkan)** untuk memulihkan label yang sudah dikerjakan. Kolom label/prediksi pada unggahan bahan komentar tidak dibawa ke anotasi buta.

## Menyimpan dan melanjutkan progres anotasi

Label disimpan ke database setiap kali **Simpan label & berikutnya** ditekan. Untuk melanjutkan progres yang masih tersimpan, buka alur anotasi biasa dengan **kode dosen dan dataset yang sama**. Jangan mengubah ID, teks, atau urutan dataset jika ingin membuka sesi anotasi yang sama.

Untuk memulihkan progres dari CSV:

1. Pilih **Dosen → Upload progres anotasi (lanjutkan)**.
2. Isi **Kode dosen untuk progres** sesuai pengenal pakar yang dituju.
3. Unggah file hasil **Unduh progres anotasi (CSV)**. Ekspor aplikasi memuat kolom `ID`, `Mahasiswa`, `Komentar`, dan `Label dosen`.
4. Periksa jumlah seluruh komentar, komentar berlabel, dan komentar yang belum dilabeli.
5. Klik **Pulihkan dan lanjutkan anotasi**, lalu lanjutkan pelabelan yang belum selesai.

Gunakan CSV progres yang memuat seluruh 112 baris, termasuk komentar yang labelnya masih kosong. Jika ID dan teks cocok dengan dataset bawaan, aplikasi dapat menghubungkannya kembali dengan contoh kode terkait.

Pemulihan CSV berfokus pada label anotasi. Ekspor progres bukan cadangan lengkap untuk alasan penilaian, adjudikasi, prediksi, dan status penguncian. Simpan audit JSON dan cadangan database bila informasi tersebut perlu dipertahankan.

### Jika label CSV berbeda dari data tersimpan

Pesan **Label CSV berbeda dari progres yang sudah tersimpan** menunjukkan konflik antara label dalam CSV dan label pada database untuk ID tertentu. Pemulihan dihentikan agar label tersimpan tidak tertimpa otomatis.

Untuk melihat versi pada database, buka **Anotasi / evaluasi seperti sebelumnya**, masukkan kode dosen yang sama, pilih dataset yang sama, lalu klik **Mulai / lanjutkan anotasi**. Buka ID yang disebut dalam pesan melalui **Pilih komentar** atau daftar progres.

Jika anotasi belum dikunci, tinjau perbedaan dengan CSV, perbaiki label melalui formulir, simpan, lalu unduh progres terbaru. Jika CSV perlu dipertahankan sebagai salinan terpisah, pulihkan menggunakan kode yang jelas, misalnya `DOSEN01_SALINAN_CSV`. Salinan tersebut tetap berasal dari pakar yang sama dan bukan anotasi pakar tambahan. Label awal yang sudah dikunci dipertahankan; hasil peninjauan sesudahnya dicatat melalui adjudikasi.

## Tiga model dan preprocessing

| Skenario | Data pelatihan | Model dan representasi teks | File model |
| --- | --- | --- | --- |
| S1 | Data asli | LinearSVC + TF-IDF karakter | `models/best_model_S1.joblib` |
| S2 | Data asli + 783 komentar augmentasi | LinearSVC + TF-IDF karakter | `models/best_model_S2.joblib` |
| S3 | Data asli + 1.050 komentar augmentasi | LinearSVC + TF-IDF kata | `models/best_model_S3.joblib` |

Ketiga konfigurasi dipilih berdasarkan fixed 5-fold cross-validation pada data validasi asli. Data test tidak digunakan untuk memilih konfigurasi. Perbandingan pada anotasi dosen merupakan evaluasi tambahan, bukan pemilihan ulang model berdasarkan label dosen.

Metadata tiap skenario berada pada `models/best_model_S1_metadata.json`, `models/best_model_S2_metadata.json`, dan `models/best_model_S3_metadata.json`. Loader juga mendukung nama alternatif `champion_S1.joblib`, `champion_S2.joblib`, dan `champion_S3.joblib` jika ketiganya tersedia pada folder model yang sama. Pertahankan seluruh file pendukung dari paket proyek.

Versi scikit-learn dikunci ke **1.6.1**, sesuai artefak model. Gunakan `requirements.txt` proyek agar versi dependensi konsisten. Aplikasi memeriksa kecocokan versi saat memuat model.

Preprocessing mengikuti implementasi Notebook 3: penyesuaian kata uppercase, penghapusan URL, penghapusan HTML setelah unescape, penghapusan emoji, dan normalisasi whitespace. Tidak ada stopword removal atau stemming tambahan. Lowercase mengikuti vectorizer terlatih. Urutan koefisien dan skor mengikuti `classifier.classes_`.

Model membaca **teks komentar**, bukan source code. Kode ditampilkan sebagai konteks bagi mahasiswa dan dosen. Dukungan contoh empat bahasa tidak berarti model melakukan analisis statis atau eksekusi program pada empat bahasa tersebut.

## Cara kerja XAI dan saran revisi

Model menggunakan fitur TF-IDF dan LinearSVC, bukan LLM. S1 dan S2 menggunakan fitur karakter, sedangkan S3 menggunakan fitur kata. Untuk kelas `c`, skor keputusan dihitung sebagai:

```text
score_c = bias_c + Σ(TF-IDF_j × coefficient_c,j)
```

Untuk membandingkan kelas prediksi `p` dengan kelas pembanding `r`:

```text
score_p − score_r
  = (bias_p − bias_r) + Σ[TF-IDF_j × (coefficient_p,j − coefficient_r,j)]
```

Aplikasi menghitung kontribusi dari koefisien model yang dipilih. Kontribusi seluruh fitur dan selisih bias direkonstruksi untuk memeriksa kesesuaiannya dengan selisih skor. Tabel XAI menampilkan beberapa fitur paling berpengaruh; jumlah kontribusi memakai seluruh fitur aktif. Fitur karakter dapat tumpang tindih dan bukan alasan semantik yang lengkap.

**Skor LinearSVC bukan probabilitas.** Selisih dua skor teratas di bawah `0.25` memunculkan ajakan meninjau. Ambang tersebut merupakan aturan kerja prototipe yang belum dikalibrasi sebagai ukuran ketidakpastian.

Saran revisi mengikuti aturan pedagogis berdasarkan definisi rubrik dan dipisahkan dari bukti XAI. Penjelasan model dan saran tidak membuktikan bahwa penilaian mahasiswa benar terhadap source code.

## Perhitungan kesepakatan dosen–model

Tujuh kategori bersifat nominal. Untuk masing-masing model S1, S2, dan S3, aplikasi menghitung Cohen’s kappa tanpa bobot ordinal:

```text
P_o = jumlah label dosen yang sama dengan prediksi / N
P_e = Σ_c [(jumlah label dosen c / N) × (jumlah prediksi c / N)]
kappa = (P_o − P_e) / (1 − P_e)
```

Untuk dataset bawaan yang sudah selesai dianotasi, `N = 112`. Jika menggunakan dataset unggahan lain, `N` mengikuti jumlah komentar pada dataset tersebut. Jika `P_e = 1`, kappa tidak terdefinisi dan tidak otomatis bernilai 1.

Yang diukur adalah **kesepakatan satu dosen dengan masing-masing model**. Nilai ini berbeda dari inter-rater reliability antara dua pakar manusia. Label dosen awal menjadi pembanding dan tidak otomatis merupakan consensus ground truth. Adjudikasi yang dilakukan setelah melihat prediksi tidak menggantikan label awal dalam metrik perbandingan.

Evaluasi pada 112 komentar sintetis perlu dilaporkan sebagai evaluasi pada data sintetis. Hasilnya tidak langsung menunjukkan kinerja pada komentar mahasiswa nyata atau generalisasi pada seluruh bahasa pemrograman. Target generasi dan prediksi model tidak menggantikan anotasi independen pakar.

## Mengunggah ke GitHub dan Streamlit Community Cloud

1. Unggah isi proyek yang sudah diekstrak ke repository GitHub dengan struktur subfolder tetap utuh. Letakkan `app_3models_compare.py` dan `requirements.txt` pada tingkat utama repository.
2. Sertakan `models/`, `pcr/`, `data/review_multibahasa_112.csv`, `java_examples/` beserta katalog dan seluruh contoh kode, serta konfigurasi `.streamlit/` jika digunakan.
3. Simpan `runtime/`, `.venv/`, cache Python, file rahasia, progres anotasi pakar, dan metadata target privat di luar unggahan repository.
4. Buka [Streamlit Community Cloud](https://share.streamlit.io/), hubungkan akun GitHub, lalu pilih **Create app** dan repository proyek.
5. Pilih branch yang sesuai, isi **Main file path** dengan `app_3models_compare.py`, lalu pilih **Python 3.12** pada **Advanced settings**.
6. Klik **Deploy**. Setelah aplikasi aktif, uji kedua peran dan pastikan data bawaan dosen menunjukkan 112 komentar.

Saat berpindah server, database anotasi lokal tidak otomatis ikut dipindahkan. Unduh progres sebelum perpindahan. Penyimpanan lokal pada Streamlit Community Cloud tidak dijamin permanen; gunakan ekspor berkala atau penyimpanan persisten untuk penggunaan berkelanjutan.

## Penyimpanan dan batas penggunaan prototipe

Review dan anotasi tersimpan dalam SQLite pada `runtime/pcr.sqlite3`. Lokasinya dapat diganti melalui environment variable `PCR_DB_PATH`. Folder runtime dibuat saat dibutuhkan. Untuk cadangan database lengkap, hentikan aplikasi terlebih dahulu agar tidak ada proses penulisan yang sedang berlangsung.

Pilihan peran hanya mengganti UI dan **belum mencakup login atau pembatasan akses berdasarkan akun**. Kode dosen merupakan pengenal anotasi, bukan kata sandi. Untuk penggunaan nyata pada server bersama, tambahkan autentikasi, otorisasi, dan penyimpanan yang sesuai.

Instalasi awal memerlukan internet untuk memasang dependensi. Inferensi model tidak memerlukan API LLM.

## Mengatasi ketidaksesuaian versi 100 dan 112 komentar

| Gejala | Pemeriksaan dan tindakan |
| --- | --- |
| Masih mencari `data/demo_comments_100.csv` | Loader lama masih dipakai. Gunakan versi terbaru `pcr/datasets.py` yang membaca `review_multibahasa_112.csv`. Mengganti nama atau menghapus CSV saja tidak memperbarui loader. |
| Menu bawaan masih menyebut 100 komentar | Pastikan yang dijalankan adalah versi terbaru `app_3models_compare.py`, lalu hentikan dan jalankan ulang Streamlit. |
| Data 112 tidak ditemukan | Periksa keberadaan `data/review_multibahasa_112.csv` dan kecocokan huruf besar-kecil nama file. |
| Pemulihan progres tidak sesuai versi terbaru | Pastikan `pcr/annotation_import.py` diperbarui bersama file utama dan loader dataset. |

Paket perbaikan default 112 memperbarui `app_3models_compare.py`, `pcr/datasets.py`, dan `pcr/annotation_import.py`. Timpa file terkait pada lokasinya; pertahankan modul lain dalam folder `pcr/`. File `demo_comments_100.csv` tidak diperlukan oleh loader versi ini.

## Pengujian pengembangan

Jika folder `tests/` dan `requirements-dev.txt` disertakan, pengujian dapat dijalankan melalui:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest tests -q
```

Pemeriksaan yang relevan meliputi pembacaan dataset, keterkaitan ID kode, inferensi model, rekonstruksi XAI, perhitungan kappa, penyimpanan anotasi, penguncian label awal, dan alur pengiriman review.

## Referensi teknis

- [LinearSVC, scikit-learn 1.6](https://scikit-learn.org/1.6/modules/generated/sklearn.svm.LinearSVC.html)
- [Cohen’s kappa, scikit-learn 1.6](https://scikit-learn.org/1.6/modules/generated/sklearn.metrics.cohen_kappa_score.html)
- [Pengujian aplikasi Streamlit](https://docs.streamlit.io/develop/api-reference/app-testing)
- [Deployment Streamlit Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
- [Organisasi file Streamlit Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization)
- [Penyimpanan file pada Streamlit Community Cloud](https://docs.streamlit.io/develop/concepts/configuration/serving-static-files)
