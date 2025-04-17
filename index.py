import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsRectItem,
    QGraphicsEllipseItem,
    QToolBar,
    QAction,
)
from PyQt5.QtGui import QPen, QBrush
from PyQt5.QtCore import Qt


class DiagramScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mode = "select"  # Modes: 'rectangle', 'ellipse', 'select'

    def setMode(self, mode):
        self.mode = mode

    def mousePressEvent(self, event):
        pos = event.scenePos()
        if self.mode == "rectangle":
            rect = QGraphicsRectItem(0, 0, 100, 50)
            rect.setPos(pos)
            rect.setPen(QPen(Qt.black))
            rect.setBrush(QBrush(Qt.yellow))
            rect.setFlags(
                QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable
                | QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable
            )
            self.addItem(rect)
        elif self.mode == "ellipse":
            ellipse = QGraphicsEllipseItem(0, 0, 100, 100)
            ellipse.setPos(pos)
            ellipse.setPen(QPen(Qt.black))
            ellipse.setBrush(QBrush(Qt.green))
            ellipse.setFlags(
                QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable
                | QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable
            )
            self.addItem(ellipse)
        else:
            # Let QGraphicsScene handle item selection/movement
            super().mousePressEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drawing Tool - Step 3")
        self.setGeometry(100, 100, 800, 600)

        # Create scene and view
        self.scene = DiagramScene()
        self.scene.setSceneRect(0, 0, 800, 600)

        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)

        # Create toolbar
        self._createToolbar()

    def _createToolbar(self):
        toolbar = QToolBar("Toolbar")
        self.addToolBar(toolbar)

        # Rectangle tool
        rect_action = QAction("Rectangle", self)
        rect_action.triggered.connect(lambda: self.scene.setMode("rectangle"))
        toolbar.addAction(rect_action)

        # Ellipse tool
        ellipse_action = QAction("Ellipse", self)
        ellipse_action.triggered.connect(lambda: self.scene.setMode("ellipse"))
        toolbar.addAction(ellipse_action)

        # Select tool
        select_action = QAction("Select", self)
        select_action.triggered.connect(lambda: self.scene.setMode("select"))
        toolbar.addAction(select_action)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
