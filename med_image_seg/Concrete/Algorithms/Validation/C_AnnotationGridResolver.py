from __future__ import annotations

from typing import TYPE_CHECKING

from ....Abstract.Algorithms.Validation.I_AnnotationGridResolver import (
    I_AnnotationGridResolver,
)

if TYPE_CHECKING:
    from ....Abstract.Domain.Imaging.I_ImageSource import I_ImageSource
import math
from typing import final


# 从同影像的已有标注恢复加载网格，防止当前界面间距使轮廓坐标与 CT 体素错位。
@final
class C_AnnotationGridResolver(I_AnnotationGridResolver):
    # 仅信任指纹相同且三轴等距的标注；其他情况继续使用用户请求的间距。
    def resolve(
        self, source: I_ImageSource, annotation_index: int, requested_spacing_mm: float
    ) -> float:
        from ...Storage.Paths.C_FilePath import C_FilePath
        from ...Storage.Projects.C_ProjectRepository import C_ProjectRepository

        path = source.annotation_path_for_index(annotation_index)
        if not path.is_file() and not C_FilePath(f"{path}.bak").is_file():
            return requested_spacing_mm
        try:
            project = C_ProjectRepository().load(path)
        except (OSError, KeyError, TypeError, ValueError):
            return requested_spacing_mm
        if project.getSourceFingerprint() != source.getFingerprint():
            return requested_spacing_mm
        spacing = project.getSpacingLpsMm()
        if (
            spacing[0] <= 0
            or not math.isfinite(spacing[0])
            or not all(
                math.isclose(value, spacing[0], rel_tol=1e-6, abs_tol=1e-6)
                for value in spacing[1:]
            )
        ):
            return requested_spacing_mm
        return spacing[0]
