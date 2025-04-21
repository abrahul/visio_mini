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
from PyQt5.QtGui import QPen, QBrush, QFont, QColor, QPainter
from PyQt5.QtCore import Qt, QPointF, QRectF


GRID_SIZE = 20  # Grid spacing in pixels


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

        # Keep track of the label's current editing status
        self.is_editing = False

    def boundingRect(self):
        return self.shape.boundingRect().united(
            self.label.boundingRect().translated(self.label.pos())
        )

    def paint(self, painter, option, widget):
        pass  # Children handle drawing

    def focusInEvent(self, event):
        """Focus event to start editing the label when selected."""
        if (
            self.label.textInteractionFlags()
            != Qt.TextInteractionFlag.TextEditorInteraction
        ):
            self.label.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextEditorInteraction
            )
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        """Update label when focus is lost."""
        if self.label.toPlainText() != self.label_text:
            self.label_text = self.label.toPlainText()
        super().focusOutEvent(event)


class DiagramScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mode = "select"

    def setMode(self, mode):
        self.mode = mode

    def drawBackground(self, painter: QPainter, rect: QRectF):
        # Draw grid lines
        left = int(rect.left()) - (int(rect.left()) % GRID_SIZE)
        top = int(rect.top()) - (int(rect.top()) % GRID_SIZE)

        lines = []
        for x in range(left, int(rect.right()), GRID_SIZE):
            lines.append((x, rect.top(), x, rect.bottom()))
        for y in range(top, int(rect.bottom()), GRID_SIZE):
            lines.append((rect.left(), y, rect.right(), y))

        pen = QPen(QColor(200, 200, 200), 1)
        painter.setPen(pen)
        for x1, y1, x2, y2 in lines:
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

    def snapToGrid(self, point: QPointF):
        x = round(point.x() / GRID_SIZE) * GRID_SIZE
        y = round(point.y() / GRID_SIZE) * GRID_SIZE
        return QPointF(x, y)

    def mousePressEvent(self, event):
        pos = event.scenePos()
        snapped_pos = self.snapToGrid(pos)

        if self.mode in ["rectangle", "ellipse"]:
            item = ShapeWithLabel(shape_type=self.mode)
            item.setPos(snapped_pos)
            self.addItem(item)
        else:
            super().mousePressEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drawing Tool - Grid + Snap")
        self.setGeometry(100, 100, 800, 600)

        self.scene = DiagramScene()
        self.scene.setSceneRect(0, 0, 800, 600)

        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)

        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setViewportUpdateMode(
            QGraphicsView.ViewportUpdateMode.FullViewportUpdate
        )

        # Enable mouse tracking for hover events
        self.view.setMouseTracking(True)
        self.scene.setSceneRect(0, 0, 2000, 2000)

        # Zoom factor
        self.zoom_level = 1.0
        self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        self._createToolbar()

    def wheelEvent(self, event):
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        self.zoom_level *= zoom_factor
        self.view.scale(zoom_factor, zoom_factor)

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
