# RAINNET (Rain Neural Network)

Aplikasi prediksi kemungkinan hujan dan tidak hujan berdasarkan variabel cuaca menggunakan Jaringan Syaraf Buatan (JSB). Sumber data: BMKG.

## Menjalankan

```bash
python -m venv venv
venv\Scripts\activate        # Windows (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
python app.py                # buka http://127.0.0.1:5000
```

Selama `model/model.pkl` belum ada, aplikasi berjalan dalam **mode demo** (rumus sementara, ada banner di atas halaman). Setelah model dipasang, banner hilang otomatis.

## Kesepakatan tim (jangan diubah sepihak)

- **Urutan fitur:** `suhu, rh, penyinaran, angin`. Sama persis saat pelatihan dan prediksi.
- **Satuan:** °C, %, jam, m/s.
- **Label:** `hujan = 1` jika `RR > 0`, selain itu `0`. Kelas 1 = hujan.
- **File model:** `model/model.pkl` dan `model/scaler.pkl` (dari `joblib.dump`).
- **Catatan data BMKG:** nilai 8888 dan 9999 berarti data kosong, buang saat pembersihan.

## Struktur

| Berkas | Isi | Pemilik |
|---|---|---|
| `training/` | pembersihan data dan pelatihan model | A |
| `model/` | `model.pkl`, `scaler.pkl` | A |
| `predictor.py`, `db.py`, `app.py` | prediksi, SQLite, route Flask | B |
| `templates/`, `static/` | tampilan | C |

## Alur Git

Satu cabang per orang (`model`, `backend`, `frontend`), gabung ke `main` lewat Pull Request. Jalankan `git pull` sebelum mulai bekerja.

## Tambahan .gitignore

```
data/
*.db
venv/
```
