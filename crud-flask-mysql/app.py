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
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('q', '')
    size = request.args.get('size', '')

    per_page = 5
    offset = (page - 1) * per_page

    cur = mysql.connection.cursor()

    where = []
    params = []

    if keyword:
        where.append("(kode_baju LIKE %s OR nama_baju LIKE %s)")
        params.extend([f"%{keyword}%", f"%{keyword}%"])

    if size:
        where.append("ukuran = %s")
        params.append(size)

    where_sql = "WHERE " + " AND ".join(where) if where else ""

    # ambil data sesuai filter + pagination
    cur.execute(f"""
        SELECT * FROM toko_baju
        {where_sql}
        LIMIT %s OFFSET %s
    """, (*params, per_page, offset))
    data = cur.fetchall()

    # hitung total data
    cur.execute(f"""
        SELECT COUNT(*) FROM toko_baju
        {where_sql}
    """, params)
    total_data = cur.fetchone()[0]
    # ambil master ukuran
    cur.execute("SELECT nama_ukuran FROM ukuran ORDER BY nama_ukuran")
    sizes = [row[0] for row in cur.fetchall()]

    total_pages = (total_data + per_page - 1) // per_page
    cur.close()

    return render_template(
        'index.html',
        dtstok=data,
        page=page,
        total_pages=total_pages,
        keyword=keyword,
        size=size,
        sizes=sizes
    )

# ukuran
@app.route('/ukuran', methods=['GET', 'POST'])
def ukuran():
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        nama = request.form['nama_ukuran'].upper()

        try:
            cur.execute(
                "INSERT INTO ukuran (nama_ukuran) VALUES (%s)",
                (nama,)
            )
            mysql.connection.commit()
            flash("Ukuran berhasil ditambahkan", "success")
        except IntegrityError:
            mysql.connection.rollback()
            flash("Ukuran sudah ada", "error")

        return redirect(url_for('ukuran'))

    # ambil semua ukuran
    cur.execute("SELECT * FROM ukuran ORDER BY nama_ukuran")
    data = cur.fetchall()
    cur.close()

    return render_template('ukuran.html', sizes=data)

# edit ukuran
@app.route('/ukuran/edit/<int:id>', methods=['GET', 'POST'])
def edit_ukuran(id):
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        nama = request.form['nama_ukuran'].upper()

        try:
            cur.execute(
                "UPDATE ukuran SET nama_ukuran=%s WHERE id=%s",
                (nama, id)
            )
            mysql.connection.commit()
            flash("Ukuran berhasil diupdate", "success")
            return redirect(url_for('ukuran'))

        except IntegrityError:
            mysql.connection.rollback()
            flash("Ukuran sudah ada", "error")
            return redirect(url_for('edit_ukuran', id=id))

    # ambil data ukuran
    cur.execute("SELECT * FROM ukuran WHERE id=%s", (id,))
    data = cur.fetchone()
    cur.close()

    return render_template('edit_ukuran.html', data=data)

# hapus ukuran
@app.route('/ukuran/delete/<int:id>')
def delete_ukuran(id):
    cur = mysql.connection.cursor()

    # cek ukuran masih dipakai produk atau tidak
    cur.execute("""
        SELECT COUNT(*) FROM toko_baju 
        WHERE ukuran = (SELECT nama_ukuran FROM ukuran WHERE id=%s)
    """, (id,))
    total = cur.fetchone()[0]

    if total > 0:
        flash("Ukuran masih digunakan oleh produk", "error")
        cur.close()
        return redirect(url_for('ukuran'))

    cur.execute("DELETE FROM ukuran WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()
    flash("Ukuran berhasil dihapus", "success")
    return redirect(url_for('ukuran'))

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
