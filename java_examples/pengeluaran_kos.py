# Bahasa: Python
# KONTEKS TUGAS (SIMULASI)
# Merekap pengeluaran per kategori, sisa saldo, peringatan bila saldo terlampaui, dan
# pilihan periode bulanan. Nominal pengeluaran harus tidak negatif.

def total_pengeluaran(catatan):
    """Menjumlahkan nominal pengeluaran; setiap catatan berisi kategori dan nominal rupiah."""
    return sum(item["nominal"] for item in catatan)


def proses_laporan(catatan, saldo_awal):
    total = total_pengeluaran(catatan)
    s = saldo_awal - total
    if total > saldo_awal:
        print("Pengeluaran melewati saldo")
    else:
        print("Saldo masih cukup")
    print("Total pengeluaran:",total)
    print("Sisa saldo:",s)
    print("Makan:", sum(item["nominal"] for item in catatan if item["kategori"] == "makan"))
    print("Transport:", sum(item["nominal"] for item in catatan if item["kategori"] == "transport"))


if __name__ == "__main__":
    catatan = [
        {"kategori": "makan", "nominal": 18000},
        {"kategori": "transport", "nominal": 12000},
        {"kategori": "makan", "nominal": 15000},
    ]
    proses_laporan(catatan, 100000)
