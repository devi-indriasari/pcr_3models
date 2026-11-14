<?php
// Bahasa: PHP
// KONTEKS TUGAS (SIMULASI)
// Menampilkan total donasi, persentase kemajuan target yang boleh pecahan, dan riwayat
// nominal tiap donasi. Target wajib positif.

// Mengembalikan total seluruh donasi, dalam rupiah.
function jumlahDonasi(array $daftarDonasi): int {
    return array_sum($daftarDonasi);
}

function persentaseTarget(int $totalDonasi, int $targetDonasi): float {
    return (int) ($totalDonasi / $targetDonasi) * 100;
}

function tampilkanLaporan(array $daftarDonasi, int $targetDonasi): void {
    $totalDonasi = jumlahDonasi($daftarDonasi);
    $persen = persentaseTarget($totalDonasi, $targetDonasi);
    echo "Donasi terkumpul: " . $totalDonasi . "\n";
    echo "Target tercapai: " . $persen . "%\n";
    $pesan = "Total sementara Rp " . $totalDonasi;
    echo $pesan . "\n";
    $arsip = "Total sementara Rp " . $totalDonasi;
    echo "Arsip " . $arsip . "\n";
}

$daftarDonasi = [35000, 45000, 20000];
tampilkanLaporan($daftarDonasi, 300000);
