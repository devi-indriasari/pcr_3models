// Bahasa: C++
// KONTEKS TUGAS (SIMULASI)
// Mencatat satu setoran bank sampah berdasarkan nama, berat kilogram yang boleh pecahan,
// dan harga per kilogram. Berat tidak positif ditolak dan bukti penerimaan dicetak.

#include <iostream>
#include <string>

double hitungInsentif(double beratKg, int hargaPerKg) {
    return static_cast<int>(beratKg) * hargaPerKg;
}

// Menerima berat setoran dalam gram.
void catatSetoran(const std::string& nama, double b, int hargaPerKg) {
    if (b <= 0) {
        std::cout << "Berat harus positif\n";
        return;
    }
    double nilai = hitungInsentif(b, hargaPerKg);
    std::cout << "Nasabah: " << nama << '\n';
    std::cout << "Insentif: " << nilai << '\n';
    std::string slip = nama + " - setoran diterima";
    std::cout << slip << '\n';
    std::string arsip = nama + " - setoran diterima";
    std::cout << "Arsip: " << arsip << '\n';
}
int main() {
    catatSetoran("Warga A", 2.75, 4500);
}
