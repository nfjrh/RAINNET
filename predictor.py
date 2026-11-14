"""Pembungkus model JSB. Anggota A: cukup letakkan model.pkl dan scaler.pkl di folder model/."""
import math

FITUR = ["suhu", "rh", "penyinaran", "angin"]  # urutan HARUS sama dengan saat pelatihan

try:
    import joblib
    _model = joblib.load("model/model.pkl")
    _scaler = joblib.load("model/scaler.pkl")
except Exception:
    _model = _scaler = None


def mode_demo():
    return _model is None


def prediksi(x):
    """x = [suhu, rh, penyinaran, angin]. Mengembalikan peluang hujan (0-1)."""
    if _model is not None:
        # asumsi kelas 1 = hujan
        return float(_model.predict_proba(_scaler.transform([x]))[0][1])
    suhu, rh, ss, angin = x  # model sementara: rumus sederhana, BUKAN hasil pelatihan
    z = 0.08 * (rh - 75) - 0.45 * (ss - 5) + 0.05 * (angin - 2) - 0.05 * (suhu - 28)
    return 1 / (1 + math.exp(-z))
