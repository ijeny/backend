from penambahan import tambah
from pengurangan import kurang
from pembagian import bagi
from perkalian import kali

def jalankan():
    print("---operasi hitung matematika---")

    try:
            a = int(input("masukkan angka pertama: "))
            b = int(input("masukkan angka kedua: "))
    except ValueError:
        print("yang anda inputkan tidak valid. masukkan angka!")
        return

    print("\n--Hasil Perhitungan---")

#penambahan
    HasilTambah = tambah(a,b)
    print(f"penambahan dari ({a}) dan ({b}) adalah ({HasilTambah})")

#pengurangan
    HasilKurang = kurang(a,b)
    print(f"pengurangan dari ({a}) dan ({b}) adalah ({HasilKurang})")

#pembagian
    HasilBagi = bagi(a,b)
    print(f"pembagian dari ({a}) dan ({b}) adalah ({HasilBagi})")

#perkalian
    HasilKali = kali(a,b)
    print(f"perkalian dari ({a}) dan ({b}) adalah ({HasilKali})")

if __name__ == "__main__":
    jalankan()