from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# koneksi database
def db():
    conn = sqlite3.connect("tokoBaju.db")
    conn.row_factory = sqlite3.Row
    return conn

# membuat tabel jika belum ada
def init_db():
    conn = db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS produk(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kode TEXT NOT NULL,
            nama TEXT NOT NULL,
            ukuran TEXT NOT NULL,
            warna TEXT NOT NULL,
            stok INTEGER NOT NULL,
            harga REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# read
@app.route("/")
def index():
    conn = db()
    rows = conn.execute("SELECT * FROM produk").fetchall()
    conn.close()
    return render_template("index.html", stoks=rows)

# create 
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        kode = request.form["kode"]
        nama = request.form["nama"]
        ukuran = request.form["ukuran"]
        warna = request.form["warna"]
        stok = request.form["stok"]
        harga = request.form["harga"]
        conn = db()
        conn.execute("INSERT INTO produk (kode, nama, ukuran, warna, stok, harga) VALUES (?, ?, ?, ?, ?, ?)", (kode, nama, ukuran, warna, stok, harga))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    return render_template("add.html")

# update
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = db()
    Stok = conn.execute("SELECT * FROM produk WHERE id=?", (id,)).fetchone()

    if request.method == "POST":
        kode = request.form["kode"]
        nama = request.form["nama"]
        ukuran = request.form["ukuran"]
        warna = request.form["warna"]
        stok = request.form["stok"]
        harga = request.form["harga"]
        conn.execute("UPDATE produk SET kode=?, nama=?, ukuran=?, warna=?, stok=?, harga=? WHERE id=?", (kode, nama, ukuran, warna, stok, harga, id))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    
    conn.close()
    return render_template("edit.html", stoks=Stok)

# delete
@app.route("/delete/<int:id>")
def delete(id):
    conn = db()
    conn.execute("DELETE FROM produk WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)