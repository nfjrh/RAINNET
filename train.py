"""Latih model JSB (MLP) untuk prediksi hujan / tidak hujan.

Jalankan:  python train.py
Hasil   :  models/rainnet_model.joblib  dan  models/metrics.json

Input model (4 variabel, sesuai mockup):
    suhu (C), kelembapan (%), tekanan laut (hPa ), kecepatan angin (km/jam)
Target:
    hujan = 1 jika curah hujan >= 1 mm pada hari yang sama, selain itu 0.

Data dibagi berdasarkan WAKTU (bukan acak): 2015-2023 untuk latih,
2024-2025 untuk uji, supaya akurasi tidak terlalu optimis.
"""
import json
import os

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "dataset_cuaca_makassar_harian.csv")
OUT_MODEL = os.path.join(BASE, "models", "rainnet_model.joblib")
OUT_METRICS = os.path.join(BASE, "models", "metrics.json")

FITUR = ["suhu", "kelembapan", "tekanan", "angin"]
TANGGAL_UJI = "2024-01-01"

    
def muat_data():
    df = pd.read_csv(DATA, parse_dates=["tanggal"])
    df = df.rename(columns={
        "suhu_rata": "suhu",
        "kelembapan_rata": "kelembapan",
        "tekanan_laut_rata_hpa": "tekanan",
    })
    df["angin"] = df["kecepatan_angin_rata_ms"] * 3.6  # m/s -> km/jam
    df = df.dropna(subset=FITUR + ["hujan"])
    return df


def buat_model():
    return make_pipeline(
        StandardScaler(),
        MLPClassifier(hidden_layer_sizes=(16, 8), activation="relu",
                      alpha=1e-3, max_iter=2000, early_stopping=True,
                      n_iter_no_change=30, random_state=42),
    )


def main():
    df = muat_data()
    latih = df[df["tanggal"] < TANGGAL_UJI]
    uji = df[df["tanggal"] >= TANGGAL_UJI]

    model = buat_model().fit(latih[FITUR], latih["hujan"])
    pred = model.predict(uji[FITUR])

    mayoritas = max(uji["hujan"].mean(), 1 - uji["hujan"].mean())
    tn, fp, fn, tp = confusion_matrix(uji["hujan"], pred).ravel()
    metrik = {
        "jumlah_data": int(len(df)),
        "data_latih": int(len(latih)),
        "data_uji": int(len(uji)),
        "periode": f"{df['tanggal'].min().date()} s.d. {df['tanggal'].max().date()}",
        "akurasi_uji": round(accuracy_score(uji["hujan"], pred) * 100, 1),
        "f1_uji": round(f1_score(uji["hujan"], pred) * 100, 1),
        "akurasi_tebak_mayoritas": round(mayoritas * 100, 1),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    }

    # Model akhir dilatih ulang dengan seluruh data
    final = buat_model().fit(df[FITUR], df["hujan"])
    os.makedirs(os.path.dirname(OUT_MODEL), exist_ok=True)
    joblib.dump(final, OUT_MODEL)
    with open(OUT_METRICS, "w", encoding="utf-8") as f:
        json.dump(metrik, f, indent=2, ensure_ascii=False)

    print(json.dumps(metrik, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
