from __future__ import annotations

from abc import ABC, abstractmethod


# 生成架构说明文本，记录分层、集合封装和依赖边界约束。
class I_ArchitectureGuide(ABC):
    # 返回架构说明的 Markdown 文本，供文档生成或展示使用。
    @abstractmethod
    def getMarkdown(self) -> str: ...
