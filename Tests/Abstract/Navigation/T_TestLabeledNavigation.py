from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Generic, TypeVar

T_Window = TypeVar("T_Window")
T_MonkeyPatch = TypeVar("T_MonkeyPatch")


# 验证前后有标注层跳转、边界提示及只读模式下的联动。
class T_TestLabeledNavigation(ABC, Generic[T_Window, T_MonkeyPatch]):
    # 验证前后标注层按钮位于切层按钮下方，且不破坏区间条对齐。
    @abstractmethod
    def test_labeled_buttons_sit_below_existing_buttons_without_misaligning_coverage(
        self, window: T_Window
    ) -> None: ...

    # 验证导航找到最近的前后轮廓层，且不把当前层算作目标。
    @abstractmethod
    def test_buttons_jump_to_nearest_strictly_earlier_or_later_polygon_slice(
        self, window: T_Window, current: int, direction: int, expected: int
    ) -> None: ...

    # 验证有标注层导航跳过仅插值层、空关键层及空复核层。
    @abstractmethod
    def test_interpolation_and_empty_keyframe_or_review_slices_are_skipped(
        self, window: T_Window, direction: int, expected: int
    ) -> None: ...

    # 验证强制空层上的已存轮廓仍计入有标注层导航。
    @abstractmethod
    def test_any_stored_polygon_counts_even_on_forced_empty_slice(
        self, window: T_Window, source: str, operation: str
    ) -> None: ...

    # 验证找不到前后目标时提示方向正确，且不回绕或移动当前层。
    @abstractmethod
    def test_missing_target_shows_directional_message_without_wrapping_or_moving(
        self,
        window: T_Window,
        monkeypatch: T_MonkeyPatch,
        direction: int,
        labels: Iterable[int],
    ) -> None: ...

    # 验证找不到目标标注层时显示真正的模态提示框。
    @abstractmethod
    def test_missing_target_dialog_is_actually_modal(
        self, window: T_Window, direction: int
    ) -> None: ...

    # 验证有标注层导航只查询当前编号项目。
    @abstractmethod
    def test_number_switch_limits_navigation_to_active_annotation(
        self, window: T_Window
    ) -> None: ...

    # 验证观察模式也可导航标注层，并同步三视图参考线。
    @abstractmethod
    def test_labeled_navigation_works_in_observation_and_updates_cross_references(
        self, window: T_Window, monkeypatch: T_MonkeyPatch
    ) -> None: ...

    # 验证未载入影像或软件忙碌时不可跳转有标注层。
    @abstractmethod
    def test_labeled_navigation_is_unavailable_without_image_or_while_busy(
        self, window: T_Window, monkeypatch: T_MonkeyPatch
    ) -> None: ...
