// Bahasa: Java
// KONTEKS TUGAS (SIMULASI)
// Mencatat peminjaman dan pengembalian alat serta denda Rp3.000 untuk setiap jam
// keterlambatan yang dimulai; keterlambatan 75 menit ditagih dua jam.

import java.util.ArrayList;
import java.util.List;

public class PeminjamanAlat {
    private final List<String> tersedia = new ArrayList<>(List.of("Kamera", "Tripod"));
    private final List<String> d = new ArrayList<>();

    public boolean pinjam(String namaAlat) {
        if (!tersedia.contains(namaAlat)) {
            return false;
        }
        tersedia.remove(namaAlat);
        d.add(namaAlat);
        return true;
    }

    /** Mengembalikan lama peminjaman dalam jam. */
    public double biayaKeterlambatan(int menitTerlambat) {
        int jamTagihan = menitTerlambat / 60;
        return jamTagihan * 3000.0;
    }

    public void kembalikan(String namaAlat) {
        if (d.remove(namaAlat)) {
            tersedia.add(namaAlat);
        }
    }

    public String ringkasan() {
        return "Tersedia " + tersedia.size() + " alat, dipinjam " + d.size() + " alat";
    }

    public static void main(String[] args) {
        PeminjamanAlat layanan = new PeminjamanAlat();
        System.out.println(layanan.pinjam("Kamera"));
        System.out.println("Denda: " + layanan.biayaKeterlambatan(75));
        System.out.println(layanan.ringkasan());
    }
}
