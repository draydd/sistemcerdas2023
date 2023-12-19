# Digunakan saat mengklasifikasi jenis makanan
# Masukan berupa gambar makanan, model tensor, dan label tensor

import numpy
from PIL import Image
import tflite_runtime.interpreter as tflite

class Classifier:
    def __init__(self, model, label, mean = 127.5, std = 127.5):
        # Rata-rata dan standar deviasi untuk normalisasi
        self.mean = mean
        self.std = std
        # Muat label dari list atau file
        self.label = self.__muat_label(label)
        # Inisialisasi model interpreter
        self.interpreter = tflite.Interpreter(model)
        self.interpreter.allocate_tensors()

    def __muat_label(self, label):
        # Cek apakah tipe label adalah sejenis array
        if isinstance(label, (list, tuple, set)): pass
        else:
            try:
                # Coba baca label sebagai file
                with open(label, "r") as file:
                    # Simpan baris-baris nama pada file label menjadi list
                    label = [ baris.strip() for baris in file.readlines() ]
            except Exception:
                # Beri tahu pengguna bila label tidak dapat terdefinisi
                print("Label tidak dapat terdefinisi")
                return None
        # Hilangkan duplikat pada label bila ada
        return list(dict.fromkeys(label))

    def klasifikasi(self, gambar):
        # Simpan detail model masuk dan keluar
        tensor_masuk = self.interpreter.get_input_details()
        tensor_keluar = self.interpreter.get_output_details()

        # Simpan dimensi dan atur ukuran gambar
        lebar = tensor_masuk[0]["shape"][1]
        tinggi = tensor_masuk[0]["shape"][2]
        gambar = Image.open(gambar).resize((lebar, tinggi))

        # Perlebar bentuk array sesuai gambar
        data_masuk = numpy.expand_dims(gambar, axis = 0)
        if tensor_masuk[0]["dtype"] == numpy.float32:
            # Normalisasi nilai data masuk
            data_masuk = (numpy.float32(data_masuk) - self.mean) / self.std

        # Prediksi kelas dari gambar saat ini
        self.interpreter.set_tensor(tensor_masuk[0]["index"], data_masuk)
        self.interpreter.invoke()
        data_keluar = self.interpreter.get_tensor(tensor_keluar[0]["index"])

        # Kembalikan prediksi kelas yang nilainya tertinggi
        hasil_maks = numpy.squeeze(data_keluar).argmax()
        return self.label[hasil_maks]