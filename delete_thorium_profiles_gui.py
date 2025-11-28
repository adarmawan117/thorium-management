import shutil
import sys
import os
import json
import traceback

import method.directory as mydir

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import pyqtSignal

from time import sleep

from delete_thorium_new import get_complete_profiles


class FolderDropTextEdit(QtWidgets.QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)  # Aktifkan fitur drag and drop

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():  # Cek apakah ada URL yang didrag
            urls = event.mimeData().urls()
            if len(urls) == 1:  # Pastikan hanya satu item yang didrag
                folder_path = urls[0].toLocalFile()
                if os.path.isdir(folder_path):  # Pastikan itu folder, bukan file
                    event.acceptProposedAction()
                    return
        event.ignore()  # Abaikan jika bukan folder atau lebih dari satu item

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if len(urls) == 1:
            folder_path = urls[0].toLocalFile()
            if os.path.isdir(folder_path):
                self.setText(folder_path)  # Set teks di QTextEdit dengan path folder
                event.acceptProposedAction()
                return
        event.ignore()


class CenterDelegate(QtWidgets.QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignCenter


class Ui_Frame(QtCore.QObject):  # Menjadikan Ui_Frame sebagai QObject
    def __init__(self, parent=None):
        super().__init__(parent)

    def log(self, message=""):
        full_message = f"[GUI] {message}"
        print(full_message)

    def setupUi(self, Frame):
        Frame.setObjectName("Frame")
        Frame.resize(594, 440)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(mydir.icon_apps_dir, "thorium-merah.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Frame.setWindowIcon(icon)
        Frame.setWindowTitle("Delete Thorium Profiles")

        # region Input File
        y = 30
        self.label_table = QtWidgets.QLabel(Frame)
        self.label_table.setText("Choose Thorium Profiles")
        self.label_table.setGeometry(QtCore.QRect(20, y, 215, 16))

        y += 20
        self.tableProfiles = QtWidgets.QTableWidget(Frame)
        self.tableProfiles.setGeometry(QtCore.QRect(20, y, 551, 250))
        self.tableProfiles.setColumnCount(4)
        self.tableProfiles.setHorizontalHeaderLabels(["No", "Nama", "Kode", "Full Path"])
        self.tableProfiles.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableProfiles.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.tableProfiles.verticalHeader().setVisible(False)   # Menghilangkan nomor urut bawaan

        self.tableProfiles.verticalHeader().setDefaultSectionSize(25)  # Atur tinggi baris
        self.tableProfiles.setItemDelegateForColumn(0, CenterDelegate(self.tableProfiles))  # Agar Semua Baris Otomatis Rata Tengah
        self.tableProfiles.setItemDelegateForColumn(2, CenterDelegate(self.tableProfiles))  # Agar Semua Baris Otomatis Rata Tengah

        self.tableProfiles.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Interactive)  # lebar otomatis tetapi tetap bisa diatur secara manual oleh user
        self.tableProfiles.setColumnWidth(0, 30)
        self.tableProfiles.setColumnWidth(1, 150)
        self.tableProfiles.setColumnWidth(2, 50)
        self.tableProfiles.setColumnWidth(3, 300)

        self.tableProfiles.installEventFilter(self)  # Pasang event filter pada tabel

        y += 260
        self.btnDelete = QtWidgets.QPushButton(Frame)
        self.btnDelete.setText("Delete")
        self.btnDelete.setGeometry(QtCore.QRect(20, y, 551, 35))
        self.btnDelete.setStyleSheet("""
                            QPushButton {
                                background-color: #950C0C;  /* Background normal */
                                color: white;  /* Foreground normal */
                                border: none;
                                padding: 10px;
                                border-radius: 6px;
                            }
                            QPushButton:hover {
                                background-color: #830B0B;  /* Background ketika hover */
                                color: white;  /* Foreground saat hover */
                            }
                        """)
        self.btnDelete.clicked.connect(self.btnProcessClicked)

        y += 35
        self.label_warning = QtWidgets.QLabel(Frame)
        self.label_warning.setGeometry(QtCore.QRect(20, y, 441, 16))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label_warning.setFont(font)

        y += 35

        # Timer untuk mengatur durasi pesan kesalahan (5 detik)
        self.timer_warning = QTimer(Frame)
        self.timer_warning.timeout.connect(self.clear_warning)

        self.resetTable()

    def resetTable(self):
        try:
            complete_profiles = get_complete_profiles()
            self.tableProfiles.setRowCount(len(complete_profiles))
            # self.tableProfiles.setRowCount(1)

            no = 0
            for profile in complete_profiles:
                print(profile)
                # if profile['kode_profile'] == 9999:
                self.tableProfiles.setItem(no, 0, QtWidgets.QTableWidgetItem(str(no+1)))
                self.tableProfiles.setItem(no, 1, QtWidgets.QTableWidgetItem(profile['name']))
                self.tableProfiles.setItem(no, 2, QtWidgets.QTableWidgetItem(str(profile['kode_profile'])))
                self.tableProfiles.setItem(no, 3, QtWidgets.QTableWidgetItem(profile['full_path']))

                no += 1
        except:
            traceback.print_exc()
            sys.exit(-1)

    def eventFilter(self, obj, event):
        if obj == self.tableProfiles and event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Delete:
                self.deleteSelectedRows()
                return True
        return super().eventFilter(obj, event)

    def deleteSelectedRows(self):
        selected_indexes = self.tableProfiles.selectionModel().selectedRows()
        if not selected_indexes:
            return

        confirm = QtWidgets.QMessageBox.question(
            None, "Konfirmasi", "Apakah Anda yakin ingin menghapus baris yang dipilih?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No
        )

        if confirm == QtWidgets.QMessageBox.Yes:
            for index in sorted(selected_indexes, key=lambda x: x.row(), reverse=True):
                self.tableProfiles.removeRow(index.row())

    def btnProcessClicked(self):
        selected_profiles = []
        for row in range(self.tableProfiles.rowCount()):
            item = self.tableProfiles.item(row, 3).text()
            selected_profiles.append(item)

        if len(selected_profiles) == 0:
            self.display_warning("Choose an account(s)")

        confirm = QtWidgets.QMessageBox.question(
            None, "Konfirmasi", "Apakah Anda yakin ingin menghapus Profile Profile ini.?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No
        )

        if confirm == QtWidgets.QMessageBox.Yes:
            for full_path in selected_profiles:
                print(f"Menghapus folder -->> {full_path}")
                shutil.rmtree(full_path)
                self.display_warning("Folder berhasil dihapus")

            self.resetTable()

    def display_warning(self, message):
        # Menampilkan pesan warning
        self.label_warning.setText(f"WARNING: {message}")

        # Mengaktifkan timer 5 detik untuk mengembalikan teks ke "WARNING: "
        self.timer_warning.start(5000)
        self.label_warning.setStyleSheet(f"color: rgb(255, 51, 51);")

    def clear_warning(self):
        # Mengembalikan teks ke "WARNING: " dan menghentikan timer
        self.label_warning.setText("")
        self.timer_warning.stop()
        self.label_warning.setStyleSheet(f"color: rgb(0, 0, 0);")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    Frame = QtWidgets.QFrame()
    ui = Ui_Frame()
    ui.setupUi(Frame)
    Frame.show()
    sys.exit(app.exec_())




