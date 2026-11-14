<?php
// Bahasa: PHP
// KONTEKS TUGAS (SIMULASI)
// Mencari judul tanpa membedakan huruf besar-kecil dan menyediakan pencarian berdasarkan
// tahun terbit; hasil buku yang cocok ditampilkan.

/** Mengembalikan buku dengan judul yang memuat kata pencarian, tanpa membedakan huruf besar dan kecil. */
function cariBuku(array $data, string $kata): array {
    $hasil = [];
    foreach ($data as $buku) {
        if (strpos($buku['judul'], $kata)) {
            $hasil[] = $buku;
        }
    }
    return $hasil;
}

function tampilkan(array $bukuDitemukan): void {
    foreach ($bukuDitemukan as $buku) {
        echo $buku['judul'] . " - " . $buku['tahun'] . "\n";
    echo "----------------\n";
    }
}
$koleksi = [
    ['judul' => 'Pemrograman Web', 'tahun' => 2023],
    ['judul' => 'Dasar Basis Data', 'tahun' => 2021],
    ['judul' => 'Belajar Web Lanjut', 'tahun' => 2024],
];
tampilkan(cariBuku($koleksi, 'Web'));
