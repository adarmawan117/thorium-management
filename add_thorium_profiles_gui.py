import sys
import os
import add_thorium_profiles

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import pyqtSignal


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


class Ui_Frame(QtCore.QObject):  # Menjadikan Ui_Frame sebagai QObject
    def __init__(self, parent=None):
        super().__init__(parent)

    def log(self, message=""):
        full_message = f"[GUI] {message}"
        print(full_message)

    def setupUi(self, Frame):
        Frame.setObjectName("Frame")
        Frame.resize(484, 280)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("resources/icon_apps/Create Chrome.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Frame.setWindowIcon(icon)

        y = 30
        self.txtPath = FolderDropTextEdit(Frame)
        self.txtPath.setGeometry(QtCore.QRect(20, y, 383, 25))
        self.txtPath.setObjectName("txtPath")
        self.txtPath.setPlaceholderText("Input or drop Thorium installation path here...")
        self.txtPath.setStyleSheet("""
                    QTextEdit {
                        background-color: #f5f5f5;
                        border: 1px solid #b0bec5;
                        border-radius: 2px;
                    }
                    QTextEdit:focus {
                        border: 1px solid #1e88e5;
                    }
                """)

        self.btnLoadProfilesFile = QtWidgets.QPushButton(Frame)
        self.btnLoadProfilesFile.setGeometry(QtCore.QRect(408, y, 55, 25))
        icon = QtGui.QIcon('resources/icon_program/Process.png')  # Ganti dengan path ikon Anda
        self.btnLoadProfilesFile.setIcon(icon)
        self.btnLoadProfilesFile.setObjectName("btnLoadProfilesFile")
        self.btnLoadProfilesFile.setStyleSheet("""
                                    QPushButton {
                                        background-color: #388E3C;  /* Background normal */
                                        color: white;  /* Foreground normal */
                                        border: none;
                                        padding: 2px;
                                        border-radius: 2px;
                                    }
                                    QPushButton:hover {
                                        background-color: #66BB6A;  /* Background ketika hover */
                                        color: white;  /* Foreground saat hover */
                                    }
                                """)
        self.btnLoadProfilesFile.clicked.connect(self.btnLoadProfilesFileClicked)

        y += 30
        self.txtPreview = QtWidgets.QPlainTextEdit(Frame)
        self.txtPreview.setGeometry(QtCore.QRect(20, y, 441, 120))
        self.txtPreview.setObjectName("txtPreview")
        self.txtPreview.setPlaceholderText("Input new profile names here...")
        self.txtPreview.setStyleSheet("""
            QPlainTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #b0bec5;
                border-radius: 4px;
            }
            QPlainTextEdit:focus {
                border: 1px solid #1e88e5;
            }
        """)

        y += 130
        self.btnCreate = QtWidgets.QPushButton(Frame)
        self.btnCreate.setGeometry(QtCore.QRect(20, y, 441, 35))
        self.btnCreate.setObjectName("btnCreate")
        self.btnCreate.setStyleSheet("""
                            QPushButton {
                                background-color: #1e88e5;  /* Background normal */
                                color: white;  /* Foreground normal */
                                border: none;
                                padding: 10px;
                                border-radius: 6px;
                            }
                            QPushButton:hover {
                                background-color: #b0bec5;  /* Background ketika hover */
                                color: white;  /* Foreground saat hover */
                            }
                        """)
        self.btnCreate.clicked.connect(self.btnProcessClicked)

        y += 35
        self.label_warning = QtWidgets.QLabel(Frame)
        self.label_warning.setGeometry(QtCore.QRect(20, y, 441, 16))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label_warning.setFont(font)
        self.label_warning.setObjectName("label_warning")

        self.retranslateUi(Frame)

        # Timer untuk mengatur durasi pesan kesalahan (5 detik)
        self.timer_warning = QTimer(Frame)
        self.timer_warning.timeout.connect(self.clear_warning)

        QtCore.QMetaObject.connectSlotsByName(Frame)

    def retranslateUi(self, Frame):
        _translate = QtCore.QCoreApplication.translate
        Frame.setWindowTitle(_translate("Frame", "Thorium Profiles Creator"))
        self.btnCreate.setText(_translate("Frame", "Create"))

    def btnLoadProfilesFileClicked(self):
        thorium_installation_path = self.txtPath.toPlainText().replace("file:///", "")
        user_data_dir = os.path.join(thorium_installation_path, 'USER_DATA')
        if not (os.path.exists(user_data_dir) and os.path.isdir(user_data_dir)):
            self.display_warning("There is no USER_DATA dir inside Thorium path")

    def btnProcessClicked(self):
        preview_text = self.txtPreview.toPlainText()
        thorium_installation_path = self.txtPath.toPlainText().replace("file:///", "")

        if thorium_installation_path == "":
            self.display_warning("You have not entered thorium installation path")
            return

        user_data_dir = os.path.join(thorium_installation_path, 'USER_DATA')
        if not (os.path.exists(user_data_dir) and os.path.isdir(user_data_dir)):
            self.display_warning("There is no USER_DATA dir inside Thorium path")
            return

        if preview_text == "":
            self.display_warning("You have not entered profile names(s)")
            return

        profile_names = preview_text.strip().split("\n")
        add_thorium_profiles.run(profile_names, thorium_installation_path)

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




