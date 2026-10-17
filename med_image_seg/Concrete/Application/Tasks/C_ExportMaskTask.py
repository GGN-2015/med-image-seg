from typing import final

from ....Abstract.Application.Projects.I_AnnotationExporter import I_AnnotationExporter
from ....Abstract.Application.Tasks.T_Task import T_Task
from ....Abstract.Domain.Annotations.I_AnnotationProject import I_AnnotationProject
from ....Abstract.Domain.Imaging.I_MedicalVolume import I_MedicalVolume
from ....Abstract.Storage.Paths.I_FilePath import I_FilePath


# 把三维掩码生成、压缩和写盘封装成纯数据任务，避免阻塞进度窗口。
@final
class C_ExportMaskTask(T_Task[I_FilePath]):
    # 只持有导出所需的领域契约，不向后台线程传递任何界面控件。
    def __init__(
        self,
        exporter: I_AnnotationExporter,
        project: I_AnnotationProject,
        volume: I_MedicalVolume,
        output: I_FilePath,
    ) -> None:
        self._exporter = exporter
        self._project = project
        self._volume = volume
        self._output = output

    # 委托既有导出逻辑，保留插值、物理几何及中文路径的处理规则。
    def execute(self) -> I_FilePath:
        return self._exporter.export(
            self._project, self._volume, self._output, interpolate=True
        )
