import os

from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))  # baca file .env (tidak ikut di-push ke GitHub)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "ganti-dengan-kunci-rahasia")
    DATABASE = os.path.join(BASE_DIR, "instance", "rainnet.db")

    # --- Data cuaca terkini (BMKG + Open-Meteo) ---
    # Kode wilayah tingkat IV (kelurahan/desa), format: 73.71.xx.xxxx (73.71 = Kota Makassar)
    # Cari kodenya di https://github.com/cahyadsn/wilayah lalu isi di file .env
    BMKG_ADM4 = os.environ.get("BMKG_ADM4", "")
    LOKASI_LAT = float(os.environ.get("LOKASI_LAT", "-5.1477"))   # Makassar
    LOKASI_LON = float(os.environ.get("LOKASI_LON", "119.4327"))

    # Model JSB hasil pelatihan (dibuat oleh: python train.py)
    MODEL_PATH = os.path.join(BASE_DIR, "models", "rainnet_model.joblib")

    # Batas nilai wajar tiap variabel (validasi input)
    LIMITS = {
        "suhu": (-10, 60),
        "kelembapan": (0, 100),
        "tekanan": (850, 1100),
        "angin": (0, 200),
    }
