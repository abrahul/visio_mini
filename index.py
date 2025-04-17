import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drawing Tool - Step 1")
        self.setGeometry(100, 100, 800, 600)

        # Create a scene and a view
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 800, 600)

        self.view = QGraphicsView(self.scene, self)
        self.setCentralWidget(self.view)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
