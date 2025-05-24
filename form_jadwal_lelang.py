import sys
import sqlite3
import json
import csv
import subprocess
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QTextEdit, QDateEdit, QMessageBox
)
from PyQt5.QtCore import QDate, Qt, QDateTime

DB_NAME = 'lelang-pl2.db'
TABLE_NAME = 'jadwal_lelang'
OUTPUT_FILE = 'data/jadwal_lelang_pl2.json'

class LelangForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Form Jadwal Lelang - PL II")
        self.resize(700, 400)
        self.selected_id = None

        self.initUI()
        self.load_data()

    def initUI(self):
        layout = QVBoxLayout()

        form_layout = QHBoxLayout()
        self.input_pejabat = QLineEdit()
        self.input_tanggal = QDateEdit(QDate.currentDate())
        self.input_tanggal.setCalendarPopup(True)
        self.input_tanggal.setDisplayFormat("yyyy-MM-dd")
        self.input_pemohon = QTextEdit()
        self.input_pemohon.setFixedHeight(50)

        form_layout.addWidget(QLabel("Pejabat:"))
        form_layout.addWidget(self.input_pejabat)
        form_layout.addWidget(QLabel("Tanggal:"))
        form_layout.addWidget(self.input_tanggal)
        form_layout.addWidget(QLabel("Pemohon:"))
        form_layout.addWidget(self.input_pemohon)
        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        self.btn_add = QPushButton("Tambah")
        self.btn_update = QPushButton("Update")
        self.btn_delete = QPushButton("Hapus")
        self.btn_clear = QPushButton("Bersihkan")
        self.btn_export_excel = QPushButton("Export ke Excel")
        self.btn_export_push = QPushButton("Export & Push JSON")

        self.btn_add.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 5px; border-radius: 5px;")
        self.btn_update.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 5px; border-radius: 5px;")
        self.btn_delete.setStyleSheet("background-color: #F44336; color: white; font-weight: bold; padding: 5px; border-radius: 5px;")
        self.btn_clear.setStyleSheet("background-color: #FFEB3B; color: black; font-weight: bold; padding: 5px; border-radius: 5px;")
        self.btn_export_excel.setStyleSheet("background-color: #9C27B0; color: white; font-weight: bold; padding: 5px; border-radius: 5px;")
        self.btn_export_push.setStyleSheet("background-color: #6A1B9A; color: white; font-weight: bold; padding: 5px; border-radius: 5px;")

        self.btn_add.clicked.connect(self.add_entry)
        self.btn_update.clicked.connect(self.update_entry)
        self.btn_delete.clicked.connect(self.delete_entry)
        self.btn_clear.clicked.connect(self.clear_form)
        self.btn_export_excel.clicked.connect(self.export_to_excel)
        self.btn_export_push.clicked.connect(self.export_and_push)

        for btn in [self.btn_add, self.btn_update, self.btn_delete, self.btn_clear, self.btn_export_excel, self.btn_export_push]:
            button_layout.addWidget(btn)

        layout.addLayout(button_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Pejabat", "Tanggal", "Pemohon"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellClicked.connect(self.fill_form_from_table)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_data(self):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(f"SELECT id, pejabat_lelang, tanggal, pemohon FROM {TABLE_NAME} ORDER BY tanggal DESC, pejabat_lelang ASC")
        rows = c.fetchall()
        conn.close()

        self.table.setRowCount(0)
        for row in rows:
            row_num = self.table.rowCount()
            self.table.insertRow(row_num)
            for col, val in enumerate(row[1:]):
                self.table.setItem(row_num, col, QTableWidgetItem(str(val)))

    def add_entry(self):
        pejabat = self.input_pejabat.text()
        tanggal = self.input_tanggal.date().toString("yyyy-MM-dd")
        pemohon = self.input_pemohon.toPlainText()
        now = QDateTime.currentDateTime().toString(Qt.ISODate)

        if not pejabat or not pemohon:
            QMessageBox.warning(self, "Input Error", "Semua field harus diisi.")
            return

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(f"INSERT INTO {TABLE_NAME} (pejabat_lelang, tanggal, pemohon, timestamp_created, timestamp_updated) VALUES (?, ?, ?, ?, ?)", (pejabat, tanggal, pemohon, now, now))
        conn.commit()
        conn.close()

        self.clear_form()
        self.load_data()

    def update_entry(self):
        if self.selected_id is None:
            QMessageBox.warning(self, "Update Error", "Pilih data yang ingin diperbarui.")
            return

        pejabat = self.input_pejabat.text()
        tanggal = self.input_tanggal.date().toString("yyyy-MM-dd")
        pemohon = self.input_pemohon.toPlainText()
        now = QDateTime.currentDateTime().toString(Qt.ISODate)

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(f"UPDATE {TABLE_NAME} SET pejabat_lelang = ?, tanggal = ?, pemohon = ?, timestamp_updated = ? WHERE id = ?", (pejabat, tanggal, pemohon, now, self.selected_id))
        conn.commit()
        conn.close()

        self.clear_form()
        self.load_data()

    def delete_entry(self):
        if self.selected_id is None:
            QMessageBox.warning(self, "Delete Error", "Pilih data yang ingin dihapus.")
            return

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(f"DELETE FROM {TABLE_NAME} WHERE id = ?", (self.selected_id,))
        conn.commit()
        conn.close()

        self.clear_form()
        self.load_data()

    def clear_form(self):
        self.input_pejabat.clear()
        self.input_tanggal.setDate(QDate.currentDate())
        self.input_pemohon.clear()
        self.selected_id = None
        self.table.clearSelection()

    def fill_form_from_table(self, row, column):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        tanggal = self.table.item(row, 1).text()
        pejabat = self.table.item(row, 0).text()
        pemohon = self.table.item(row, 2).text()
        c.execute(f"SELECT id FROM {TABLE_NAME} WHERE pejabat_lelang = ? AND tanggal = ? AND pemohon = ? LIMIT 1", (pejabat, tanggal, pemohon))
        result = c.fetchone()
        conn.close()
        if result:
            self.selected_id = result[0]
            self.input_pejabat.setText(pejabat)
            self.input_tanggal.setDate(QDate.fromString(tanggal, "yyyy-MM-dd"))
            self.input_pemohon.setPlainText(pemohon)

    def export_to_excel(self):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(f"SELECT * FROM {TABLE_NAME} ORDER BY tanggal DESC, pejabat_lelang ASC")
        rows = c.fetchall()
        headers = [description[0] for description in c.description]
        conn.close()

        with open('jadwal_lelang_export.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)

        QMessageBox.information(self, "Export Sukses", "Data berhasil diekspor ke 'jadwal_lelang_export.csv'")

    def export_and_push(self):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(f"SELECT pejabat_lelang, tanggal, pemohon FROM {TABLE_NAME} ORDER BY tanggal DESC, pejabat_lelang ASC")
        rows = c.fetchall()
        conn.close()

        result = {
            "judul": "Jadwal Lelang Oleh Pejabat Lelang Kelas II - SJB",
            "data": [{"pejabat_lelang": row[0], "tanggal": row[1], "pemohon": row[2]} for row in rows]
        }

        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        try:
            subprocess.run(['git', 'add', OUTPUT_FILE], check=True)
            subprocess.run(['git', 'commit', '-m', 'Manual Export & Push from Form'], check=True)
            subprocess.run(['git', 'push'], check=True)
            QMessageBox.information(self, "Export Sukses", "Data berhasil diekspor dan dipush ke GitHub!")
        except subprocess.CalledProcessError as e:
            QMessageBox.warning(self, "Git Error", f"Gagal push ke GitHub:\n{e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = LelangForm()
    form.show()
    sys.exit(app.exec_())
