from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from flask_mysqldb import MySQL
import os
import math
from werkzeug.utils import secure_filename

# konfigurasi dasar
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.secret_key = "rahasia_app_jeny"

# konfigurasi database & upload
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'ijeny46'
app.config['MYSQL_DB'] = 'crud_toko_baju'
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}

# memastikan kalau folder upload sudah ada, jika belum ada maka akan dibuat scra otomatis
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# mengaktifkan koneksi MySQL untuk flask ini
mysql = MySQL(app)

# ini untuk mengecek apakah file yang diup itu pake ekstensi yang dibolehin
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# --- ROUTE INDEX ---
@app.route('/', methods=['GET'])
def index():
    # menampilkan daftar produk dengan pagination dan search
    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 5
    offset = (page - 1) * per_page

    cur = mysql.connection.cursor()

    # menghitung total produk biar tau total ada berapa halaman
    if search_query:
        cur.execute("SELECT COUNT(*) FROM toko_baju WHERE nama_baju LIKE %s", (f"%{search_query}%",))
    else:
        cur.execute("SELECT COUNT(*) FROM toko_baju")

    row = cur.fetchone()
    total_rows = row[0] if row else 0
    total_pages = math.ceil(total_rows / per_page) if total_rows > 0 else 1

    # mengambil data sesuai pagination dan pencarian (dihalaman sekarang)
    if search_query:
        cur.execute("""
            SELECT * FROM toko_baju
            WHERE nama_baju LIKE %s
            LIMIT %s OFFSET %s
        """, (f"%{search_query}%", per_page, offset))
    else:
        cur.execute("SELECT * FROM toko_baju LIMIT %s OFFSET %s", (per_page, offset)) # mengambil semua baris sebagai list/touple

    stoks = cur.fetchall() # untuk mengambil semua hasil data dari query SQL yg terakhir dijalankan
    cur.close() # menutup cursor

    return render_template('indexuts.html',
            dts_stok=stoks, # ini nyimpen hasilnya yg nanti bakal dikiirm ke template html dan ditampilin ke pengguna
            page=page,
            total_pages=total_pages,
            search_query=search_query)

# --- ROUTE UPLOAD FILE ---
@app.route('/uploads/<path:filename>') # buat nentuin url khusus buat nampilin file yg ada di folder uploads
def uploaded_file(filename):
    return send_from_directory(os.path.join(app.root_path, 'uploads'), filename)

# --- ROUTE TAMBAH DATA ---
@app.route('/add', methods=['GET', 'POST'])
def add_file():
    if request.method == 'POST':
        kode_baju = request.form['kode_baju']
        nama = request.form['nama_baju']
        ukuran = request.form['ukuran']
        warna = request.form['warna']

        # mengecek apakah data yang dimasukkan adalah angka
        try:
            stok = int(request.form['stok'])
            harga = float(request.form['harga'])
        except ValueError:
            flash("Stok dan Harga harus berupa angka!", "danger")
            return redirect(url_for('add_file'))

        # cek apakah kode_baju sudah digunakan
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM toko_baju WHERE kode_baju = %s", (kode_baju,))
        if cur.fetchone():
            cur.close()
            flash("Kode baju sudah ada!", "danger")
            return redirect(url_for('add_file'))

        # mengambil dan menyimpan gambar produk
        file = request.files.get('file')
        filename = None
        if file and allowed_file(file.filename): # untuk mastiin kalau format fotonya itu yg dibolehin diatas tdi
            filename = secure_filename(file.filename) # biar nama filenya ga aneh
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) # fotonya nanti bakal kesimpen di folder uploads scra otomatis

        # menyimpan data baru ke tabel toko_baju
        cur.execute("""
            INSERT INTO toko_baju (kode_baju, nama_baju, ukuran, warna, stok, harga, filename)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (kode_baju, nama, ukuran, warna, stok, harga, filename))
        mysql.connection.commit()
        cur.close()

        flash("Data berhasil ditambahkan!", "success")
        return redirect(url_for('index')) # kembali ke halaman utama (/) setelah datanya kesimpen

    return render_template('adduts.html') # kembali ke halaman tempat edit/add data baru

# --- ROUTE EDIT DATA ---
@app.route('/edit/<id>', methods=['GET','POST'])
def edit_file(id):
    # edit produk berdasarkan kode
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM toko_baju WHERE kode_baju = %s", (id,))
    stok_data = cur.fetchone()

    if not stok_data:
        cur.close()
        return "Produk tidak ditemukan!", 404

    if request.method == 'POST': # ini dijalanin kalau sudah disimpan datanya
        kode_baju = request.form['kode_baju']
        nama = request.form['nama_baju']
        ukuran = request.form['ukuran']
        warna = request.form['warna']
        stok = request.form['stok']
        harga = request.form['harga']
        new_file = request.files.get('file')

        filename = stok_data[6]  # posisi kolom filename

        # jika upload file baru
        if new_file and allowed_file(new_file.filename):
            # hapus file lama jika ada dan biar ga numpuk
            if filename:
                old_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                if os.path.exists(old_path):
                    os.remove(old_path)

            filename = secure_filename(new_file.filename) # nyimpen gambar baru ke folder pakai nama yg aman
            new_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # mengubah data lama jadi data baru berdasarkan kode baju
        cur.execute("""
            UPDATE toko_baju 
            SET kode_baju=%s, nama_baju=%s, ukuran=%s, warna=%s, stok=%s, harga=%s, filename=%s 
            WHERE kode_baju=%s 
        """, (kode_baju, nama, ukuran, warna, stok, harga, filename, id)) # ini mastiin cman data dg kode_baju tertentu yg bakal dirubah

        mysql.connection.commit() # nyimpen perubahan ke database
        cur.close()
        flash("Data berhasil diperbarui!", "success")
        return redirect(url_for('index')) # kalau udah selesai bakal mbalik ke halaman utama

    # ini dijalanin waktu pertama kali mbuka halaman edit 
    cur.close()
    return render_template('edituts.html', stok_data=stok_data) # ngirim data lama ke editutd.html biar formnya otomatis keiisi dg data lama

# --- ROUTE HAPUS DATA ---
@app.route('/delete/<id>')
def delete_file(id):
    # hapus produk berdasarkan kode
    cur = mysql.connection.cursor()
    cur.execute("SELECT filename FROM toko_baju WHERE kode_baju = %s", (id,))
    file_data = cur.fetchone()

    # buat ngecek kalau produk itu punya gambar apa ga 
    if file_data and file_data[0]:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_data[0])
        if os.path.exists(file_path):
            os.remove(file_path)

    # hapus data di database berdasarkan kode baju
    cur.execute("DELETE FROM toko_baju WHERE kode_baju = %s", (id,))
    mysql.connection.commit()
    cur.close()

    flash("Data berhasil dihapus!", "info")
    return redirect(url_for('index'))

# --- Jalankan Aplikasi ---
if __name__ == '__main__':
    app.run(debug=True)