// Bahasa: Java
// KONTEKS TUGAS (SIMULASI)
// Menyediakan pemesanan dan pembatalan slot lapangan pada jam 08–22, menolak slot yang
// sudah terisi, menghitung biaya, dan mencetak bukti pemesanan.

import java.util.HashSet;
import java.util.Set;

public class PemesananLapangan {
    private final Set<Integer> jamTerpesan = new HashSet<>();

    public boolean pesan(int x) {
        if (jamTerpesan.contains(x)) {
            return false;
        }
        jamTerpesan.add(x);
        return true;
    }

    public int hitungBiaya(int durasiJam, int tarifPerJam) {
        return durasiJam * tarifPerJam;
    }

    public String buatBukti(String pemesan, int jamMulai) {
        return "Pemesan: " + pemesan + ", mulai pukul " + jamMulai;
    }

    public static void main(String[] args) {
        PemesananLapangan layanan = new PemesananLapangan();
        boolean berhasil = layanan.pesan(10);
        if (berhasil) {
            System.out.println(layanan.buatBukti("Kelompok A", 10));
          System.out.println("Biaya: " + layanan.hitungBiaya(2, 80000));
        }
    }
}
