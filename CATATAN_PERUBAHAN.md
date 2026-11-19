# Catatan perubahan dari mockup (untuk asistensi)

| Bagian | Mockup | Aplikasi final | Alasan |
|---|---|---|---|
| Jumlah variabel di Beranda | "enam variabel cuaca" | empat variabel | Form dan halaman lain di mockup hanya memakai empat variabel |
| Sumber data | BMKG | Dataset cuaca harian Makassar (CSV , 2015-2025, 4.017 hari) | Data Online BMKG hanya menyediakan data bulanan; layanan PTSP berbayar dan tidak memuat data harian.
| Variabel input | suhu, kelembapan, tekanan, angin | sama (suhu rata-rata, kelembapan rata-rata, tekanan laut rata-rata, kecepatan angin rata-rata) | Semua tersedia di dataset |
| Satuan angin | km/jam | km/jam | Dataset dalam m/s, dikonversi (x 3,6) saat pelatihan |
| Label hujan | tidak dijelaskan | hujan = curah hujan harian >= 1 mm | Ambang umum; sudah sesuai kolom `hujan` di dataset |
| Model | JSB | MLP (scikit-learn), 2 lapisan tersembunyi (16 dan 8 neuron) | JSB sederhana yang cukup untuk 4 variabel |
| Pengujian akurasi | perlu diuji | data dibagi berdasarkan waktu: latih 2015-2023, uji 2024-2025 | Menghindari akurasi yang terlalu optimis |
| Hasil | - | akurasi uji 80,3% (pembanding: selalu menebak mayoritas 60,3%) | Lihat `models/metrics.json` |

## Keterbatasan
- Model memakai rata-rata harian, bukan kondisi sesaat.
- Prediksi adalah "hujan pada hari yang sama" dari kondisi rata-rata hari itu, bukan prakiraan hari esok.
- Kolom `hujan_besok` ada di dataset tetapi tidak dipakai.
- Kolom `tutupan_awan`, `suhu_min/max`, dan `tekanan_stasiun` tidak dipakai agar sesuai mockup.
- Satu lokasi (Makassar), satu rentang waktu; belum diuji di tempat lain.
