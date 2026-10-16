from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T_Context = TypeVar("T_Context")


# 构建控件、绑定快捷键并切换界面文案，集中管理 Qt 布局。
class T_LayoutService(ABC, Generic[T_Context]):
    # 构建影像列表、主画布和右侧编辑面板，登记供状态切换使用的控件。
    @abstractmethod
    def build_ui(self, context: T_Context, spacing_mm: float) -> None: ...

    # 根据当前语言更新标题、按钮、状态及操作提示文本。
    @abstractmethod
    def retranslate_ui(self, context: T_Context) -> None: ...

    # 把编辑和切片导航快捷键连接到对应动作，并登记可禁用项。
    @abstractmethod
    def bind_shortcuts(self, context: T_Context) -> None: ...

    # 按影像集合顺序重建列表，并保留来源对象与列表项的关联。
    @abstractmethod
    def refresh_source_list(self, context: T_Context) -> None: ...

    # 根据编辑、观察或外置预览状态启用相应控件和快捷键。
    @abstractmethod
    def apply_mode_ui(self, context: T_Context) -> None: ...

    # 按需创建 PS、SL 非模态窗口，避免重复打开同一截面。
    @abstractmethod
    def ensure_observation_windows(self, context: T_Context) -> None: ...
