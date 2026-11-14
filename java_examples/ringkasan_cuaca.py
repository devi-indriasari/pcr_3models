# Bahasa: Python
# KONTEKS TUGAS (SIMULASI)
# Merangkum rata-rata, suhu tertinggi dan terendah dari pengamatan harian; tampilkan
# peringatan panas untuk rata-rata minimal 30 derajat dan tangani data kosong.

def rata_rata(suhu_harian):
    return sum(suhu_harian) / len(suhu_harian)


def suhu_tertinggi(suhu_harian):
    return max(suhu_harian)


def tampilkan_laporan(data):
    rerata = rata_rata(data)
    print("Rata-rata:", rerata)
    print("Suhu tertinggi:", suhu_tertinggi(data))
    if rerata >= 30:
        print("Cuaca cenderung panas")
        print("Pantau suhu siang hari")


if __name__ == "__main__":
    suhu_harian = [28.5, 30.0, 31.5, 29.0]
    tampilkan_laporan(suhu_harian)
