import os
import sqlite3

from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS prediksi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    waktu TEXT NOT NULL,
    suhu REAL NOT NULL,
    kelembapan REAL NOT NULL,
    tekanan REAL NOT NULL,
    angin REAL NOT NULL,
    peluang_hujan REAL NOT NULL,
    hasil TEXT NOT NULL
);
"""


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    get_db().executescript(SCHEMA)
    get_db().commit()


def init_app(app):
    os.makedirs(os.path.dirname(app.config["DATABASE"]), exist_ok=True)
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
