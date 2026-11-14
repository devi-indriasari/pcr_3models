# PCR · Code Quality Alignment

Aplikasi Streamlit sederhana dengan satu halaman dan pilihan peran **Mahasiswa** atau **Dosen**. Model terbaik dari unggahan sudah disertakan: **LinearSVC + TF-IDF karakter 2–5**, tanpa pelatihan ulang.

## Menjalankan aplikasi

Gunakan **Python 3.12**. Ekstrak ZIP, lalu buka terminal di folder `pcr_streamlit`.

```bash
python -m venv .venv
```

Aktifkan lingkungan:

Windows:

```powershell
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Pasang dependensi dan jalankan:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Buka alamat yang muncul pada terminal, biasanya `http://localhost:8501`. Pada Windows, Anda juga dapat menjalankan `run_windows.bat` jika Python 3.12 tersedia melalui perintah `py`.

## Untuk mahasiswa

1. Pilih **Mahasiswa** dan isi kode mahasiswa. Gunakan kode samaran untuk uji coba.
2. Baca contoh kode Java dan deskripsi tugasnya. Kode awal dipilih acak; pilihan tetap selama interaksi. **Acak kode** mengganti kode dan mengosongkan isian komentar.
3. Isi enam komentar: **Variable, Expression, Control Flow, Comment, Layout and Formatting, Decomposition**. Deskripsi dan batas setiap kategori tersedia di samping isian. **General tidak menjadi kolom rubrik**, tetapi tetap dapat diprediksi model.
4. Klik **Periksa komentar**. Setiap hasil menampilkan komentar asli yang masuk, prediksi, saran revisi, skor keputusan, dan bukti kontribusi fitur.
5. Perbaiki komentar yang berbeda fokus, terprediksi General, atau memiliki dua skor teratas yang berdekatan. Setelah mengedit, klik **Periksa komentar** lagi. Hasil lama otomatis tidak berlaku.
6. Bila prediksi menurut Anda keliru, bagian **Prediksi model menurut saya keliru** memungkinkan Anda mempertahankan komentar dengan alasan setelah meninjau kode/rubrik. Keputusan ini ikut dicatat, bukan dianggap sebagai kegagalan mahasiswa.
7. Konfirmasikan pemeriksaan isi, lalu klik **Kirim review akhir**. Pesan berhasil, ID review, waktu WIB, dan unduhan bukti JSON ditampilkan. Review masuk ke daftar komentar yang dapat dipilih dosen.

Pemeriksaan awal tidak mengirim review. Tombol pengiriman akhir hanya aktif untuk enam komentar terbaru yang sudah diperiksa. Satu review menghasilkan enam komentar dan tidak dikirim ulang hanya karena halaman melakukan rerun.

## Untuk dosen

1. Pilih **Dosen**, isi kode dosen, dan pilih sumber komentar.
2. **100 komentar simulasi** memuat satu komentar untuk masing-masing 100 mahasiswa fiktif. Semuanya teks sintetis yang baru disusun untuk demonstrasi, bukan komentar dari mahasiswa nyata. Tidak ada label target generasi di dataset.
3. Anda juga dapat memilih **Review mahasiswa terkirim** atau **Unggah CSV**. Kolom wajib CSV: `comment_id`, `student_id`, `comment`. `code_id` opsional. ID komentar wajib unik; satu baris untuk satu komentar. Kolom label/prediksi lain di CSV tidak ditampilkan dalam anotasi buta.
4. Klik **Mulai / lanjutkan anotasi**. Pilih komentar, tentukan satu dari tujuh label, lalu klik **Simpan label & berikutnya**. Alasan penilaian dapat ditulis. Progres disimpan ke database pada setiap klik simpan. Daftar seluruh komentar dan progres label dapat dibuka di bawah formulir.
5. Gunakan kode dosen dan dataset yang sama untuk melanjutkan anotasi tersimpan, termasuk dari sesi browser baru. Keadaan label pada formulir yang belum ditekan **Simpan** belum menjadi anotasi tersimpan.
6. Setelah seluruh komentar dilabeli, klik **Kunci anotasi & bandingkan dengan model**. Prediksi disembunyikan sebelum tahap ini. Label awal dikunci agar perbandingan tidak berubah karena dosen telah melihat keluaran model.
7. Lihat jumlah kesepakatan, Cohen’s kappa, matriks perbandingan, dan penjelasan per komentar. Untuk label berbeda, XAI membandingkan kelas prediksi dengan label dosen.
8. Adjudikasi opsional dicatat pada kolom terpisah. Label awal dan kappa awal dipertahankan. Ekspor hasil CSV dan audit JSON tersedia.

