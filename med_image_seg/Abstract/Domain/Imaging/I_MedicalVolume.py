from __future__ import annotations

from typing import TYPE_CHECKING

from ...Storage.Paths.I_FilePath import I_FilePath
from ..Annotations.I_Record import I_Record
from ..Records.I_RecordFieldList import I_RecordFieldList
from .I_Metadata import I_Metadata

if TYPE_CHECKING:
    from ...Storage.Paths.I_FilePath import I_FilePath
    from .I_Metadata import I_Metadata
from abc import abstractmethod

import numpy as np
from numpy.typing import NDArray


# 保存 LPS 网格中的体素及物理几何，供显示、标注和导出共用。
class I_MedicalVolume(I_Record):
    # 返回 LPS 顺序的体素数组。
    @abstractmethod
    def getData(self) -> NDArray[np.float32]: ...

    # 返回 LPS 网格间距，单位为毫米。
    @abstractmethod
    def getSpacingMm(self) -> tuple[float, float, float]: ...

    # 返回 LPS 物理原点，单位为毫米。
    @abstractmethod
    def getOriginLpsMm(self) -> tuple[float, float, float]: ...

    # 返回影像元数据的只读快照。
    @abstractmethod
    def getMetadata(self) -> I_Metadata: ...

    # 返回原始影像的输入路径。
    @abstractmethod
    def getSource(self) -> I_FilePath: ...

    # 返回有序的记录字段名，供序列化读取。
    @abstractmethod
    def getRecordFields(self) -> I_RecordFieldList: ...
