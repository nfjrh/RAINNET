from flask import Flask, render_template, request, abort
import db
import predictor

app = Flask(__name__)
db.init_db()

# nama, batas bawah, batas atas. Urutan = urutan fitur model.
BATAS = {
    "suhu": ("Suhu udara", 10, 45),
    "rh": ("Kelembapan udara", 0, 100),
    "penyinaran": ("Lama penyinaran", 0, 14),
    "angin": ("Kecepatan angin", 0, 40),
}


@app.context_processor
def umum():
    return {"mode_demo": predictor.mode_demo()}


def susun(p, id_=None):
    persen = round(p * 100)
    hujan = p >= 0.5
    return {
        "id": id_, "hujan": hujan, "persen_hujan": persen, "persen_tidak": 100 - persen,
        "besar": persen if hujan else 100 - persen,
        "label": "Berpotensi hujan" if hujan else "Cenderung tidak hujan",
        "saran": "Siapkan payung sebelum beraktivitas." if hujan
        else "Aktivitas luar ruangan lebih memungkinkan.",
    }


def baca_form():
    nilai, galat, x = {}, [], []
    for k, (nama, lo, hi) in BATAS.items():
        mentah = request.form.get(k, "").strip().replace(",", ".")
        nilai[k] = mentah
        try:
            v = float(mentah)
        except ValueError:
            galat.append(f"{nama} harus berupa angka.")
            continue
        if not lo <= v <= hi:
            galat.append(f"{nama} harus antara {lo} dan {hi}.")
            continue
        x.append(v)
    return nilai, galat, x


@app.route("/")
def beranda():
    return render_template("beranda.html")


@app.route("/prediksi", methods=["GET", "POST"])
def prediksi():
    nilai, galat, hasil = {}, [], None
    if request.method == "POST":
        nilai, galat, x = baca_form()
        if not galat:
            p = predictor.prediksi(x)
            hasil = susun(p, db.simpan(x, p))
    return render_template("prediksi.html", nilai=nilai, galat=galat, hasil=hasil)


@app.route("/riwayat")
def riwayat():
    tanggal = request.args.get("tanggal", "")
    baris = db.semua(tanggal or None)
    return render_template("riwayat.html", baris=baris, tanggal=tanggal,
                           total=len(baris), hujan=sum(b["hasil"] == "Hujan" for b in baris))


@app.route("/riwayat/<int:id_>")
def detail(id_):
    b = db.satu(id_)
    if b is None:
        abort(404)
    return render_template("detail.html", b=b, hasil=susun(b["peluang_hujan"], id_))


@app.route("/tentang")
def tentang():
    return render_template("tentang.html")


if __name__ == "__main__":
    app.run(debug=True)
