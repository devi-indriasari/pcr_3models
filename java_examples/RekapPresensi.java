// Bahasa: Java
// KONTEKS TUGAS (SIMULASI)
// Menghitung persentase hadir, menentukan izin ujian pada batas 75%, dan menampilkan
// jumlah mahasiswa pada masing-masing status. Persentase boleh mengandung pecahan.

public class RekapPresensi {
    /** Mengembalikan persentase kehadiran dari jumlah hadir dan total pertemuan. */
    public static double persentase(int hadir, int pertemuan) {
        return hadir * 100 / pertemuan;
    }

    public static void proses(String[] nama, int[] a, int pertemuan) {
        for (int i = 0; i < nama.length; i++) {
            double persen = persentase(a[i], pertemuan);
            if (persen >= 75) {
                System.out.println(nama[i] + " boleh ujian");
            } else {
                System.out.println(nama[i] + " belum boleh ujian");
            }
          System.out.println("Kehadiran: " + persen + "%");
        }
    }
    public static void main(String[] args) {
        String[] nama = {"Sinta", "Dodi", "Mega"};
        int[] hadir = {11, 8, 12};
        proses(nama, hadir, 14);
    }
}
