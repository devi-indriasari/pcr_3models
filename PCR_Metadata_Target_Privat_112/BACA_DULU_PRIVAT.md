# Khusus pengelola: jangan dibagikan sebelum anotasi independen

Arsip ini berisi target generasi untuk memastikan rancangan seimbang. **Target generasi bukan ground truth, bukan hasil anotasi pakar, dan bukan prediksi model.**

Jangan meletakkan arsip atau isinya pada repository aplikasi yang dapat diakses pakar. Untuk pelabelan, pakar hanya memerlukan file input tanpa target dan source code pada paket pengganti.

## Isi

- `target_generasi_JANGAN_UNTUK_EXPERT.json`: 112 record lengkap, target kategori, jenis feedback, subtopik, potongan bukti dan nomor baris kode, alasan fokus target, serta penanda keanggotaan subset 100.
- `distribusi_target_generasi.json`: distribusi per bahasa, target kategori, jenis feedback, dan kode untuk set 112 dan subset 100.
- `laporan_validasi_data.json`: pemeriksaan struktur, hubungan komentar–kode, sintaks, eksekusi contoh yang tersedia, dan keterbacaan oleh aplikasi asli.
- `source_application_fingerprints.json`: sidik SHA-256 file aplikasi sumber v2 sebelum penggantian data; tidak mencakup bytecode cache.
- `replacement_file_fingerprints.json`: sidik SHA-256 file data dan kode baru untuk membekukan versi bahan yang digunakan seluruh pakar.

## Distribusi target

| Target kategori | Java (112) | C++ (112) | PHP (112) | Python (112) | Total set 112 | Total subset 100 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Variable | 4 | 4 | 4 | 4 | 16 | 14 |
| Expression | 4 | 4 | 4 | 4 | 16 | 14 |
| Control Flow | 4 | 4 | 4 | 4 | 16 | 14 |
| Comment | 4 | 4 | 4 | 4 | 16 | 14 |
| Layout and Formatting | 4 | 4 | 4 | 4 | 16 | 14 |
| Decomposition | 4 | 4 | 4 | 4 | 16 | 15 |
| General | 4 | 4 | 4 | 4 | 16 | 15 |
| **Total** | **28** | **28** | **28** | **28** | **112** | **100** |

Set 112: 28 komentar pada masing-masing jenis feedback. Dalam setiap sel bahasa–target terdapat tepat satu Appreciation, Problem, Suggestion, dan Mixed. Subset 100: 25 komentar per bahasa dan 25 per jenis feedback.

Urutan komentar diacak menggunakan seed `20261106`; ID disematkan setelah pengacakan dan tidak mengodekan target kategori. Subset 100 dipilih berdasarkan keseimbangan bahasa, target kategori, jenis feedback, dan keterwakilan kode. Tidak ada prediksi model yang dipakai dalam pembuatan atau pemilihan komentar.

## Penggunaan penelitian

1. Tetapkan set yang akan dipakai sebelum membuka hasil model. Set 100 adalah subset dari 112, sehingga keduanya bukan dua sampel terpisah.
2. Bekukan file komentar dan kode yang digunakan semua pakar. Masing-masing pakar memberi satu kategori dominan berdasarkan definisi tujuh label dan konteks kode/tugas.
3. Simpan anotasi independen sebelum diskusi. Jika dilakukan adjudikasi, pertahankan label awal agar kesepakatan antar-pakar tetap dapat dihitung sebelum adjudikasi.
4. Gunakan label hasil verifikasi sebagai reference ketika membandingkan S1, S2, dan S3 pada komentar yang sama. Jangan mengganti label pakar hanya agar target kembali seimbang.
5. Laporkan distribusi label hasil pakar, bukan hanya target generasi. Sertakan jumlah source code per bahasa dan jelaskan bahwa data komentar bersifat sintetis.

Target kategori pada General mengikuti definisi penilaian umum atau kelengkapan kebutuhan tugas. Konteks tugas ditulis di kepala setiap source code agar komentar mengenai fitur wajib dapat diperiksa. Label Comment merujuk komentar/dokumentasi di dalam source code, bukan kualitas feedback mahasiswa.

Metadata ini tidak menyatakan ketepatan label 100%, validasi pakar, lolos ambang cosine similarity tertentu, atau bebas tumpang tindih dengan training corpus yang tidak tersedia. Nomor baris bukti diperiksa secara mekanis; penetapan kategori tetap memerlukan pakar.
