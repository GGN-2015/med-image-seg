from __future__ import annotations

from collections.abc import Iterable
from itertools import pairwise
from typing import final

from PySide6.QtCore import QEvent, QObject, QPoint, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPaintEvent
from PySide6.QtWidgets import QSlider, QStyle, QStyleOptionSlider, QWidget

from ....Abstract.Presentation.Navigation.T_MutableMaskCoverageBar import (
    T_MutableMaskCoverageBar,
)
from ..Metaclasses.C_Qt_AbcMeta import C_Qt_AbcMeta


# 按滑块几何绘制掩码区间，保证绿色层位置与切片编号对齐且不可拖动。
@final
class C_Qt_MaskCoverageBar(
    QWidget, T_MutableMaskCoverageBar[QWidget, QSlider], metaclass=C_Qt_AbcMeta
):
    # 返回区间条对齐所参照的切片滑块。
    def getInternalSlider(self) -> QSlider:
        return self._state_slider

    # 记录区间条对齐所参照的切片滑块。
    def setInternalSlider(self, value: QSlider) -> None:
        self._state_slider = value

    # 返回逐层掩码存在性快照。
    def getInternalPresence(self) -> tuple[bool, ...]:
        return self._state_presence

    # 复制逐层存在性数据，防止外部容器变化影响区间绘制。
    def setInternalPresence(self, value: tuple[bool, ...]) -> None:
        self._state_presence = value

    # 关联切片滑块并监听几何变化，使区间绘制与原生滑块对齐。
    def __init__(self, slider: QSlider) -> None:
        super().__init__()
        self.setInternalSlider(slider)
        self.setInternalPresence(())
        self.setFixedHeight(10)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        slider.installEventFilter(self)

    # 返回逐层前景存在性快照，保留分离区间和孤立层。
    def getPresence(self) -> tuple[bool, ...]:
        return self.getInternalPresence()

    # 复制逐层掩码存在性数据并请求重绘区间条。
    def set_presence(self, presence: Iterable[bool]) -> None:
        self.setInternalPresence(tuple(bool(value) for value in presence))
        self.update()

    # 使用原生滑块的槽和滑块宽度计算每层中心，保证区间条逐层对齐。
    def slice_centers(self) -> tuple[int, ...]:
        option = QStyleOptionSlider()
        self.getInternalSlider().initStyleOption(option)
        offset = self.mapFromGlobal(
            self.getInternalSlider().mapToGlobal(QPoint(0, 0))
        ).x()
        centers: list[int] = []
        for index in range(
            self.getInternalSlider().minimum(), self.getInternalSlider().maximum() + 1
        ):
            option.sliderPosition = index
            option.sliderValue = index
            handle = (
                self.getInternalSlider()
                .style()
                .subControlRect(
                    QStyle.ComplexControl.CC_Slider,
                    option,
                    QStyle.SubControl.SC_SliderHandle,
                    self.getInternalSlider(),
                )
            )
            centers.append(offset + handle.center().x())
        return tuple(centers)

    # 响应关联控件的几何或样式变化，更新依赖其位置的界面显示。
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self.getInternalSlider() and event.type() in (
            QEvent.Type.Resize,
            QEvent.Type.StyleChange,
            QEvent.Type.LayoutDirectionChange,
            QEvent.Type.Paint,
        ):
            self.update()
        return super().eventFilter(watched, event)

    # 按原生滑块的层中心绘制绿色掩码区间和灰色空白区间。
    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#c7ccd2"))
        if not self.getInternalPresence():
            return
        centers = self.slice_centers()
        if len(centers) != len(self.getInternalPresence()):
            return
        cells = sorted(zip(centers, self.getInternalPresence(), strict=True))
        boundaries = [0.0]
        boundaries.extend(((left[0] + right[0]) / 2 for left, right in pairwise(cells)))
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

    # 返回底层界面宿主。
    def getHost(self) -> QWidget:
        return self
