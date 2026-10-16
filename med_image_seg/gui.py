"""PySide6 multi-polygon medical image annotation GUI."""

from __future__ import annotations

import operator
import sys
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from itertools import pairwise
from pathlib import Path

import numpy as np
from PySide6.QtCore import (
    QEvent,
    QEventLoop,
    QPoint,
    QPointF,
    QRectF,
    Qt,
    QThread,
    QTime,
    QTimer,
    Signal,
)
from PySide6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QFont,
    QFontDatabase,
    QImage,
    QKeySequence,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QPolygonF,
    QShortcut,
    QValidator,
)
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QApplication,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsPathItem,
    QGraphicsPixmapItem,
    QGraphicsPolygonItem,
    QGraphicsScene,
    QGraphicsView,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QProgressDialog,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QStyle,
    QStyleOptionSlider,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from .annotation import AnnotationExporter, AnnotationProject, PolygonAnnotation
from .io import MedicalMaskReader, MedicalVolume, MedicalVolumeReader
from .localization import UiLanguage, normalize_language, translate
from .observation import AXIS_COLORS, OBSERVATION_PLANES, ObservationPlane
from .sources import ImageCollection, ImageSource

EXTERNAL_MASK_COLOR = (255, 128, 128, 90)


@dataclass(frozen=True, slots=True)
class ExternalMaskViewState:
    mode: str
    annotation_index: int
    position: tuple[int, int, int]
    coverage: tuple[bool, ...]
    autosave_active: bool


class AnnotationIndexSpinBox(QAbstractSpinBox):
    """An unrestricted nonnegative integer selector with commit-only value changes."""

    valueChanged = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self._value = 0
        self.lineEdit().setText("0")
        self.setKeyboardTracking(False)
        self.setAccelerated(True)
        self.editingFinished.connect(self._commit_text)

    def value(self) -> int:
        return self._value

    def setValue(self, value: int) -> None:
        value = operator.index(value)
        if value < 0:
            raise ValueError("annotation index must be nonnegative")
        self.lineEdit().setText(str(value))
        if value != self._value:
            self._value = value
            self.valueChanged.emit(value)

    def validate(self, text: str, position: int):
        if not text:
            state = QValidator.State.Intermediate
        elif text.isascii() and text.isdecimal():
            state = QValidator.State.Acceptable
        else:
            state = QValidator.State.Invalid
        return state, text, position

    def fixup(self, text: str) -> str:
        return str(self._value)

    def _commit_text(self) -> None:
        text = self.lineEdit().text()
        self.setValue(int(text) if text else self._value)

    def stepBy(self, steps: int) -> None:
        text = self.lineEdit().text()
        current = int(text) if text else self._value
        self.setValue(max(0, current + steps))

    def stepEnabled(self):
        if self.isReadOnly():
            return QAbstractSpinBox.StepEnabledFlag.StepNone
        flags = QAbstractSpinBox.StepEnabledFlag.StepUpEnabled
        text = self.lineEdit().text()
        if (int(text) if text else self._value) > 0:
            flags |= QAbstractSpinBox.StepEnabledFlag.StepDownEnabled
        return flags


class MaskCoverageBar(QWidget):
    """Read-only mask coverage aligned to the native slice slider handle centers."""

    def __init__(self, slider: QSlider) -> None:
        super().__init__()
        self._slider = slider
        self._presence: tuple[bool, ...] = ()
        self.setFixedHeight(10)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        slider.installEventFilter(self)

    @property
    def presence(self) -> tuple[bool, ...]:
        return self._presence

    def set_presence(self, presence: Iterable[bool]) -> None:
        self._presence = tuple(bool(value) for value in presence)
        self.update()

    def slice_centers(self) -> tuple[int, ...]:
        option = QStyleOptionSlider()
        self._slider.initStyleOption(option)
        offset = self.mapFromGlobal(self._slider.mapToGlobal(QPoint(0, 0))).x()
        centers: list[int] = []
        for index in range(self._slider.minimum(), self._slider.maximum() + 1):
            option.sliderPosition = index
            option.sliderValue = index
            handle = self._slider.style().subControlRect(
                QStyle.ComplexControl.CC_Slider,
                option,
                QStyle.SubControl.SC_SliderHandle,
                self._slider,
            )
            centers.append(offset + handle.center().x())
        return tuple(centers)

    def eventFilter(self, watched, event) -> bool:
        if watched is self._slider and event.type() in (
            QEvent.Type.Resize,
            QEvent.Type.StyleChange,
            QEvent.Type.LayoutDirectionChange,
            QEvent.Type.Paint,
        ):
            self.update()
        return super().eventFilter(watched, event)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#c7ccd2"))
        if not self._presence:
            return
        centers = self.slice_centers()
        if len(centers) != len(self._presence):
            return
        cells = sorted(zip(centers, self._presence, strict=True))
        boundaries = [0.0]
        boundaries.extend((left[0] + right[0]) / 2 for left, right in pairwise(cells))
        boundaries.append(float(self.width()))
        for index, (_center, present) in enumerate(cells):
            if present:
                painter.fillRect(
                    QRectF(
                        boundaries[index],
                        0.0,
                        boundaries[index + 1] - boundaries[index],
                        float(self.height()),
                    ),
                    QColor("#00b878"),
                )


