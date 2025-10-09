from flask import Flask, jsonify
import json

#membuat instance Flask
app = Flask(__name__)

#fungsi untuk memuat data dari file json
def DataProduk(file_type):
    if file_type == 'snack':
        with open('Tugas-P3\DataSnack.json', 'r') as f:
            return json.load(f)
    elif file_type == 'drink':
        with open('Tugas-P3\DataDrink.json', 'r') as f:
            return json.load(f)


#endpoint untuk mendapatkan halaman home
@app.route('/', methods=['GET'])
def Beranda():
    return jsonify({
        "pesan" : "Selamat Datang di Produk UMKM"
    })

#endpoint untuk mendapatkan semua produk snack
@app.route('/produk/snack', methods=['GET'])
def GetProdukSnack():
    data = DataProduk('snack')
    return jsonify({
        "pesan" : "Halaman Produk Semua Snack...",
        "data"  : data
    })

#endpoint untuk mendapatkan semua produk snack dan drink
@app.route('/produk/drink', methods=['GET'])
def GetProdukDrink():
    data = DataProduk('drink')
    return jsonify({
        "pesan" : "Halaman Produk Semua Soft Drink...",
        "data"  : data
    })

#endpoint untuk mendapatkan produk snack dengan id yang sesuai
@app.route('/produk/snack/<string:IdProduk>', methods=['GET'])
def GetByIdSnack(IdProduk):
    data = DataProduk('snack')
    ID = next((item for item in data if str(item["id"]) == IdProduk), None)
    if ID:
        return jsonify({"pesan": f"Halaman Produk Snack dengan id = {IdProduk}", "data": ID})
    else:
        return jsonify({"pesan": "ID tidak ditemukan pada kategori snack!!"}), 404
    
#endpoint untuk mendapatkan produk drink dengan id yang sesuai
@app.route('/produk/drink/<string:IdProduk>', methods=['GET'])
def GetByIdDrink(IdProduk):
    data = DataProduk('drink')
    ID = next((item for item in data if str(item["id"]) == IdProduk), None)
    if ID:
        return jsonify({"pesan": f"Halaman Produk Soft Drink dengan id = {IdProduk}", "data": ID})
    else:
        return jsonify({"pesan": "ID tidak ditemukan pada kategori drink!!"}), 404
    
if __name__ == '__main__':
    app.run(debug=True)