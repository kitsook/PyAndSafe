import sys
import untangle
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, \
    QFileDialog, QMessageBox, QVBoxLayout, QTableWidget, QTableWidgetItem, \
    QDesktopWidget, QProgressDialog

from cipher import aesDecrypt

class AndSafeExportFile:
    def __init__(self, content):
        self.content = content

    def isValid(self):
        return self.content and self.content.database and self.content.database['name'] == 'safe'

class Signature:
    def __init__(self, content):
        self.signatureObj = None

        if content.database.table:
            for table in content.database.table:
                if table['name'] == 'signature':
                    self.signatureObj = table

    def validate(self, password):
        if not self.signatureObj:
            return False

        data = self.signatureObj.row
        # convert to dict for quick access
        entries = { col['name']: col.cdata for col in data.col }
        # only support verstion 2
        if not entries['ver'] or entries['ver'] != '2':
            return False

        try:
            decrypted = aesDecrypt(entries['iv'], entries['salt'], password, entries['payload'])
            return entries['plain'] == decrypted.decode('ascii')
        except:
            return False

class Note:
    def __init__(self, content):
        self.noteTable = None

        if content.database.table:
            for table in content.database.table:
                if table['name'] == 'notes':
                    self.noteTable = table

    def count(self):
        if not self.noteTable or not self.noteTable.row:
            return 0
        return len(self.noteTable.row)

    def notes(self, password):
        if not self.noteTable or not self.noteTable.row:
            return

        for note in self.noteTable.row:
            entries = { col['name']: col.cdata for col in note.col }
            yield {
                'category': entries['cat_id'],
                'title': entries['title'],
                'body': aesDecrypt(entries['iv'], entries['salt'], password, entries['body']).decode('utf-8'),
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

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

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
        else:
            self.loadContent(content, password)

    def openFile(self):
        fileName = self._selectFile()
        if fileName:
            content = untangle.parse(fileName)
            password = self._promptPassword()
            if password:
                self.parseAndDisplay(content, password)

    def _msg(self, title, message):
        QMessageBox.information(self, title, message, QMessageBox.Ok)

    def _errMsg(self, message):
        self._msg('Error', message)

    def _selectFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, 'Select AndSafe export file', '', 'XML Files (*.xml);;All Files (*)', options=options)
        return fileName

    def _promptPassword(self):
        text, okPressed = QInputDialog.getText(self, 'Password', 'Password to decrypt the file:', QLineEdit.Password, '')
        return text


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
