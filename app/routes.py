from datetime import datetime

from flask import (Blueprint, abort, current_app, redirect, render_template,
                   request, url_for)

from .db import get_db
from .services.predictor import hitung_peluang_hujan, klasifikasi, muat_metrik

bp = Blueprint("main", __name__)

BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
         "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]

FIELD_LABEL = {
    "suhu": "Suhu udara",
    "kelembapan": "Kelembapan udara",
    "tekanan": "Tekanan udara",
    "angin": "Kecepatan angin",
}


@bp.app_template_filter("tanggal")
def format_tanggal(iso_str, panjang=False):
    dt = datetime.fromisoformat(iso_str)
    bulan = BULAN[dt.month - 1]
    if panjang:
        return f"{dt.day} {bulan} {dt.year} · {dt:%H:%M}"
    return f"{dt.day:02d} {bulan} {dt.year} · {dt:%H:%M}"


@bp.app_template_filter("angka")
def format_angka(nilai):
    """28.0 -> 28, 28.5 -> 28.5"""
    return f"{nilai:g}"


def _baca_input(form):
    """Validasi form. Kembalikan (nilai, error)."""
    nilai, error = {}, {}
    for key, (low, high) in current_app.config["LIMITS"].items():
        mentah = form.get(key, "").strip().replace(",", ".")
        try:
            angka = float(mentah)
        except ValueError:
            error[key] = f"{FIELD_LABEL[key]} harus berupa angka."
            continue
        if not low <= angka <= high:
            error[key] = f"{FIELD_LABEL[key]} harus antara {low} dan {high}."
            continue
        nilai[key] = angka
    return nilai, error


@bp.route("/")
def beranda():
    return render_template("beranda.html")


@bp.route("/prediksi", methods=["GET", "POST"])
def prediksi():
    hasil, error, isian = None, {}, {}
    if request.method == "POST":
        isian = request.form
        nilai, error = _baca_input(request.form)
        if not error:
            peluang = hitung_peluang_hujan(**nilai)
            info = klasifikasi(peluang)
            db = get_db()
            db.execute(
                "INSERT INTO prediksi (waktu, suhu, kelembapan, tekanan, angin,"
                " peluang_hujan, hasil) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (datetime.now().isoformat(timespec="seconds"),
                 nilai["suhu"], nilai["kelembapan"], nilai["tekanan"],
                 nilai["angin"], peluang, info["label"]),
            )
            db.commit()
            hasil = {"peluang": peluang, "tidak": round(100 - peluang, 1), **info}
    return render_template("prediksi.html", hasil=hasil, error=error, isian=isian)


@bp.route("/riwayat")
def riwayat():
    tanggal = request.args.get("tanggal", "").strip()
    db = get_db()
    if tanggal:
        baris = db.execute(
            "SELECT * FROM prediksi WHERE date(waktu) = ? ORDER BY waktu DESC",
            (tanggal,)).fetchall()
    else:
        baris = db.execute("SELECT * FROM prediksi ORDER BY waktu DESC").fetchall()

    ringkasan = db.execute(
        "SELECT COUNT(*) AS total,"
        " COALESCE(SUM(hasil = 'Hujan'), 0) AS hujan,"
        " COALESCE(SUM(hasil = 'Tidak hujan'), 0) AS tidak FROM prediksi"
    ).fetchone()
    total_semua = ringkasan["total"]
    return render_template("riwayat.html", baris=baris, ringkasan=ringkasan,
                           tanggal=tanggal, total_semua=total_semua)


@bp.route("/riwayat/<int:id>")
def detail(id):
    row = get_db().execute("SELECT * FROM prediksi WHERE id = ?", (id,)).fetchone()
    if row is None:
        abort(404)
    peluang_hujan = row["peluang_hujan"]
    info = klasifikasi(peluang_hujan)
    if row["hasil"] == "Hujan":
        utama, lawan = peluang_hujan, round(100 - peluang_hujan, 1)
    else:
        utama, lawan = round(100 - peluang_hujan, 1), peluang_hujan
    return render_template("detail.html", row=row, info=info,
                           utama=utama, lawan=lawan)


@bp.route("/tentang")
def tentang():
    return render_template("tentang.html", m=muat_metrik())


@bp.app_errorhandler(404)
def tidak_ditemukan(e):
    return render_template("404.html"), 404
