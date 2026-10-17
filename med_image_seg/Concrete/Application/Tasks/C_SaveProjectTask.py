from typing import final

from ....Abstract.Application.Tasks.T_Task import T_Task
from ....Abstract.Domain.Annotations.I_MutableAnnotationProject import (
    I_MutableAnnotationProject,
)
from ....Abstract.Storage.Paths.I_FilePath import I_FilePath


# 封装已有项目保存逻辑，使闭合期间的 JSON 编码与磁盘写入可在后台完成。
@final
class C_SaveProjectTask(T_Task[I_FilePath]):
    # 记录目标路径与空文件策略，不把界面提示或控件传给后台线程。
    def __init__(
        self,
        project: I_MutableAnnotationProject,
        path: I_FilePath,
        *,
        delete_if_empty: bool = False,
    ) -> None:
        self._project = project
        self._path = path
        self._delete_if_empty = delete_if_empty

    # 保留零号实时落盘和非零号空标注删除规则，以及既有文件格式和备份。
    def execute(self) -> I_FilePath:
        if self._delete_if_empty:
            return self._project.save(self._path, delete_if_empty=True)
        return self._project.save(self._path)
