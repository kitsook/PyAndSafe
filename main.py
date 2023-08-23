import sys
import untangle
from PyQt6 import QtGui
from PyQt6.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, \
    QFileDialog, QMessageBox, QVBoxLayout, QTableWidget, QTableWidgetItem, \
    QProgressDialog

from cipher import aes_decrypt, aes_encrypt

class AndSafeExportFile:
    def __init__(self, content):
        self.content = content

    def is_valid(self):
        return self.content and self.content.database and self.content.database['name'] == 'safe'

class Signature:
    def __init__(self, content):
        self.signature_obj = None

        if content.database.table:
            for table in content.database.table:
                if table['name'] == 'signature':
                    self.signature_obj = table

    def validate(self, password):
        if not self.signature_obj:
            return False

        data = self.signature_obj.row
        # convert to dict for quick access
        entries = { col['name']: col.cdata for col in data.col }
        # only support verstion 2 or 3
        if not entries['ver'] or not (entries['ver'] == '2' or entries['ver'] == '3'):
            return False

        try:
            encrypted = aes_encrypt(entries['iv'], entries['salt'], password, entries['plain'])
            return len(entries['payload']) > 0 and \
                entries['payload'].upper() == encrypted.hex()[0:len(entries['payload'])].upper()
        except Exception:
            return False

class Note:
    def __init__(self, content):
        self.note_table = None

        if content.database.table:
            for table in content.database.table:
                if table['name'] == 'notes':
                    self.note_table = table

    def count(self):
        if not self.note_table or not self.note_table.row:
            return 0
        return len(self.note_table.row)

    def notes(self, password):
        if not self.note_table or not self.note_table.row:
            return

        for note in self.note_table.row:
            entries = { col['name']: col.cdata for col in note.col }
            yield {
                'category': entries['cat_id'],
                'title': entries['title'],
                'body': aes_decrypt(entries['iv'], entries['salt'], password, entries['body']).decode('utf-8'),
                'modified': entries['last_update']
            }

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'PyAndSafe - read export files from AndSafe'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        qt_rectangle = self.frameGeometry()
        center_point = QtGui.QGuiApplication.primaryScreen().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())

        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(['Category', 'Last Modified', 'Title', 'Content'])
        self.tableWidget.horizontalHeader().setStretchLastSection(True)

        layout = QVBoxLayout()
        layout.addWidget(self.tableWidget)
        self.setLayout(layout)

        self.show()
        self.openFile()

    def loadContent(self, content, password):
        collections = Note(content)
        self.tableWidget.setRowCount(collections.count())

        row = 0
        progress = QProgressDialog('Loading...', None, 0, collections.count())
        progress.setWindowTitle(' ')
        progress.setModal(True)
        progress.setValue(0)
        progress.show()

        self.tableWidget.setSortingEnabled(False)
        for note in collections.notes(password):
            self.tableWidget.setItem(row, 0, QTableWidgetItem(note['category']))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(note['modified']))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(note['title']))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(note['body']))
            row += 1
            progress.setValue(row)
        self.tableWidget.setSortingEnabled(True)
        self.tableWidget.resizeRowsToContents()

    def parseAndDisplay(self, content, password):
        signature = Signature(content)
        if not signature.validate(password):
            self._errMsg("Incorrect password")
            self.openFile()
        else:
            self.loadContent(content, password)

    def openFile(self):
        while True:
            try:
                file_name = self._selectFile()
                if file_name:
                    content = untangle.parse(file_name)
                    password = self._promptPassword()
                    if password:
                        self.parseAndDisplay(content, password)
                        break;
                else:
                    break;
            except Exception:
                self._errMsg("Problem opening file")

    def _msg(self, title, message):
        QMessageBox.information(self, title, message, QMessageBox.StandardButton.Ok)

    def _errMsg(self, message):
        self._msg('Error', message)

    def _selectFile(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Select AndSafe export file', '', 'XML Files (*.xml);;All Files (*)', options=QFileDialog.Option.DontUseNativeDialog)
        return file_name

    def _promptPassword(self):
        text, _ = QInputDialog.getText(self, 'Password', 'Password to decrypt the file:', QLineEdit.EchoMode.Password, '')
        return text


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec())