Alasan dosen hanya ditampilkan jika dosen menuliskannya. Aplikasi tidak menebak alasan pribadi dosen berdasarkan labelnya.

## Cara kerja XAI dan saran revisi

Model ini menggunakan fitur karakter, bukan LLM. Untuk kelas `c`, skor keputusannya adalah:

```text
score_c = bias_c + Σ(TF-IDF_j × coefficient_c,j)
```

Untuk membandingkan kelas prediksi `p` dengan kelas pembanding `r`:

```text
score_p − score_r
  = (bias_p − bias_r) + Σ[TF-IDF_j × (coefficient_p,j − coefficient_r,j)]
```

Aplikasi menghitung kontribusi tersebut langsung dari koefisien model. Kontribusi seluruh fitur dan bias harus merekonstruksi selisih skor dalam toleransi numerik. Tabel menampilkan beberapa fragmen paling berpengaruh, sedangkan jumlah yang dilaporkan memakai **seluruh** fitur aktif. Fragmen dapat tumpang tindih dan bukan alasan semantik yang lengkap.

Skor LinearSVC **bukan probabilitas**. Aplikasi tidak mengubahnya menjadi persentase keyakinan. Selisih dua skor teratas di bawah `0.25` memunculkan ajakan meninjau; ini aturan kerja prototipe yang **belum dikalibrasi atau divalidasi** sebagai ukuran ketidakpastian.

Saran revisi menggunakan aturan pedagogis yang mengikuti definisi rubrik dari pengguna. Saran itu dipisahkan dari bukti XAI. Aplikasi tidak mengklaim bahwa saran dihasilkan oleh model SVM atau membuktikan komentar benar terhadap kode. Source code ditampilkan untuk dibaca manusia; masukan model tetap teks komentar.

## Perhitungan kesepakatan / IRR

Tujuh kelas merupakan kategori nominal. Aplikasi menghitung Cohen’s kappa **tanpa bobot ordinal**:

```text
P_o = jumlah label dosen yang sama dengan prediksi / N
P_e = Σ_c [(jumlah label dosen c / N) × (jumlah prediksi c / N)]
kappa = (P_o − P_e) / (1 − P_e)
```

Jika `P_e = 1`, kappa dilaporkan **tidak terdefinisi**, bukan otomatis 1. Rumus, jumlah tiap kelas, `P_o`, dan `P_e` ditampilkan dalam aplikasi dan audit JSON.

Yang diukur adalah **kesepakatan dosen–model**, bukan reliabilitas antara dua pakar manusia. Label dosen awal merupakan pembanding dan tidak otomatis menjadi ground truth terverifikasi. Kappa pada 100 komentar simulasi tidak boleh dilaporkan sebagai hasil evaluasi ilmiah model pada komentar mahasiswa asli. Dataset simulasi tidak diperiksa duplikasinya terhadap training corpus karena corpus tersebut tidak tersedia dalam paket ini.

## Sepuluh contoh kode Java

Semua contoh merupakan bahan latihan yang sengaja memuat peluang kritik; kekeliruan logika pada beberapa contoh dipertahankan agar dapat direview. Seluruh contoh dapat dikompilasi dengan Java 17. Menjalankan Java tidak diperlukan untuk menjalankan aplikasi Streamlit.

