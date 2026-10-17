from __future__ import annotations

from typing import final

from PySide6.QtCore import QPointF, QRectF, Qt, QThread, QTimer, SignalInstance
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QGraphicsEllipseItem,
    QGraphicsPathItem,
    QGraphicsPixmapItem,
    QGraphicsPolygonItem,
    QGraphicsView,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
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

from ....Abstract.Presentation.Canvas.T_MutableSliceCanvas import T_MutableSliceCanvas
from ....Abstract.Presentation.Canvas.T_MutableVertexHandle import T_MutableVertexHandle
from ....Abstract.Presentation.Layout.T_LayoutService import T_LayoutService
from ....Abstract.Presentation.Loading.T_MutableExternalMaskLoadThread import (
    T_MutableExternalMaskLoadThread,
)
from ....Abstract.Presentation.Loading.T_MutableVolumeLoadThread import (
    T_MutableVolumeLoadThread,
)
from ....Abstract.Presentation.Navigation import (
    T_MutableAnnotationIndexSpinBox,
)
from ....Abstract.Presentation.Navigation.T_MutableMaskCoverageBar import (
    T_MutableMaskCoverageBar,
)
from ....Abstract.Presentation.Observation import (
    T_MutableOrthogonalSliceWindow,
)
from ....Abstract.Presentation.Window.T_MutableAnnotationMainWindow import (
    T_MutableAnnotationMainWindow,
)


