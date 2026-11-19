"""Logika prediksi: memuat model JSB hasil `train.py` dan menghitung peluang hujan."""
import json
import os
from functools import lru_cache

import joblib
import pandas as pd
from flask import current_app

FITUR = ["suhu", "kelembapan", "tekanan", "angin"]


@lru_cache(maxsize=1)
def _muat_model(path):
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Model belum ada di {path}. Jalankan dulu:  python train.py")
    return joblib.load(path)


def muat_metrik():
    """Metrik evaluasi model (untuk halaman Tentang). None jika belum ada."""
    path = os.path.join(os.path.dirname(current_app.config["MODEL_PATH"]),
                        "metrics.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def hitung_peluang_hujan(suhu, kelembapan, tekanan, angin):
    """Kembalikan peluang hujan (0-100, persen).

    Satuan input: suhu C, kelembapan %, tekanan hPa, angin km/jam.
    """
    model = _muat_model(current_app.config["MODEL_PATH"])
    x = pd.DataFrame([[suhu, kelembapan, tekanan, angin]], columns=FITUR)
    peluang = model.predict_proba(x)[0][1]  # kelas 1 = hujan
    # Batasi 0,1-99,9 agar tidak tampil "100%" (model tidak pernah benar-benar pasti)
    return round(min(max(float(peluang) * 100, 0.1), 99.9), 1)


def klasifikasi(peluang_hujan):
    """Ubah peluang menjadi label hasil dan teks saran."""
    if peluang_hujan >= 50:
        return {
            "label": "Hujan",
            "judul": "Berpotensi hujan",
            "saran_utama": "Siapkan payung sebelum beraktivitas",
            "saran_tambahan": "Pertimbangkan aktivitas di dalam ruangan.",
        }
    return {
        "label": "Tidak hujan",
        "judul": "Cenderung tidak hujan",
        "saran_utama": "Aktivitas luar ruangan lebih memungkinkan",
        "saran_tambahan": "Tetap pantau perubahan cuaca sebelum memulai perjalanan atau aktivitas.",
    }
