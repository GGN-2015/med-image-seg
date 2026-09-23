"""PySide6 multi-polygon medical image annotation GUI."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PySide6.QtCore import QPointF, QRectF, Qt, QThread, QTime, QTimer, Signal
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
)
from PySide6.QtWidgets import (
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
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from .annotation import AnnotationExporter, AnnotationProject, PolygonAnnotation
from .io import MedicalVolume, MedicalVolumeReader
from .localization import UiLanguage, normalize_language, translate
from .sources import ImageCollection, ImageSource


class SliceCanvas(QGraphicsView):
    """Zoomable axial canvas that emits completed or edited polygons."""

    polygon_finished = Signal(object, str)
    polygon_changed = Signal(int, object)

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

    def set_operation(self, operation: str) -> None:
        self._operation = operation
        self.cancel_polygon()

    def set_slice(
        self,
        image: np.ndarray,
        polygons: list[PolygonAnnotation],
        interpolated_mask: np.ndarray | None = None,
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
        self._image_rect = QRectF(0, 0, width, height)
        self.scene().setSceneRect(self._image_rect)
        if interpolated_mask is not None:
            overlay = np.zeros((height, width, 4), dtype=np.uint8)
            overlay[np.asarray(interpolated_mask, dtype=bool)] = (49, 180, 255, 72)
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
                self.scene().addItem(handle)
                self._handles.append(handle)
        if self._first_image:
            self.fitInView(self._image_rect, Qt.AspectRatioMode.KeepAspectRatio)
            self._first_image = False

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
        if len(self._draft_points) < 3:
            return
        points = [(point.x(), point.y()) for point in self._draft_points]
        self._draft_points.clear()
        self._update_draft()
        self.polygon_finished.emit(points, self._operation)

    def cancel_polygon(self) -> None:
        self._draft_points.clear()
        self._update_draft()

    def mousePressEvent(self, event) -> None:
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
        if event.button() == Qt.MouseButton.LeftButton:
            self.finish_polygon()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event) -> None:
        factor = 1.2 if event.angleDelta().y() > 0 else 1 / 1.2
        self.scale(factor, factor)
        event.accept()


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
        self.current_slice = 0
        self.load_thread: VolumeLoadThread | None = None
        self._loading_source: ImageSource | None = None
        self.loading_dialog: QProgressDialog | None = None
        self._load_error: str | None = None
        self._dirty = False
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
        center_layout.addWidget(self.canvas, 1)
        slice_row = QHBoxLayout()
        self.previous_button = QPushButton()
        self.previous_button.clicked.connect(lambda: self.move_slice(-1))
        self.next_button = QPushButton()
        self.next_button.clicked.connect(lambda: self.move_slice(1))
        self.slice_slider = QSlider(Qt.Orientation.Horizontal)
        self.slice_slider.valueChanged.connect(self.set_slice)
        self.slice_spin = QSpinBox()
        self.slice_spin.valueChanged.connect(self.set_slice)
        slice_row.addWidget(self.previous_button)
        slice_row.addWidget(self.slice_slider, 1)
        slice_row.addWidget(self.slice_spin)
        slice_row.addWidget(self.next_button)
        center_layout.addLayout(slice_row)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        self.mode_group = QGroupBox()
        mode_layout = QVBoxLayout(self.mode_group)
        self.add_radio = QRadioButton()
        self.erase_radio = QRadioButton()
        self.add_radio.setChecked(True)
        modes = QButtonGroup(self)
        modes.addButton(self.add_radio)
        modes.addButton(self.erase_radio)
        self.add_radio.toggled.connect(self.update_operation)
        mode_layout.addWidget(self.add_radio)
        mode_layout.addWidget(self.erase_radio)
        right_layout.addWidget(self.mode_group)

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
        center.setEnabled(False)
        right.setEnabled(False)
        self.editor_widgets = (center, right)
        self._retranslate_ui()

    def _text(self, key: str, **values: object) -> str:
        return translate(key, self.language, **values)

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
        self.image_collection_label.setText(self._text("image_collection"))
        self.file_button.setText(self._text("import_files"))
        self.dicom_button.setText(self._text("import_dicom"))
        self.language_label.setText(self._text("language"))
        self.imported_images_label.setText(self._text("imported_images"))
        self.spacing_label.setText(self._text("annotation_grid"))
        self.load_button.setText(self._text("load_selected"))
        self.previous_button.setText(self._text("previous_slice"))
        self.next_button.setText(self._text("next_slice"))
        self.mode_group.setTitle(self._text("polygon_mode"))
        self.add_radio.setText(self._text("add_region"))
        self.erase_radio.setText(self._text("erase_region"))
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
        self.hint_label.setText(self._text("hint"))
        if self.volume is not None and self.project is not None:
            self.refresh_slice()
            if self.project_path is not None:
                self.autosave_status.setText(
                    self._text("autosave_path", path=self.project_path)
                )
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
        QShortcut(
            QKeySequence(Qt.Key.Key_Space), self, activated=self.canvas.finish_polygon
        )
        QShortcut(
            QKeySequence(Qt.Key.Key_Escape), self, activated=self.canvas.cancel_polygon
        )
        QShortcut(
            QKeySequence.StandardKey.Undo,
            self,
            activated=self.delete_last_edited_polygon,
        )
        QShortcut(QKeySequence("C"), self, activated=self.copy_previous_slice)
        QShortcut(QKeySequence("M"), self, activated=self.toggle_completed)
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
        if item is None or self.load_thread is not None:
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
        self.export_action.setEnabled(False)
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

    def volume_loaded(self, volume: MedicalVolume) -> None:
        assert self._loading_source is not None
        source = self._loading_source
        project_path = source.annotation_path
        try:
            if project_path.is_file() or Path(f"{project_path}.bak").is_file():
                project = AnnotationProject.load(project_path)
                project.validate_volume(volume)
                if project.source_fingerprint != source.fingerprint:
                    raise ValueError("annotation fingerprint does not match this image")
            else:
                project = AnnotationProject.create(
                    image_id=source.source_id,
                    source_fingerprint=source.fingerprint,
                    volume=volume,
                )
                project.save(project_path)
        except Exception as exc:
            self._load_error = f"{type(exc).__name__}: {exc}"
            return
        self.current_source = source
        self.volume = volume
        self.project_path = project_path
        self.project = project
        self._dirty = False
        self.autosave_status.setText(
            self._text("autosave_path", path=self.project_path)
        )
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
        self.canvas.set_operation("add" if self.add_radio.isChecked() else "erase")

    def _windowed_slice(self) -> np.ndarray:
        assert self.volume is not None
        plane = self.volume.data[:, :, self.current_slice].T
        level = self.level_spin.value()
        width = self.width_spin.value()
        low = level - width / 2
        scaled = np.clip((plane - low) / width, 0.0, 1.0)
        return np.asarray(np.rint(scaled * 255), dtype=np.uint8)

    def refresh_slice(self) -> None:
        if self.volume is None or self.project is None:
            return
        annotation = self.project.annotation(self.current_slice)
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

    def set_slice(self, index: int) -> None:
        if self.volume is None:
            return
        index = int(np.clip(index, 0, self.volume.data.shape[2] - 1))
        self.canvas.cancel_polygon()
        self.current_slice = index
        self.slice_slider.blockSignals(True)
        self.slice_spin.blockSignals(True)
        self.slice_slider.setValue(index)
        self.slice_spin.setValue(index)
        self.slice_slider.blockSignals(False)
        self.slice_spin.blockSignals(False)
        self.refresh_slice()

    def move_slice(self, offset: int) -> None:
        self.set_slice(self.current_slice + offset)

    def add_polygon(self, points: list[tuple[float, float]], operation: str) -> None:
        if self.project is None:
            return
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
        if self.project is None:
            return
        self.project.replace_polygon(
            self.current_slice,
            polygon_index,
            tuple(points),
        )
        self.commit_change()
        self.refresh_slice()

    def delete_last_edited_polygon(self) -> None:
        if self.project is None:
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
        if self.project is None:
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
        if self.project is None or self.current_slice == 0:
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
        if self.project is None:
            return
        self.project.set_completed(self.current_slice, completed)
        self.commit_change()
        self.refresh_slice()

    def set_force_empty(self, force_empty: bool) -> None:
        if self.project is None:
            return
        self.project.set_force_empty(self.current_slice, force_empty)
        self.commit_change()
        self.refresh_slice()

    def toggle_completed(self) -> None:
        if self.project is not None:
            self.completed_check.setChecked(not self.completed_check.isChecked())

    def go_to_next_incomplete(self) -> None:
        if self.project is None:
            return
        depth = self.project.shape_lps[2]
        for offset in range(1, depth + 1):
            index = (self.current_slice + offset) % depth
            if not self.project.annotation(index).completed:
                self.set_slice(index)
                return

    def commit_change(self) -> None:
        self._dirty = True
        self.save_project()

    def autosave_if_needed(self) -> None:
        if self._dirty:
            self.save_project()

    def save_project(self, *, notify: bool = False) -> bool:
        if self.project is None or self.project_path is None or not self._dirty:
            return True
        try:
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
        if self.project is None or self.volume is None or self.current_source is None:
            return
        if not self.save_project(notify=True):
            return
        output = self.current_source.mask_path
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
        super().closeEvent(event)


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
