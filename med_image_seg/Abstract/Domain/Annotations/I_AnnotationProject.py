from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

from ..Imaging.I_MedicalVolume import I_MedicalVolume
from ..Imaging.I_Metadata import I_Metadata
from ..Records.I_RecordFieldList import I_RecordFieldList
from .I_Record import I_Record
from .I_SliceAnnotation import I_SliceAnnotation

if TYPE_CHECKING:
    from ..Imaging.I_MedicalVolume import I_MedicalVolume
    from ..Imaging.I_Metadata import I_Metadata
    from .I_SliceAnnotation import I_SliceAnnotation
from abc import abstractmethod
from typing import final

import numpy as np
from numpy.typing import NDArray


# 管理各层轮廓、复核和插值状态，生成与影像网格对应的三维掩码。
class I_AnnotationProject(I_Record):
    # 返回标注所属的影像标识。
    @abstractmethod
    def getImageId(self) -> str: ...

    # 返回项目绑定的影像指纹。
    @abstractmethod
    def getSourceFingerprint(self) -> str: ...

    # 返回 L、P、S 三轴的体素数量。
    @abstractmethod
    def getShapeLps(self) -> tuple[int, int, int]: ...

    # 返回 L、P、S 三轴的网格间距，单位为毫米。
    @abstractmethod
    def getSpacingLpsMm(self) -> tuple[float, float, float]: ...

    # 返回 LPS 物理原点，单位为毫米。
    @abstractmethod
    def getOriginLpsMm(self) -> tuple[float, float, float]: ...

    # 返回影像元数据的只读快照。
    @abstractmethod
    def getMetadata(self) -> I_Metadata: ...

    # 返回项目级编辑序号计数器。
    @abstractmethod
    def getEditCounter(self) -> int: ...

    # 返回标注 JSON 的格式版本。
    @abstractmethod
    def getSchemaVersion(self) -> int: ...

    # 返回项目最近一次保存时间。
    @abstractmethod
    def getUpdatedAt(self) -> str: ...

    # 返回有序的记录字段名，供序列化读取。
    @abstractmethod
    def getRecordFields(self) -> I_RecordFieldList: ...

    # 核对标注与影像的体素尺寸、间距和原点，拒绝几何不一致。
    @abstractmethod
    def validate_volume(self, volume: I_MedicalVolume) -> None: ...

    # 统计已经复核的切片数量。
    @abstractmethod
    def getCompletedCount(self) -> int: ...

    # 检查项目是否存有轮廓，不以最终前景体素数量判断。
    @abstractmethod
    def getHasPolygons(self) -> bool: ...

    # 按层号顺序提供插值关键层，包括显式空边界层。
    @abstractmethod
    def getKeyframeIndices(self) -> tuple[int, ...]: ...

    # 统计处于有效关键层插值范围内的切片数量。
    @abstractmethod
    def getInterpolatedSliceCount(self) -> int: ...

    # 查询当前层两侧的插值关键层，遇到显式状态时不跨越其边界。
    @abstractmethod
    def interpolation_bounds(self, slice_index: int) -> tuple[int, int] | None: ...

    # 在相邻关键层距离场之间插值，显式标注或边界层不使用自动结果。
    @abstractmethod
    def interpolated_plane(self, slice_index: int) -> NDArray[np.bool_] | None: ...

    # 计算各层是否实际含前景，保留强制空层造成的间断并避免分配完整体积。
    @abstractmethod
    def mask_presence(self, *, interpolate: bool = True) -> NDArray[np.bool_]: ...

    # 生成 LPS 三维二值掩码，按参数选择是否填入关键层之间的插值。
    @abstractmethod
    def to_mask(self, *, interpolate: bool = True) -> NDArray[np.uint8]: ...

    # 返回指定层轮廓合成的二值结果，不填入自动插值。
    @abstractmethod
    def getManualPlane(self, slice_index: int) -> NDArray[np.bool_]: ...

    # 返回指定二值切片的有符号距离场，供插值计算使用。
    @abstractmethod
    def getSignedDistance(self, plane: NDArray[np.bool_]) -> NDArray[np.float32]: ...

    # 返回保存了显式状态的层记录数量，而不是影像总层数。
    @abstractmethod
    def getSliceCount(self) -> int: ...

    # 查询已存在的层标注，不创建新层且不暴露内部字典。
    @abstractmethod
    def findSlice(self, index: int) -> I_SliceAnnotation | None: ...

    # 遍历已保存标注状态的层号，不为未标注层创建记录。
    @abstractmethod
    def iterSliceIndices(self) -> Iterator[int]: ...

    # 按层号取得已有标注，缺失时报错而不是创建新层。
    @final
    def getSlice(self, index: int) -> I_SliceAnnotation:
        value = self.findSlice(index)
        if value is None:
            raise KeyError(index)
        return value
