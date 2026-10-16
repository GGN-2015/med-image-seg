from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...Domain.Annotations.I_MutableAnnotationProject import (
        I_MutableAnnotationProject,
    )
from abc import ABC, abstractmethod

import numpy as np
from numpy.typing import NDArray


# 按来源分别合成轮廓掩码，依次应用添加与擦除后取并集。
class I_ManualPlaneAlgorithm(ABC):
    # 按存储顺序分别合成人工与机器轮廓，再取两者并集。
    @abstractmethod
    def manual_plane(
        self, context: I_MutableAnnotationProject, slice_index: int
    ) -> NDArray[np.bool_]: ...
