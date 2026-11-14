// Bahasa: C++
// KONTEKS TUGAS (SIMULASI)
// Menampilkan persentase sisa kuota yang boleh pecahan dan peringatan sisa di bawah 20%,
// serta ringkasan total pemakaian semua pengguna. Kuota awal harus positif.

#include <iostream>
#include <string>
#include <vector>

struct Pemakaian {
    std::string pengguna;
    int kuotaAwalMb;
    int terpakaiMb;
};

// Mengembalikan persentase sisa kuota sebagai bilangan desimal.
double persentaseSisa(int kuotaAwalMb, int terpakaiMb) {
    return (kuotaAwalMb - terpakaiMb) * 100 / kuotaAwalMb;
}

int main() {
    std::vector<Pemakaian> daftar = {{"Nina", 1500, 640}, {"Riko", 1000, 720}};
    for (const auto& catatan : daftar) {
        double sisa = persentaseSisa(catatan.kuotaAwalMb, catatan.terpakaiMb);
        std::cout << catatan.pengguna << ": " << sisa << "%\n";
        if (sisa < 20) {
            std::cout << "Kuota hampir habis\n";
        }
        std::string pesan = catatan.pengguna + " - laporan pemakaian";
        std::cout << pesan << '\n';
        std::string arsip = catatan.pengguna + " - laporan pemakaian";
        std::cout << "Arsip: " << arsip << '\n';
    }
}