# 构建控件、绑定快捷键并切换界面文案，集中管理 Qt 布局。
@final
class C_Qt_LayoutService(
    T_LayoutService[
        T_MutableAnnotationMainWindow[
            QMainWindow,
            QTimer,
            QToolBar,
            QAction,
            QLabel,
            QPushButton,
            QComboBox,
            QSplitter,
            QListWidget,
            QDoubleSpinBox,
            QSlider,
            QSpinBox,
            QGroupBox,
            QRadioButton,
            QCheckBox,
            QProgressBar,
            QProgressDialog,
            QShortcut,
            QWidget,
            QButtonGroup,
            T_MutableSliceCanvas[
                QGraphicsView,
                QPointF,
                QRectF,
                QGraphicsPixmapItem,
                QGraphicsPathItem,
                QGraphicsPolygonItem,
                T_MutableVertexHandle[QGraphicsEllipseItem],
                SignalInstance,
            ],
            T_MutableOrthogonalSliceWindow[
                QWidget,
                QLabel,
                T_MutableSliceCanvas[
                    QGraphicsView,
                    QPointF,
                    QRectF,
                    QGraphicsPixmapItem,
                    QGraphicsPathItem,
                    QGraphicsPolygonItem,
                    T_MutableVertexHandle[QGraphicsEllipseItem],
                    SignalInstance,
                ],
                QSpinBox,
                SignalInstance,
            ],
            T_MutableAnnotationIndexSpinBox[QAbstractSpinBox, SignalInstance],
            T_MutableMaskCoverageBar[QWidget, QSlider],
            T_MutableVolumeLoadThread[QThread, SignalInstance],
            T_MutableExternalMaskLoadThread[QThread, SignalInstance],
            QPointF,
        ]
    ]
):
    # 构建影像列表、主画布和右侧编辑面板，登记供状态切换使用的控件。
    def build_ui(
        self,
        context: T_MutableAnnotationMainWindow[
            QMainWindow,
            QTimer,
            QToolBar,
            QAction,
            QLabel,
            QPushButton,
            QComboBox,
            QSplitter,
            QListWidget,
            QDoubleSpinBox,
            QSlider,
            QSpinBox,
            QGroupBox,
            QRadioButton,
            QCheckBox,
            QProgressBar,
            QProgressDialog,
            QShortcut,
            QWidget,
            QButtonGroup,
            T_MutableSliceCanvas[
                QGraphicsView,
                QPointF,
                QRectF,
                QGraphicsPixmapItem,
                QGraphicsPathItem,
                QGraphicsPolygonItem,
                T_MutableVertexHandle[QGraphicsEllipseItem],
                SignalInstance,
            ],
            T_MutableOrthogonalSliceWindow[
                QWidget,
                QLabel,
                T_MutableSliceCanvas[
                    QGraphicsView,
                    QPointF,
                    QRectF,
                    QGraphicsPixmapItem,
                    QGraphicsPathItem,
                    QGraphicsPolygonItem,
                    T_MutableVertexHandle[QGraphicsEllipseItem],
                    SignalInstance,
                ],
                QSpinBox,
                SignalInstance,
            ],
            T_MutableAnnotationIndexSpinBox[QAbstractSpinBox, SignalInstance],
            T_MutableMaskCoverageBar[QWidget, QSlider],
            T_MutableVolumeLoadThread[QThread, SignalInstance],
            T_MutableExternalMaskLoadThread[QThread, SignalInstance],
            QPointF,
        ],
        spacing_mm: float,
    ) -> None:
        from ..Canvas.C_Qt_SliceCanvas import C_Qt_SliceCanvas
        from ..Navigation.C_Qt_AnnotationIndexSpinBox import C_Qt_AnnotationIndexSpinBox
        from ..Navigation.C_Qt_MaskCoverageBar import C_Qt_MaskCoverageBar

        context.setAnnotationToolbar(QToolBar())
        context.getAnnotationToolbar().setMovable(False)
        context.getHost().addToolBar(context.getAnnotationToolbar())
        context.setExportAction(QAction(context.getHost()))
        context.getExportAction().setEnabled(False)
        context.getExportAction().triggered.connect(context.export_mask)
        context.getAnnotationToolbar().addAction(context.getExportAction())
        context.setExportUbdAction(QAction(context.getHost()))
        context.getExportUbdAction().setEnabled(False)
        context.getExportUbdAction().triggered.connect(context.export_ubd_mask)
        context.getAnnotationToolbar().addAction(context.getExportUbdAction())
        context.setExportJsonAction(QAction(context.getHost()))
        context.getExportJsonAction().setEnabled(False)
        context.getExportJsonAction().triggered.connect(context.export_annotations)
        context.getAnnotationToolbar().addAction(context.getExportJsonAction())
        root_widget = QWidget()
        root_layout = QVBoxLayout(root_widget)
        import_row = QHBoxLayout()
        context.setImageCollectionLabel(QLabel())
        import_row.addWidget(context.getImageCollectionLabel())
        context.setFileButton(QPushButton())
        context.getFileButton().clicked.connect(context.choose_image_files)
        context.setDicomButton(QPushButton())
        context.getDicomButton().clicked.connect(context.choose_dicom_directory)
        import_row.addWidget(context.getFileButton())
        import_row.addWidget(context.getDicomButton())
        import_row.addStretch(1)
        context.setLanguageLabel(QLabel())
        context.setLanguageCombo(QComboBox())
        context.getLanguageCombo().addItem("English", "en")
        context.getLanguageCombo().addItem("中文", "zh")
        context.getLanguageCombo().setCurrentIndex(
            context.getLanguageCombo().findData(context.getLanguage())
        )
        context.getLanguageCombo().currentIndexChanged.connect(
            context._language_changed
        )
        import_row.addWidget(context.getLanguageLabel())
        import_row.addWidget(context.getLanguageCombo())
        root_layout.addLayout(import_row)
        context.setSplitter(QSplitter())
        root_layout.addWidget(context.getSplitter(), 1)
        left = QWidget()
        left_layout = QVBoxLayout(left)
        context.setImportedImagesLabel(QLabel())
        left_layout.addWidget(context.getImportedImagesLabel())
        context.setSourceList(QListWidget())
        context.getSourceList().itemDoubleClicked.connect(context.load_selected_source)
        left_layout.addWidget(context.getSourceList(), 1)
        spacing_row = QHBoxLayout()
        context.setSpacingLabel(QLabel())
        spacing_row.addWidget(context.getSpacingLabel())
        context.setSpacingSpin(QDoubleSpinBox())
        context.getSpacingSpin().setRange(0.2, 2.0)
        context.getSpacingSpin().setSingleStep(0.1)
        context.getSpacingSpin().setDecimals(2)
        context.getSpacingSpin().setValue(spacing_mm)
        context.getSpacingSpin().setSuffix(" mm")
        spacing_row.addWidget(context.getSpacingSpin())
        context.setLoadButton(QPushButton())
        context.getLoadButton().clicked.connect(context.load_selected_source)
        left_layout.addLayout(spacing_row)
        left_layout.addWidget(context.getLoadButton())
        context.setUnloadImageButton(QPushButton())
        context.getUnloadImageButton().setEnabled(False)
        context.getUnloadImageButton().clicked.connect(context.unload_imported_image)
        left_layout.addWidget(context.getUnloadImageButton())
        center = QWidget()
        center_layout = QVBoxLayout(center)
        context.setCanvas(C_Qt_SliceCanvas())
        context.getCanvas().getPolygonFinished().connect(context.add_polygon)
        context.getCanvas().getPolygonChanged().connect(context.update_polygon)
        context.getCanvas().getPositionClicked().connect(
            lambda point: context._observation_clicked("LP", point)
        )
        center_layout.addWidget(context.getCanvas().getHost(), 1)
        slice_row = QGridLayout()
        slice_row.setColumnStretch(1, 1)
        slice_row.setVerticalSpacing(2)
        context.setPreviousButton(QPushButton())
        context.getPreviousButton().clicked.connect(lambda: context.move_slice(-1))
        context.setNextButton(QPushButton())
        context.getNextButton().clicked.connect(lambda: context.move_slice(1))
        context.setPreviousLabeledButton(QPushButton())
        context.getPreviousLabeledButton().clicked.connect(
            lambda: context.go_to_labeled_slice(-1)
        )
        context.setNextLabeledButton(QPushButton())
        context.getNextLabeledButton().clicked.connect(
            lambda: context.go_to_labeled_slice(1)
        )
        context.setSliceSlider(QSlider(Qt.Orientation.Horizontal))
        context.getSliceSlider().valueChanged.connect(context.set_slice)
        context.setMaskCoverageBar(C_Qt_MaskCoverageBar(context.getSliceSlider()))
        context.setSliceSpin(QSpinBox())
        context.getSliceSpin().valueChanged.connect(context.set_slice)
        slice_row.addWidget(context.getPreviousButton(), 0, 0)
        slice_row.addWidget(context.getSliceSlider(), 0, 1)
        slice_row.addWidget(context.getSliceSpin(), 0, 2)
        slice_row.addWidget(context.getNextButton(), 0, 3)
        slice_row.addWidget(context.getMaskCoverageBar().getHost(), 1, 1)
        slice_row.addWidget(context.getPreviousLabeledButton(), 1, 0)
        slice_row.addWidget(context.getNextLabeledButton(), 1, 3)
        center_layout.addLayout(slice_row)
        right = QWidget()
        right_layout = QVBoxLayout(right)
        annotation_row = QHBoxLayout()
        context.setAnnotationIndexLabel(QLabel())
        context.setAnnotationIndexSpin(C_Qt_AnnotationIndexSpinBox())
        context.getAnnotationIndexLabel().setBuddy(
            context.getAnnotationIndexSpin().getHost()
        )
        context.getAnnotationIndexSpin().getValueChanged().connect(
            context.set_annotation_index
        )
        annotation_row.addWidget(context.getAnnotationIndexLabel())
        annotation_row.addWidget(context.getAnnotationIndexSpin().getHost(), 1)
        right_layout.addLayout(annotation_row)
        context.setModeGroup(QGroupBox())
        mode_layout = QVBoxLayout(context.getModeGroup())
        context.setAddRadio(QRadioButton())
        context.setEraseRadio(QRadioButton())
        context.setObserveRadio(QRadioButton())
        context.getAddRadio().setChecked(True)
        modes = QButtonGroup(context.getHost())
        modes.addButton(context.getAddRadio())
        modes.addButton(context.getEraseRadio())
        modes.addButton(context.getObserveRadio())
        modes.buttonToggled.connect(
            lambda _button, checked: context.update_operation() if checked else None
        )
        mode_layout.addWidget(context.getAddRadio())
        mode_layout.addWidget(context.getEraseRadio())
        mode_layout.addWidget(context.getObserveRadio())
        right_layout.addWidget(context.getModeGroup())
        context.setObservationStatus(QLabel())
        context.getObservationStatus().setWordWrap(True)
        context.getObservationStatus().hide()
        right_layout.addWidget(context.getObservationStatus())
        context.setFinishButton(QPushButton())
        context.getFinishButton().clicked.connect(context.getCanvas().finish_polygon)
        context.setCancelButton(QPushButton())
        context.getCancelButton().clicked.connect(context.getCanvas().cancel_polygon)
        context.setDeleteButton(QPushButton())
        context.getDeleteButton().clicked.connect(context.delete_last_edited_polygon)
        context.setCopyButton(QPushButton())
        context.getCopyButton().clicked.connect(context.copy_previous_slice)
        context.setClearButton(QPushButton())
        context.getClearButton().clicked.connect(context.clear_current_slice)
        for button in (
            context.getFinishButton(),
            context.getCancelButton(),
            context.getDeleteButton(),
            context.getCopyButton(),
            context.getClearButton(),
        ):
            right_layout.addWidget(button)
        context.setCompletedCheck(QCheckBox())
        context.getCompletedCheck().toggled.connect(context.set_slice_completed)
        right_layout.addWidget(context.getCompletedCheck())
        context.setForceEmptyCheck(QCheckBox())
        context.getForceEmptyCheck().toggled.connect(context.set_force_empty)
        right_layout.addWidget(context.getForceEmptyCheck())
        context.setNextIncompleteButton(QPushButton())
        context.getNextIncompleteButton().clicked.connect(context.go_to_next_incomplete)
        right_layout.addWidget(context.getNextIncompleteButton())
        context.setReviewProgress(QProgressBar())
        right_layout.addWidget(context.getReviewProgress())
        context.setShowInterpolation(QCheckBox())
        context.getShowInterpolation().setChecked(True)
        context.getShowInterpolation().toggled.connect(context.refresh_slice)
        right_layout.addWidget(context.getShowInterpolation())
        context.setInterpolationStatus(QLabel())
        context.getInterpolationStatus().setWordWrap(True)
        right_layout.addWidget(context.getInterpolationStatus())
        context.setAutosaveStatus(QLabel())
        context.getAutosaveStatus().setWordWrap(True)
        right_layout.addWidget(context.getAutosaveStatus())
        context.setWindowGroup(QGroupBox())
        window_layout = QVBoxLayout(context.getWindowGroup())
        level_row = QHBoxLayout()
        context.setLevelLabel(QLabel())
        level_row.addWidget(context.getLevelLabel())
        context.setLevelSpin(QDoubleSpinBox())
        context.getLevelSpin().setDecimals(1)
        context.getLevelSpin().valueChanged.connect(context.refresh_slice)
        level_row.addWidget(context.getLevelSpin())
        width_row = QHBoxLayout()
        context.setWidthLabel(QLabel())
        width_row.addWidget(context.getWidthLabel())
        context.setWidthSpin(QDoubleSpinBox())
        context.getWidthSpin().setDecimals(1)
        context.getWidthSpin().setMinimum(1.0)
        context.getWidthSpin().valueChanged.connect(context.refresh_slice)
        width_row.addWidget(context.getWidthSpin())
        window_layout.addLayout(level_row)
        window_layout.addLayout(width_row)
        right_layout.addWidget(context.getWindowGroup())
        external_mask_row = QHBoxLayout()
        context.setLoadExternalMaskButton(QPushButton())
        context.getLoadExternalMaskButton().clicked.connect(
            context.choose_external_mask
        )
        context.setUnloadExternalMaskButton(QPushButton())
        context.getUnloadExternalMaskButton().setEnabled(False)
        context.getUnloadExternalMaskButton().clicked.connect(
            context.unload_external_mask
        )
        external_mask_row.addWidget(context.getLoadExternalMaskButton())
        external_mask_row.addWidget(context.getUnloadExternalMaskButton())
        right_layout.addLayout(external_mask_row)
        right_layout.addStretch(1)
        context.setHintLabel(QLabel())
        context.getHintLabel().setWordWrap(True)
        right_layout.addWidget(context.getHintLabel())
        context.getSplitter().addWidget(left)
        context.getSplitter().addWidget(center)
        context.getSplitter().addWidget(right)
        context.getSplitter().setSizes([310, 900, 280])
        context.getHost().setCentralWidget(root_widget)
        context.getHost().setStatusBar(QStatusBar())
        context.setEditingControls(
            (
                context.getFinishButton(),
                context.getCancelButton(),
                context.getDeleteButton(),
                context.getCopyButton(),
                context.getClearButton(),
                context.getCompletedCheck(),
                context.getForceEmptyCheck(),
            )
        )
        context.setEditorWidgets(
            (
                center,
                context.getModeGroup(),
                context.getAnnotationIndexSpin().getHost(),
                context.getWindowGroup(),
                context.getNextIncompleteButton(),
                context.getReviewProgress(),
                context.getShowInterpolation(),
                *context.iterEditingControls(),
            )
        )
        for widget in context.iterEditorWidgets():
            widget.setEnabled(False)
        context._retranslate_ui()

    # 根据当前语言更新标题、按钮、状态及操作提示文本。
    def retranslate_ui(
        self,
        context: T_MutableAnnotationMainWindow[
            QMainWindow,
            QTimer,
            QToolBar,
            QAction,
            QLabel,
            QPushButton,
            QComboBox,
            QSplitter,
            QListWidget,
            QDoubleSpinBox,
            QSlider,
            QSpinBox,
            QGroupBox,
            QRadioButton,
            QCheckBox,
            QProgressBar,
            QProgressDialog,
            QShortcut,
            QWidget,
            QButtonGroup,
            T_MutableSliceCanvas[
                QGraphicsView,
                QPointF,
                QRectF,
                QGraphicsPixmapItem,
                QGraphicsPathItem,
                QGraphicsPolygonItem,
                T_MutableVertexHandle[QGraphicsEllipseItem],
                SignalInstance,
            ],
            T_MutableOrthogonalSliceWindow[
                QWidget,
                QLabel,
                T_MutableSliceCanvas[
                    QGraphicsView,
                    QPointF,
                    QRectF,
                    QGraphicsPixmapItem,
                    QGraphicsPathItem,
                    QGraphicsPolygonItem,
                    T_MutableVertexHandle[QGraphicsEllipseItem],
                    SignalInstance,
                ],
                QSpinBox,
                SignalInstance,
            ],
            T_MutableAnnotationIndexSpinBox[QAbstractSpinBox, SignalInstance],
            T_MutableMaskCoverageBar[QWidget, QSlider],
            T_MutableVolumeLoadThread[QThread, SignalInstance],
            T_MutableExternalMaskLoadThread[QThread, SignalInstance],
            QPointF,
        ],
    ) -> None:
        context.getHost().setWindowTitle(context._text("window_title"))
        context.getAnnotationToolbar().setWindowTitle(
            context._text("toolbar_annotation")
        )
        context.getExportAction().setText(context._text("export_mask"))
        context.getExportUbdAction().setText(context._text("export_ubd_mask"))
        context.getExportJsonAction().setText(context._text("export_annotations"))
        context.getMaskCoverageBar().getHost().setAccessibleName(
            context._text("mask_coverage_name")
        )
        context.getMaskCoverageBar().getHost().setToolTip(
            context._text("mask_coverage_tooltip")
        )
        context.getImageCollectionLabel().setText(context._text("image_collection"))
        context.getFileButton().setText(context._text("import_files"))
        context.getDicomButton().setText(context._text("import_dicom"))
        context.getLanguageLabel().setText(context._text("language"))
        context.getImportedImagesLabel().setText(context._text("imported_images"))
        context.getSpacingLabel().setText(context._text("annotation_grid"))
        context.getLoadButton().setText(context._text("load_selected"))
        context.getUnloadImageButton().setText(context._text("unload_imported_image"))
        context.getUnloadImageButton().setToolTip(context._text("unload_image_tooltip"))
        context.getPreviousButton().setText(context._text("previous_slice"))
        context.getNextButton().setText(context._text("next_slice"))
        context.getPreviousLabeledButton().setText(
            context._text("previous_labeled_slice")
        )
        context.getNextLabeledButton().setText(context._text("next_labeled_slice"))
        context.getPreviousLabeledButton().setToolTip(
            context._text("labeled_slice_tooltip")
        )
        context.getNextLabeledButton().setToolTip(
            context._text("labeled_slice_tooltip")
        )
        context.getModeGroup().setTitle(context._text("polygon_mode"))
        context.getAnnotationIndexLabel().setText(context._text("annotation_index"))
        context.getAnnotationIndexSpin().getHost().setAccessibleName(
            context._text("annotation_index")
        )
        context.getAnnotationIndexSpin().getHost().setToolTip(
            context._text("annotation_index_tooltip")
        )
        context.getAddRadio().setText(context._text("add_region"))
        context.getEraseRadio().setText(context._text("erase_region"))
        context.getObserveRadio().setText(context._text("observe_mode"))
        context.getFinishButton().setText(context._text("finish_polygon"))
        context.getCancelButton().setText(context._text("cancel_polygon"))
        context.getDeleteButton().setText(context._text("delete_last"))
        context.getCopyButton().setText(context._text("copy_previous"))
        context.getClearButton().setText(context._text("clear_slice"))
        context.getCompletedCheck().setText(context._text("completed"))
        context.getForceEmptyCheck().setText(context._text("force_empty"))
        context.getForceEmptyCheck().setToolTip(context._text("force_empty_tooltip"))
        context.getNextIncompleteButton().setText(context._text("next_incomplete"))
        context.getReviewProgress().setFormat(context._text("review_progress"))
        context.getShowInterpolation().setText(context._text("show_interpolation"))
        context.getWindowGroup().setTitle(context._text("window"))
        context.getLevelLabel().setText(context._text("window_level"))
        context.getWidthLabel().setText(context._text("window_width"))
        context.getLoadExternalMaskButton().setText(context._text("load_external_mask"))
        context.getUnloadExternalMaskButton().setText(
            context._text("unload_external_mask")
        )
        context.getHintLabel().setText(context._text(context._hint_key()))
        if context.getVolume() is not None and context.getProject() is not None:
            context.refresh_slice()
            if context.getProjectPath() is not None:
                context._show_annotation_path()
        else:
            context.getInterpolationStatus().setText(context._text("slice_not_loaded"))
            context.getAutosaveStatus().setText(context._text("autosave_waiting"))
            context.getHost().statusBar().showMessage(context._text("no_images_status"))

    # 把编辑和切片导航快捷键连接到对应动作，并登记可禁用项。
    def bind_shortcuts(
        self,
        context: T_MutableAnnotationMainWindow[
            QMainWindow,
            QTimer,
            QToolBar,
            QAction,
            QLabel,
            QPushButton,
            QComboBox,
            QSplitter,
            QListWidget,
            QDoubleSpinBox,
            QSlider,
            QSpinBox,
            QGroupBox,
            QRadioButton,
            QCheckBox,
            QProgressBar,
            QProgressDialog,
            QShortcut,
            QWidget,
            QButtonGroup,
            T_MutableSliceCanvas[
                QGraphicsView,
                QPointF,
                QRectF,
                QGraphicsPixmapItem,
                QGraphicsPathItem,
                QGraphicsPolygonItem,
                T_MutableVertexHandle[QGraphicsEllipseItem],
                SignalInstance,
            ],
            T_MutableOrthogonalSliceWindow[
                QWidget,
                QLabel,
                T_MutableSliceCanvas[
                    QGraphicsView,
                    QPointF,
                    QRectF,
                    QGraphicsPixmapItem,
                    QGraphicsPathItem,
                    QGraphicsPolygonItem,
                    T_MutableVertexHandle[QGraphicsEllipseItem],
                    SignalInstance,
                ],
                QSpinBox,
                SignalInstance,
            ],
            T_MutableAnnotationIndexSpinBox[QAbstractSpinBox, SignalInstance],
            T_MutableMaskCoverageBar[QWidget, QSlider],
            T_MutableVolumeLoadThread[QThread, SignalInstance],
            T_MutableExternalMaskLoadThread[QThread, SignalInstance],
            QPointF,
        ],
    ) -> None:
        previous = QShortcut(QKeySequence(Qt.Key.Key_Left.value), context.getHost())
        previous.activated.connect(lambda: context.move_slice(-1))
        following = QShortcut(QKeySequence(Qt.Key.Key_Right.value), context.getHost())
        following.activated.connect(lambda: context.move_slice(1))
        shortcuts: list[QShortcut] = []
        for sequence, callback in (
            (QKeySequence(Qt.Key.Key_Space.value), context.getCanvas().finish_polygon),
            (QKeySequence(Qt.Key.Key_Escape.value), context.getCanvas().cancel_polygon),
            (
                QKeySequence(QKeySequence.StandardKey.Undo),
                context.delete_last_edited_polygon,
            ),
            (QKeySequence("C"), context.copy_previous_slice),
            (QKeySequence("M"), context.toggle_completed),
        ):
            shortcut = QShortcut(sequence, context.getHost())
            shortcut.activated.connect(callback)
            shortcuts.append(shortcut)
        context.setEditingShortcuts(shortcuts)
        export = QShortcut(QKeySequence("E"), context.getHost())
        export.activated.connect(context.export_mask)

    # 按影像集合顺序重建列表，并保留来源对象与列表项的关联。
    def refresh_source_list(
        self,
        context: T_MutableAnnotationMainWindow[
            QMainWindow,
            QTimer,
            QToolBar,
            QAction,
            QLabel,
            QPushButton,
            QComboBox,
            QSplitter,
            QListWidget,
            QDoubleSpinBox,
            QSlider,
            QSpinBox,
            QGroupBox,
            QRadioButton,
            QCheckBox,
            QProgressBar,
            QProgressDialog,
            QShortcut,
            QWidget,
            QButtonGroup,
            T_MutableSliceCanvas[
                QGraphicsView,
                QPointF,
                QRectF,
                QGraphicsPixmapItem,
                QGraphicsPathItem,
                QGraphicsPolygonItem,
                T_MutableVertexHandle[QGraphicsEllipseItem],
                SignalInstance,
            ],
            T_MutableOrthogonalSliceWindow[
                QWidget,
                QLabel,
                T_MutableSliceCanvas[
                    QGraphicsView,
                    QPointF,
                    QRectF,
                    QGraphicsPixmapItem,
                    QGraphicsPathItem,
                    QGraphicsPolygonItem,
                    T_MutableVertexHandle[QGraphicsEllipseItem],
                    SignalInstance,
                ],
                QSpinBox,
                SignalInstance,
            ],
            T_MutableAnnotationIndexSpinBox[QAbstractSpinBox, SignalInstance],
            T_MutableMaskCoverageBar[QWidget, QSlider],
            T_MutableVolumeLoadThread[QThread, SignalInstance],
            T_MutableExternalMaskLoadThread[QThread, SignalInstance],
            QPointF,
        ],
    ) -> None:
        context.getSourceList().clear()
        for index, source in enumerate(context.getSources()):
            item = QListWidgetItem(source.getDisplayName())
            item.setData(Qt.ItemDataRole.UserRole, index)
            item.setToolTip(str(source.getPath()))
            context.getSourceList().addItem(item)

    # 根据编辑、观察或外置预览状态启用相应控件和快捷键。
    def apply_mode_ui(
        self,
        context: T_MutableAnnotationMainWindow[
            QMainWindow,
            QTimer,
            QToolBar,
            QAction,
            QLabel,
            QPushButton,
            QComboBox,
            QSplitter,
            QListWidget,
            QDoubleSpinBox,
            QSlider,
            QSpinBox,
            QGroupBox,
            QRadioButton,
            QCheckBox,
            QProgressBar,
            QProgressDialog,
            QShortcut,
            QWidget,
            QButtonGroup,
            T_MutableSliceCanvas[
                QGraphicsView,
                QPointF,
                QRectF,
                QGraphicsPixmapItem,
                QGraphicsPathItem,
                QGraphicsPolygonItem,
                T_MutableVertexHandle[QGraphicsEllipseItem],
                SignalInstance,
            ],
            T_MutableOrthogonalSliceWindow[
                QWidget,
                QLabel,
                T_MutableSliceCanvas[
                    QGraphicsView,
                    QPointF,
                    QRectF,
                    QGraphicsPixmapItem,
                    QGraphicsPathItem,
                    QGraphicsPolygonItem,
                    T_MutableVertexHandle[QGraphicsEllipseItem],
                    SignalInstance,
                ],
                QSpinBox,
                SignalInstance,
            ],
            T_MutableAnnotationIndexSpinBox[QAbstractSpinBox, SignalInstance],
            T_MutableMaskCoverageBar[QWidget, QSlider],
            T_MutableVolumeLoadThread[QThread, SignalInstance],
            T_MutableExternalMaskLoadThread[QThread, SignalInstance],
            QPointF,
        ],
    ) -> None:
        has_volume = (
            context.getVolume() is not None and context.getProject() is not None
        )
        external = context.getExternalPreviewActive()
        context.getUnloadImageButton().setEnabled(
            has_volume
            and context.getLoadThread() is None
            and context.getExternalMaskThread() is None
            and not context.getInternalClosingPolygon()
            and not context.getInternalSwitchingAnnotation()
        )
        for control in context.iterEditingControls():
            control.setEnabled(has_volume and (not context.getReadOnly()))
        for shortcut in context.iterEditingShortcuts():
            shortcut.setEnabled(has_volume and (not context.getReadOnly()))
        context.getShowInterpolation().setEnabled(
            has_volume and (not context.getReadOnly())
        )
        context.getAnnotationIndexSpin().getHost().setEnabled(
            has_volume and (not context.getReadOnly())
        )
        context.getModeGroup().setEnabled(has_volume and (not external))
        context.getNextIncompleteButton().setEnabled(has_volume and (not external))
        context.getReviewProgress().setEnabled(has_volume and (not external))
        context.getPreviousLabeledButton().setEnabled(not external)
        context.getNextLabeledButton().setEnabled(not external)
        for widget in (
            context.getFileButton(),
            context.getDicomButton(),
            context.getLoadButton(),
            context.getSourceList(),
            context.getSpacingSpin(),
        ):
            widget.setEnabled(not external)
        for action in context.getAnnotationToolbar().actions():
            action.setEnabled(has_volume and (not external))
        context.getLoadExternalMaskButton().setEnabled(not external)
        context.getUnloadExternalMaskButton().setEnabled(
            context.getExternalMask() is not None
        )
        context.getObservationStatus().setVisible(context.getReadOnly())
        context.getHintLabel().setText(context._text(context._hint_key()))

    # 按需创建 PS、SL 非模态窗口，避免重复打开同一截面。
    def ensure_observation_windows(
        self,
        context: T_MutableAnnotationMainWindow[
            QMainWindow,
            QTimer,
            QToolBar,
            QAction,
            QLabel,
            QPushButton,
            QComboBox,
            QSplitter,
            QListWidget,
            QDoubleSpinBox,
            QSlider,
            QSpinBox,
            QGroupBox,
            QRadioButton,
            QCheckBox,
            QProgressBar,
            QProgressDialog,
            QShortcut,
            QWidget,
            QButtonGroup,
            T_MutableSliceCanvas[
                QGraphicsView,
                QPointF,
                QRectF,
                QGraphicsPixmapItem,
                QGraphicsPathItem,
                QGraphicsPolygonItem,
                T_MutableVertexHandle[QGraphicsEllipseItem],
                SignalInstance,
            ],
            T_MutableOrthogonalSliceWindow[
                QWidget,
                QLabel,
                T_MutableSliceCanvas[
                    QGraphicsView,
                    QPointF,
                    QRectF,
                    QGraphicsPixmapItem,
                    QGraphicsPathItem,
                    QGraphicsPolygonItem,
                    T_MutableVertexHandle[QGraphicsEllipseItem],
                    SignalInstance,
                ],
                QSpinBox,
                SignalInstance,
            ],
            T_MutableAnnotationIndexSpinBox[QAbstractSpinBox, SignalInstance],
            T_MutableMaskCoverageBar[QWidget, QSlider],
            T_MutableVolumeLoadThread[QThread, SignalInstance],
            T_MutableExternalMaskLoadThread[QThread, SignalInstance],
            QPointF,
        ],
    ) -> None:
        from ...Algorithms.Observation.C_ObservationPlanes import C_ObservationPlanes
        from ..Observation.C_Qt_OrthogonalSliceWindow import C_Qt_OrthogonalSliceWindow

        for name in ("PS", "SL"):
            if name in {
                _entry_index: context.getObservationWindow(_entry_index)
                for _entry_index in context.iterObservationWindowNames()
            }:
                continue
            view = C_Qt_OrthogonalSliceWindow(
                context.getHost(), C_ObservationPlanes().getPlanes().getByName(name)
            )
            view.getCanvas().getPositionClicked().connect(
                lambda point, name=name: context._observation_clicked(name, point)
            )
            view.getSliceSpin().valueChanged.connect(
                lambda index, name=name: context._set_observation_axis(name, index)
            )
            context.setObservationWindow(name, view)
            screen = context.getHost().screen().availableGeometry()
            width = min(560, screen.width() // 2)
            height = min(540, screen.height() // 2)
            view.resize(width, height)
            view.move(
                screen.right() - width, screen.top() + (0 if name == "PS" else height)
            )
