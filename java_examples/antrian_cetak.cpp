// Bahasa: C++
// KONTEKS TUGAS (SIMULASI)
// Menyediakan antrean layanan cetak yang dapat menampung beberapa pekerjaan pengguna,
// memproses antrean dengan aman, dan menghitung biaya halaman × salinan × tarif.

#include <iostream>
#include <queue>
#include <string>

struct Pekerjaan {
    std::string pemilik;
    int h;
};

int hitungBiaya(int halaman, int salinan, int tarif) {
    return halaman * salinan * tarif;
}

Pekerjaan ambilBerikutnya(std::queue<Pekerjaan>& antrean) {
    Pekerjaan hasil = antrean.front();
    antrean.pop();
    return hasil;
}

void cetakStatus(const Pekerjaan& pekerjaan) {
    std::cout << "Pencetakan untuk " << pekerjaan.pemilik << '\n';
  std::cout << "Halaman: " << pekerjaan.h << '\n';
}

int main() {
    std::queue<Pekerjaan> antrean;
    antrean.push({"Lia", 6});
    Pekerjaan pertama = ambilBerikutnya(antrean);
    cetakStatus(pertama);
    std::cout << "Biaya: " << hitungBiaya(pertama.h, 2, 250) << '\n';
}
