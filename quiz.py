import sys
import pyautogui
import pytesseract
import cv2
import numpy as np
import pyperclip
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QFileDialog, QMessageBox, QRubberBand
from PyQt5.QtCore import Qt, QRect, QPoint, QSize
from PyQt5.QtGui import QScreen, QGuiApplication, QPixmap

# Set default Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class ScreenCaptureOCR(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.rubberBand = None
        self.origin = QPoint()
        self.fullScreenLabel = None
        self.fullScreenPixmap = None
        
    def initUI(self):
        self.setWindowTitle('Screen Capture OCR')
        self.setGeometry(100, 100, 300, 200)
        
        layout = QVBoxLayout()
        
        self.captureBtn = QPushButton('Capture Screen Region', self)
        self.captureBtn.clicked.connect(self.startCapture)
        layout.addWidget(self.captureBtn)
        
        self.statusLabel = QLabel('Ready to capture', self)
        layout.addWidget(self.statusLabel)
        
        self.setLayout(layout)
        
    def startCapture(self):
        self.hide()
        screen = QGuiApplication.primaryScreen()
        self.fullScreenPixmap = screen.grabWindow(0)
        self.fullScreenLabel = QLabel()
        self.fullScreenLabel.setPixmap(self.fullScreenPixmap)
        self.fullScreenLabel.showFullScreen()
        self.fullScreenLabel.setCursor(Qt.CrossCursor)
        self.fullScreenLabel.mousePressEvent = self.mousePressEvent
        self.fullScreenLabel.mouseMoveEvent = self.mouseMoveEvent
        self.fullScreenLabel.mouseReleaseEvent = self.mouseReleaseEvent
        
    def mousePressEvent(self, event):
        self.origin = event.pos()
        if self.rubberBand:
            self.rubberBand.deleteLater()
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self.fullScreenLabel)
        self.rubberBand.setGeometry(QRect(self.origin, QSize()))
        self.rubberBand.show()

    def mouseMoveEvent(self, event):
        if self.rubberBand:
            self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        if self.rubberBand:
            selectedRect = self.rubberBand.geometry()
            self.rubberBand.hide()
            self.rubberBand.deleteLater()
            self.rubberBand = None
            
            if self.fullScreenLabel:
                self.fullScreenLabel.hide()
                self.fullScreenLabel.deleteLater()
                self.fullScreenLabel = None
            
            self.processCapture(selectedRect)
            self.show()

    def processCapture(self, rect):
        if self.fullScreenPixmap:
            # Capture the selected region
            screenshot = self.fullScreenPixmap.copy(rect)
            
            # Convert QPixmap to numpy array
            image = screenshot.toImage()
            s = image.bits().asstring(image.width() * image.height() * 4)
            arr = np.frombuffer(s, dtype=np.uint8).reshape((image.height(), image.width(), 4))
            
            # Convert RGBA to RGB
            arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2RGB)
            
            try:
                # Perform OCR
                text = pytesseract.image_to_string(arr)
                
                # Copy text to clipboard
                pyperclip.copy(text)
                
                self.statusLabel.setText('Text copied to clipboard!')
            except Exception as e:
                self.statusLabel.setText(f'Error: {str(e)}')
        else:
            self.statusLabel.setText('Error: No screenshot available')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ScreenCaptureOCR()
    ex.show()
    sys.exit(app.exec_())
