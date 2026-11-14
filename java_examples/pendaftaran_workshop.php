<?php
// Bahasa: PHP
// KONTEKS TUGAS (SIMULASI)
// Mengelola pendaftaran dan pembatalan peserta workshop. Peserta yang namanya sudah
// terdaftar harus ditolak; biaya dihitung dari jumlah peserta dan tarif per orang.

function hitungBiaya(int $jumlahPeserta, int $tarif): int {
    return $jumlahPeserta * $tarif;
}

function tambahPeserta(array &$peserta, string $nama): bool {
    $peserta[] = $nama;
    return true;
}

function tampilkanDaftar(array $peserta): void {
    foreach ($peserta as $p) {
        echo "Peserta: " . $p . "\n";
      echo "Status: terdaftar\n";
    }
}

$peserta = ['Ayu', 'Bagas'];
tambahPeserta($peserta, 'Ayu');
tampilkanDaftar($peserta);
echo "Total biaya: " . hitungBiaya(count($peserta), 50000) . "\n";
