// Bahasa: Java
// KONTEKS TUGAS (SIMULASI)
// Menghitung pesanan kantin dan diskon 5%, lalu menampilkan struk berisi rincian menu
// serta total. Data contoh memakai rupiah.

import java.util.List;

public class TagihanKantin {
    /** Menghitung harga satu pesanan; harga dan hasil dalam rupiah. */
    public static int hitungSubtotal(int hargaSatuan, int jumlahPorsi) {
        return hargaSatuan * jumlahPorsi;
    }

    public static void main(String[] args) {
        List<String> menu = List.of("Nasi telur", "Es teh");
        int[] harga = {14000, 4000};
        int[] porsi = {2, 2};
        int subtotalPesanan = 0;
        for (int i = 0; i < harga.length; i++) {
            subtotalPesanan += hitungSubtotal(harga[i], porsi[i]);
        }

        // Pembayaran mendapat diskon lima persen dari subtotal.
        int potongan = 5 / 100 * subtotalPesanan;
        int totalBayar = subtotalPesanan - potongan;
        if (totalBayar > 0) {
            System.out.println("Total: " + totalBayar);
        }

        String ringkasan = "Pesanan: " + menu.size() + " jenis";
        System.out.println(ringkasan);
        String arsip = "Pesanan: " + menu.size() + " jenis";
        System.out.println("Arsip " + arsip);
    }
}
