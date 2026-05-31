import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow,
    QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QLabel
)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QPoint


class MainWindow(QMainWindow):
    # window constructor
    def __init__(self):
        super().__init__()

        # init
        self.setWindowIcon(QIcon("icon.png"))
        self.setWindowTitle("Sigma")
        self.setGeometry(0, 0, 700, 500)

        # size needed for 'aero snap' feature
        self.oldSize = self.size()

            # hide default title bar and window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

            # position window on screen center
        qtRectangle = self.frameGeometry()
        centerPoint = QApplication.primaryScreen().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

            # drag variables
        self.dragging = False
        self.dragPosition = QPoint()

            # resize variables
        self.BORDER = 8
        self.resizing = False
        self.resizeDir = None
        self.setMouseTracking(True)

            # ui elements

                # custom title bar elements

                    # title bar
        
        self.titleBar = QWidget()
        self.titleBar.setObjectName("titleBar")
        self.titleBar.setFixedHeight(33)

                    # drag with title bar logic
        self.titleBar.mousePressEvent = self.titleMousePressEvent
        self.titleBar.mouseMoveEvent = self.titleMouseMoveEvent
        self.titleBar.mouseReleaseEvent = self.titleMouseReleaseEvent

        self.titleBar.enterEvent = lambda e: self.unsetCursor()

                    # icon
        self.sigmaIcon = QLabel(self)
        self.sigmaIcon.setPixmap(QPixmap("icon.png").scaled(27,27,transformMode=Qt.TransformationMode.SmoothTransformation))
        self.sigmaIcon.setObjectName("icon")
        self.sigmaIcon.setFixedSize(30, 30)

                    # minimize button
        self.minimizeButton = QPushButton("—")
        self.minimizeButton.setObjectName("minimizeButton")
        self.minimizeButton.clicked.connect(self.showMinimized)
        self.minimizeButton.setFixedSize(31, 31)

                    # maximize button
        self.maximizeButton = QPushButton("🗖")
        self.maximizeButton.setObjectName("maximizeButton")
        self.maximizeButton.clicked.connect(self.toggle_maximize)
        self.maximizeButton.setFixedSize(31, 31)

                    # close button
        self.closeButton = QPushButton("✕")
        self.closeButton.setObjectName("closeButton")
        self.closeButton.clicked.connect(self.close)
        self.closeButton.setFixedSize(31, 31)

                #buttons
        self.button1 = QPushButton("1")
        self.button2 = QPushButton("2")
        self.button3 = QPushButton("3")
        
        self.buildUI()

    # UI assembler
    def buildUI(self):
        # set css
        with open("style.css", "r") as file:
            self.setStyleSheet(file.read())

        # main widget
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(2, 2, 2, 2)
        mainLayout.setSpacing(0)

        central_widget = QWidget()
        central_widget.setObjectName("mainWindow")
        self.setCentralWidget(central_widget)
        central_widget.setMouseTracking(True)

        central_widget.setLayout(mainLayout)

        # build title bar
        titleLayout = QHBoxLayout()
        titleLayout.setContentsMargins(2, 0, 0, 2)

        titleLayout.addWidget(self.sigmaIcon)
        titleLayout.addStretch()
        titleLayout.addWidget(self.minimizeButton)
        titleLayout.addWidget(self.maximizeButton)
        titleLayout.addWidget(self.closeButton)

        self.titleBar.setLayout(titleLayout)

        # build content
        contentLayout = QHBoxLayout()

        contentLayout.addWidget(self.button1)
        contentLayout.addWidget(self.button2)
        contentLayout.addWidget(self.button3)

        contentWidget = QWidget()
        contentWidget.setObjectName("content")
        contentWidget.setLayout(contentLayout)
        contentWidget.setMouseTracking(True)

        # assemble UI
        mainLayout.addWidget(self.titleBar)
        mainLayout.addWidget(contentWidget)

    # maximize / unmaximize logic
    def toggle_maximize(self):
        if self.isMaximized():
            self.maximizeButton.setText("🗖")
            self.showNormal()

            self.centralWidget().setObjectName("mainWindow")
            with open("style.css", "r") as file:
                self.setStyleSheet(file.read())
        else:
            self.maximizeButton.setText("◱")
            self.showMaximized()

            self.centralWidget().setObjectName("mainWindowMax")
            with open("style.css", "r") as file:
                self.setStyleSheet(file.read())

    # drag with title bar logic
    def titleMousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.dragPosition = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            
    def titleMouseMoveEvent(self, event):
        if self.dragging and event.buttons() == Qt.MouseButton.LeftButton:
            # window resize after maximizing
            if self.isMaximized():
                self.toggle_maximize()
                self.dragPosition = QPoint(self.width() // 2, 15)
            elif self.height() == QApplication.primaryScreen().availableGeometry().height():
                self.dragPosition = QPoint(self.width() // 2, 15)
                self.resize(self.oldSize.width(), self.oldSize.height())

            self.move(event.globalPosition().toPoint() - self.dragPosition)
            event.accept()

        # 'aero snap' feature
    def titleMouseReleaseEvent(self, event):
        desktop = QApplication.primaryScreen().availableGeometry()
        desktopWitdh = desktop.width()
        desktopHeight = desktop.height()
        desktopHalfWidth = desktopWitdh // 2
        position = event.globalPosition().toPoint()

        if position.y() <= 5:
            self.toggle_maximize()
        elif position.x() <= 5:
            self.setGeometry(0, 0, desktopHalfWidth, desktopHeight)
        elif position.x() >= desktopWitdh - 5:
            self.setGeometry(desktopHalfWidth, 0, desktopHalfWidth, desktopHeight)
            
        self.dragging = False

    # resize logic 🥀
    def getResizeDirection(self, pos):
        rect = self.rect()
        x, y = pos.x(), pos.y()

        left = x <= self.BORDER
        right = x >= rect.width() - self.BORDER
        top = y <= self.BORDER
        bottom = y >= rect.height() - self.BORDER

        if top and left:
            return "top_left"
        if top and right:
            return "top_right"
        if bottom and left:
            return "bottom_left"
        if bottom and right:
            return "bottom_right"
        if left:
            return "left"
        if right:
            return "right"
        if top:
            return "top"
        if bottom:
            return "bottom"

        return None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.resizeDir = self.getResizeDirection(event.position().toPoint())

            if self.resizeDir:
                self.resizing = True
                self.startGeometry = self.geometry()
                self.startPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.isMaximized():
            return

        if not self.resizing:
            pos = self.mapFromGlobal(event.globalPosition().toPoint())
            direction = self.getResizeDirection(pos)

            if direction in ("left", "right"):
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            elif direction in ("top", "bottom"):
                self.setCursor(Qt.CursorShape.SizeVerCursor)
            elif direction in ("top_left", "bottom_right"):
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            elif direction in ("top_right", "bottom_left"):
                self.setCursor(Qt.CursorShape.SizeBDiagCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
        else:
            self.performResize(event.globalPosition().toPoint())

    def mouseReleaseEvent(self, event):
        self.oldSize = self.size()
        self.resizing = False

    def performResize(self, globalPos):
        diff = globalPos - self.startPos
        geom = self.startGeometry

        x, y, w, h = geom.x(), geom.y(), geom.width(), geom.height()

        if "right" in self.resizeDir:
            w += diff.x()
        if "bottom" in self.resizeDir:
            h += diff.y()
        if "left" in self.resizeDir:
            x += diff.x()
            w -= diff.x()
        if "top" in self.resizeDir:
            y += diff.y()
            h -= diff.y()

        minW, minH = 300, 200

        if w >= minW and h >= minH:
            self.setGeometry(x, y, w, h)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()