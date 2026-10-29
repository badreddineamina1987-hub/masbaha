import os
import sqlite3
from flask import Flask, g, render_template, request, redirect, url_for, jsonify, abort

app = Flask(__name__)
DB_PATH = os.environ.get("DB_PATH", "tasbih.db")

DUA = {
    "f": "اللهم اغفر لها وارحمها وعافها واعف عنها، وأكرم نزلها ووسّع مدخلها، واغسلها بالماء والثلج والبرد، "
         "ونقّها من الخطايا كما نقّيت الثوب الأبيض من الدنس. اللهم أبدلها داراً خيراً من دارها وأهلاً خيراً من أهلها، "
         "اللهم انقلها من ضيق اللحود ومن مراتع الدود إلى جناتك جنات الخلود. لا إله إلا أنت يا حنّان يا منّان "
         "يا بديع السماوات والأرض، تغمّد ({name}) برحمتك يا أرحم الراحمين.",
    "m": "اللهم اغفر له وارحمه وعافه واعف عنه، وأكرم نزله ووسّع مدخله، واغسله بالماء والثلج والبرد، "
         "ونقّه من الخطايا كما نقّيت الثوب الأبيض من الدنس. اللهم أبدله داراً خيراً من داره وأهلاً خيراً من أهله، "
         "اللهم انقله من ضيق اللحود ومن مراتع الدود إلى جناتك جنات الخلود. لا إله إلا أنت يا حنّان يا منّان "
         "يا بديع السماوات والأرض، تغمّد ({name}) برحمتك يا أرحم الراحمين.",
}


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.execute(
        """CREATE TABLE IF NOT EXISTS pages(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            gender TEXT NOT NULL DEFAULT 'f',
            creator TEXT,
            affiliation TEXT,
            c0 INTEGER NOT NULL DEFAULT 0,
            c1 INTEGER NOT NULL DEFAULT 0,
            c2 INTEGER NOT NULL DEFAULT 0,
            visitors INTEGER NOT NULL DEFAULT 0,
            created TEXT DEFAULT CURRENT_TIMESTAMP)"""
    )
    if db.execute("SELECT COUNT(*) FROM pages").fetchone()[0] == 0:
        db.execute(
            "INSERT INTO pages(name, gender, creator, affiliation) VALUES (?,?,?,?)",
            (
                "والدة الزميلة خلادي راضية",
                "f",
                "د. بدر الدين أمينة — Dr. BADREDDINE Amina",
                "أستاذة محاضرة، قسم العلوم الاقتصادية والتسيير، جامعة محمد بوقرة، بومرداس، الجزائر",
            ),
        )
    db.commit()
    db.close()


init_db()


def page_or_404(pid):
    row = get_db().execute("SELECT * FROM pages WHERE id=?", (pid,)).fetchone()
    if row is None:
        abort(404)
    return row


@app.route("/")
def index():
    rows = get_db().execute(
        "SELECT id, name, c0+c1+c2 AS total FROM pages ORDER BY id DESC LIMIT 20"
    ).fetchall()
    return render_template("index.html", rows=rows)


@app.route("/new", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        name = request.form.get("name", "").strip()[:120]
        if not name:
            return render_template("new.html", error="اكتب اسم المتوفى"), 400
        gender = "m" if request.form.get("gender") == "m" else "f"
        creator = request.form.get("creator", "").strip()[:150]
        aff = request.form.get("affiliation", "").strip()[:250]
        cur = get_db().execute(
            "INSERT INTO pages(name, gender, creator, affiliation) VALUES (?,?,?,?)",
            (name, gender, creator, aff),
        )
        get_db().commit()
        return redirect(url_for("tasbih", pid=cur.lastrowid))
    return render_template("new.html", error=None)


@app.route("/tasbih/<int:pid>")
def tasbih(pid):
    p = page_or_404(pid)
    dua = DUA[p["gender"]].format(name=p["name"])
    return render_template("tasbih.html", p=p, dua=dua)


@app.post("/api/<int:pid>/tap")
def tap(pid):
    page_or_404(pid)
    data = request.get_json(silent=True) or {}
    try:
        idx = int(data.get("dhikr", 0))
        n = max(1, min(int(data.get("n", 1)), 100))
    except (TypeError, ValueError):
        abort(400)
    if idx not in (0, 1, 2):
        abort(400)
    db = get_db()
    db.execute(f"UPDATE pages SET c{idx}=c{idx}+? WHERE id=?", (n, pid))
    db.commit()
    return stats(pid)


@app.post("/api/<int:pid>/join")
def join(pid):
    page_or_404(pid)
    db = get_db()
    db.execute("UPDATE pages SET visitors=visitors+1 WHERE id=?", (pid,))
    db.commit()
    return stats(pid)


@app.get("/api/<int:pid>/stats")
def stats(pid):
    p = page_or_404(pid)
    return jsonify(c=[p["c0"], p["c1"], p["c2"]], total=p["c0"] + p["c1"] + p["c2"], visitors=p["visitors"])


if __name__ == "__main__":
    app.run(debug=True)
