from flask import Flask, render_template, request
from flask_mysqldb import MySQL
import math

app = Flask(__name__)

# Konfigurasi koneksi MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'ijeny46'
app.config['MYSQL_DB'] = 'crud_upload_db'

mysql = MySQL(app)

@app.route('/', methods=['GET'])
def index():
    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 5
    offset = (page - 1) * per_page

    cur = mysql.connection.cursor()

    # Hitung total data
    if search_query:
        cur.execute("SELECT COUNT(*) FROM stok WHERE nama LIKE %s",
                    (f"%{search_query}%",))
    else:
        cur.execute("SELECT COUNT(*) FROM stok")

    total_rows = cur.fetchone()[0]
    total_pages = math.ceil(total_rows / per_page)

    # Ambil data berdasarkan pagination dan pencarian
    if search_query:
        cur.execute("""
            SELECT * FROM stok
            WHERE nama LIKE %s
            LIMIT %s OFFSET %s
            """,
            (f"%{search_query}%", per_page, offset))
    else:
        cur.execute("SELECT * FROM stok LIMIT %s OFFSET %s", (per_page, offset))

    stoks = cur.fetchall()
    cur.close()

    return render_template('index.html', dts_stok=stoks, page=page,
                           total_pages=total_pages, search_query=search_query)


if __name__ == '__main__':
    app.run(debug=True)