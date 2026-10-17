from typing import final

import numpy as np
from numpy.typing import NDArray

from ....Abstract.Application.Tasks.T_Task import T_Task
from ....Abstract.Domain.Annotations.I_MutableAnnotationProject import (
    I_MutableAnnotationProject,
)


# 后台计算逐层前景存在性，避免跨层插值使进度窗口停止刷新。
@final
class C_MaskPresenceTask(T_Task[NDArray[np.bool_]]):
    # 持有编辑锁保护的项目，不复制或更改其插值规则。
    def __init__(self, project: I_MutableAnnotationProject) -> None:
        self._project = project

    # 复用原有区间算法，包含插值层并保留强制空层产生的断点。
    def execute(self) -> NDArray[np.bool_]:
        return self._project.mask_presence()
