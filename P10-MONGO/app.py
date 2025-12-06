from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

client = MongoClient("mongodb://localhost:27017/")
db = client["toko_baju"]
collection = db["produk"]

try:
    collection.create_index("kode", unique=True)
except Exception:
    pass

@app.route("/")
def index():
    data = list(collection.find())
    return render_template('index.html', data=data)

@app.route("/add", methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        kode = request.form['kode']
        nama = request.form['nama']
        ukuran = request.form['ukuran']
        warna = request.form['warna']
        stok = request.form['stok']
        harga = request.form['harga']
        # filename = request.form['filename']  # ❌ dihapus

        existing = collection.find_one({'kode': kode})
        if existing:
            flash('Kode barang sudah ada! Kode barang harus unik.', 'error')
            return redirect(url_for('add'))

        filename = ''
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename != '':
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                else:
                    flash(
                        'Ekstensi file tidak diizinkan! Hanya file dengan ekstensi: ' +
                        ', '.join(ALLOWED_EXTENSIONS),
                        'error'
                    )
                    return redirect(url_for('add'))

        try:
            collection.insert_one({
                "kode": kode,
                "nama": nama,
                "ukuran": ukuran,
                "warna": warna,
                "stok": stok,
                "harga": harga,
                "gambar": filename
            })
            flash('Produk berhasil ditambahkan!', 'success')
        except Exception as e:
            flash('Kode barang sudah ada! Kode barang harus unik.', 'error')
            return redirect(url_for('add'))

        return redirect(url_for('index'))

    return render_template('add.html')

@app.route("/edit/<id>", methods=['GET', 'POST'])
def edit(id):
    item = collection.find_one({"_id": ObjectId(id)})
    if request.method == 'POST':
        kode = request.form['kode']
        nama = request.form['nama']
        ukuran = request.form['ukuran']
        warna = request.form['warna']
        stok = request.form['stok']
        harga = request.form['harga']
        
        update_data = {
            'kode': kode,
            'nama': nama,
            'ukuran': ukuran,
            'warna': warna,
            'stok':stok,
            'harga': harga,
        }
        
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename != '':
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    update_data["gambar"] = filename
                else:
                    flash('Ekstensi file tidak diizinkan! Hanya file dengan ekstensi: ' + ', '.join(ALLOWED_EXTENSIONS), 'error')
                    return redirect(url_for('edit', id=id))
        
        collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})
        flash('Produk berhasil diupdate!', 'success')
        return redirect(url_for("index"))
    return render_template("edit.html", item=item)

@app.route("/delete/<id>")
def delete(id):
    collection.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
