from __future__ import annotations

from collections.abc import Iterable
from typing import final

from ....Abstract.Domain.Collections.I_MutableImageCollection import (
    I_MutableImageCollection,
)
from ....Abstract.Domain.Imaging.I_ImageSource import I_ImageSource
from ....Abstract.Storage.Paths.I_FilePath import I_FilePath


# 按指纹去重并保留导入顺序，通过数量、索引和指纹查询影像。
@final
class C_ImageCollection(I_MutableImageCollection):
    # 建立按顺序存储和按指纹查询的索引，再逐项导入去重。
    def __init__(
        self, sources: Iterable[str | I_FilePath | I_ImageSource] = ()
    ) -> None:
        self._sources: list[I_ImageSource] = []
        self._by_fingerprint: dict[str, I_ImageSource] = {}
        self.extend(sources)

    # 返回按指纹去重后的影像数量。
    def getCount(self) -> int:
        return len(self._sources)

    # 按导入顺序查询指定索引的影像源，不暴露内部列表。
    def getSource(self, index: int) -> I_ImageSource:
        return self._sources[index]

    # 按指纹查询已导入影像，不存在时返回空值。
    def findByFingerprint(self, fingerprint: str) -> I_ImageSource | None:
        return self._by_fingerprint.get(fingerprint)

    # 按指纹添加影像；重复来源复用已有项，首次导入保持顺序。
    def add(self, source: str | I_FilePath | I_ImageSource) -> I_ImageSource:
        from ....Abstract.Domain.Imaging.I_ImageSource import I_ImageSource
        from ...Storage.Volumes.C_ImageSourceFactory import C_ImageSourceFactory

        item = (
            source
            if isinstance(source, I_ImageSource)
            else C_ImageSourceFactory().from_path(source)
        )
        existing = self.findByFingerprint(item.getFingerprint())
        if existing is not None:
            return existing
        self._sources.append(item)
        self._by_fingerprint[item.getFingerprint()] = item
        return item

    # 逐项导入并去重，保持新增影像的首次出现顺序。
    def extend(self, sources: Iterable[str | I_FilePath | I_ImageSource]) -> None:
        for source in sources:
            self.add(source)
