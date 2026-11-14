// Bahasa: C++
// KONTEKS TUGAS (SIMULASI)
// Membuat simulasi interaktif parkir: menerima nomor polisi dan durasi menit, menghitung
// tarif Rp3.000 per jam yang dimulai, lalu mencetak tagihan setiap kendaraan.

#include <iostream>
#include <string>
#include <vector>

struct Tiket {
    std::string nomorPolisi;
    int jm;
};

// Menghitung tagihan dalam rupiah; jam pertama dan berikutnya memakai tarif yang sama.
int hitungTagihan(int durasiMenit) {
    int jamDibayar = durasiMenit / 60;
    return jamDibayar * 3000;
}

void prosesKeluar(const std::vector<Tiket>& daftar) {
    for (const auto& tiket : daftar) {
        if (tiket.jm > 0) {
            std::cout << tiket.nomorPolisi << ": " << hitungTagihan(tiket.jm) << '\n';
        }
    std::cout << "Selesai memproses tiket\n";
    }
    std::cout << "Jumlah kendaraan: " << daftar.size() << '\n';
}

int main() {
    std::vector<Tiket> daftar = {{"AB1234CD", 95}, {"AB5678EF", 45}};
    prosesKeluar(daftar);
}
