import components as comp
import classifier as model
import api as api

# User dan password autentikasi FatSecret
fs_client_id = "341f2de724574423a20c75dccfb7ba30"
fs_client_secret = "f876d9a152984f6d9e2dfb2b6437dbfe"

def setup():
    # Set sebagai variabel global agar dapat diakses dari luar
    global kamera, load_cell, tflite, fatsecret
    # Inisialisasi sensor dan aktuator
    kamera = comp.Kamera(server = "http://192.168.242.150/", folder_simpan = "capture")
    load_cell = comp.LoadCell(dout_pin = 5, sck_pin = 6, rasio = -205)
    # Inisialisasi model klasifikasi dari file
    tflite = model.Classifier("config/model_klasifikasi.tflite", "config/label_makanan.txt")
    # Inisialisasi FatSecret API dan simpan akses token ke dalam file
    fatsecret = api.FatSecret(fs_client_id, fs_client_secret, "config/fatsecret_token.txt")

def loop():
    # Berat minimum dimana timbangan dianggap berisi (gram)
    berat_minimum = 2
    # Berat hasil pengukuran sebelumnya
    berat_sebelum = 0

    while True:
        berat_sekarang = load_cell.timbang()
        # Bila timbangan berisi maka...
        if berat_sebelum < berat_minimum <= berat_sekarang:
            print(f"Berat timbangan (telah diisi): {berat_sekarang}")
            # Tunggu X detik lalu potret dan klasifikasi makanan
            file_gambar = kamera.potret(3)
            jenis_makanan = tflite.klasifikasi(file_gambar)
            # Dapatkan estimasi kalori per gram dari id makanan paling relevan
            kalori = fatsecret.estimasi_kalori(fatsecret.cari_makanan(jenis_makanan, 20, True))
            # Simpan jenis makanan dan estimasi kalori total
            info_makanan = f"{jenis_makanan}\nKalori: {round(kalori * berat_sekarang)}"
            # Tampilkan info dan berat makanan ke terminal
            print(info_makanan + f"\nBerat: {berat_sekarang}")
        elif berat_minimum < berat_sebelum:
            print(f"Berat timbangan (isi belum berubah): {berat_sekarang}")
        else:
            print(f"Berat timbangan (kosong): {berat_sekarang}")
        # Simpan berat saat ini untuk perulangan selanjutnya
        berat_sebelum = berat_sekarang

if __name__ == "__main__":

    # Program utama
    setup()
    loop()