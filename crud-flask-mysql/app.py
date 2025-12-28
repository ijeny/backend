from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from MySQLdb import IntegrityError
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "secret123"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'img')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# meastikan folder upload ada
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# mysql config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'ijeny46'
app.config['MYSQL_DB'] = 'crud_toko_baju'

mysql = MySQL(app)

# index
@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM toko_baju")
    data = cur.fetchall()
    cur.close()
    return render_template('index.html', dtstok=data)

# add
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        kode = request.form['kode_baju']
        nama = request.form['nama_baju']
        ukuran = request.form['ukuran']
        warna = request.form['warna']
        stok = request.form['stok']
        harga = request.form['harga']

        # FILE UPLOAD
        file = request.files.get('foto')
        filename = ''

        if file and file.filename != '':
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                flash("Format gambar tidak valid", "error")
                return redirect(url_for('add'))

        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                INSERT INTO toko_baju
                (kode_baju, nama_baju, ukuran, warna, stok, harga, filename)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (kode, nama, ukuran, warna, stok, harga, filename))

            mysql.connection.commit()
            flash("Produk berhasil ditambahkan", "success")
            return redirect(url_for('index'))

        except IntegrityError:
            mysql.connection.rollback()
            flash("Kode barang sudah ada. Gunakan kode lain.", "error")
            return redirect(url_for('add'))

        finally:
            cur.close()

    return render_template('add.html')

# edit
@app.route('/edit/<kode_baju>', methods=['GET', 'POST'])
def edit(kode_baju):
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        nama = request.form['nama_baju']
        ukuran = request.form['ukuran']
        warna = request.form['warna']
        stok = request.form['stok']
        harga = request.form['harga']

        file = request.files.get('foto')
        filename = None

        if file and file.filename != '':
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                flash("Format gambar tidak valid", "error")
                return redirect(url_for('edit', kode_baju=kode_baju))

        if filename:
            cur.execute("""
                UPDATE toko_baju SET
                    nama_baju=%s,
                    ukuran=%s,
                    warna=%s,
                    stok=%s,
                    harga=%s,
                    filename=%s
                WHERE kode_baju=%s
            """, (nama, ukuran, warna, stok, harga, filename, kode_baju))
        else:
            cur.execute("""
                UPDATE toko_baju SET
                    nama_baju=%s,
                    ukuran=%s,
                    warna=%s,
                    stok=%s,
                    harga=%s
                WHERE kode_baju=%s
            """, (nama, ukuran, warna, stok, harga, kode_baju))

        mysql.connection.commit()
        cur.close()
        flash("Produk berhasil diupdate", "success")
        return redirect(url_for('index'))

    cur.execute("SELECT * FROM toko_baju WHERE kode_baju=%s", (kode_baju,))
    data = cur.fetchone()
    cur.close()
    return render_template('edit.html', dtstok=data)

# delete
@app.route('/delete/<kode_baju>')
def delete(kode_baju):
    cur = mysql.connection.cursor()

    # ambil nama file dulu
    cur.execute("SELECT filename FROM toko_baju WHERE kode_baju=%s", (kode_baju,))
    row = cur.fetchone()

    if row and row[0]:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], row[0])
        if os.path.exists(file_path):
            os.remove(file_path)

    cur.execute("DELETE FROM toko_baju WHERE kode_baju=%s", (kode_baju,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
