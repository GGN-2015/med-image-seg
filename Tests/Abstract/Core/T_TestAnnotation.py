from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath

T_MonkeyPatch = TypeVar("T_MonkeyPatch")


# 验证轮廓合成、关键层插值、强制空层和项目持久化行为。
class T_TestAnnotation(ABC, Generic[T_MonkeyPatch]):
    # 验证删除操作针对最近编辑的轮廓，而不是列表最后一项。
    @abstractmethod
    def test_delete_targets_last_edited_polygon_not_last_list_item(self) -> None: ...

    # 验证原子保存与备份恢复，避免写盘中断破坏项目。
    @abstractmethod
    def test_save_is_atomic_and_recovers_from_backup(
        self, tmp_path: I_FilePath
    ) -> None: ...

    # 核验相邻人工关键层之间产生预期的掩码插值。
    @abstractmethod
    def test_interpolation_between_keyframes(self) -> None: ...

    # 验证强制空层优先于人工轮廓及自动插值结果。
    @abstractmethod
    def test_force_empty_overrides_polygons_and_interpolation(self) -> None: ...

    # 验证新增轮廓会清除该层的强制空掩码标志。
    @abstractmethod
    def test_adding_polygon_clears_force_empty(self) -> None: ...

    # 验证人工和机器轮廓以并集组合，保留原有来源语义。
    @abstractmethod
    def test_manual_and_prototype_sources_are_combined_as_a_union(self) -> None: ...

    # 往返保存和加载 JSON，核验强制空层标志保留。
    @abstractmethod
    def test_force_empty_round_trips_through_json(
        self, tmp_path: I_FilePath
    ) -> None: ...

    # 复核机器轮廓，验证来源仍为机器而不会改成人工。
    @abstractmethod
    def test_reviewing_machine_polygon_preserves_its_source(self) -> None: ...

    # 逐层比较存在性结果与完整导出掩码是否含前景。
    @abstractmethod
    def test_mask_presence_matches_exported_mask(
        self, seed: int, interpolate: bool
    ) -> None: ...

    # 核验不相交关键层之间可能为空的插值不会错误高亮。
    @abstractmethod
    def test_mask_presence_handles_disjoint_keyframes_with_empty_interpolation(
        self,
    ) -> None: ...

    # 验证轮廓全部擦除后，存在性区间可为空而标注记录仍保留。
    @abstractmethod
    def test_mask_presence_can_be_empty_despite_stored_contours(self) -> None: ...

    # 验证掩码存在性保留多个分离区间和孤立层。
    @abstractmethod
    def test_mask_presence_keeps_separate_intervals_and_isolated_slices(
        self,
    ) -> None: ...

    # 验证重叠关键层的存在性快速路径不计算距离场或分配完整体积。
    @abstractmethod
    def test_mask_presence_overlapping_keyframes_avoids_distance_and_volume_allocation(
        self, monkeypatch: T_MonkeyPatch
    ) -> None: ...

    # 验证复核等非轮廓状态不会阻止空编号文件删除。
    @abstractmethod
    def test_empty_project_removal_ignores_non_polygon_state(
        self, tmp_path: I_FilePath, state: str
    ) -> None: ...

    # 验证 0 号项目即使没有轮廓仍保留主文件和备份。
    @abstractmethod
    def test_default_save_keeps_empty_project_and_backup(
        self, tmp_path: I_FilePath
    ) -> None: ...

    # 验证空项目删除策略依据已存轮廓数量，而非最终前景体素数量。
    @abstractmethod
    def test_delete_if_empty_counts_stored_polygons_not_nonzero_mask(
        self, tmp_path: I_FilePath, operation: str, forced: bool
    ) -> None: ...

    # 验证删除从未保存的空项目不会创建多余目录。
    @abstractmethod
    def test_deleting_absent_empty_project_does_not_create_directories(
        self, tmp_path: I_FilePath
    ) -> None: ...

    # 验证备份删除失败时不会继续删除主标注文件。
    @abstractmethod
    def test_backup_removal_failure_does_not_delete_primary_annotation(
        self, tmp_path: I_FilePath, monkeypatch: T_MonkeyPatch
    ) -> None: ...
