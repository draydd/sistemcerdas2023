# Digunakan saat mengakses komponen sensor dan aktuator
# Masukan dapat berupa nomor pin GPIO, dsb

import requests
import RPi.GPIO as GPIO
import time

# Butuh RPi.GPIO (pip)
from hx711_multi import HX711

class Kamera:
    def __init__(self, server, folder_simpan = "capture", format_file = "%Y-%m-%d %H:%M:%S"):
        # Alamat web server kamera
        self.server = server
        # Direktori untuk menyimpan gambar
        self.folder_simpan = folder_simpan
        # Format penamaan file gambar
        self.format_file = format_file

    def __waktu(self):
        # Berikan waktu saat ini sesuai format nama file gambar
        return time.strftime(self.format_file)
    
    def potret(self, jeda = 0):
        # Tunggu X detik sebelum potret
        if jeda > 0: time.sleep(jeda)
        # Tangkap gambar dari web server kamera
        gambar = requests.get(f"{self.server}/capture")
        if gambar.status_code == 200:
            # Simpan gambar ke folder destinasi sesuai format nama
            destinasi = f"{self.folder_simpan}/{self.__waktu()}.jpg"
            with open(destinasi, "wb") as file:
                try: file.write(gambar.content)
                except Exception:
                    # Beri tahu pengguna bila gagal menyimpan gambar
                    print("Destinasi gambar tidak bisa diakses atau ditulis...")
                    return None
            # Kembalikan path file gambar yang tersimpan
            return destinasi
        else:
            # Beri tahu pengguna bila server tidak dapat diakses
            print(f"Server kamera tidak dapat diakses (error {gambar.status_code})...")
            return None

class LoadCell:
    def __init__(self, dout_pin, sck_pin, rasio = 0):
        # Nomor GPIO (bukan nomor pin) sebagai acuan
        GPIO.setmode(GPIO.BCM)
        # Inisialisasi modul HX711
        self.hx711 = HX711(dout_pin, sck_pin, 128, "A", False, "CRITICAL")
        # Reset pin SCK sebelum memulai pembacaan
        self.hx711.reset()
        # Set berat yang terbaca saat ini sebagai titik nol
        input("Kosongkan beban pada timbangan dan tekan ENTER...")
        self.hx711.zero()

        if rasio == 0:
            # Kalibrasi sensor berat jika rasio belum diketahui
            kalibrasi = str(input("Ingin kalibrasi sensor berat (Y/N)? "))
            if kalibrasi == "Y" or kalibrasi == "y": self.kalibrasi()
        else:
            # Set rasio kalibrasi bila sudah diketahui
            self.hx711.set_weight_multiples(rasio)

    def __del__(self):
        # Bersihkan GPIO setelah selesai
        try: GPIO.cleanup()
        except Exception: pass
    
    def __timbang_mentah(self, hitung = 30):
        # Hitung performa (waktu) pengukuran berat
        mulai = time.perf_counter()
        # Ukur berat mentah dari beban saat ini sampai terbaca
        while self.hx711.read_raw(hitung) == None:
            durasi = int(round(time.perf_counter() - mulai))
            print(f"Berat tidak terbaca ({durasi} detik), mencoba ulang...")

    def kalibrasi(self):
        # Minta pengguna untuk meletakkan beban yang beratnya diketahui
        input("Letakkan beban pada timbangan dan tekan ENTER...")
        # Ukur berat mentah dari beban saat ini sampai terbaca
        self.__timbang_mentah()
        # Dapatkan hasil pengukuran berat mentah terakhir
        berat_mentah = self.hx711.get_raw()
        print(f"Berat mentah: {berat_mentah}")
        # Minta pengguna memasukkan berat beban sesungguhnya
        berat_asli = float(input("Masukkan berat sesungguhnya (gram): "))
        # Lakukan kalibrasi nilai berat untuk pengukuran selanjutnya
        rasio = round(berat_mentah / berat_asli, 3)
        self.hx711.set_weight_multiples(rasio)
        print(f"Rasio kalibrasi: {rasio}")

    def timbang(self):
        # Ukur berat mentah dari beban saat ini sampai terbaca
        self.__timbang_mentah()
        # Berikan hasil pengukuran berat terakhir (berat mentah dibagi rasio)
        return round(self.hx711.get_weight(), 3)