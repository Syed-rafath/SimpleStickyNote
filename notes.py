import sys

from database import Note, session 
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMenu,
    QPushButton,
    QSystemTrayIcon,
    QTextEdit, 
    QVBoxLayout, 
    QWidget
)

#sys.argv is needed for os communication
app = QApplication(sys.argv)


active_notewindows = {}

class NoteWindow(QWidget):
    def __init__(self, note = None):
        super().__init__()
        self.setWindowFlags(
            self.windowFlags()
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self .setStyleSheet(
            "background: #FFFF99; color: #62622f; border: 0; font-size: 16pt;"
        )
        layout = QVBoxLayout()
        #layout.setSpacing(0)
        
        buttons = QHBoxLayout()
        self.close_btn = QPushButton("x")
        self.close_btn.setStyleSheet(
            "font-weight: bold; font-size: 25px; width: 25px; height: 25px;"
        )
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.clicked.connect(self.delete)
        buttons.addStretch() # Add Stretch one leflt to push button right
        buttons.addWidget(self.close_btn)
        layout.addLayout(buttons)

        self.text = QTextEdit()
        layout.addWidget(self.text)
        self.setLayout(layout)

        self.text.textChanged.connect(self.save)

        active_notewindows[id(self)] = self

        if note is None:
            self.note = Note()
            self.save()
        else:
            self.note = note
            self.load()

    #mousePressEven , mouseMoveEvent, globalPosition() are predifined we are overriding     
    def mousePressEvent(self, e):
        self.previous_pos = e.globalPosition()

    def mouseMoveEvent(self, e):
        delta = e.globalPosition() - self.previous_pos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.previous_pos = e.globalPosition()        

    def mouseReleaseEvent(self, event):
        self.save()


    def load(self):
        self.move(self.note.x, self.note.y)
        self.text.setText(self.note.text)

    def save(self):
        self.note.x = self.x()
        self.note.y = self.y()
        self.note.text = self.text.toPlainText()
        #write the data to the database, adding the Note object to the 
        #current session and commiting changes
        session.add(self.note)
        session.commit()        

    def delete(self):
        session.delete(self.note)
        session.commit()
        del active_notewindows[id(self)]
        self.close() #removing the window

def create_notewindow(note=None):
# note = NoteWindow()
# note.show() #draws the window
    note = NoteWindow(note)
    note.show()

existing_notes = session.query(Note).all()

if existing_notes:
    for note in existing_notes:
        create_notewindow(note)
else:
    create_notewindow()


#create system tray icon 
icon = QIcon("sticky-note.png")

#create the tray 
tray = QSystemTrayIcon()
tray.setIcon(icon)
tray.setVisible(True)

def handle_tray_click(reason):
    if(
        QSystemTrayIcon.ActivationReason(reason)
        == QSystemTrayIcon.ActivationReason.Trigger
    ):
        create_notewindow()

tray.activated.connect(handle_tray_click)

#Don't automatically close app when the last window is closed
app.setQuitOnLastWindowClosed(False)

#create the menu 
menu = QMenu()
add_note_action = QAction("Add Note")
add_note_action.triggered.connect(create_notewindow)
menu.addAction(add_note_action)

#addign a quit option to the menu
quit_action = QAction("Quit")
quit_action.triggered.connect(app.quit)
menu.addAction(quit_action)

#adding the menu to the tray 
tray.setContextMenu(menu)

app.exec()  #runs the app (process in taskmanager)
