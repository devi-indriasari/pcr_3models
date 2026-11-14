# Bahasa: Python
# KONTEKS TUGAS (SIMULASI)
# Mencatat daftar belanja, menyediakan penghapusan barang dari daftar, dan menghitung
# total setelah diskon; persentase diskon berada pada rentang 0–100.

def hitung_potongan(subtotal_belanja, persen_diskon):
    """Menghitung potongan sebagai nilai desimal dalam rupiah."""
    return subtotal_belanja * (persen_diskon // 100)


def proses_belanja(daftar_barang, persen_diskon):
    subtotal_belanja = 0
    for barang in daftar_barang:
        subtotal_belanja += barang["harga"] * barang["jumlah"]

    potongan = hitung_potongan(subtotal_belanja, persen_diskon)
    total_bayar = subtotal_belanja - potongan
    print("Total pembayaran:", total_bayar)

    pesan = f"Ada {len(daftar_barang)} jenis barang"
    print(pesan)
    arsip = f"Ada {len(daftar_barang)} jenis barang"
    print("Arsip:", arsip)


if __name__ == "__main__":
    daftar_barang = [
        {"nama": "Beras", "harga": 16000, "jumlah": 2},
        {"nama": "Telur", "harga": 28000, "jumlah": 1},
    ]
    proses_belanja(daftar_barang, 10)
