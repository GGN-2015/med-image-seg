from __future__ import annotations

from abc import ABC, abstractmethod


# 维护中英文本及语言回退规则，让业务代码通过消息键取得文案。
class I_Localizer(ABC):
    # 返回可选的中英语言代码。
    @abstractmethod
    def getSupportedLanguages(self) -> tuple[str, ...]: ...

    # 规范中英语言代码，不支持的值按既定规则回退。
    @abstractmethod
    def normalize_language(self, language: str) -> str: ...

    # 按消息键选择中英文案，缺省时回退并填入动态参数。
    @abstractmethod
    def translate(
        self, key: str, language: str = "en", **values: str | int | float
    ) -> str: ...
