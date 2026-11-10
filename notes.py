import sys
from PySide6.QtWidgets import QApplication, QTextEdit, QVBoxLayout, QWidget


#sys.argv is needed for os communication
app = QApplication(sys.argv)


class NoteWindow(QWidget):
    def __init__(self):
        super().__init__()
        self .setStyleSheet(
            "background: #FFFF99; color: #62622f; border: 0; font-size: 16pt;"
        )
        layout = QVBoxLayout()
        self.text = QTextEdit()
        layout.addWidget(self.text)
        self.setLayout(layout)


note = NoteWindow()
note.show() #draws the window
app.exec()  #runs the app (process in taskmanager)
