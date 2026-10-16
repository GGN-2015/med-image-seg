from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Generic, TypeVar

T_Window = TypeVar("T_Window")
T_Button = TypeVar("T_Button")


# 构造有多段标注的项目，供前后标注层导航测试使用。
class T_LabeledNavigationFixtures(ABC, Generic[T_Window, T_Button]):
    # 生成可复现的标注样本，供多个测试场景使用。
    @abstractmethod
    def seed(self, window: T_Window, indices: Iterable[int]) -> None: ...

    # 创建按钮并连接点击回调，统一布局服务的控件装配。
    @abstractmethod
    def button(self, window: T_Window, direction: int) -> T_Button: ...
