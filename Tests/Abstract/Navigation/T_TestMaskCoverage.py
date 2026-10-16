from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath

T_MonkeyPatch = TypeVar("T_MonkeyPatch")


# 验证掩码区间条的显示、层号对齐和计算缓存。
class T_TestMaskCoverage(ABC, Generic[T_MonkeyPatch]):
    # 改变窗口尺寸，逐层核对区间条中心与原生滑块位置一致。
    @abstractmethod
    def test_coverage_centers_match_native_slider_for_every_slice_after_resize(
        self, style_name: str, depth: int, rtl: bool, inverted: bool
    ) -> None: ...

    # 验证分段区间正确着色，点击区间条不会改变切片滑块。
    @abstractmethod
    def test_coverage_paints_separate_intervals_and_cannot_change_slider(
        self, inverted: bool
    ) -> None: ...

    # 逐次编辑、插值和强制空层，核验区间条及时反映实际掩码。
    @abstractmethod
    def test_window_coverage_tracks_edits_interpolation_and_forced_empty_slices(
        self, tmp_path: I_FilePath, monkeypatch: T_MonkeyPatch
    ) -> None: ...

    # 验证切层和显示设置变化复用掩码存在性缓存。
    @abstractmethod
    def test_coverage_is_cached_during_navigation_and_preview_changes(
        self, tmp_path: I_FilePath, monkeypatch: T_MonkeyPatch
    ) -> None: ...

    # 验证载入 JSON 后直接生成区间条，不分配完整三维掩码。
    @abstractmethod
    def test_loaded_annotation_populates_coverage_without_allocating_full_mask(
        self, tmp_path: I_FilePath, monkeypatch: T_MonkeyPatch
    ) -> None: ...
