from __future__ import annotations

from typing import TYPE_CHECKING

from ...Storage.Paths.I_FilePath import I_FilePath
from ..Annotations.I_Record import I_Record
from ..Records.I_RecordFieldList import I_RecordFieldList
from .E_SourceKind import E_SourceKind

if TYPE_CHECKING:
    from ...Storage.Paths.I_FilePath import I_FilePath
    from .E_SourceKind import E_SourceKind
from abc import abstractmethod


# 描述影像来源及配套文件路径，用指纹关联影像与标注项目。
class I_ImageSource(I_Record):
    # 返回影像输入路径。
    @abstractmethod
    def getPath(self) -> I_FilePath: ...

    # 返回影像的 DICOM、NIfTI 或 UBD 格式类别。
    @abstractmethod
    def getKind(self) -> E_SourceKind: ...

    # 返回影像来源标识。
    @abstractmethod
    def getSourceId(self) -> str: ...

    # 返回不包含标注输出文件的影像指纹。
    @abstractmethod
    def getFingerprint(self) -> str: ...

    # 返回影像旁的默认标注路径。
    @abstractmethod
    def getAnnotationPath(self) -> I_FilePath: ...

    # 返回NIfTI 掩码输出路径。
    @abstractmethod
    def getMaskPath(self) -> I_FilePath: ...

    # 返回有序的记录字段名，供序列化读取。
    @abstractmethod
    def getRecordFields(self) -> I_RecordFieldList: ...

    # 返回UBD 掩码输出路径。
    @abstractmethod
    def getUbdMaskPath(self) -> I_FilePath: ...

    # 按编号生成标注路径：0 号保留原名，其余使用数字后缀。
    @abstractmethod
    def annotation_path_for_index(self, index: int) -> I_FilePath: ...

    # 返回可区分短文件名的列表名称，长度判断包含扩展名。
    @abstractmethod
    def getDisplayName(self) -> str: ...
