from __future__ import annotations

from typing import TYPE_CHECKING

from ...Domain.Annotations.I_Record import I_Record
from ...Domain.Collections.I_ImageCollection import I_ImageCollection
from ...Domain.Records.I_RecordFieldList import I_RecordFieldList

if TYPE_CHECKING:
    from ...Domain.Collections.I_ImageCollection import I_ImageCollection
from abc import abstractmethod


# 应用启动配置：保存语言、标注间距和影像集合，不依赖界面框架。
class I_AnnotationApplication(I_Record):
    # 返回 LPS 网格间距，单位为毫米。
    @abstractmethod
    def getSpacingMm(self) -> float: ...

    # 返回当前中英界面语言代码。
    @abstractmethod
    def getLanguage(self) -> str: ...

    # 通过集合接口访问影像，支持按数量、索引和指纹查询。
    @abstractmethod
    def getSources(self) -> I_ImageCollection: ...

    # 返回有序的记录字段名，供序列化读取。
    @abstractmethod
    def getRecordFields(self) -> I_RecordFieldList: ...
