from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_mysqldb import MySQL
import os
import math
from werkzeug.utils import secure_filename

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'ijeny46'
app.config['MYSQL_DB'] = 'crud_toko_baju'
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'UPLOAD_FOLDER')
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}

# folder untuk foto
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

mysql = MySQL(app)

def allowed_file(filename):
    """Mengecek apakah ekstensi file diizinkan."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET'])
def index():
    """Menampilkan daftar produk dengan fitur pagination dan search."""
    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 5
    offset = (page - 1) * per_page

    cur = mysql.connection.cursor()

    # menghitung total data 
    if search_query:
        cur.execute("SELECT COUNT(*) FROM toko_baju WHERE nama_baju LIKE %s", 
                    (f"%{search_query}%",))
    else:
        cur.execute("SELECT COUNT(*) FROM toko_baju")

    total_rows = cur.fetchone()[0]
    total_pages = math.ceil(total_rows / per_page)

    # mengambil data berdasarkan pagination dan pencarian
    if search_query:
        cur.execute("""
            SELECT * FROM toko_baju
            WHERE nama_baju LIKE %s
            LIMIT %s OFFSET %s
            """,
            (f"%{search_query}%", per_page, offset))
    else:
        cur.execute("SELECT * FROM toko_baju LIMIT %s OFFSET %s", (per_page, offset))

    stoks = cur.fetchall()
    cur.close()

    # mengirimkan data ke template indexuts.html
    return render_template('indexuts.html', dts_stok=stoks, page=page,
                           total_pages=total_pages, search_query=search_query)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Menyajikan file yang diunggah dari folder 'uploads'."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/add', methods=['GET','POST'])
def add_file():
    if request.method == 'POST':
        kode = request.form['kode_baju']
        nama = request.form['nama_baju']
        ukuran = request.form['ukuran']
        warna = request.form['warna']
        # Pastikan input numerik diubah ke int/float jika diperlukan di Python
        try:
            stok = int(request.form['stok'])
            harga = float(request.form['harga'])
        except ValueError:
            # Handle error jika input bukan angka
            return "Error: Stok dan Harga harus berupa angka!", 400 
            
        file = request.files.get('file')

        filename = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # Kueri INSERT
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO toko_baju (kode_baju, nama_baju, ukuran, warna, stok, harga, filename) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, 
            (kode, nama, ukuran, warna, stok, harga, filename)) 
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('index'))

    return render_template('adduts.html')

@app.route('/edit/<id>', methods=['GET','POST'])
def edit_file(id):
    """Mengedit produk berdasarkan kode (UPDATE)."""
    cur = mysql.connection.cursor()
    # PENTING: Kolom yang dicari harus 'kode', bukan 'id' jika id di URL adalah kode
    cur.execute("SELECT * FROM toko_baju WHERE kode = %s", (id,)) 
    stok_data = cur.fetchone()

    # Handle jika data tidak ditemukan
    if not stok_data:
        cur.close()
        return "Produk tidak ditemukan!", 404

    if request.method == 'POST': 
        kode = request.form['kode_baju']
        nama = request.form['nama_baju']
        ukuran = request.form['ukuran']
        warna = request.form['warna']
        stok = request.form['stok']
        harga = request.form['harga']
        new_file = request.files.get('file')

        # Ambil nama file lama (index 7, jika SELECT * digunakan)
        filename = stok_data[7] 

        if new_file and allowed_file(new_file.filename):
            # menghapus file lama (jika ada)
            if filename: 
                old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
            
            # menyimpan file baru
            filename = secure_filename(new_file.filename)
            new_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # mengupdate dengan filename baru
            cur.execute("""
                UPDATE toko_baju SET kode_baju = %s, nama_baju = %s, ukuran = %s, warna = %s, stok = %s, harga = %s, filename = %s 
                WHERE kode_baju = %s
                """, 
                (kode, nama, ukuran, warna, stok, harga, filename, id))
        else:
            # update tanpa mengubah filename 
            cur.execute("""
                UPDATE toko_baju SET kode_baju = %s, nama_baju = %s, ukuran = %s, warna = %s, stok = %s, harga = %s 
                WHERE kode_baju = %s
                """, 
                (kode, nama, ukuran, warna, stok, harga, id))
            
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('index'))

    cur.close()
    return render_template('edituts.html', stok_data=stok_data)

@app.route('/delete/<id>')
def delete_file(id):
    """Menghapus produk berdasarkan kode (DELETE)."""
    cur = mysql.connection.cursor()
    
    # mengambil nama file untuk dihapus
    cur.execute("SELECT filename FROM toko_baju WHERE kode = %s", (id,))
    file_data = cur.fetchone()
    
    # menghapus file dari folder
    if file_data and file_data[0]:
        file = file_data[0]
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
        if file and os.path.exists(file_path):
            os.remove(file_path)
            
    # menghapus data dari database
    cur.execute("DELETE FROM toko_baju WHERE kode = %s", (id,))
    mysql.connection.commit()
    cur.close()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
