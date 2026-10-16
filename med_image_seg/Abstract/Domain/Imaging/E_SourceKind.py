from __future__ import annotations

from enum import StrEnum


# 列举受支持的影像格式，替代散落在业务代码中的格式字符串。
class E_SourceKind(StrEnum):
    DICOM = "dicom"
    NIFTI = "nifti"
    UBD = "ubd"
