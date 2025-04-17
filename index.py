import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsRectItem,
    QGraphicsEllipseItem,
    QGraphicsTextItem,
    QToolBar,
    QAction,
    QGraphicsItemGroup,
)
from PyQt5.QtGui import QPen, QBrush, QFont
from PyQt5.QtCore import Qt


class DiagramScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mode = "select"

    def setMode(self, mode):
        self.mode = mode

    def mousePressEvent(self, event):
        pos = event.scenePos()
        if self.mode in ["rectangle", "ellipse"]:
            # Create shape
            if self.mode == "rectangle":
                shape = QGraphicsRectItem(0, 0, 100, 50)
                shape.setBrush(QBrush(Qt.yellow))
                label_text = "Rectangle"
            else:
                shape = QGraphicsEllipseItem(0, 0, 100, 100)
                shape.setBrush(QBrush(Qt.green))
                label_text = "Ellipse"

            shape.setPen(QPen(Qt.black))

            # Create label
            label = QGraphicsTextItem(label_text)
            label.setFont(QFont("Arial", 12))
            label.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
            label.setPos(10, 10)  # relative to shape

            # Group shape and label
            group = QGraphicsItemGroup()
            group.addToGroup(shape)
            group.addToGroup(label)
            group.setPos(pos)

            # Make group selectable & movable
            group.setFlags(
                QGraphicsItemGroup.GraphicsItemFlag.ItemIsSelectable
                | QGraphicsItemGroup.GraphicsItemFlag.ItemIsMovable
            )

            self.addItem(group)
        else:
            super().mousePressEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drawing Tool - Step 4: Labels")
        self.setGeometry(100, 100, 800, 600)

        self.scene = DiagramScene()
        self.scene.setSceneRect(0, 0, 800, 600)

        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)

        self._createToolbar()

    def _createToolbar(self):
        toolbar = QToolBar("Toolbar")
        self.addToolBar(toolbar)

        rect_action = QAction("Rectangle", self)
        rect_action.triggered.connect(lambda: self.scene.setMode("rectangle"))
        toolbar.addAction(rect_action)

        ellipse_action = QAction("Ellipse", self)
        ellipse_action.triggered.connect(lambda: self.scene.setMode("ellipse"))
        toolbar.addAction(ellipse_action)

        select_action = QAction("Select", self)
        select_action.triggered.connect(lambda: self.scene.setMode("select"))
        toolbar.addAction(select_action)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
