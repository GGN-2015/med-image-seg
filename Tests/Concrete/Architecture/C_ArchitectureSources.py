from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import final

from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath

from ...Abstract.Architecture.I_ArchitectureSources import I_ArchitectureSources


# 遍历包、测试和文档源码，排除缓存后供架构规则检查使用。
@final
class C_ArchitectureSources(I_ArchitectureSources):
    # 遍历包、测试和文档的 Python 源码，跳过缓存目录。
    def iterFiles(self) -> Iterator[I_FilePath]:
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath

        root = Path(__file__).resolve().parents[3]
        for name in ("med_image_seg", "Tests", "Docs"):
            for path in (root / name).rglob("*.py"):
                if "__pycache__" not in path.parts:
                    yield C_FilePath(path)
