import sqlite3
from datetime import datetime

DB = "rainnet.db"


def sambung():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with sambung() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS riwayat (
            id INTEGER PRIMARY KEY AUTOINCREMENT, waktu TEXT, suhu REAL,
            kelembapan REAL, penyinaran REAL, angin REAL,
            peluang_hujan REAL, hasil TEXT)""")


def simpan(x, p):
    hasil = "Hujan" if p >= 0.5 else "Tidak hujan"
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M")
    with sambung() as c:
        cur = c.execute(
            "INSERT INTO riwayat (waktu, suhu, kelembapan, penyinaran, angin, peluang_hujan, hasil) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)", (waktu, *x, p, hasil))
        return cur.lastrowid


def semua(tanggal=None):
    sql, arg = "SELECT * FROM riwayat", ()
    if tanggal:
        sql, arg = sql + " WHERE waktu LIKE ?", (tanggal + "%",)
    with sambung() as c:
        return c.execute(sql + " ORDER BY id DESC", arg).fetchall()


def satu(id_):
    with sambung() as c:
        return c.execute("SELECT * FROM riwayat WHERE id = ?", (id_,)).fetchone()
