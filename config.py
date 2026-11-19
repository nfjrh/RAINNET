import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "ganti-dengan-kunci-rahasia")
    DATABASE = os.path.join(BASE_DIR, "instance", "rainnet.db")

    # Model JSB hasil pelatihan (dibuat oleh: python train.py)
    MODEL_PATH = os.path.join(BASE_DIR, "models", "rainnet_model.joblib")

    # Batas nilai wajar tiap variabel (validasi input)
    LIMITS = {
        "suhu": (-10, 60),
        "kelembapan": (0, 100),
        "tekanan": (850, 1100),
        "angin": (0, 200),
    }
