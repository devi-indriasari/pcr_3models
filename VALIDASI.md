# Catatan validasi aplikasi

Tanggal pemeriksaan: **5 November 2026**.

| Pemeriksaan | Hasil |
| --- | --- |
| Pengujian otomatis inti dan UI Streamlit | **21 pengujian lulus** |
| Prediksi 100 komentar simulasi dibandingkan pipeline asli | Sama untuk seluruh masukan setelah preprocessing yang sama |
| Rekonstruksi selisih skor dari kontribusi XAI pada 100 komentar simulasi | **100/100 sesuai** dalam toleransi numerik |
| Kappa pada pasangan label uji dibandingkan implementasi scikit-learn | Sesuai; keadaan tidak terdefinisi juga ditangani |
| Kompilasi sepuluh file contoh Java | **10/10 berhasil**, OpenJDK 17 |
| Uji browser: enam isian → pemeriksaan/XAI → konfirmasi → kirim review | Berhasil; pesan pengiriman dan data tersimpan tampil |
| Uji browser: pilihan peran dosen → dataset simulasi → anotasi buta | Berhasil; progres awal 0/100 dan prediksi belum dibuka |
| Galat JavaScript pada alur browser yang diuji | Tidak ada |
| Overflow horizontal halaman pada viewport desktop 1440 × 1000 | Tidak terdeteksi |

Pengujian juga memeriksa pengiriman satu kali, hasil pemeriksaan yang kedaluwarsa setelah revisi, pergantian kode dan peran, kelanjutan anotasi tersimpan, penguncian label awal, dan pemisahan adjudikasi dari label awal. Uji browser menggunakan interaksi bertahap dengan menunggu pembaruan Streamlit selesai.

Pemeriksaan ini memverifikasi implementasi aplikasi. Angka 100/100 pada XAI merupakan **kesesuaian rekonstruksi matematis skor**, bukan akurasi klasifikasi atau validasi pakar terhadap komentar sintetis. Aplikasi tetap menggunakan prediksi model asli tanpa menggantinya dengan aturan kata kunci.
