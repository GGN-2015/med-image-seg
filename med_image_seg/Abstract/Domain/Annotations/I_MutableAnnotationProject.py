from __future__ import annotations

from typing import TYPE_CHECKING

from ...Storage.Paths.I_FilePath import I_FilePath
from ..Geometry.I_PointList import I_PointList
from ..Imaging.I_Metadata import I_Metadata
from .I_AnnotationProject import I_AnnotationProject
from .I_MutableSliceAnnotation import I_MutableSliceAnnotation
from .I_PolygonAnnotation import I_PolygonAnnotation

if TYPE_CHECKING:
    from ...Storage.Paths.I_FilePath import I_FilePath
    from ..Imaging.I_Metadata import I_Metadata
    from .I_MutableSliceAnnotation import I_MutableSliceAnnotation
    from .I_PolygonAnnotation import I_PolygonAnnotation
from abc import abstractmethod


# 在只读项目上增加轮廓编辑、复核和插值状态修改，集中管理写盘所需数据。
class I_MutableAnnotationProject(I_AnnotationProject):
    # 记录标注所属的影像标识。
    @abstractmethod
    def setImageId(self, value: str) -> None: ...

    # 记录项目绑定的影像指纹。
    @abstractmethod
    def setSourceFingerprint(self, value: str) -> None: ...

    # 记录L、P、S 三轴的体素数量。
    @abstractmethod
    def setShapeLps(self, value: tuple[int, int, int]) -> None: ...

    # 记录L、P、S 三轴的网格间距，单位为毫米。
    @abstractmethod
    def setSpacingLpsMm(self, value: tuple[float, float, float]) -> None: ...

    # 记录LPS 物理原点，单位为毫米。
    @abstractmethod
    def setOriginLpsMm(self, value: tuple[float, float, float]) -> None: ...

    # 记录影像元数据的只读快照。
    @abstractmethod
    def setMetadata(self, value: I_Metadata) -> None: ...

    # 记录项目级编辑序号计数器。
    @abstractmethod
    def setEditCounter(self, value: int) -> None: ...

    # 记录标注 JSON 的格式版本。
    @abstractmethod
    def setSchemaVersion(self, value: int) -> None: ...

    # 记录项目最近一次保存时间。
    @abstractmethod
    def setUpdatedAt(self, value: str) -> None: ...

    # 取得指定层的可写标注；缺失时创建，越界时拒绝访问。
    @abstractmethod
    def annotation(self, slice_index: int) -> I_MutableSliceAnnotation: ...

    # 向指定层加入轮廓，清除强制空层标志并分配新的编辑序号。
    @abstractmethod
    def add_polygon(self, slice_index: int, polygon: I_PolygonAnnotation) -> None: ...

    # 更新指定轮廓坐标，清除强制空层标志并刷新其编辑顺序。
    @abstractmethod
    def replace_polygon(
        self, slice_index: int, polygon_index: int, points: I_PointList
    ) -> None: ...

    # 按编辑序号删除本层最近修改的轮廓，而非简单删除列表末项。
    @abstractmethod
    def delete_last_edited_polygon(
        self, slice_index: int
    ) -> I_PolygonAnnotation | None: ...

    # 复制源层轮廓并改为人工来源，清除目标层复核与强制空标志。
    @abstractmethod
    def copy_slice(self, source_index: int, target_index: int) -> None: ...

    # 设置指定层的复核标志；已复核的空层也作为插值关键边界。
    @abstractmethod
    def set_completed(self, slice_index: int, completed: bool) -> None: ...

    # 更新当前层强制空掩码状态，使它优先于轮廓和自动插值。
    @abstractmethod
    def set_force_empty(self, slice_index: int, force_empty: bool) -> None: ...

    # 设置指定层是否作为显式插值关键层。
    @abstractmethod
    def set_keyframe(self, slice_index: int, keyframe: bool) -> None: ...

    # 移除指定层的标注记录，使该层恢复未标注状态。
    @abstractmethod
    def clear_slice(self, slice_index: int) -> None: ...

    # 委托持久化算法保存项目，同时传递非零编号的空文件删除策略。
    @abstractmethod
    def save(
        self, path: str | I_FilePath, *, delete_if_empty: bool = False
    ) -> I_FilePath: ...

    # 查询已存在的层标注，不创建新层且不暴露内部字典。
    @abstractmethod
    def findSlice(self, index: int) -> I_MutableSliceAnnotation | None: ...
