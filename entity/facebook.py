from enum import Enum


class AkunFacebook:
    def __init__(self, nama="Unloggedin", email="", password="", tanggal_dibuat="", kode_profile=""):
        self.nama = nama
        self.email = email
        self.password = password
        self.tanggal_dibuat = tanggal_dibuat
        self.kode_profile = kode_profile

    def debug(self):
        print(f"Nama : {self.nama}")
        print(f"Email : {self.email}")
