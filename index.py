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
    QGraphicsItem,
)
from PyQt5.QtGui import QPen, QBrush, QFont
from PyQt5.QtCore import Qt, QPointF


class ShapeWithLabel(QGraphicsItem):
    def __init__(self, shape_type="rectangle", parent=None):
        super().__init__(parent)

        # Create shape
        if shape_type == "rectangle":
            self.shape = QGraphicsRectItem(0, 0, 100, 50, self)
            self.shape.setBrush(QBrush(Qt.yellow))
            self.label_text = "Rectangle"
        elif shape_type == "ellipse":
            self.shape = QGraphicsEllipseItem(0, 0, 100, 100, self)
            self.shape.setBrush(QBrush(Qt.green))
            self.label_text = "Ellipse"

        self.shape.setPen(QPen(Qt.black))

        # Create label
        self.label = QGraphicsTextItem(self.label_text, self)
        self.label.setFont(QFont("Arial", 12))
        self.label.setPos(10, 10)
        self.label.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)

        # Enable movement and selection for the whole item
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )

    def boundingRect(self):
        # Union of shape and label bounding rects
        return self.shape.boundingRect().united(
            self.label.boundingRect().translated(self.label.pos())
        )

    def paint(self, painter, option, widget):
        pass  # Everything is drawn by child items


class DiagramScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mode = "select"

    def setMode(self, mode):
        self.mode = mode

    def mousePressEvent(self, event):
        pos = event.scenePos()
        if self.mode in ["rectangle", "ellipse"]:
            item = ShapeWithLabel(shape_type=self.mode)
            item.setPos(pos)
            self.addItem(item)
        else:
            super().mousePressEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drawing Tool - Editable Labels")
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