class SliceCanvas(QGraphicsView):
    """Zoomable axial canvas that emits completed or edited polygons."""

    polygon_finished = Signal(object, str)
    polygon_changed = Signal(int, object)
    position_clicked = Signal(QPointF)

    def __init__(self) -> None:
        super().__init__()
        self.setScene(QGraphicsScene(self))
        self.setBackgroundBrush(QColor("#111318"))
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self._interpolation_item: QGraphicsPixmapItem | None = None
        self._draft_item: QGraphicsPathItem | None = None
        self._draft_points: list[QPointF] = []
        self._polygon_items: list[QGraphicsPolygonItem] = []
        self._polygon_points: list[list[QPointF]] = []
        self._handles: list[VertexHandle] = []
        self._dragging_handle: VertexHandle | None = None
        self._operation = "add"
        self._image_rect = QRectF()
        self._first_image = True
        self._auto_fit = True
        self.read_only = False
        self._crosshair_position: QPointF | None = None
        self._crosshair_colors: tuple[str, str, str] = ("", "", "")

    def set_read_only(self, read_only: bool) -> None:
        self.read_only = read_only
        self._dragging_handle = None
        self.cancel_polygon()
        for handle in self._handles:
            handle.setCursor(
                Qt.CursorShape.ArrowCursor
                if read_only
                else Qt.CursorShape.SizeAllCursor
            )

    def set_crosshair(
        self, plane: ObservationPlane | None, position: tuple[int, int, int]
    ) -> None:
        if plane is None:
            self._crosshair_position = None
        else:
            self._crosshair_position = QPointF(
                position[plane.horizontal_axis] + 0.5,
                position[plane.vertical_axis] + 0.5,
            )
            self._crosshair_colors = (
                AXIS_COLORS[plane.horizontal_axis],
                AXIS_COLORS[plane.vertical_axis],
                plane.color,
            )
        self.viewport().update()

    def drawForeground(self, painter: QPainter, rect: QRectF) -> None:
        super().drawForeground(painter, rect)
        point = self._crosshair_position
        if point is None:
            return
        painter.save()
        painter.setClipRect(self._image_rect)
        vertical_color, horizontal_color, center_color = self._crosshair_colors
        for color, start, end in (
            (
                vertical_color,
                QPointF(point.x(), 0),
                QPointF(point.x(), self._image_rect.height()),
            ),
            (
                horizontal_color,
                QPointF(0, point.y()),
                QPointF(self._image_rect.width(), point.y()),
            ),
        ):
            pen = QPen(QColor(color), 1.0)
            pen.setCosmetic(True)
            painter.setPen(pen)
            painter.drawLine(start, end)
        pen = QPen(QColor(center_color), 2.0)
        pen.setCosmetic(True)
        painter.setPen(pen)
        radius = 6.0 / max(abs(self.transform().m11()), 0.001)
        painter.drawLine(
            point + QPointF(-radius, -radius), point + QPointF(radius, radius)
        )
        painter.drawLine(
            point + QPointF(-radius, radius), point + QPointF(radius, -radius)
        )
        painter.drawEllipse(point, radius / 2, radius / 2)
        painter.restore()

    def set_operation(self, operation: str) -> None:
        self._operation = operation
        self.cancel_polygon()

    def set_slice(
        self,
        image: np.ndarray,
        polygons: list[PolygonAnnotation],
        interpolated_mask: np.ndarray | None = None,
        *,
        overlay_color: tuple[int, int, int, int] = (49, 180, 255, 72),
    ) -> None:
        self.scene().clear()
        self._interpolation_item = None
        self._draft_item = None
        self._draft_points.clear()
        self._polygon_items.clear()
        self._polygon_points.clear()
        self._handles.clear()
        self._dragging_handle = None
        grayscale = np.ascontiguousarray(image, dtype=np.uint8)
        height, width = grayscale.shape
        qimage = QImage(
            grayscale.data,
            width,
            height,
            grayscale.strides[0],
            QImage.Format.Format_Grayscale8,
        ).copy()
        image_item = self.scene().addPixmap(QPixmap.fromImage(qimage))
        image_item.setZValue(0)
        image_rect = QRectF(0, 0, width, height)
        image_size_changed = image_rect != self._image_rect
        self._image_rect = image_rect
        self.scene().setSceneRect(self._image_rect)
        if interpolated_mask is not None:
            overlay = np.zeros((height, width, 4), dtype=np.uint8)
            overlay[np.asarray(interpolated_mask, dtype=bool)] = overlay_color
            overlay_image = QImage(
                overlay.data,
                width,
                height,
                overlay.strides[0],
                QImage.Format.Format_RGBA8888,
            ).copy()
            self._interpolation_item = self.scene().addPixmap(
                QPixmap.fromImage(overlay_image)
            )
            self._interpolation_item.setZValue(1)
        for polygon_index, polygon in enumerate(polygons):
            points = [QPointF(x, y) for x, y in polygon.points]
            item = QGraphicsPolygonItem(QPolygonF(points))
            if polygon.source == "prototype" and polygon.operation == "add":
                color = QColor(255, 183, 77, 230)
                fill = QColor(255, 183, 77, 48)
            elif polygon.source == "prototype":
                color = QColor(186, 104, 200, 230)
                fill = QColor(186, 104, 200, 45)
            elif polygon.operation == "add":
                color = QColor(0, 224, 135, 220)
                fill = QColor(0, 224, 135, 45)
            else:
                color = QColor(255, 92, 92, 230)
                fill = QColor(255, 92, 92, 45)
            item.setPen(QPen(color, 1.5))
            item.setBrush(QBrush(fill))
            item.setZValue(2)
            self.scene().addItem(item)
            self._polygon_items.append(item)
            self._polygon_points.append(points)
            for vertex_index, point in enumerate(points):
                handle = VertexHandle(polygon_index, vertex_index, color)
                handle.setPos(point)
                if self.read_only:
                    handle.setCursor(Qt.CursorShape.ArrowCursor)
                self.scene().addItem(handle)
                self._handles.append(handle)
        if self._first_image or image_size_changed:
            self.fitInView(self._image_rect, Qt.AspectRatioMode.KeepAspectRatio)
            self._first_image = False
            self._auto_fit = True

    def _update_draft(self) -> None:
        if self._draft_item is not None:
            self.scene().removeItem(self._draft_item)
        if not self._draft_points:
            self._draft_item = None
            return
        path = QPainterPath(self._draft_points[0])
        for point in self._draft_points[1:]:
            path.lineTo(point)
        self._draft_item = self.scene().addPath(
            path,
            QPen(QColor("#ffd166"), 2.0),
        )
        self._draft_item.setZValue(3)

    def finish_polygon(self) -> None:
        if self.read_only or not self.isEnabled() or len(self._draft_points) < 3:
            return
        points = [(point.x(), point.y()) for point in self._draft_points]
        self._draft_points.clear()
        self._update_draft()
        self.polygon_finished.emit(points, self._operation)

    def cancel_polygon(self) -> None:
        self._draft_points.clear()
        self._update_draft()

    def mousePressEvent(self, event) -> None:
        if self.read_only:
            if event.button() == Qt.MouseButton.LeftButton:
                point = self.mapToScene(event.position().toPoint())
                if self._image_rect.contains(point):
                    self.position_clicked.emit(point)
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton:
            if not self._draft_points:
                item = self.itemAt(event.position().toPoint())
                if isinstance(item, VertexHandle):
                    self._dragging_handle = item
                    event.accept()
                    return
            point = self.mapToScene(event.position().toPoint())
            if self._image_rect.contains(point):
                self._draft_points.append(point)
                self._update_draft()
                event.accept()
                return
        if event.button() == Qt.MouseButton.RightButton:
            self.finish_polygon()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._dragging_handle is not None:
            point = self.mapToScene(event.position().toPoint())
            point = QPointF(
                float(
                    np.clip(
                        point.x(), self._image_rect.left(), self._image_rect.right()
                    )
                ),
                float(
                    np.clip(
                        point.y(), self._image_rect.top(), self._image_rect.bottom()
                    )
                ),
            )
            handle = self._dragging_handle
            points = self._polygon_points[handle.polygon_index]
            points[handle.vertex_index] = point
            handle.setPos(point)
            self._polygon_items[handle.polygon_index].setPolygon(QPolygonF(points))
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if (
            event.button() == Qt.MouseButton.LeftButton
            and self._dragging_handle is not None
        ):
            handle = self._dragging_handle
            polygon_index = handle.polygon_index
            points = [
                (point.x(), point.y()) for point in self._polygon_points[polygon_index]
            ]
            self._dragging_handle = None
            self.polygon_changed.emit(polygon_index, points)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:
        if self.read_only:
            self.mousePressEvent(event)
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self.finish_polygon()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event) -> None:
        self._auto_fit = False
        factor = 1.2 if event.angleDelta().y() > 0 else 1 / 1.2
        self.scale(factor, factor)
        event.accept()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self._auto_fit and not self._image_rect.isEmpty():
            self.fitInView(self._image_rect, Qt.AspectRatioMode.KeepAspectRatio)


class VertexHandle(QGraphicsEllipseItem):
    def __init__(self, polygon_index: int, vertex_index: int, color: QColor) -> None:
        super().__init__(-4.5, -4.5, 9.0, 9.0)
        self.polygon_index = polygon_index
        self.vertex_index = vertex_index
        self.setPen(QPen(QColor("#ffffff"), 1.0))
        self.setBrush(QBrush(color))
        self.setZValue(4)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, True)
        self.setCursor(Qt.CursorShape.SizeAllCursor)


class OrthogonalSliceWindow(QWidget):
    """A nonmodal companion view whose lifetime is controlled by the main window."""

    def __init__(self, parent: QWidget, plane: ObservationPlane) -> None:
        super().__init__(
            parent,
            Qt.WindowType.Window
            | Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.WindowMinMaxButtonsHint,
        )
        self.plane = plane
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.resize(560, 540)
        layout = QVBoxLayout(self)
        self.axes_label = QLabel()
        layout.addWidget(self.axes_label)
        self.canvas = SliceCanvas()
        self.canvas.set_read_only(True)
        layout.addWidget(self.canvas, 1)
        navigation = QHBoxLayout()
        self.slice_label = QLabel()
        navigation.addWidget(self.slice_label)
        self.slice_spin = QSpinBox()
        navigation.addWidget(self.slice_spin)
        layout.addLayout(navigation)

    def closeEvent(self, event) -> None:
        event.ignore()


class VolumeLoadThread(QThread):
    """Load and resample a volume without blocking the Qt event loop."""

    loaded = Signal(object)
    failed = Signal(str)

    def __init__(self, source: ImageSource, spacing_mm: float) -> None:
        super().__init__()
        self.source = source
        self.spacing_mm = spacing_mm

    def run(self) -> None:
        try:
            volume = MedicalVolumeReader(self.spacing_mm).read(self.source.path)
        except Exception as exc:
            self.failed.emit(f"{type(exc).__name__}: {exc}")
            return
        self.loaded.emit(volume)


class ExternalMaskLoadThread(QThread):
    """Read, align, and measure external mask coverage off the GUI thread."""

    loaded = Signal(object, object)
    failed = Signal(str)

    def __init__(self, path: Path, reference: MedicalVolume, parent: QWidget) -> None:
        super().__init__(parent)
        self.path = path
        self.reference = reference

    def run(self) -> None:
        try:
            mask = MedicalMaskReader().read(self.path, self.reference)
            presence = mask.any(axis=(0, 1))
        except Exception as exc:
            self.failed.emit(f"{type(exc).__name__}: {exc}")
            return
        self.loaded.emit(mask, presence)


