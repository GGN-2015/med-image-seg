from abc import ABC, abstractmethod
from collections.abc import Iterator

from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath


# 遍历包、测试和文档源码，排除缓存后供架构规则检查使用。
class I_ArchitectureSources(ABC):
    # 遍历包、测试和文档的 Python 源码，跳过缓存目录。
    @abstractmethod
    def iterFiles(self) -> Iterator[I_FilePath]: ...
