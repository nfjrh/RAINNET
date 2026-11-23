"""Ambil data cuaca terkini dari API gratis.

Sumber data:
  - BMKG (api.bmkg.go.id)  -> suhu (t), kelembapan (hu), kecepatan angin (ws, km/jam)
  - Open-Meteo             -> tekanan udara permukaan laut (pressure_msl, hPa)

Catatan: API prakiraan cuaca BMKG TIDAK menyediakan tekanan udara, jadi
tekanan diambil dari Open-Meteo (gratis, tanpa API key, non-komersial).

Model dilatih dengan RATA-RATA HARIAN, jadi di sini kita juga merata-ratakan
seluruh data hari ini (BMKG: per 3 jam, Open-Meteo: per jam).

WAJIB: tampilkan "BMKG" sebagai sumber data di aplikasi (syarat dari BMKG).
"""
from datetime import datetime
from statistics import mean

import requests

BMKG_URL = "https://api.bmkg.go.id/publik/prakiraan-cuaca"
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT = 10  # detik


class DataCuacaError(Exception):
    """Gagal mengambil / membaca data cuaca dari API."""


def _get_json(url, params):
    try:
        r = requests.get(url, params=params, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        raise DataCuacaError(f"Tidak bisa menghubungi {url}: {e}") from e
    except ValueError as e:
        raise DataCuacaError(f"Respons dari {url} bukan JSON yang valid.") from e


def _slot_bmkg(data):
    """Ratakan struktur BMKG -> list slot per 3 jam.

    Struktur: data["data"][0]["cuaca"] = [ [slot, slot, ...], [..hari 2..], ... ]
    """
    try:
        hari = data["data"][0]["cuaca"]
        return [slot for harian in hari for slot in harian]
    except (KeyError, IndexError, TypeError) as e:
        raise DataCuacaError("Format data BMKG tidak sesuai yang diharapkan.") from e


def ambil_bmkg(adm4):
    """Rata-rata hari ini: suhu (C), kelembapan (%), angin (km/jam) + nama lokasi."""
    data = _get_json(BMKG_URL, {"adm4": adm4})
    slot = _slot_bmkg(data)
    if not slot:
        raise DataCuacaError("BMKG tidak mengembalikan data prakiraan.")

    # Ambil slot yang tanggal lokalnya = tanggal lokal slot pertama (hari ini).
    tanggal = slot[0]["local_datetime"][:10]
    hari_ini = [s for s in slot if s["local_datetime"][:10] == tanggal]

    try:
        return {
            "suhu": round(mean(float(s["t"]) for s in hari_ini), 1),
            "kelembapan": round(mean(float(s["hu"]) for s in hari_ini), 1),
            "angin": round(mean(float(s["ws"]) for s in hari_ini), 1),
            "tanggal": tanggal,
            "jumlah_slot": len(hari_ini),
            "lokasi": data.get("lokasi", {}),
        }
    except (KeyError, ValueError, TypeError) as e:
        raise DataCuacaError("Field t/hu/ws pada data BMKG tidak lengkap.") from e


def ambil_tekanan(lat, lon, tz="Asia/Makassar"):
    """Rata-rata tekanan permukaan laut (hPa) untuk hari ini dari Open-Meteo."""
    data = _get_json(OPEN_METEO_URL, {
        "latitude": lat, "longitude": lon,
        "hourly": "pressure_msl", "timezone": tz, "forecast_days": 1,
    })
    try:
        nilai = [v for v in data["hourly"]["pressure_msl"] if v is not None]
        return round(mean(nilai), 1)
    except (KeyError, TypeError, ValueError) as e:
        raise DataCuacaError("Data tekanan Open-Meteo tidak lengkap.") from e


def ambil_data_terkini(adm4, lat, lon):
    """Gabungkan BMKG + Open-Meteo menjadi 4 input model RainNet."""
    bmkg = ambil_bmkg(adm4)
    tekanan = ambil_tekanan(lat, lon)
    return {
        "suhu": bmkg["suhu"],
        "kelembapan": bmkg["kelembapan"],
        "tekanan": tekanan,
        "angin": bmkg["angin"],
        "info": {
            "lokasi": bmkg["lokasi"],
            "tanggal": bmkg["tanggal"],
            "jumlah_slot": bmkg["jumlah_slot"],
            "diambil": datetime.now().isoformat(timespec="seconds"),
        },
    }
