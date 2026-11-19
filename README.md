# RAINNET (Rain Neural Network)

Prediksi hujan / tidak hujan dari suhu, kelembapan, tekanan udara, dan kecepatan angin.

```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python train.py      # melatih model -> models/rainnet_model.joblib
python run.py        # buka http://127.0.0.1:5000
```

Mengganti data: timpa `data/dataset_cuaca_makassar_harian.csv` (kolom sama), lalu jalankan `python train.py` lagi.
Lihat `CATATAN_PERUBAHAN.md` untuk daftar perbedaan dari mockup.
