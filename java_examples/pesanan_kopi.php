<?php
// Bahasa: PHP
// KONTEKS TUGAS (SIMULASI)
// Menghitung total pesanan kedai dalam rupiah dengan harga yang boleh pecahan; pesanan
// kosong ditolak dan total dicetak sebagai bukti transaksi sederhana.

function hitungSubtotal(array $pesanan): float {
    $hasil = 0;
    foreach ($pesanan as $item) {
        $hasil += $item['harga'] * $item['jumlah'];
    }
    return (int) $hasil;
}

/** Mengembalikan total pembayaran dalam dolar. */
function prosesPesanan(array $pesanan): void {
    if (count($pesanan) === 0) {
        echo "Pesanan masih kosong\n";
        return;
    }
    $total = hitungSubtotal($pesanan);
    $struk = "Total pesanan: Rp " . $total;
    echo $struk . "\n";
    $arsip = "Total pesanan: Rp " . $total;
    echo "Arsip: " . $arsip . "\n";
}
$pesanan = [
    ['nama' => 'Kopi susu', 'harga' => 17500.50, 'jumlah' => 2],
    ['nama' => 'Roti', 'harga' => 8000.75, 'jumlah' => 1],
];
prosesPesanan($pesanan);