class AnnotationMainWindow(QMainWindow):
    """Interactive annotation window with colocated realtime persistence."""

    def __init__(
        self,
        *,
        sources: list[ImageSource] | None = None,
        spacing_mm: float = 0.8,
        language: UiLanguage = "en",
    ) -> None:
        super().__init__()
        if sys.platform == "win32":
            QFontDatabase.addApplicationFont("C:/Windows/Fonts/msyh.ttc")
            QApplication.instance().setFont(QFont("Microsoft YaHei UI", 9))
        self.language = normalize_language(language)
        self.resize(1500, 920)
        self.sources = ImageCollection(sources or [])
        self.current_source: ImageSource | None = None
        self.volume: MedicalVolume | None = None
        self.project: AnnotationProject | None = None
        self.project_path: Path | None = None
        self.annotation_index = 0
        self._switching_annotation = False
        self.current_slice = 0
        self.load_thread: VolumeLoadThread | None = None
        self._loading_source: ImageSource | None = None
        self.loading_dialog: QProgressDialog | None = None
        self._load_error: str | None = None
        self._dirty = False
        self._closing_polygon = False
        self._mask_coverage_dirty = True
        self.read_only = False
        self.observation_position = (0, 0, 0)
        self._observation_mask: np.ndarray | None = None
        self.observation_windows: dict[str, OrthogonalSliceWindow] = {}
        self._editing_interpolation_visible = True
        self.external_mask: np.ndarray | None = None
        self.external_mask_path: Path | None = None
        self.external_mask_thread: ExternalMaskLoadThread | None = None
        self.external_loading_dialog: QProgressDialog | None = None
        self._external_view_state: ExternalMaskViewState | None = None
        self._external_mask_error: str | None = None
        self._external_loading_widget_states: list[tuple[QWidget, bool]] = []
        self._external_loading_shortcut_states: list[tuple[QShortcut, bool]] = []
        self._build_ui(spacing_mm)
        self._bind_shortcuts()
        self._refresh_source_list()
        self.autosave_timer = QTimer(self)
        self.autosave_timer.setInterval(10_000)
        self.autosave_timer.timeout.connect(self.autosave_if_needed)
        self.autosave_timer.start()
        if len(self.sources):
            QTimer.singleShot(0, self.load_first_source)

    def _build_ui(self, spacing_mm: float) -> None:
        self.annotation_toolbar = QToolBar()
        self.annotation_toolbar.setMovable(False)
        self.addToolBar(self.annotation_toolbar)
        self.export_action = QAction(self)
        self.export_action.setEnabled(False)
        self.export_action.triggered.connect(self.export_mask)
        self.annotation_toolbar.addAction(self.export_action)
        self.export_ubd_action = QAction(self)
        self.export_ubd_action.setEnabled(False)
        self.export_ubd_action.triggered.connect(self.export_ubd_mask)
        self.annotation_toolbar.addAction(self.export_ubd_action)
        self.export_json_action = QAction(self)
        self.export_json_action.setEnabled(False)
        self.export_json_action.triggered.connect(self.export_annotations)
        self.annotation_toolbar.addAction(self.export_json_action)

        root_widget = QWidget()
        root_layout = QVBoxLayout(root_widget)
        import_row = QHBoxLayout()
        self.image_collection_label = QLabel()
        import_row.addWidget(self.image_collection_label)
        self.file_button = QPushButton()
        self.file_button.clicked.connect(self.choose_image_files)
        self.dicom_button = QPushButton()
        self.dicom_button.clicked.connect(self.choose_dicom_directory)
        import_row.addWidget(self.file_button)
        import_row.addWidget(self.dicom_button)
        import_row.addStretch(1)
        self.language_label = QLabel()
        self.language_combo = QComboBox()
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("中文", "zh")
        self.language_combo.setCurrentIndex(self.language_combo.findData(self.language))
        self.language_combo.currentIndexChanged.connect(self._language_changed)
        import_row.addWidget(self.language_label)
        import_row.addWidget(self.language_combo)
        root_layout.addLayout(import_row)

        self.splitter = QSplitter()
        root_layout.addWidget(self.splitter, 1)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        self.imported_images_label = QLabel()
        left_layout.addWidget(self.imported_images_label)
        self.source_list = QListWidget()
        self.source_list.itemDoubleClicked.connect(self.load_selected_source)
        left_layout.addWidget(self.source_list, 1)
        spacing_row = QHBoxLayout()
        self.spacing_label = QLabel()
        spacing_row.addWidget(self.spacing_label)
        self.spacing_spin = QDoubleSpinBox()
        self.spacing_spin.setRange(0.2, 2.0)
        self.spacing_spin.setSingleStep(0.1)
        self.spacing_spin.setDecimals(2)
        self.spacing_spin.setValue(spacing_mm)
        self.spacing_spin.setSuffix(" mm")
        spacing_row.addWidget(self.spacing_spin)
        self.load_button = QPushButton()
        self.load_button.clicked.connect(self.load_selected_source)
        left_layout.addLayout(spacing_row)
        left_layout.addWidget(self.load_button)

        center = QWidget()
        center_layout = QVBoxLayout(center)
        self.canvas = SliceCanvas()
        self.canvas.polygon_finished.connect(self.add_polygon)
        self.canvas.polygon_changed.connect(self.update_polygon)
        self.canvas.position_clicked.connect(
            lambda point: self._observation_clicked("LP", point)
        )
        center_layout.addWidget(self.canvas, 1)
        slice_row = QGridLayout()
        slice_row.setColumnStretch(1, 1)
        slice_row.setVerticalSpacing(2)
        self.previous_button = QPushButton()
        self.previous_button.clicked.connect(lambda: self.move_slice(-1))
        self.next_button = QPushButton()
        self.next_button.clicked.connect(lambda: self.move_slice(1))
        self.previous_labeled_button = QPushButton()
        self.previous_labeled_button.clicked.connect(
            lambda: self.go_to_labeled_slice(-1)
        )
        self.next_labeled_button = QPushButton()
        self.next_labeled_button.clicked.connect(lambda: self.go_to_labeled_slice(1))
        self.slice_slider = QSlider(Qt.Orientation.Horizontal)
        self.slice_slider.valueChanged.connect(self.set_slice)
        self.mask_coverage_bar = MaskCoverageBar(self.slice_slider)
        self.slice_spin = QSpinBox()
        self.slice_spin.valueChanged.connect(self.set_slice)
        slice_row.addWidget(self.previous_button, 0, 0)
        slice_row.addWidget(self.slice_slider, 0, 1)
        slice_row.addWidget(self.slice_spin, 0, 2)
        slice_row.addWidget(self.next_button, 0, 3)
        slice_row.addWidget(self.mask_coverage_bar, 1, 1)
        slice_row.addWidget(self.previous_labeled_button, 1, 0)
        slice_row.addWidget(self.next_labeled_button, 1, 3)
        center_layout.addLayout(slice_row)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        annotation_row = QHBoxLayout()
        self.annotation_index_label = QLabel()
        self.annotation_index_spin = AnnotationIndexSpinBox()
        self.annotation_index_label.setBuddy(self.annotation_index_spin)
        self.annotation_index_spin.valueChanged.connect(self.set_annotation_index)
        annotation_row.addWidget(self.annotation_index_label)
        annotation_row.addWidget(self.annotation_index_spin, 1)
        right_layout.addLayout(annotation_row)
        self.mode_group = QGroupBox()
        mode_layout = QVBoxLayout(self.mode_group)
        self.add_radio = QRadioButton()
        self.erase_radio = QRadioButton()
        self.observe_radio = QRadioButton()
        self.add_radio.setChecked(True)
        modes = QButtonGroup(self)
        modes.addButton(self.add_radio)
        modes.addButton(self.erase_radio)
        modes.addButton(self.observe_radio)
        modes.buttonToggled.connect(
            lambda _button, checked: self.update_operation() if checked else None
        )
        mode_layout.addWidget(self.add_radio)
        mode_layout.addWidget(self.erase_radio)
        mode_layout.addWidget(self.observe_radio)
        right_layout.addWidget(self.mode_group)
        self.observation_status = QLabel()
        self.observation_status.setWordWrap(True)
        self.observation_status.hide()
        right_layout.addWidget(self.observation_status)

        self.finish_button = QPushButton()
        self.finish_button.clicked.connect(self.canvas.finish_polygon)
        self.cancel_button = QPushButton()
        self.cancel_button.clicked.connect(self.canvas.cancel_polygon)
        self.delete_button = QPushButton()
        self.delete_button.clicked.connect(self.delete_last_edited_polygon)
        self.copy_button = QPushButton()
        self.copy_button.clicked.connect(self.copy_previous_slice)
        self.clear_button = QPushButton()
        self.clear_button.clicked.connect(self.clear_current_slice)
        for button in (
            self.finish_button,
            self.cancel_button,
            self.delete_button,
            self.copy_button,
            self.clear_button,
        ):
            right_layout.addWidget(button)

        self.completed_check = QCheckBox()
        self.completed_check.toggled.connect(self.set_slice_completed)
        right_layout.addWidget(self.completed_check)
        self.force_empty_check = QCheckBox()
        self.force_empty_check.toggled.connect(self.set_force_empty)
        right_layout.addWidget(self.force_empty_check)
        self.next_incomplete_button = QPushButton()
        self.next_incomplete_button.clicked.connect(self.go_to_next_incomplete)
        right_layout.addWidget(self.next_incomplete_button)
        self.review_progress = QProgressBar()
        right_layout.addWidget(self.review_progress)
        self.show_interpolation = QCheckBox()
        self.show_interpolation.setChecked(True)
        self.show_interpolation.toggled.connect(self.refresh_slice)
        right_layout.addWidget(self.show_interpolation)
        self.interpolation_status = QLabel()
        self.interpolation_status.setWordWrap(True)
        right_layout.addWidget(self.interpolation_status)
        self.autosave_status = QLabel()
        self.autosave_status.setWordWrap(True)
        right_layout.addWidget(self.autosave_status)

        self.window_group = QGroupBox()
        window_layout = QVBoxLayout(self.window_group)
        level_row = QHBoxLayout()
        self.level_label = QLabel()
        level_row.addWidget(self.level_label)
        self.level_spin = QDoubleSpinBox()
        self.level_spin.setDecimals(1)
        self.level_spin.valueChanged.connect(self.refresh_slice)
        level_row.addWidget(self.level_spin)
        width_row = QHBoxLayout()
        self.width_label = QLabel()
        width_row.addWidget(self.width_label)
        self.width_spin = QDoubleSpinBox()
        self.width_spin.setDecimals(1)
        self.width_spin.setMinimum(1.0)
        self.width_spin.valueChanged.connect(self.refresh_slice)
        width_row.addWidget(self.width_spin)
        window_layout.addLayout(level_row)
        window_layout.addLayout(width_row)
        right_layout.addWidget(self.window_group)
        external_mask_row = QHBoxLayout()
        self.load_external_mask_button = QPushButton()
        self.load_external_mask_button.clicked.connect(self.choose_external_mask)
        self.unload_external_mask_button = QPushButton()
        self.unload_external_mask_button.setEnabled(False)
        self.unload_external_mask_button.clicked.connect(self.unload_external_mask)
        external_mask_row.addWidget(self.load_external_mask_button)
        external_mask_row.addWidget(self.unload_external_mask_button)
        right_layout.addLayout(external_mask_row)
        right_layout.addStretch(1)
        self.hint_label = QLabel()
        self.hint_label.setWordWrap(True)
        right_layout.addWidget(self.hint_label)

        self.splitter.addWidget(left)
        self.splitter.addWidget(center)
        self.splitter.addWidget(right)
        self.splitter.setSizes([310, 900, 280])
        self.setCentralWidget(root_widget)
        self.setStatusBar(QStatusBar())
        self.editing_controls = (
            self.finish_button,
            self.cancel_button,
            self.delete_button,
            self.copy_button,
            self.clear_button,
            self.completed_check,
            self.force_empty_check,
        )
        self.editor_widgets = (
            center,
            self.mode_group,
            self.annotation_index_spin,
            self.window_group,
            self.next_incomplete_button,
            self.review_progress,
            self.show_interpolation,
            *self.editing_controls,
        )
        for widget in self.editor_widgets:
            widget.setEnabled(False)
        self._retranslate_ui()

    def _text(self, key: str, **values: object) -> str:
        return translate(key, self.language, **values)

    @property
    def external_preview_active(self) -> bool:
        return self._external_view_state is not None

    def _hint_key(self) -> str:
        if self.external_preview_active:
            return "external_mask_hint"
        return "observation_hint" if self.read_only else "hint"

    def _begin_external_preview(self) -> bool:
        if (
            self.external_preview_active
            or self.load_thread is not None
            or self._closing_polygon
        ):
            return False
        if self.volume is None or self.project is None:
            QMessageBox.information(
                self,
                self._text("external_mask_title"),
                self._text("external_mask_no_image"),
            )
            return False
        self.canvas.finish_polygon()
        if not self.save_project(notify=True):
            return False
        self._external_view_state = ExternalMaskViewState(
            mode="observe" if self.read_only else self.canvas._operation,
            annotation_index=self.annotation_index,
            position=self.observation_position,
            coverage=self.mask_coverage_bar.presence,
            autosave_active=self.autosave_timer.isActive(),
        )
        self.autosave_timer.stop()
        self.mask_coverage_bar.set_presence([False] * self.volume.data.shape[2])
        self.observe_radio.setChecked(True)
        self._apply_mode_ui()
        self.refresh_slice()
        return True

    def choose_external_mask(self) -> None:
        if not self._begin_external_preview():
            return
        try:
            selected, _ = QFileDialog.getOpenFileName(
                self,
                self._text("external_mask_choose"),
                str(self.current_source.path.parent),
                self._text("external_mask_filter"),
            )
        except Exception as exc:
            self.unload_external_mask()
            QMessageBox.critical(self, self._text("external_mask_failed"), str(exc))
            return
        if not selected:
            self.unload_external_mask()
            return
        self._start_external_mask_load(Path(selected))

    def load_external_mask(self, path: str | Path) -> bool:
        """Start a non-editable external-mask preview without opening a file dialog."""

        if not self._begin_external_preview():
            return False
        self._start_external_mask_load(Path(path))
        return True

    def _start_external_mask_load(self, path: Path) -> None:
        assert self.volume is not None
        self.external_mask_path = path.expanduser().resolve()
        self._external_mask_error = None
        self._external_loading_widget_states = [
            (widget, widget.isEnabled())
            for widget in (
                self.centralWidget(),
                self.annotation_toolbar,
                *self.observation_windows.values(),
            )
        ]
        self._external_loading_shortcut_states = [
            (shortcut, shortcut.isEnabled())
            for shortcut in self.findChildren(QShortcut)
        ]
        for widget, _enabled in self._external_loading_widget_states:
            widget.setEnabled(False)
        for shortcut, _enabled in self._external_loading_shortcut_states:
            shortcut.setEnabled(False)
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        dialog = QProgressDialog(
            self._text("external_mask_loading", path=self.external_mask_path),
            "",
            0,
            0,
            self,
        )
        dialog.setWindowTitle(self._text("external_mask_title"))
        dialog.setCancelButton(None)
        dialog.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        dialog.setMinimumDuration(0)
        dialog.setAutoClose(False)
        dialog.setAutoReset(False)
        dialog.show()
        self.external_loading_dialog = dialog
        self.external_mask_thread = ExternalMaskLoadThread(
            self.external_mask_path, self.volume, self
        )
        self.external_mask_thread.loaded.connect(self.external_mask_loaded)
        self.external_mask_thread.failed.connect(self.external_mask_load_failed)
        self.external_mask_thread.finished.connect(self.external_mask_thread_finished)
        self.external_mask_thread.start()

    def external_mask_loaded(self, mask: np.ndarray, presence: np.ndarray) -> None:
        if self.volume is None or mask.shape != self.volume.data.shape:
            self._external_mask_error = self._text("external_mask_shape_error")
            return
        self.external_mask = mask
        self.mask_coverage_bar.set_presence(presence)
        self.refresh_slice()

    def external_mask_load_failed(self, message: str) -> None:
        self._external_mask_error = message

    def external_mask_thread_finished(self) -> None:
        thread = self.external_mask_thread
        self.external_mask_thread = None
        if thread is not None:
            thread.deleteLater()
        if self.external_loading_dialog is not None:
            self.external_loading_dialog.close()
            self.external_loading_dialog.deleteLater()
            self.external_loading_dialog = None
        for widget, enabled in self._external_loading_widget_states:
            widget.setEnabled(enabled)
        for shortcut, enabled in self._external_loading_shortcut_states:
            shortcut.setEnabled(enabled)
        self._external_loading_widget_states.clear()
        self._external_loading_shortcut_states.clear()
        QApplication.restoreOverrideCursor()
        if self._external_mask_error is not None:
            error = self._external_mask_error
            self.unload_external_mask()
            QMessageBox.critical(self, self._text("external_mask_failed"), error)
            return
        self._apply_mode_ui()
        self.statusBar().showMessage(
            self._text("external_mask_loaded", path=self.external_mask_path)
        )

    def unload_external_mask(self) -> bool:
        state = self._external_view_state
        if state is None or self.external_mask_thread is not None:
            return False
        with self._polygon_busy_ui("external_mask_unloading"):
            self.external_mask = None
            self.external_mask_path = None
            self._external_view_state = None
            self.annotation_index = state.annotation_index
            self._sync_annotation_index_spin()
            self.observation_position = state.position
            self.current_slice = state.position[2]
            self.mask_coverage_bar.set_presence(state.coverage)
            self._mask_coverage_dirty = False
            radio = {
                "add": self.add_radio,
                "erase": self.erase_radio,
                "observe": self.observe_radio,
            }[state.mode]
            radio.setChecked(True)
            self._apply_mode_ui()
            self.set_slice(state.position[2])
            self._show_annotation_path()
        if state.autosave_active:
            self.autosave_timer.start()
        self._apply_mode_ui()
        self.statusBar().showMessage(self._text("external_mask_unloaded"))
        return True

    def _language_changed(self, index: int) -> None:
        language = self.language_combo.itemData(index)
        if language is not None:
            self.set_language(str(language))

    def set_language(self, language: str) -> None:
        """Switch the visible interface language without restarting the GUI."""

        self.language = normalize_language(language)
        combo_index = self.language_combo.findData(self.language)
        if combo_index >= 0 and combo_index != self.language_combo.currentIndex():
            self.language_combo.blockSignals(True)
            self.language_combo.setCurrentIndex(combo_index)
            self.language_combo.blockSignals(False)
        self._retranslate_ui()

    def _retranslate_ui(self) -> None:
        self.setWindowTitle(self._text("window_title"))
        self.annotation_toolbar.setWindowTitle(self._text("toolbar_annotation"))
        self.export_action.setText(self._text("export_mask"))
        self.export_ubd_action.setText(self._text("export_ubd_mask"))
        self.export_json_action.setText(self._text("export_annotations"))
        self.mask_coverage_bar.setAccessibleName(self._text("mask_coverage_name"))
        self.mask_coverage_bar.setToolTip(self._text("mask_coverage_tooltip"))
        self.image_collection_label.setText(self._text("image_collection"))
        self.file_button.setText(self._text("import_files"))
        self.dicom_button.setText(self._text("import_dicom"))
        self.language_label.setText(self._text("language"))
        self.imported_images_label.setText(self._text("imported_images"))
        self.spacing_label.setText(self._text("annotation_grid"))
        self.load_button.setText(self._text("load_selected"))
        self.previous_button.setText(self._text("previous_slice"))
        self.next_button.setText(self._text("next_slice"))
        self.previous_labeled_button.setText(self._text("previous_labeled_slice"))
        self.next_labeled_button.setText(self._text("next_labeled_slice"))
        self.previous_labeled_button.setToolTip(self._text("labeled_slice_tooltip"))
        self.next_labeled_button.setToolTip(self._text("labeled_slice_tooltip"))
        self.mode_group.setTitle(self._text("polygon_mode"))
        self.annotation_index_label.setText(self._text("annotation_index"))
        self.annotation_index_spin.setAccessibleName(self._text("annotation_index"))
        self.annotation_index_spin.setToolTip(self._text("annotation_index_tooltip"))
        self.add_radio.setText(self._text("add_region"))
        self.erase_radio.setText(self._text("erase_region"))
        self.observe_radio.setText(self._text("observe_mode"))
        self.finish_button.setText(self._text("finish_polygon"))
        self.cancel_button.setText(self._text("cancel_polygon"))
        self.delete_button.setText(self._text("delete_last"))
        self.copy_button.setText(self._text("copy_previous"))
        self.clear_button.setText(self._text("clear_slice"))
        self.completed_check.setText(self._text("completed"))
        self.force_empty_check.setText(self._text("force_empty"))
        self.force_empty_check.setToolTip(self._text("force_empty_tooltip"))
        self.next_incomplete_button.setText(self._text("next_incomplete"))
        self.review_progress.setFormat(self._text("review_progress"))
        self.show_interpolation.setText(self._text("show_interpolation"))
        self.window_group.setTitle(self._text("window"))
        self.level_label.setText(self._text("window_level"))
        self.width_label.setText(self._text("window_width"))
        self.load_external_mask_button.setText(self._text("load_external_mask"))
        self.unload_external_mask_button.setText(self._text("unload_external_mask"))
        self.hint_label.setText(self._text(self._hint_key()))
        if self.volume is not None and self.project is not None:
            self.refresh_slice()
            if self.project_path is not None:
                self._show_annotation_path()
        else:
            self.interpolation_status.setText(self._text("slice_not_loaded"))
            self.autosave_status.setText(self._text("autosave_waiting"))
            self.statusBar().showMessage(self._text("no_images_status"))

    def _bind_shortcuts(self) -> None:
        QShortcut(
            QKeySequence(Qt.Key.Key_Left), self, activated=lambda: self.move_slice(-1)
        )
        QShortcut(
            QKeySequence(Qt.Key.Key_Right), self, activated=lambda: self.move_slice(1)
        )
        self.editing_shortcuts = [
            QShortcut(QKeySequence(sequence), self, activated=callback)
            for sequence, callback in (
                (Qt.Key.Key_Space, self.canvas.finish_polygon),
                (Qt.Key.Key_Escape, self.canvas.cancel_polygon),
                (QKeySequence.StandardKey.Undo, self.delete_last_edited_polygon),
                ("C", self.copy_previous_slice),
                ("M", self.toggle_completed),
            )
        ]
        QShortcut(QKeySequence("E"), self, activated=self.export_mask)

    def _refresh_source_list(self) -> None:
        self.source_list.clear()
        for index, source in enumerate(self.sources):
            item = QListWidgetItem(source.display_name)
            item.setData(Qt.ItemDataRole.UserRole, index)
            item.setToolTip(str(source.path))
            self.source_list.addItem(item)

    def add_sources(self, paths: list[str | Path]) -> list[ImageSource]:
        """Public GUI API for adding images without loading them synchronously."""

        added: list[ImageSource] = []
        errors: list[str] = []
        previous_count = len(self.sources)
        for path in paths:
            try:
                source = self.sources.add(path)
            except (OSError, ValueError) as exc:
                errors.append(f"{path}: {exc}")
            else:
                added.append(source)
        self._refresh_source_list()
        if len(self.sources) > previous_count:
            self.statusBar().showMessage(
                self._text("sources_added", count=len(self.sources))
            )
        if errors:
            QMessageBox.warning(
                self,
                self._text("partial_import_title"),
                "\n".join(errors),
            )
        return added

    def choose_image_files(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self,
            self._text("choose_images_title"),
            "",
            self._text("image_filter"),
        )
        if files:
            self.add_sources(files)

    def choose_dicom_directory(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            self,
            self._text("choose_dicom_title"),
        )
        if directory:
            self.add_sources([directory])

    def load_first_source(self) -> None:
        if len(self.sources) and self.load_thread is None:
            self.source_list.setCurrentRow(0)
            self.load_selected_source()

    def load_selected_source(self, _item=None) -> None:
        item = self.source_list.currentItem()
        if item is None or self.load_thread is not None or self.external_preview_active:
            return
        if not self.save_project(notify=True):
            return
        source = self.sources[int(item.data(Qt.ItemDataRole.UserRole))]
        self._loading_source = source
        self._load_error = None
        self._show_loading(source)
        self.load_thread = VolumeLoadThread(source, self.spacing_spin.value())
        self.load_thread.loaded.connect(self.volume_loaded)
        self.load_thread.failed.connect(self.volume_load_failed)
        self.load_thread.finished.connect(self.load_thread_finished)
        self.load_thread.start()

    def _show_loading(self, source: ImageSource) -> None:
        self.centralWidget().setEnabled(False)
        for view in self.observation_windows.values():
            view.setEnabled(False)
        self.export_action.setEnabled(False)
        self.export_ubd_action.setEnabled(False)
        self.export_json_action.setEnabled(False)
        dialog = QProgressDialog(
            self._text("loading_message", path=source.path),
            "",
            0,
            0,
            self,
        )
        dialog.setWindowTitle(self._text("loading_title"))
        dialog.setCancelButton(None)
        dialog.setMinimumDuration(0)
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        dialog.setAutoClose(False)
        dialog.setAutoReset(False)
        dialog.show()
        self.loading_dialog = dialog
        self.statusBar().showMessage(
            self._text("loading_status", name=source.display_name)
        )

    def _finish_loading_ui(self) -> None:
        if self.loading_dialog is not None:
            self.loading_dialog.close()
            self.loading_dialog.deleteLater()
            self.loading_dialog = None
        self.centralWidget().setEnabled(True)
        has_volume = self.volume is not None and self.project is not None
        for widget in self.editor_widgets:
            widget.setEnabled(has_volume)
        self.export_action.setEnabled(has_volume)
        self.export_ubd_action.setEnabled(has_volume)
        self.export_json_action.setEnabled(has_volume)
        for view in self.observation_windows.values():
            view.setEnabled(has_volume)
        self._apply_mode_ui()

    def load_thread_finished(self) -> None:
        self.load_thread = None
        self._finish_loading_ui()
        if self._load_error is not None:
            QMessageBox.warning(
                self,
                self._text("load_failed_title"),
                self._load_error,
            )
            self.statusBar().showMessage(self._text("load_failed_status"))
        self._loading_source = None

    def volume_load_failed(self, message: str) -> None:
        self._load_error = message

    @staticmethod
    def _open_annotation_project(
        source: ImageSource, volume: MedicalVolume, index: int
    ) -> tuple[AnnotationProject, Path]:
        path = source.annotation_path_for_index(index)
        if path.is_file() or Path(f"{path}.bak").is_file():
            project = AnnotationProject.load(path)
            project.validate_volume(volume)
            if project.source_fingerprint != source.fingerprint:
                raise ValueError("annotation fingerprint does not match this image")
        else:
            project = AnnotationProject.create(
                image_id=source.source_id,
                source_fingerprint=source.fingerprint,
                volume=volume,
            )
            if index == 0:
                project.save(path)
        if index > 0 and not project.has_polygons:
            project.save(path, delete_if_empty=True)
        return project, path

    def _sync_annotation_index_spin(self) -> None:
        was_blocked = self.annotation_index_spin.blockSignals(True)
        self.annotation_index_spin.setValue(self.annotation_index)
        self.annotation_index_spin.blockSignals(was_blocked)

    def _show_annotation_path(self) -> None:
        if self.external_preview_active:
            self.autosave_status.setText(
                self._text(
                    "external_mask_json_paused",
                    index=self.annotation_index,
                    path=self.project_path,
                )
            )
            return
        empty_numbered = (
            self.annotation_index > 0
            and self.project is not None
            and not self.project.has_polygons
        )
        self.autosave_status.setText(
            self._text(
                "annotation_empty_status" if empty_numbered else "autosave_path",
                index=self.annotation_index,
                path=self.project_path,
            )
        )

    def set_annotation_index(self, index: int) -> bool:
        """Save the active annotation and switch without reloading the image."""

        index = operator.index(index)
        if index < 0:
            raise ValueError("annotation index must be nonnegative")
        if (
            self._closing_polygon
            or self._switching_annotation
            or self.load_thread is not None
            or self.read_only
            or self.external_preview_active
        ):
            self._sync_annotation_index_spin()
            return False
        if index == self.annotation_index:
            self._sync_annotation_index_spin()
            return True
        if self.project is None or self.volume is None or self.current_source is None:
            self.annotation_index = index
            self._sync_annotation_index_spin()
            return True
        self._switching_annotation = True
        try:
            self.canvas.finish_polygon()
            if not self.save_project(notify=True, force=True):
                return False
            error = None
            with self._polygon_busy_ui("switching_annotation_status"):
                try:
                    project, path = self._open_annotation_project(
                        self.current_source, self.volume, index
                    )
                    observation_mask = (
                        project.to_mask(interpolate=True) if self.read_only else None
                    )
                except Exception as exc:
                    error = exc
                else:
                    self.canvas.cancel_polygon()
                    self.project = project
                    self.project_path = path
                    self.annotation_index = index
                    self._dirty = False
                    self._mask_coverage_dirty = True
                    self._observation_mask = observation_mask
                    self._sync_annotation_index_spin()
                    self._show_annotation_path()
                    self.refresh_slice()
            if error is not None:
                QMessageBox.critical(
                    self, self._text("annotation_switch_failed"), str(error)
                )
                return False
            self.statusBar().showMessage(
                self._text("annotation_selected", index=index, path=self.project_path)
            )
            return True
        finally:
            self._switching_annotation = False
            self._sync_annotation_index_spin()

    def volume_loaded(self, volume: MedicalVolume) -> None:
        if self.external_preview_active:
            return
        assert self._loading_source is not None
        source = self._loading_source
        try:
            project, project_path = self._open_annotation_project(
                source, volume, self.annotation_index
            )
            observation_mask = (
                project.to_mask(interpolate=True) if self.read_only else None
            )
        except Exception as exc:
            self._load_error = f"{type(exc).__name__}: {exc}"
            return
        self.current_source = source
        self.volume = volume
        self.project_path = project_path
        self.project = project
        self._dirty = False
        self._mask_coverage_dirty = True
        self._observation_mask = observation_mask
        self.observation_position = tuple(size // 2 for size in volume.data.shape)
        self.current_slice = self.observation_position[2]
        self._sync_annotation_index_spin()
        self._show_annotation_path()
        depth = volume.data.shape[2]
        self.slice_slider.setRange(0, depth - 1)
        self.slice_spin.setRange(0, depth - 1)
        self.review_progress.setRange(0, depth)
        finite = volume.data[np.isfinite(volume.data)]
        stride = max(1, finite.size // 500_000)
        low, high = np.percentile(finite[::stride], (1.0, 99.0))
        data_min, data_max = float(finite.min()), float(finite.max())
        self.level_spin.setRange(data_min, data_max)
        self.width_spin.setRange(1.0, max(1.0, 2 * (data_max - data_min)))
        self.level_spin.setValue(float((low + high) / 2))
        self.width_spin.setValue(float(max(1.0, high - low)))
        self.current_slice = depth // 2
        self.slice_slider.setValue(self.current_slice)
        self.slice_spin.setValue(self.current_slice)
        self.refresh_slice()
        modality = str(volume.metadata.get("modality", "UNKNOWN"))
        self.statusBar().showMessage(
            self._text(
                "loaded_status",
                name=self.current_source.display_name,
                shape=volume.data.shape,
                spacing=volume.spacing_mm,
                modality=modality,
            )
        )

    def update_operation(self) -> None:
        observe = self.observe_radio.isChecked()
        if self.external_preview_active and not observe:
            self.observe_radio.setChecked(True)
            return
        if observe == self.read_only:
            if not observe:
                self.canvas.set_operation(
                    "add" if self.add_radio.isChecked() else "erase"
                )
            return
        if observe:
            if self.project is None:
                self.add_radio.setChecked(True)
                return
            self.canvas.finish_polygon()
            if not self.external_preview_active:
                try:
                    with self._polygon_busy_ui("preparing_observation"):
                        self._observation_mask = self.project.to_mask(interpolate=True)
                except Exception as exc:
                    radio = (
                        self.add_radio
                        if self.canvas._operation == "add"
                        else self.erase_radio
                    )
                    radio.setChecked(True)
                    QMessageBox.critical(
                        self, self._text("observation_failed"), str(exc)
                    )
                    return
            self._editing_interpolation_visible = self.show_interpolation.isChecked()
        self.read_only = observe
        self.canvas.set_read_only(observe)
        self.show_interpolation.blockSignals(True)
        self.show_interpolation.setChecked(
            True if observe else self._editing_interpolation_visible
        )
        self.show_interpolation.blockSignals(False)
        if observe:
            self._ensure_observation_windows()
        else:
            for view in self.observation_windows.values():
                view.hide()
            self.canvas.set_crosshair(None, self.observation_position)
            self.canvas.set_operation("add" if self.add_radio.isChecked() else "erase")
            self._observation_mask = None
        self._apply_mode_ui()
        self.refresh_slice()

    def _apply_mode_ui(self) -> None:
        has_volume = self.volume is not None and self.project is not None
        external = self.external_preview_active
        for control in self.editing_controls:
            control.setEnabled(has_volume and not self.read_only)
        for shortcut in self.editing_shortcuts:
            shortcut.setEnabled(has_volume and not self.read_only)
        self.show_interpolation.setEnabled(has_volume and not self.read_only)
        self.annotation_index_spin.setEnabled(has_volume and not self.read_only)
        self.mode_group.setEnabled(has_volume and not external)
        self.next_incomplete_button.setEnabled(has_volume and not external)
        self.review_progress.setEnabled(has_volume and not external)
        self.previous_labeled_button.setEnabled(not external)
        self.next_labeled_button.setEnabled(not external)
        for widget in (
            self.file_button,
            self.dicom_button,
            self.load_button,
            self.source_list,
            self.spacing_spin,
        ):
            widget.setEnabled(not external)
        for action in self.annotation_toolbar.actions():
            action.setEnabled(has_volume and not external)
        self.load_external_mask_button.setEnabled(not external)
        self.unload_external_mask_button.setEnabled(self.external_mask is not None)
        self.observation_status.setVisible(self.read_only)
        self.hint_label.setText(self._text(self._hint_key()))

    def _ensure_observation_windows(self) -> None:
        for name in ("PS", "SL"):
            if name in self.observation_windows:
                continue
            view = OrthogonalSliceWindow(self, OBSERVATION_PLANES[name])
            view.canvas.position_clicked.connect(
                lambda point, name=name: self._observation_clicked(name, point)
            )
            view.slice_spin.valueChanged.connect(
                lambda index, name=name: self._set_observation_axis(name, index)
            )
            self.observation_windows[name] = view
            screen = self.screen().availableGeometry()
            width = min(560, screen.width() // 2)
            height = min(540, screen.height() // 2)
            view.resize(width, height)
            view.move(
                screen.right() - width, screen.top() + (0 if name == "PS" else height)
            )

    def _observation_clicked(self, name: str, point: QPointF) -> None:
        if not self.read_only or self.volume is None:
            return
        self.observation_position = OBSERVATION_PLANES[name].position_at(
            self.observation_position, point.x(), point.y(), self.volume.data.shape
        )
        self.set_slice(self.observation_position[2])

    def _set_observation_axis(self, name: str, index: int) -> None:
        if not self.read_only or self.volume is None:
            return
        axis = OBSERVATION_PLANES[name].fixed_axis
        position = list(self.observation_position)
        position[axis] = int(np.clip(index, 0, self.volume.data.shape[axis] - 1))
        self.observation_position = tuple(position)
        self.set_slice(self.observation_position[2])

    def _refresh_observation_views(self) -> None:
        assert self.volume is not None
        external = self.external_preview_active
        mask = self.external_mask if external else self._observation_mask
        if not external:
            assert mask is not None
        self.canvas.set_crosshair(OBSERVATION_PLANES["LP"], self.observation_position)
        self.observation_status.setText(
            self._text(
                "observation_position",
                **dict(zip("LPS", self.observation_position, strict=True)),
            )
        )
        for view in self.observation_windows.values():
            plane = view.plane
            index = self.observation_position[plane.fixed_axis]
            axis = "LPS"[plane.fixed_axis]
            view.canvas.set_slice(
                self._windowed_plane(
                    plane.section(self.volume.data, self.observation_position)
                ),
                [],
                None
                if mask is None
                else plane.section(mask, self.observation_position),
                overlay_color=EXTERNAL_MASK_COLOR if external else (49, 180, 255, 72),
            )
            view.canvas.set_crosshair(plane, self.observation_position)
            view.slice_spin.blockSignals(True)
            view.slice_spin.setRange(0, self.volume.data.shape[plane.fixed_axis] - 1)
            view.slice_spin.setValue(index)
            view.slice_spin.blockSignals(False)
            view.slice_label.setText(self._text("observation_slice", axis=axis))
            view.axes_label.setText(
                self._text(
                    "observation_axes",
                    horizontal="LPS"[plane.horizontal_axis],
                    vertical="LPS"[plane.vertical_axis],
                )
            )
            view.setWindowTitle(
                self._text(
                    "observation_title", plane=plane.name, axis=axis, index=index
                )
            )
            if self.isVisible():
                view.show()

    def _windowed_slice(self) -> np.ndarray:
        assert self.volume is not None
        plane = self.volume.data[:, :, self.current_slice].T
        return self._windowed_plane(plane)

    def _windowed_plane(self, plane: np.ndarray) -> np.ndarray:
        level = self.level_spin.value()
        width = self.width_spin.value()
        low = level - width / 2
        scaled = np.clip((plane - low) / width, 0.0, 1.0)
        return np.asarray(np.rint(scaled * 255), dtype=np.uint8)

    def refresh_slice(self) -> None:
        if self.volume is None or self.project is None:
            return
        if self.external_preview_active:
            self.canvas.set_slice(
                self._windowed_slice(),
                [],
                None
                if self.external_mask is None
                else self.external_mask[:, :, self.current_slice].T,
                overlay_color=EXTERNAL_MASK_COLOR,
            )
            self.interpolation_status.setText(
                self._text(
                    "external_mask_current",
                    index=self.current_slice,
                    path=self.external_mask_path or "…",
                )
            )
            self._show_annotation_path()
            self._refresh_observation_views()
            return
        if self._mask_coverage_dirty:
            self.mask_coverage_bar.set_presence(self.project.mask_presence())
            self._mask_coverage_dirty = False
        annotation = self.project.annotation(self.current_slice)
        if self.read_only:
            assert self._observation_mask is not None
            interpolated = (
                self._observation_mask[:, :, self.current_slice].T
                if self.project.interpolation_bounds(self.current_slice) is not None
                else None
            )
        else:
            interpolated = (
                self.project.interpolated_plane(self.current_slice)
                if self.show_interpolation.isChecked()
                else None
            )
        self.canvas.set_slice(
            self._windowed_slice(),
            [] if annotation.force_empty else annotation.polygons,
            interpolated_mask=interpolated,
        )
        self.completed_check.blockSignals(True)
        self.completed_check.setChecked(annotation.completed)
        self.completed_check.blockSignals(False)
        self.force_empty_check.blockSignals(True)
        self.force_empty_check.setChecked(annotation.force_empty)
        self.force_empty_check.blockSignals(False)
        self.review_progress.setValue(self.project.completed_count)
        if annotation.force_empty:
            state = self._text("state_force_empty")
        elif annotation.polygons:
            sources = {polygon.source for polygon in annotation.polygons}
            if sources == {"prototype"}:
                prefix = self._text("state_machine")
            elif sources == {"manual"}:
                prefix = self._text("state_manual")
            else:
                prefix = self._text("state_union")
            review = self._text(
                "state_reviewed" if annotation.completed else "state_unreviewed"
            )
            state = f"{prefix} ({review})"
        elif annotation.completed:
            state = self._text("state_empty_boundary")
        elif annotation.keyframe:
            state = self._text("state_empty_keyframe")
        elif interpolated is not None:
            bounds = self.project.interpolation_bounds(self.current_slice)
            state = self._text(
                "state_interpolated",
                lower=bounds[0],
                upper=bounds[1],
            )
        else:
            state = self._text("state_unannotated")
        self.interpolation_status.setText(self._text("current_slice", state=state))
        if self.read_only:
            self._refresh_observation_views()

    def set_slice(self, index: int) -> None:
        if self.volume is None:
            return
        index = int(np.clip(index, 0, self.volume.data.shape[2] - 1))
        self.canvas.cancel_polygon()
        self.current_slice = index
        self.observation_position = (*self.observation_position[:2], index)
        self.slice_slider.blockSignals(True)
        self.slice_spin.blockSignals(True)
        self.slice_slider.setValue(index)
        self.slice_spin.setValue(index)
        self.slice_slider.blockSignals(False)
        self.slice_spin.blockSignals(False)
        self.refresh_slice()

    def move_slice(self, offset: int) -> None:
        self.set_slice(self.current_slice + offset)

    def go_to_labeled_slice(self, direction: int) -> None:
        if (
            self.project is None
            or self.volume is None
            or self._closing_polygon
            or self._switching_annotation
            or self.load_thread is not None
            or self.external_preview_active
        ):
            return
        candidates = (
            index
            for index, annotation in self.project.slices.items()
            if annotation.polygons and (index - self.current_slice) * direction > 0
        )
        target = (max if direction < 0 else min)(candidates, default=None)
        if target is None:
            QMessageBox.information(
                self,
                self._text("labeled_slice_title"),
                self._text(
                    "previous_labeled_not_found"
                    if direction < 0
                    else "next_labeled_not_found"
                ),
            )
            return
        self.set_slice(target)

    @contextmanager
    def _polygon_busy_ui(
        self, status_key: str = "closing_polygon_status"
    ) -> Iterator[None]:
        was_enabled = self.isEnabled()
        action_states = [
            (action, action.isEnabled()) for action in self.annotation_toolbar.actions()
        ]
        shortcut_states = [
            (shortcut, shortcut.isEnabled())
            for shortcut in self.findChildren(QShortcut)
        ]
        autosave_active = self.autosave_timer.isActive()
        previous_message = self.statusBar().currentMessage()
        self._closing_polygon = True
        self.autosave_timer.stop()
        self.setEnabled(False)
        for action, _enabled in action_states:
            action.setEnabled(False)
        for shortcut, _enabled in shortcut_states:
            shortcut.setEnabled(False)
        self.statusBar().showMessage(self._text(status_key))
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            QApplication.processEvents(
                QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents
            )
            yield
        finally:
            try:
                QApplication.processEvents()
            finally:
                self.setEnabled(was_enabled)
                for action, enabled in action_states:
                    action.setEnabled(enabled)
                for shortcut, enabled in shortcut_states:
                    shortcut.setEnabled(enabled)
                self.statusBar().showMessage(previous_message)
                QApplication.restoreOverrideCursor()
                self._closing_polygon = False
                if autosave_active:
                    self.autosave_timer.start()

    def add_polygon(self, points: list[tuple[float, float]], operation: str) -> None:
        if self.project is None or self._closing_polygon or self.read_only:
            return
        with self._polygon_busy_ui():
            self.project.add_polygon(
                self.current_slice,
                PolygonAnnotation(points=tuple(points), operation=operation),
            )
            self.commit_change()
            self.refresh_slice()

    def update_polygon(
        self,
        polygon_index: int,
        points: list[tuple[float, float]],
    ) -> None:
        if self.project is None or self.read_only:
            return
        self.project.replace_polygon(
            self.current_slice,
            polygon_index,
            tuple(points),
        )
        self.commit_change()
        self.refresh_slice()

    def delete_last_edited_polygon(self) -> None:
        if self.project is None or self.read_only:
            return
        self.canvas.cancel_polygon()
        if self.project.annotation(self.current_slice).force_empty:
            self.statusBar().showMessage(self._text("force_empty_delete"))
            return
        deleted = self.project.delete_last_edited_polygon(self.current_slice)
        if deleted is None:
            self.statusBar().showMessage(self._text("no_polygon_delete"))
            return
        self.commit_change()
        self.refresh_slice()
        self.statusBar().showMessage(self._text("polygon_deleted"))

    def clear_current_slice(self) -> None:
        if self.project is None or self.read_only:
            return
        annotation = self.project.annotation(self.current_slice)
        if not (
            annotation.polygons
            or annotation.completed
            or annotation.keyframe
            or annotation.force_empty
        ):
            return
        answer = QMessageBox.question(
            self,
            self._text("clear_title"),
            self._text("clear_message"),
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.project.clear_slice(self.current_slice)
        self.commit_change()
        self.refresh_slice()

    def copy_previous_slice(self) -> None:
        if self.project is None or self.current_slice == 0 or self.read_only:
            return
        target = self.project.annotation(self.current_slice)
        if target.polygons:
            answer = QMessageBox.question(
                self,
                self._text("overwrite_title"),
                self._text("overwrite_message"),
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
        self.project.copy_slice(self.current_slice - 1, self.current_slice)
        self.commit_change()
        self.refresh_slice()

    def set_slice_completed(self, completed: bool) -> None:
        if self.project is None or self.read_only:
            return
        self.project.set_completed(self.current_slice, completed)
        self.commit_change()
        self.refresh_slice()

    def set_force_empty(self, force_empty: bool) -> None:
        if self.project is None or self.read_only:
            return
        self.project.set_force_empty(self.current_slice, force_empty)
        self.commit_change()
        self.refresh_slice()

    def toggle_completed(self) -> None:
        if self.project is not None and not self.read_only:
            self.completed_check.setChecked(not self.completed_check.isChecked())

    def go_to_next_incomplete(self) -> None:
        if self.project is None or self.external_preview_active:
            return
        depth = self.project.shape_lps[2]
        for offset in range(1, depth + 1):
            index = (self.current_slice + offset) % depth
            if not self.project.annotation(index).completed:
                self.set_slice(index)
                return

    def commit_change(self) -> None:
        if self.external_preview_active:
            return
        self._dirty = True
        self._mask_coverage_dirty = True
        self._observation_mask = None
        self.save_project()

    def autosave_if_needed(self) -> None:
        if (
            self._dirty
            and not self._closing_polygon
            and not self.external_preview_active
        ):
            self.save_project()

    def save_project(self, *, notify: bool = False, force: bool = False) -> bool:
        if self.external_preview_active:
            return True
        empty_numbered = (
            self.annotation_index > 0
            and self.project is not None
            and not self.project.has_polygons
        )
        if (
            self.project is None
            or self.project_path is None
            or (not self._dirty and not force and not empty_numbered)
        ):
            return True
        try:
            if self.annotation_index > 0:
                self.project.save(self.project_path, delete_if_empty=True)
            else:
                self.project.save(self.project_path)
        except Exception as exc:
            self.autosave_status.setText(self._text("autosave_failed", error=exc))
            if notify:
                QMessageBox.critical(
                    self,
                    self._text("autosave_failed_title"),
                    str(exc),
                )
            return False
        self._dirty = False
        if empty_numbered:
            self._show_annotation_path()
            return True
        saved_at = QTime.currentTime().toString("HH:mm:ss")
        self.autosave_status.setText(
            self._text(
                "autosave_success",
                time=saved_at,
                path=self.project_path,
            )
        )
        return True

    def export_mask(self) -> None:
        if self.current_source is not None:
            self._export_mask(self.current_source.mask_path)

    def export_ubd_mask(self) -> None:
        if self.current_source is not None:
            self._export_mask(self.current_source.ubd_mask_path)

    def export_annotations(self) -> None:
        if (
            self.project is None
            or self.project_path is None
            or self.external_preview_active
        ):
            return
        if not self.save_project(notify=True, force=True):
            return
        QMessageBox.information(
            self,
            self._text("export_complete_title"),
            self._text(
                "export_annotations_empty_message"
                if self.annotation_index > 0 and not self.project.has_polygons
                else "export_annotations_complete_message",
                index=self.annotation_index,
                path=self.project_path,
            ),
        )

    def _export_mask(self, output: Path) -> None:
        if self.project is None or self.volume is None or self.external_preview_active:
            return
        if not self.save_project(notify=True):
            return
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            AnnotationExporter().export(
                self.project,
                self.volume,
                output,
                interpolate=True,
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                self._text("export_failed_title"),
                str(exc),
            )
            return
        finally:
            QApplication.restoreOverrideCursor()
        QMessageBox.information(
            self,
            self._text("export_complete_title"),
            self._text(
                "export_complete_message",
                path=output,
                count=self.project.interpolated_slice_count,
            ),
        )

    def closeEvent(self, event) -> None:
        if self.external_mask_thread is not None:
            event.ignore()
            return
        if self._closing_polygon:
            event.ignore()
            return
        if self.load_thread is not None:
            QMessageBox.information(
                self,
                self._text("loading_close_title"),
                self._text("loading_close_message"),
            )
            event.ignore()
            return
        if not self.save_project(notify=True):
            event.ignore()
            return
        for view in self.observation_windows.values():
            view.hide()
        super().closeEvent(event)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        if self.read_only and self.volume is not None:
            for view in self.observation_windows.values():
                view.show()

    def hideEvent(self, event) -> None:
        for view in self.observation_windows.values():
            view.hide()
        super().hideEvent(event)


def run_annotation_app(
    *,
    sources: list[ImageSource] | None = None,
    spacing_mm: float = 0.8,
    language: UiLanguage = "en",
) -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    window = AnnotationMainWindow(
        sources=sources,
        spacing_mm=spacing_mm,
        language=language,
    )
    window.show()
    return app.exec()


__all__ = [
    "AnnotationMainWindow",
    "SliceCanvas",
    "VolumeLoadThread",
    "run_annotation_app",
]