| ID | File | Konteks |
| --- | --- | --- |
| JAVA01 | `KasirBelanja.java` | Subtotal, diskon, dan struk |
| JAVA02 | `NilaiMahasiswa.java` | Rata-rata dan predikat |
| JAVA03 | `PerpustakaanMini.java` | Koleksi dan peminjaman |
| JAVA04 | `RekeningBank.java` | Setoran, penarikan, dan saldo |
| JAVA05 | `ReservasiKursi.java` | Indeks dan status kursi |
| JAVA06 | `InventarisBarang.java` | Stok dan penjualan |
| JAVA07 | `KonversiSuhu.java` | Fahrenheit dan Kelvin |
| JAVA08 | `Penggajian.java` | Lembur, pajak, dan arsip |
| JAVA09 | `StatistikAngka.java` | Median dan rentang |
| JAVA10 | `PengirimanPaket.java` | Pembulatan berat dan ongkir |

## Model dan preprocessing

- Model asli disalin ke `models/best_model.joblib`. Metadata asli ada di `models/best_model_metadata.json`.
- Pemilihan model pada metadata: `S1_Original_Only`, fixed 5-fold CV pada data asli, metrik utama macro-F1. Test tidak digunakan untuk pemilihan. Metadata tidak menyediakan angka performa CV sehingga aplikasi tidak mengarang angka akurasi.
- Versi scikit-learn dikunci ke **1.6.1**, sama dengan versi saat model disimpan. Aplikasi menolak versi yang berbeda untuk menghindari ketidakcocokan artefak.
- Implementasi `clean_text` disamakan dengan cell `f3743f07` dari `PCR_Notebook_03_ML_FixedCV_Original_vs_783_vs_1050(1).ipynb`: penyesuaian kata uppercase, penghapusan URL, penghapusan HTML setelah unescape, penghapusan emoji, lalu normalisasi whitespace. Tidak ada stopword removal atau stemming tambahan. Lowercase dilakukan oleh vectorizer terlatih.
- Urutan kelas untuk koefisien dan skor mengikuti `classifier.classes_`, sedangkan tabel rubrik mengikuti urutan tujuh label pengguna.
- Informasi asal artefak dan hash tersedia dalam `models/deployment_provenance.json`.

## Penyimpanan dan penggunaan prototipe

Review terkirim dan anotasi tersimpan dalam SQLite pada `runtime/pcr.sqlite3`. Lokasi dapat diganti melalui environment variable `PCR_DB_PATH`. File runtime tidak disertakan pada paket awal. Simpan/backup database ini jika ingin mempertahankan data antarrestart atau pemindahan server. Host dengan filesystem sementara memerlukan penyimpanan persisten atau ekspor data berkala.

Pilihan peran adalah pergantian UI untuk demonstrasi dan **tidak mencakup login atau pembatasan akses berdasarkan akun**. Kode dosen digunakan sebagai pengenal anotasi, bukan kata sandi. Sebelum digunakan untuk kelas sungguhan di server bersama, tambahkan autentikasi, otorisasi, dan penyimpanan yang sesuai. Dependensi dipasang melalui internet pada instalasi awal; inferensi tidak memerlukan API LLM atau layanan eksternal.

## Pengujian

```bash
python -m pip install -r requirements-dev.txt
python -m pytest tests -q
```

Pengujian mencakup kesamaan inferensi dengan pipeline asli, rekonstruksi XAI, kappa terhadap implementasi scikit-learn, validasi dataset, penyimpanan, anotasi buta, penguncian label awal, revisi komentar, pergantian peran, dan pengiriman akhir.

## Referensi teknis

- [LinearSVC, scikit-learn 1.6.1](https://scikit-learn.org/1.6/modules/generated/sklearn.svm.LinearSVC.html)
- [Cohen’s kappa, scikit-learn 1.6.1](https://scikit-learn.org/1.6/modules/generated/sklearn.metrics.cohen_kappa_score.html)
- [Streamlit AppTest 1.50.0](https://docs.streamlit.io/1.50.0/develop/api-reference/app-testing/st.testing.v1.apptest)
