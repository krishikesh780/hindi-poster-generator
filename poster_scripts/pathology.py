import sys
import datetime
import csv
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QSpinBox, QDockWidget, QStackedWidget, QMessageBox, QDialog, QInputDialog,
    QFileDialog, QHeaderView, QDialogButtonBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QFont, QPageSize
from PySide6.QtPrintSupport import QPrinter
import sqlite3

def create_db():
    conn = sqlite3.connect('lab.db')
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS doctors
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  specialization TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS patients
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  age INTEGER NOT NULL,
                  gender TEXT NOT NULL,
                  phone TEXT NOT NULL,
                  address TEXT NOT NULL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS tests
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  test_name TEXT NOT NULL,
                  price REAL NOT NULL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS invoices
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  doctor_id INTEGER,
                  patient_id INTEGER,
                  date DATETIME,
                  net_total REAL,
                  discount REAL,
                  total_paid REAL,
                  balance REAL,
                  FOREIGN KEY(doctor_id) REFERENCES doctors(id),
                  FOREIGN KEY(patient_id) REFERENCES patients(id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS invoice_tests
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  invoice_id INTEGER,
                  test_id INTEGER,
                  quantity INTEGER,
                  amount REAL,
                  FOREIGN KEY(invoice_id) REFERENCES invoices(id),
                  FOREIGN KEY(test_id) REFERENCES tests(id))''')
    
    # Insert sample data if empty
    c.execute("SELECT COUNT(*) FROM doctors")
    if c.fetchone()[0] == 0:
        samples = [("Dr. Smith", "General"), ("Dr. Johnson", "Radiology")]
        c.executemany("INSERT INTO doctors (name, specialization) VALUES (?, ?)", samples)
    
    c.execute("SELECT COUNT(*) FROM tests")
    if c.fetchone()[0] == 0:
        samples = [("Blood Test", 100.0), ("X-Ray", 500.0), ("Ultrasound", 800.0), ("CBC", 200.0)]
        c.executemany("INSERT INTO tests (test_name, price) VALUES (?, ?)", samples)
    
    conn.commit()
    conn.close()

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login")
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 20px;
            }
            QLabel {
                color: #2c3e50;
                font-size: 14px;
            }
            QLineEdit {
                border: 1px solid #ced4da;
                padding: 8px;
                background-color: #f8f9fa;
                border-radius: 4px;
                font-size: 14px;
            }
            QDialogButtonBox {
                margin-top: 20px;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        layout = QFormLayout()
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter username")
        layout.addRow("Username *", self.username_edit)
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Enter password")
        layout.addRow("Password *", self.password_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def accept(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        initial_username = "admin"
        initial_password = "admin123"
        if username == initial_username and password == initial_password:
            super().accept()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password. Please try again.")
            self.username_edit.clear()
            self.password_edit.clear()

class WelcomeWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        welcome_label = QLabel("Welcome to Pathology CMS", alignment=Qt.AlignCenter)
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; padding: 20px;")
        layout.addWidget(welcome_label)
        self.setLayout(layout)

class AddDoctorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Doctor")
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 20px;
            }
            QLabel {
                color: #2c3e50;
                font-size: 14px;
            }
            QLineEdit {
                border: 1px solid #ced4da;
                padding: 8px;
                background-color: #f8f9fa;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        layout = QFormLayout()
        self.name_edit = QLineEdit()
        layout.addRow("Name *", self.name_edit)
        self.spec_edit = QLineEdit()
        layout.addRow("Specialization", self.spec_edit)
        buttons = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addRow(buttons)
        self.setLayout(layout)

    def save(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Name required")
            return
        conn = sqlite3.connect('lab.db')
        c = conn.cursor()
        c.execute("INSERT INTO doctors (name, specialization) VALUES (?, ?)", (name, self.spec_edit.text()))
        conn.commit()
        conn.close()
        self.accept()

class NewInvoicePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        
        header = QLabel("New Invoice")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        self.layout.addWidget(header)
        
        doctor_layout = QHBoxLayout()
        doctor_label = QLabel("Doctor Name *")
        self.doctor_combo = QComboBox()
        self.load_doctors()
        doctor_layout.addWidget(doctor_label)
        doctor_layout.addWidget(self.doctor_combo)
        add_doc_btn = QPushButton("Add New Doctor")
        add_doc_btn.clicked.connect(self.add_doctor)
        doctor_layout.addWidget(add_doc_btn)
        self.layout.addLayout(doctor_layout)
        
        patient_form = QFormLayout()
        self.name_edit = QLineEdit()
        patient_form.addRow("Name *", self.name_edit)
        self.age_edit = QLineEdit()
        patient_form.addRow("Age *", self.age_edit)
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Male", "Female", "Other"])
        patient_form.addRow("Gender *", self.gender_combo)
        self.phone_edit = QLineEdit()
        patient_form.addRow("Phone *", self.phone_edit)
        self.address_edit = QLineEdit()
        patient_form.addRow("Address *", self.address_edit)
        self.layout.addLayout(patient_form)
        
        add_test_btn = QPushButton("Add Test")
        add_test_btn.clicked.connect(self.add_test_row)
        self.layout.addWidget(add_test_btn)
        self.tests_table = QTableWidget(0, 5)
        self.tests_table.setHorizontalHeaderLabels(["Tests *", "Quantity *", "Price *", "Amount *", "Action"])
        self.tests_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.tests_table)
        
        summary_layout = QFormLayout()
        self.net_total_label = QLabel("0.00")
        summary_layout.addRow("Net Total *", self.net_total_label)
        self.discount_edit = QLineEdit("0")
        self.discount_edit.textChanged.connect(self.update_due)
        summary_layout.addRow("Discount Amount *", self.discount_edit)
        self.paid_edit = QLineEdit("0")
        self.paid_edit.textChanged.connect(self.update_due)
        summary_layout.addRow("Total Paid *", self.paid_edit)
        self.due_label = QLabel("0.00")
        summary_layout.addRow("Total Due:", self.due_label)
        self.layout.addLayout(summary_layout)
        
        save_btn = QPushButton("Save Invoice")
        save_btn.setObjectName("saveBtn")
        save_btn.clicked.connect(self.save_invoice)
        self.layout.addWidget(save_btn)
        
        self.setLayout(self.layout)

    def load_doctors(self):
        self.doctor_combo.clear()
        conn = sqlite3.connect('lab.db')
        c = conn.cursor()
        c.execute("SELECT id, name FROM doctors")
        for id, name in c.fetchall():
            self.doctor_combo.addItem(name, id)
        conn.close()

    def add_doctor(self):
        dialog = AddDoctorDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.load_doctors()

    def add_test_row(self):
        row = self.tests_table.rowCount()
        self.tests_table.insertRow(row)
        
        test_combo = QComboBox()
        conn = sqlite3.connect('lab.db')
        c = conn.cursor()
        c.execute("SELECT id, test_name, price FROM tests")
        tests = c.fetchall()
        conn.close()
        for id, name, price in tests:
            test_combo.addItem(name, {"id": id, "price": price})
        test_combo.currentIndexChanged.connect(lambda idx: self.update_price(row))
        self.tests_table.setCellWidget(row, 0, test_combo)
        
        qty_spin = QSpinBox()
        qty_spin.setMinimum(1)
        qty_spin.valueChanged.connect(lambda val: self.update_amount(row))
        self.tests_table.setCellWidget(row, 1, qty_spin)
        
        price_label = QLabel("0")
        self.tests_table.setCellWidget(row, 2, price_label)
        
        amount_label = QLabel("0.00")
        self.tests_table.setCellWidget(row, 3, amount_label)
        
        remove_btn = QPushButton("Remove")
        remove_btn.setObjectName("removeBtn")
        remove_btn.clicked.connect(lambda: self.remove_row(row))
        self.tests_table.setCellWidget(row, 4, remove_btn)
        
        self.update_price(row)

    def remove_row(self, row):
        self.tests_table.removeRow(row)
        self.update_net_total()

    def update_price(self, row):
        if row >= self.tests_table.rowCount():
            return
        test_combo = self.tests_table.cellWidget(row, 0)
        data = test_combo.currentData()
        if data:
            price = data["price"]
            self.tests_table.cellWidget(row, 2).setText(str(price))
            self.update_amount(row)

    def update_amount(self, row):
        if row >= self.tests_table.rowCount():
            return
        qty = self.tests_table.cellWidget(row, 1).value()
        price_text = self.tests_table.cellWidget(row, 2).text()
        try:
            price = float(price_text)
            amount = qty * price
            self.tests_table.cellWidget(row, 3).setText(f"{amount:.2f}")
            self.update_net_total()
        except ValueError:
            pass

    def update_net_total(self):
        total = 0.0
        for row in range(self.tests_table.rowCount()):
            amount_text = self.tests_table.cellWidget(row, 3).text()
            try:
                total += float(amount_text)
            except ValueError:
                pass
        self.net_total_label.setText(f"{total:.2f}")
        self.update_due()

    def update_due(self):
        try:
            net = float(self.net_total_label.text())
            disc = float(self.discount_edit.text() or "0")
            paid = float(self.paid_edit.text() or "0")
            due = net - disc - paid
            self.due_label.setText(f"{due:.2f}" if due >= 0 else "0.00")
        except ValueError:
            self.due_label.setText("0.00")

    def save_invoice(self):
        if self.doctor_combo.currentIndex() == -1:
            QMessageBox.warning(self, "Error", "Select Doctor")
            return
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Patient Name required")
            return
        age_text = self.age_edit.text().strip()
        if not age_text.isdigit():
            QMessageBox.warning(self, "Error", "Age must be number")
            return
        age = int(age_text)
        gender = self.gender_combo.currentText()
        if not gender:
            QMessageBox.warning(self, "Error", "Select Gender")
            return
        phone = self.phone_edit.text().strip()
        if not phone.isdigit():
            QMessageBox.warning(self, "Error", "Phone must be numeric")
            return
        address = self.address_edit.text().strip()
        if not address:
            QMessageBox.warning(self, "Error", "Address required")
            return
        if self.tests_table.rowCount() == 0:
            QMessageBox.warning(self, "Error", "Add at least one test")
            return
        net = float(self.net_total_label.text())
        if net == 0:
            QMessageBox.warning(self, "Error", "Net Total cannot be zero")
            return
        try:
            disc = float(self.discount_edit.text() or "0")
            paid = float(self.paid_edit.text() or "0")
        except ValueError:
            QMessageBox.warning(self, "Error", "Discount and Paid must be numbers")
            return
        if disc < 0 or paid < 0:
            QMessageBox.warning(self, "Error", "Negative values not allowed")
            return
        if disc > net:
            QMessageBox.warning(self, "Error", "Discount cannot exceed Net Total")
            return
        if paid > net - disc:
            QMessageBox.warning(self, "Error", "Total Paid cannot exceed amount after discount")
            return
        balance = net - disc - paid
        
        conn = sqlite3.connect('lab.db')
        c = conn.cursor()
        c.execute("INSERT INTO patients (name, age, gender, phone, address) VALUES (?, ?, ?, ?, ?)",
                  (name, age, gender, phone, address))
        patient_id = c.lastrowid
        doctor_id = self.doctor_combo.currentData()
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO invoices (doctor_id, patient_id, date, net_total, discount, total_paid, balance) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (doctor_id, patient_id, date, net, disc, paid, balance))
        invoice_id = c.lastrowid
        for row in range(self.tests_table.rowCount()):
            test_combo = self.tests_table.cellWidget(row, 0)
            test_id = test_combo.currentData()["id"]
            qty = self.tests_table.cellWidget(row, 1).value()
            amount = float(self.tests_table.cellWidget(row, 3).text())
            c.execute("INSERT INTO invoice_tests (invoice_id, test_id, quantity, amount) VALUES (?, ?, ?, ?)",
                      (invoice_id, test_id, qty, amount))
        conn.commit()
        conn.close()
        QMessageBox.information(self, "Success", "Invoice saved")
        self.name_edit.clear()
        self.age_edit.clear()
        self.gender_combo.setCurrentIndex(0)
        self.phone_edit.clear()
        self.address_edit.clear()
        self.tests_table.setRowCount(0)
        self.discount_edit.setText("0")
        self.paid_edit.setText("0")
        self.update_net_total()

class InvoiceListPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_page = 0
        self.per_page = 20
        self.total_pages = 0
        layout = QVBoxLayout()
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self.search_changed)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)
        self.invoices_table = QTableWidget(0, 11)
        self.invoices_table.setHorizontalHeaderLabels(["Invoice ID", "Date", "Doctor", "Patient", "Age", "Gender", "Tests", "Net Total", "Paid", "Balance", "Action"])
        self.invoices_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.invoices_table)
        pag_layout = QHBoxLayout()
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.prev_page)
        pag_layout.addWidget(self.prev_btn)
        self.page_label = QLabel("Page 1 of 1")
        pag_layout.addWidget(self.page_label)
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.next_page)
        pag_layout.addWidget(self.next_btn)
        layout.addLayout(pag_layout)
        self.setLayout(layout)
        self.load_invoices()

    def search_changed(self):
        self.current_page = 0
        self.load_invoices()

    def load_invoices(self):
        search = self.search_edit.text().strip().lower()
        conn = sqlite3.connect('lab.db')
        c = conn.cursor()
        count_query = """
        SELECT COUNT(*)
        FROM invoices i
        JOIN doctors d ON i.doctor_id = d.id
        JOIN patients p ON i.patient_id = p.id
        """
        params = ()
        if search:
            count_query += " WHERE LOWER(p.name) LIKE ? OR LOWER(p.phone) LIKE ? OR LOWER(i.date) LIKE ?"
            params = (f"%{search}%", f"%{search}%", f"%{search}%")
        c.execute(count_query, params)
        total = c.fetchone()[0]
        self.total_pages = (total + self.per_page - 1) // self.per_page if total > 0 else 1
        self.page_label.setText(f"Page {self.current_page + 1} of {self.total_pages}")
        if self.current_page >= self.total_pages:
            self.current_page = self.total_pages - 1

        query = """
        SELECT i.id, i.date, d.name, p.name, p.age, p.gender, i.net_total, i.total_paid, i.balance
        FROM invoices i
        JOIN doctors d ON i.doctor_id = d.id
        JOIN patients p ON i.patient_id = p.id
        """
        if search:
            query += " WHERE LOWER(p.name) LIKE ? OR LOWER(p.phone) LIKE ? OR LOWER(i.date) LIKE ?"
        query += " ORDER BY i.id DESC LIMIT ? OFFSET ?"
        offset = self.current_page * self.per_page
        if search:
            params = (f"%{search}%", f"%{search}%", f"%{search}%", self.per_page, offset)
        else:
            params = (self.per_page, offset)
        c.execute(query, params)
        invoices = c.fetchall()
        self.invoices_table.setRowCount(0)
        for inv in invoices:
            row = self.invoices_table.rowCount()
            self.invoices_table.insertRow(row)
            self.invoices_table.setItem(row, 0, QTableWidgetItem(str(inv[0])))
            self.invoices_table.setItem(row, 1, QTableWidgetItem(inv[1]))
            self.invoices_table.setItem(row, 2, QTableWidgetItem(inv[2]))
            self.invoices_table.setItem(row, 3, QTableWidgetItem(inv[3]))
            self.invoices_table.setItem(row, 4, QTableWidgetItem(str(inv[4])))
            self.invoices_table.setItem(row, 5, QTableWidgetItem(inv[5]))
            c.execute("""
            SELECT t.test_name
            FROM invoice_tests it
            JOIN tests t ON it.test_id = t.id
            WHERE it.invoice_id = ?
            """, (inv[0],))
            tests = [row[0] for row in c.fetchall()]
            self.invoices_table.setItem(row, 6, QTableWidgetItem(", ".join(tests)))
            self.invoices_table.setItem(row, 7, QTableWidgetItem(f"{inv[6]:.2f}"))
            self.invoices_table.setItem(row, 8, QTableWidgetItem(f"{inv[7]:.2f}"))
            self.invoices_table.setItem(row, 9, QTableWidgetItem(f"{inv[8]:.2f}"))
            export_btn = QPushButton("Export PDF")
            export_btn.clicked.connect(lambda checked, id=inv[0]: self.export_pdf(id))
            self.invoices_table.setCellWidget(row, 10, export_btn)
        conn.close()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.load_invoices()

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.load_invoices()

    def export_pdf(self, inv_id):
        conn = sqlite3.connect('lab.db')
        c = conn.cursor()
        c.execute("SELECT * FROM invoices WHERE id=?", (inv_id,))
        inv = c.fetchone()
        if not inv:
            QMessageBox.warning(self, "Error", "Invoice not found")
            conn.close()
            return
        c.execute("SELECT name, specialization FROM doctors WHERE id=?", (inv[1],))
        doc = c.fetchone()
        c.execute("SELECT name, age, gender, phone, address FROM patients WHERE id=?", (inv[2],))
        pat = c.fetchone()
        c.execute("SELECT t.test_name, it.quantity, t.price, it.amount FROM invoice_tests it JOIN tests t ON it.test_id=t.id WHERE it.invoice_id=?", (inv_id,))
        tests = c.fetchall()
        conn.close()
        
        printer = QPrinter()
        printer.setPageSize(QPageSize(QPageSize.A4))  # Fixed using QPageSize.A4
        printer.setOutputFormat(QPrinter.PdfFormat)
        file_name, _ = QFileDialog.getSaveFileName(self, "Save PDF", f"invoice_{inv_id}.pdf", "PDF (*.pdf)")
        if file_name:
            printer.setOutputFileName(file_name)
            painter = QPainter(printer)
            painter.setFont(QFont("Arial", 16, QFont.Bold))
            painter.drawText(200, 100, "Diagnostic Lab Invoice")
            painter.setFont(QFont("Arial", 10))
            painter.drawLine(100, 120, 500, 120)
            
            y = 150
            painter.drawText(100, y, f"Invoice ID: {inv[0]}")
            y += 30
            painter.drawText(100, y, f"Date: {inv[3]}")
            y += 30
            painter.drawText(100, y, f"Doctor: {doc[0]} ({doc[1] if doc[1] else 'N/A'})")
            y += 30
            painter.drawText(100, y, f"Patient: {pat[0]}, Age: {pat[1]}, Gender: {pat[2]}")
            y += 30
            painter.drawText(100, y, f"Phone: {pat[3]}, Address: {pat[4]}")
            y += 60
            
            painter.setFont(QFont("Arial", 10, QFont.Bold))
            headers = ["Test Name", "Quantity", "Price", "Amount"]
            x_positions = [100, 300, 400, 500]
            for i, h in enumerate(headers):
                painter.drawText(x_positions[i], y, h)
            y += 20
            painter.drawLine(100, y, 600, y)
            painter.setFont(QFont("Arial", 10))
            for test in tests:
                y += 20
                painter.drawText(x_positions[0], y, test[0])
                painter.drawText(x_positions[1], y, str(test[1]))
                painter.drawText(x_positions[2], y, f"{test[2]:.2f}")
                painter.drawText(x_positions[3], y, f"{test[3]:.2f}")
            y += 20
            painter.drawLine(100, y, 600, y)
            
            y += 40
            painter.drawText(100, y, f"Net Total: {inv[4]:.2f}")
            y += 20
            painter.drawText(100, y, f"Discount: {inv[5]:.2f}")
            y += 20
            painter.drawText(100, y, f"Paid: {inv[6]:.2f}")
            y += 20
            painter.drawText(100, y, f"Balance: {inv[7]:.2f}")
            
            painter.end()
            QMessageBox.information(self, "Success", "PDF exported")

class PatientsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.patients_table = QTableWidget(0, 6)
        self.patients_table.setHorizontalHeaderLabels(["ID", "Name", "Age", "Gender", "Phone", "Address"])
        self.patients_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.patients_table)
        self.setLayout(layout)
        self.load_patients()

    def load_patients(self):
        conn = sqlite3.connect('lab.db')
        c = conn.cursor()
        c.execute("SELECT * FROM patients ORDER BY id DESC")
        self.patients_table.setRowCount(0)
        for row_data in c.fetchall():
            row = self.patients_table.rowCount()
            self.patients_table.insertRow(row)
            for col, val in enumerate(row_data):
                self.patients_table.setItem(row, col, QTableWidgetItem(str(val)))
        conn.close()

class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Settings", styleSheet="font-size: 18px; font-weight: bold; color: #2c3e50;"))
        add_test_btn = QPushButton("Add New Test")
        add_test_btn.clicked.connect(self.add_test)
        layout.addWidget(add_test_btn)
        import_tests_btn = QPushButton("Import Tests from CSV")
        import_tests_btn.clicked.connect(self.import_tests)
        layout.addWidget(import_tests_btn)
        sample_tests_btn = QPushButton("Download Sample Tests CSV")
        sample_tests_btn.clicked.connect(self.download_sample_tests)
        layout.addWidget(sample_tests_btn)
        import_docs_btn = QPushButton("Import Doctors from CSV")
        import_docs_btn.clicked.connect(self.import_doctors)
        layout.addWidget(import_docs_btn)
        sample_docs_btn = QPushButton("Download Sample Doctors CSV")
        sample_docs_btn.clicked.connect(self.download_sample_doctors)
        layout.addWidget(sample_docs_btn)
        export_btn = QPushButton("Export Invoice to PDF")
        export_btn.clicked.connect(self.export_pdf_prompt)
        layout.addWidget(export_btn)
        layout.addStretch()
        self.setLayout(layout)

    def add_test(self):
        name, ok = QInputDialog.getText(self, "Add Test", "Test Name:")
        if ok and name.strip():
            price, ok = QInputDialog.getDouble(self, "Add Test", "Price:", 0.0, 0.0, 100000.0, 2)
            if ok:
                conn = sqlite3.connect('lab.db')
                c = conn.cursor()
                c.execute("INSERT INTO tests (test_name, price) VALUES (?, ?)", (name.strip(), price))
                conn.commit()
                conn.close()
                QMessageBox.information(self, "Success", "Test added")

    def import_tests(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select CSV", "", "CSV (*.csv)")
        if file_name:
            with open(file_name, 'r', newline='') as f:
                reader = csv.reader(f)
                try:
                    next(reader)  # Skip header
                except StopIteration:
                    pass
                conn = sqlite3.connect('lab.db')
                c = conn.cursor()
                inserted = 0
                for row in reader:
                    if len(row) >= 2:
                        name = row[0].strip()
                        price = float(row[1].strip())
                        if name and price >= 0:
                            c.execute("INSERT OR IGNORE INTO tests (test_name, price) VALUES (?, ?)", (name, price))
                            if c.rowcount > 0:
                                inserted += 1
                conn.commit()
                conn.close()
                QMessageBox.information(self, "Success", f"{inserted} tests imported")

    def download_sample_tests(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Sample CSV", "sample_tests.csv", "CSV (*.csv)")
        if file_name:
            with open(file_name, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Test Name", "Price"])
                writer.writerow(["Blood Test", 100.0])
                writer.writerow(["X-Ray", 500.0])
                writer.writerow(["Ultrasound", 800.0])
                writer.writerow(["CBC", 200.0])
            QMessageBox.information(self, "Success", "Sample Tests CSV downloaded")

    def import_doctors(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select CSV", "", "CSV (*.csv)")
        if file_name:
            with open(file_name, 'r', newline='') as f:
                reader = csv.reader(f)
                try:
                    next(reader)  # Skip header
                except StopIteration:
                    pass
                conn = sqlite3.connect('lab.db')
                c = conn.cursor()
                inserted = 0
                for row in reader:
                    if len(row) >= 2:
                        name = row[0].strip()
                        spec = row[1].strip()
                        if name:
                            c.execute("INSERT OR IGNORE INTO doctors (name, specialization) VALUES (?, ?)", (name, spec))
                            if c.rowcount > 0:
                                inserted += 1
                conn.commit()
                conn.close()
                QMessageBox.information(self, "Success", f"{inserted} doctors imported")

    def download_sample_doctors(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Sample CSV", "sample_doctors.csv", "CSV (*.csv)")
        if file_name:
            with open(file_name, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Name", "Specialization"])
                writer.writerow(["Dr. Smith", "General"])
                writer.writerow(["Dr. Johnson", "Radiology"])
                writer.writerow(["Dr. Lee", "Cardiology"])
                writer.writerow(["Dr. Brown", "Neurology"])
            QMessageBox.information(self, "Success", "Sample Doctors CSV downloaded")

    def export_pdf_prompt(self):
        inv_id, ok = QInputDialog.getInt(self, "Export PDF", "Invoice ID:", 1, 1, 1000000)
        if ok:
            self.export_pdf(inv_id)

    def export_pdf(self, inv_id):
        conn = sqlite3.connect('lab.db')
        c = conn.cursor()
        c.execute("SELECT * FROM invoices WHERE id=?", (inv_id,))
        inv = c.fetchone()
        if not inv:
            QMessageBox.warning(self, "Error", "Invoice not found")
            conn.close()
            return
        c.execute("SELECT name, specialization FROM doctors WHERE id=?", (inv[1],))
        doc = c.fetchone()
        c.execute("SELECT name, age, gender, phone, address FROM patients WHERE id=?", (inv[2],))
        pat = c.fetchone()
        c.execute("SELECT t.test_name, it.quantity, t.price, it.amount FROM invoice_tests it JOIN tests t ON it.test_id=t.id WHERE it.invoice_id=?", (inv_id,))
        tests = c.fetchall()
        conn.close()
        
        printer = QPrinter()
        printer.setPageSize(QPageSize(QPageSize.A4))  # Fixed using QPageSize.A4
        printer.setOutputFormat(QPrinter.PdfFormat)
        file_name, _ = QFileDialog.getSaveFileName(self, "Save PDF", f"invoice_{inv_id}.pdf", "PDF (*.pdf)")
        if file_name:
            printer.setOutputFileName(file_name)
            painter = QPainter(printer)
            painter.setFont(QFont("Arial", 16, QFont.Bold))
            painter.drawText(200, 100, "Diagnostic Lab Invoice")
            painter.setFont(QFont("Arial", 10))
            painter.drawLine(100, 120, 500, 120)
            
            y = 150
            painter.drawText(100, y, f"Invoice ID: {inv[0]}")
            y += 30
            painter.drawText(100, y, f"Date: {inv[3]}")
            y += 30
            painter.drawText(100, y, f"Doctor: {doc[0]} ({doc[1] if doc[1] else 'N/A'})")
            y += 30
            painter.drawText(100, y, f"Patient: {pat[0]}, Age: {pat[1]}, Gender: {pat[2]}")
            y += 30
            painter.drawText(100, y, f"Phone: {pat[3]}, Address: {pat[4]}")
            y += 60
            
            painter.setFont(QFont("Arial", 10, QFont.Bold))
            headers = ["Test Name", "Quantity", "Price", "Amount"]
            x_positions = [100, 300, 400, 500]
            for i, h in enumerate(headers):
                painter.drawText(x_positions[i], y, h)
            y += 20
            painter.drawLine(100, y, 600, y)
            painter.setFont(QFont("Arial", 10))
            for test in tests:
                y += 20
                painter.drawText(x_positions[0], y, test[0])
                painter.drawText(x_positions[1], y, str(test[1]))
                painter.drawText(x_positions[2], y, f"{test[2]:.2f}")
                painter.drawText(x_positions[3], y, f"{test[3]:.2f}")
            y += 20
            painter.drawLine(100, y, 600, y)
            
            y += 40
            painter.drawText(100, y, f"Net Total: {inv[4]:.2f}")
            y += 20
            painter.drawText(100, y, f"Discount: {inv[5]:.2f}")
            y += 20
            painter.drawText(100, y, f"Paid: {inv[6]:.2f}")
            y += 20
            painter.drawText(100, y, f"Balance: {inv[7]:.2f}")
            
            painter.end()
            QMessageBox.information(self, "Success", "PDF exported")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pathology CMS")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QDockWidget {
                background-color: #e9ecef;
                font-size: 14px;
                border: none;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton#removeBtn {
                background-color: #dc3545;
            }
            QPushButton#removeBtn:hover {
                background-color: #c82333;
            }
            QPushButton#saveBtn {
                background-color: #28a745;
            }
            QPushButton#saveBtn:hover {
                background-color: #218838;
            }
            QTableWidget {
                border: 1px solid #dee2e6;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #e9ecef;
                padding: 8px;
                border: 1px solid #dee2e6;
                font-weight: bold;
                color: #2c3e50;
            }
            QLabel {
                color: #2c3e50;
            }
            QLineEdit, QComboBox, QSpinBox {
                border: 1px solid #ced4da;
                padding: 8px;
                background-color: #f8f9fa;
                border-radius: 4px;
                font-size: 14px;
                color: #000000;
            }
        """)
        
        self.login_dialog = LoginDialog(self)
        if self.login_dialog.exec() == QDialog.Accepted:
            self.welcome_window = WelcomeWindow(self)
            self.setCentralWidget(self.welcome_window)
            
            sidebar = QDockWidget("Menu", self)
            sidebar.setFeatures(QDockWidget.NoDockWidgetFeatures)
            sidebar_widget = QWidget()
            sidebar_layout = QVBoxLayout()
            buttons = [
                ("Patients", self.show_patients),
                ("New Invoice", self.show_new_invoice),
                ("Invoice List", self.show_invoice_list),
                ("Settings", self.show_settings),
                ("Logout", self.logout)
            ]
            for text, slot in buttons:
                btn = QPushButton(text)
                btn.clicked.connect(slot)
                sidebar_layout.addWidget(btn)
            sidebar_layout.addStretch()
            sidebar_widget.setLayout(sidebar_layout)
            sidebar.setWidget(sidebar_widget)
            self.addDockWidget(Qt.LeftDockWidgetArea, sidebar)
            
            self.stack = QStackedWidget()
            self.patients_page = PatientsPage()
            self.new_invoice_page = NewInvoicePage()
            self.invoice_list_page = InvoiceListPage()
            self.settings_page = SettingsPage()
            self.stack.addWidget(self.patients_page)
            self.stack.addWidget(self.new_invoice_page)
            self.stack.addWidget(self.invoice_list_page)
            self.stack.addWidget(self.settings_page)
            self.welcome_window.layout().addWidget(self.stack)
            self.show_patients()
        else:
            self.close()

    def show_patients(self):
        self.patients_page.load_patients()
        self.stack.setCurrentWidget(self.patients_page)

    def show_new_invoice(self):
        self.new_invoice_page.load_doctors()
        self.stack.setCurrentWidget(self.new_invoice_page)

    def show_invoice_list(self):
        self.invoice_list_page.load_invoices()
        self.stack.setCurrentWidget(self.invoice_list_page)

    def show_settings(self):
        self.stack.setCurrentWidget(self.settings_page)

    def logout(self):
        self.login_dialog = LoginDialog(self)
        if self.login_dialog.exec() == QDialog.Accepted:
            self.show_patients()
        else:
            self.close()

if __name__ == "__main__":
    create_db()
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())