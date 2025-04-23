import sys
import math
import uuid

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
from PyQt5.QtGui import QPen, QBrush, QFont, QColor, QPainter, QPolygonF
from PyQt5.QtCore import Qt, QPointF, QRectF, QLineF

GRID_SIZE = 20


class ShapeWithLabel(QGraphicsItem):
    def __init__(self, shape_type="rectangle", parent=None, shape_id=None):
        super().__init__(parent)
        self.connectors = []
        self.shape_id = shape_id or str(uuid.uuid4())

        if shape_type == "rectangle":
            self.shape = QGraphicsRectItem(0, 0, 100, 50, self)
            self.shape.setBrush(QBrush(Qt.yellow))
            self.label_text = "Rectangle"
        elif shape_type == "ellipse":
            self.shape = QGraphicsEllipseItem(0, 0, 100, 100, self)
            self.shape.setBrush(QBrush(Qt.green))
            self.label_text = "Ellipse"

        self.shape.setPen(QPen(Qt.black))

        self.label = QGraphicsTextItem(self.label_text, self)
        self.label.setFont(QFont("Arial", 12))
        self.label.setPos(10, 10)
        self.label.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )

    def boundingRect(self):
        return self.shape.boundingRect().united(
            self.label.boundingRect().translated(self.label.pos())
        )

    def paint(self, painter, option, widget):
        self.shape.paint(painter, option, widget)
        if self.isSelected():
            pen = QPen(QColor(0, 0, 255), 3, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for connector in self.connectors:
                connector.updatePosition()
        return super().itemChange(change, value)

    def removeConnector(self, connector):
        if connector in self.connectors:
            self.connectors.remove(connector)


class ConnectorLine(QGraphicsItem):
    def __init__(self, start_item, end_item, parent=None):
        super().__init__(parent)
        self.start_item = start_item
        self.end_item = end_item
        self.pen = QPen(Qt.red, 2, Qt.PenStyle.SolidLine)

        self.setZValue(-1)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        self.start_item.connectors.append(self)
        self.end_item.connectors.append(self)

    def boundingRect(self):
        p1 = self.start_item.mapToScene(self.start_item.boundingRect().center())
        p2 = self.end_item.mapToScene(self.end_item.boundingRect().center())
        return QRectF(p1, p2).normalized().adjusted(-10, -10, 10, 10)

    def paint(self, painter, option, widget):
        start = self.start_item.mapToScene(self.start_item.boundingRect().center())
        end = self.end_item.mapToScene(self.end_item.boundingRect().center())

        line = QLineF(start, end)
        painter.setPen(self.pen)
        painter.drawLine(line)

        angle = line.angle()
        arrow_size = 10
        angle_rad = (angle - 180) * math.pi / 180.0

        p1 = end
        p2 = end + QPointF(
            arrow_size * -0.5 * math.cos(angle_rad - 0.5),
            arrow_size * -0.5 * math.sin(angle_rad - 0.5),
        )
        p3 = end + QPointF(
            arrow_size * -0.5 * math.cos(angle_rad + 0.5),
            arrow_size * -0.5 * math.sin(angle_rad + 0.5),
        )

        arrow = QPolygonF([p1, p2, p3])
        painter.setBrush(Qt.red)
        painter.drawPolygon(arrow)

    def updatePosition(self):
        self.prepareGeometryChange()
        self.update()

    def removeSelf(self):
        if self.scene():
            self.scene().removeItem(self)
        if self.start_item:
            self.start_item.removeConnector(self)
        if self.end_item:
            self.end_item.removeConnector(self)


class DiagramScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mode = "select"
        self.selected_shapes = []
        self.undo_stack = []
        self.redo_stack = []

    def setMode(self, mode):
        self.mode = mode

    def drawBackground(self, painter: QPainter, rect: QRectF):
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
            self.undo_stack.append(("add", item))
            self.redo_stack.clear()

        elif self.mode == "connect":
            for item in self.items(event.scenePos()):
                if isinstance(item, ShapeWithLabel):
                    if item not in self.selected_shapes:
                        self.selected_shapes.append(item)
                    if len(self.selected_shapes) == 2:
                        start_item, end_item = self.selected_shapes
                        connector = ConnectorLine(start_item, end_item)
                        self.addItem(connector)
                        self.undo_stack.append(
                            ("connect", (start_item.shape_id, end_item.shape_id))
                        )
                        self.redo_stack.clear()
                        self.selected_shapes.clear()
                    break
        else:
            super().mousePressEvent(event)

    def deleteSelectedItem(self):
        for item in self.selectedItems():
            if isinstance(item, ConnectorLine):
                item.removeSelf()
                self.undo_stack.append(("delete_connector", item))
            elif isinstance(item, ShapeWithLabel):
                for connector in list(item.connectors):
                    connector.removeSelf()
                self.removeItem(item)
                self.undo_stack.append(("delete_shape", item))
        self.redo_stack.clear()

    def undo(self):
        if not self.undo_stack:
            return

        action = self.undo_stack.pop()
        self.redo_stack.append(action)

        if action[0] == "add":
            item = action[1]
            self.removeItem(item)

        elif action[0] == "connect":
            start_id, end_id = action[1]
            conn = self.findConnector(start_id, end_id)
            if conn:
                conn.removeSelf()

        elif action[0] == "delete_shape":
            self.addItem(action[1])

        elif action[0] == "delete_connector":
            self.addItem(action[1])

    def redo(self):
        if not self.redo_stack:
            return

        action = self.redo_stack.pop()
        self.undo_stack.append(action)

        if action[0] == "add":
            self.addItem(action[1])

        elif action[0] == "connect":
            start_id, end_id = action[1]
            start_item = self.findShapeById(start_id)
            end_item = self.findShapeById(end_id)
            if start_item and end_item:
                connector = ConnectorLine(start_item, end_item)
                self.addItem(connector)

        elif action[0] == "delete_shape":
            self.removeItem(action[1])

        elif action[0] == "delete_connector":
            action[1].removeSelf()

    def findShapeById(self, shape_id):
        for item in self.items():
            if isinstance(item, ShapeWithLabel) and item.shape_id == shape_id:
                return item
        return None

    def findConnector(self, start_id, end_id):
        for item in self.items():
            if isinstance(item, ConnectorLine):
                if (
                    item.start_item.shape_id == start_id
                    and item.end_item.shape_id == end_id
                ) or (
                    item.start_item.shape_id == end_id
                    and item.end_item.shape_id == start_id
                ):
                    return item
        return None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drawing Tool - Grid + Snap + Connectors")
        self.setGeometry(100, 100, 800, 600)

        self.scene = DiagramScene()
        self.scene.setSceneRect(0, 0, 800, 600)

        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)

        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setViewportUpdateMode(
            QGraphicsView.ViewportUpdateMode.FullViewportUpdate
        )

        self.view.setMouseTracking(True)
        self.scene.setSceneRect(0, 0, 2000, 2000)
        self.statusBar().showMessage("Mode: Select")

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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.scene.deleteSelectedItem()
        elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier:
            self.scene.undo()
        elif event.key() == Qt.Key_Y and event.modifiers() & Qt.ControlModifier:
            self.scene.redo()

    def updateStatusBar(self, text):
        self.statusBar().showMessage(f"Mode: {text}")

    def setModeAndUpdate(self, mode):
        self.scene.setMode(mode)
        self.updateStatusBar(mode.capitalize())

    def _createToolbar(self):
        toolbar = QToolBar("Toolbar")
        self.addToolBar(toolbar)

        rect_action = QAction("Rectangle", self)
        rect_action.triggered.connect(lambda: self.setModeAndUpdate("rectangle"))
        toolbar.addAction(rect_action)

        ellipse_action = QAction("Ellipse", self)
        ellipse_action.triggered.connect(lambda: self.setModeAndUpdate("ellipse"))
        toolbar.addAction(ellipse_action)

        connect_action = QAction("Connect", self)
        connect_action.triggered.connect(lambda: self.setModeAndUpdate("connect"))
        toolbar.addAction(connect_action)

        select_action = QAction("Select", self)
        select_action.triggered.connect(lambda: self.setModeAndUpdate("select"))
        toolbar.addAction(select_action)

        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.scene.deleteSelectedItem())
        toolbar.addAction(delete_action)

        undo_action = QAction("Undo", self)
        undo_action.triggered.connect(self.scene.undo)
        toolbar.addAction(undo_action)

        redo_action = QAction("Redo", self)
        redo_action.triggered.connect(self.scene.redo)
        toolbar.addAction(redo_action)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
