"""Definisi mengikuti prompt rubrik yang diberikan pengguna, tanpa skor kualitas kode."""

LABELS = ["Variable", "Expression", "Control Flow", "Comment",
          "Layout and Formatting", "Decomposition", "General"]
RUBRICS = LABELS[:-1]

DEFINITIONS = {
    "Variable": "Penamaan variabel: kejelasan, makna, konsistensi, keterbacaan, dan kesesuaian nama dengan tujuan atau data yang disimpan.",
    "Expression": "Ekspresi, rumus, operator, operasi aritmetika atau logika, kesederhanaan ekspresi, dan ketepatan tipe data. Fokus pada cara nilai dihitung atau dikombinasikan.",
    "Control Flow": "Alur eksekusi, percabangan, perulangan, kondisi penghentian, kompleksitas nesting, exception handling, dan penanganan kondisi khusus.",
    "Comment": "Keberadaan, kejelasan, kelengkapan, relevansi, dan manfaat dokumentasi DI DALAM source code: header, inline comment, tujuan method, parameter, dan alasan keputusan program.",
    "Layout and Formatting": "Keterbacaan visual source code: indentasi, spasi, baris kosong, panjang baris, pengelompokan visual, urutan penempatan kode, serta konsistensi tanda kurung dan kurung kurawal.",
    "Decomposition": "Pembagian tanggung jawab ke fungsi, method, class, atau modul; kejelasan tugas, pengurangan duplikasi, modularisasi, dan pembatasan shared variables.",
    "General": "Penilaian keseluruhan, pujian atau kritik tanpa aspek teknis rubrik yang spesifik, pemenuhan persyaratan tugas, atau kelengkapan file pengumpulan.",
}
BOUNDARIES = {
    "Variable": "Bahas NAMA variabel. Rumus atau penggunaan variabel dalam perhitungan termasuk Expression.",
    "Expression": "Bahas perhitungan atau tipe data. Struktur if, loop, dan penanganan error termasuk Control Flow.",
    "Control Flow": "Jelaskan keputusan atau jalur eksekusi. Rumus saja termasuk Expression.",
    "Comment": "Yang dinilai adalah komentar/dokumentasi di kode, bukan komentar peer review yang sedang Anda tulis.",
    "Layout and Formatting": "Bahas penataan visual. Pemisahan menjadi method/class baru termasuk Decomposition.",
    "Decomposition": "Bahas pembagian tugas dan ketergantungan antarbagiannya. Spasi dan indentasi termasuk Layout and Formatting.",
    "General": "Komentar teknis yang jelas tetap masuk aspek spesifik meskipun kalimatnya singkat.",
}
PROMPTS = {
    "Variable": "Sebutkan nama variabel yang Anda nilai, jelaskan apakah namanya mewakili data yang disimpan, lalu berikan alasan atau usulan nama jika diperlukan.",
    "Expression": "Tunjukkan ekspresi atau tipe data yang dinilai, jelaskan dampaknya pada hasil perhitungan, dan usulkan perubahan bila diperlukan.",
    "Control Flow": "Tunjukkan percabangan, loop, atau penanganan error yang dinilai. Jelaskan kondisi input, jalur eksekusi, serta dampak atau perbaikannya.",
    "Comment": "Tunjukkan dokumentasi di dalam kode yang dinilai, atau bagian yang memerlukan dokumentasi. Jelaskan informasi yang membantu pembaca memahami program.",
    "Layout and Formatting": "Tunjukkan bagian kode yang penataannya Anda nilai. Jelaskan dampak indentasi, spasi, panjang baris, atau kurung kurawal pada keterbacaan.",
    "Decomposition": "Tunjukkan method/class atau bagian dengan tanggung jawab bercampur/berulang. Jelaskan pembagian tugas yang sudah tepat atau pemisahan yang Anda usulkan.",
}
PLACEHOLDERS = {
    "Variable": "Nilai satu atau beberapa nama variabel yang benar-benar ada pada kode...",
    "Expression": "Nilai perhitungan, operator, atau tipe data pada kode...",
    "Control Flow": "Nilai jalur if/else, loop, penghentian, atau penanganan error...",
    "Comment": "Nilai komentar atau dokumentasi DI DALAM kode...",
    "Layout and Formatting": "Nilai indentasi, spasi, panjang baris, atau penataan kode...",
    "Decomposition": "Nilai pembagian tanggung jawab method/class dan duplikasi...",
}

def slug(label):
    return label.lower().replace(" ", "_")
