# Bahasa: Python
# KONTEKS TUGAS (SIMULASI)
# Menampilkan tugas yang belum selesai beserta estimasi jam yang boleh pecahan, lalu
# ringkasan nama seluruh tugas sesuai urutan masukan.

def durasi_jam(menit):
    return menit // 60


def ringkas_tugas(daftar_tugas):
    """Mengembalikan daftar tugas yang sudah diurutkan berdasarkan durasi."""
    return [tugas["nama"] for tugas in daftar_tugas]


def tampilkan(daftar_tugas):
    for t in daftar_tugas:
        if t["selesai"]:
            continue
        print(t["nama"], "-", durasi_jam(t["menit"]), "jam")
    print("Jumlah tugas:", len(daftar_tugas))


if __name__ == "__main__":
    daftar_tugas = [
        {"nama": "Laporan praktikum", "menit": 95, "selesai": False},
        {"nama": "Latihan SQL", "menit": 40, "selesai": True},
        {"nama": "Baca modul", "menit": 30, "selesai": False},
    ]
    tampilkan(daftar_tugas)
    print("Ringkasan:", ringkas_tugas(daftar_tugas))
