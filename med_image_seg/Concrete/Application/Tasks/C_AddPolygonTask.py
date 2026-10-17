from typing import final

from ....Abstract.Application.Tasks.T_Task import T_Task
from ....Abstract.Domain.Annotations.I_MutableAnnotationProject import (
    I_MutableAnnotationProject,
)
from ....Abstract.Domain.Annotations.I_PolygonAnnotation import I_PolygonAnnotation


# 把轮廓加入项目的数据操作独立成任务，避免闭合时在界面线程修改大型项目。
@final
class C_AddPolygonTask(T_Task[None]):
    # 固定当前项目、层号和只读轮廓，执行期间不读取窗口状态。
    def __init__(
        self,
        project: I_MutableAnnotationProject,
        slice_index: int,
        polygon: I_PolygonAnnotation,
    ) -> None:
        self._project = project
        self._slice_index = slice_index
        self._polygon = polygon

    # 沿用项目原有的轮廓添加与编辑序号规则。
    def execute(self) -> None:
        self._project.add_polygon(self._slice_index, self._polygon)
