from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_mysqldb import MySQL
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'secret123'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'ijeny46'
app.config['MYSQL_DB'] = 'crud_upload_db'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}

mysql = MySQL(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM stok")
    stok_list = cur.fetchall()
    cur.close()
    return render_template('index.html', files=stok_list)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/add', methods=['GET','POST'])
def add_file():
    if request.method == 'POST':
        kode = request.form['kode']
        nama = request.form['nama']
        harga = request.form['harga']
        file = request.files.get('file')

        filename = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO stok (kode, nama, harga, filename) VALUES (%s, %s, %s, %s)", (kode, nama, harga, filename))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('index'))

    return render_template('add.html')

@app.route('/edit/<id>', methods=['GET','POST'])
def edit_file(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM stok WHERE kode = %s", (id,))
    stok_data = cur.fetchone()

    if request.method == 'POST':
        if stok_data and stok_data[3]:
            old_file = stok_data[3]
            if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], old_file)):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], old_file))

        kode = request.form['kode']
        nama = request.form['nama']
        harga = request.form['harga']
        new_file = request.files.get('file')

        if new_file and allowed_file(new_file.filename):
            filename = secure_filename(new_file.filename)
            new_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cur.execute("UPDATE stok SET kode = %s, nama = %s, harga = %s, filename = %s WHERE kode = %s", (kode, nama, harga, filename, id))
        else:
            cur.execute("UPDATE stok SET kode = %s, nama = %s, harga = %s WHERE kode = %s", (kode, nama, harga, id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('index'))

    cur.close()
    return render_template('edit.html', stok_data=stok_data)


@app.route('/delete/<id>')
def delete_file(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT filename FROM stok WHERE kode = %s", (id,))
    file_data = cur.fetchone()
    if file_data and file_data[0]:
        file = file_data[0]
        if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], file)):
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file))
    cur.execute("DELETE FROM stok WHERE kode = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)