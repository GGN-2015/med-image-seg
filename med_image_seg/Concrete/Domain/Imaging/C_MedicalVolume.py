from __future__ import annotations

from typing import TYPE_CHECKING

from ....Abstract.Domain.Imaging.I_MedicalVolume import I_MedicalVolume
from ....Abstract.Domain.Imaging.I_Metadata import I_Metadata
from ....Abstract.Domain.Records.I_RecordFieldList import I_RecordFieldList
from ....Abstract.Storage.Paths.I_FilePath import I_FilePath

if TYPE_CHECKING:
    from ....Abstract.Domain.Imaging.I_Metadata import I_Metadata
    from ....Abstract.Storage.Paths.I_FilePath import I_FilePath
from dataclasses import dataclass
from typing import final

import numpy as np
from numpy.typing import NDArray


# 保存 LPS 网格中的体素及物理几何，供显示、标注和导出共用。
@final
@dataclass(slots=True, frozen=True, init=False)
class C_MedicalVolume(I_MedicalVolume):
    _state_data: NDArray[np.float32]
    _state_spacing_mm: tuple[float, float, float]
    _state_origin_lps_mm: tuple[float, float, float]
    _state_metadata: I_Metadata
    _state_source: I_FilePath

    # 保存 LPS 体素、间距、原点和影像来源信息。
    def __init__(
        self,
        data: NDArray[np.float32],
        spacing_mm: tuple[float, float, float],
        origin_lps_mm: tuple[float, float, float],
        metadata: I_Metadata,
        source: I_FilePath,
    ) -> None:
        from ...Numerics.Arrays.C_ArrayFactory import C_ArrayFactory
        from ...Storage.Paths.C_FilePath import C_FilePath

        object.__setattr__(self, "_state_data", C_ArrayFactory().wrap(data))
        object.__setattr__(self, "_state_spacing_mm", spacing_mm)
        object.__setattr__(self, "_state_origin_lps_mm", origin_lps_mm)
        object.__setattr__(self, "_state_metadata", metadata)
        object.__setattr__(self, "_state_source", C_FilePath(source))

    # 返回 LPS 顺序的体素数组。
    def getData(self) -> NDArray[np.float32]:
        return self._state_data

    # 返回 LPS 网格间距，单位为毫米。
    def getSpacingMm(self) -> tuple[float, float, float]:
        return self._state_spacing_mm

    # 返回 LPS 物理原点，单位为毫米。
    def getOriginLpsMm(self) -> tuple[float, float, float]:
        return self._state_origin_lps_mm

    # 返回影像元数据的只读快照。
    def getMetadata(self) -> I_Metadata:
        return self._state_metadata

    # 返回原始影像的输入路径。
    def getSource(self) -> I_FilePath:
        return self._state_source

    # 返回有序的记录字段名，供序列化读取。
    def getRecordFields(self) -> I_RecordFieldList:
        from ..Records.C_RecordFieldList import C_RecordFieldList

        return C_RecordFieldList(
            ("data", "spacing_mm", "origin_lps_mm", "metadata", "source")
        )
