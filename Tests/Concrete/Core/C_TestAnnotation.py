from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from pytest import MonkeyPatch

from med_image_seg.Abstract.Domain.Annotations import (
    I_MutableAnnotationProject,
)

from ...Abstract.Core.T_TestAnnotation import T_TestAnnotation

if TYPE_CHECKING:
    from med_image_seg.Abstract.Domain.Imaging.I_MedicalVolume import I_MedicalVolume
    from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath
import json
from typing import final

import numpy as np
import pytest


# 验证轮廓合成、关键层插值、强制空层和项目持久化行为。
@final
class C_TestAnnotation(T_TestAnnotation[MonkeyPatch]):
    # 为当前测试类配置离屏 Qt 环境。
    @pytest.fixture(autouse=True, name="configure_environment")
    def _configure_environment_fixture(self) -> None:
        from ..Environment.C_TestEnvironment import C_TestEnvironment

        C_TestEnvironment().configure()

    # 构造与测试影像源对应的体素和几何信息。
    def _volume(self) -> I_MedicalVolume:
        from .C_AnnotationFixtures import C_AnnotationFixtures

        return C_AnnotationFixtures().volume()

    # 构造与测试影像几何匹配的标注项目。
    def _project(self) -> I_MutableAnnotationProject:
        from .C_AnnotationFixtures import C_AnnotationFixtures

        return C_AnnotationFixtures().project()

    # 验证删除操作针对最近编辑的轮廓，而不是列表最后一项。
    def test_delete_targets_last_edited_polygon_not_last_list_item(self) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_PolygonAnnotation import (
            C_PolygonAnnotation,
        )
        from med_image_seg.Concrete.Domain.Geometry.C_Point2D import C_Point2D
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList

        from .C_AnnotationFixtures import C_AnnotationFixtures

        project = C_AnnotationFixtures().project()
        first = C_PolygonAnnotation(points=((1, 1), (6, 1), (3, 6)))
        second = C_PolygonAnnotation(points=((10, 1), (15, 1), (12, 6)))
        project.add_polygon(2, first)
        project.add_polygon(2, second)
        project.replace_polygon(2, 0, C_PointList(((2, 2), (7, 2), (4, 7))))
        deleted = project.delete_last_edited_polygon(2)
        assert deleted is not None
        assert deleted.getPoints()[0] == C_Point2D(2.0, 2.0)
        assert project.annotation(2).getPolygon(0).getPoints() == second.getPoints()

    # 验证原子保存与备份恢复，避免写盘中断破坏项目。
    def test_save_is_atomic_and_recovers_from_backup(
        self, tmp_path: I_FilePath
    ) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_PolygonAnnotation import (
            C_PolygonAnnotation,
        )
        from med_image_seg.Concrete.Domain.Geometry.C_Point2D import C_Point2D
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath
        from med_image_seg.Concrete.Storage.Projects.C_ProjectRepository import (
            C_ProjectRepository,
        )

        from .C_AnnotationFixtures import C_AnnotationFixtures

        project = C_AnnotationFixtures().project()
        project.add_polygon(2, C_PolygonAnnotation(points=((1, 1), (6, 1), (3, 6))))
        path = project.save(tmp_path / "scan.med-image-seg.json")
        project.replace_polygon(2, 0, C_PointList(((2, 2), (7, 2), (4, 7))))
        project.save(path)
        assert C_FilePath(f"{path}.bak").is_file()
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert "source_path" not in payload
        assert payload["edit_counter"] == 2
        path.write_text("broken", encoding="utf-8")
        recovered = C_ProjectRepository().load(path)
        assert recovered.annotation(2).getPolygon(0).getPoints()[0] == C_Point2D(
            1.0, 1.0
        )

    # 核验相邻人工关键层之间产生预期的掩码插值。
    def test_interpolation_between_keyframes(self) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_PolygonAnnotation import (
            C_PolygonAnnotation,
        )

        from .C_AnnotationFixtures import C_AnnotationFixtures

        project = C_AnnotationFixtures().project()
        project.add_polygon(
            0, C_PolygonAnnotation(points=((2, 4), (8, 4), (8, 12), (2, 12)))
        )
        project.add_polygon(
            4, C_PolygonAnnotation(points=((6, 4), (12, 4), (12, 12), (6, 12)))
        )
        preview = project.interpolated_plane(2)
        mask = project.to_mask()
        assert preview is not None and preview.any()
        assert np.array_equal(mask[:, :, 2], preview.T)

    # 验证强制空层优先于人工轮廓及自动插值结果。
    def test_force_empty_overrides_polygons_and_interpolation(self) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_PolygonAnnotation import (
            C_PolygonAnnotation,
        )

        from .C_AnnotationFixtures import C_AnnotationFixtures

        project = C_AnnotationFixtures().project()
        polygon = C_PolygonAnnotation(points=((2, 4), (12, 4), (12, 14), (2, 14)))
        project.add_polygon(0, polygon)
        project.add_polygon(4, polygon)
        assert (preview := project.interpolated_plane(2)) is not None and preview.any()
        project.set_force_empty(2, True)
        assert project.interpolated_plane(2) is None
        assert not project.to_mask()[:, :, 2].any()
        assert project.annotation(2).getForceEmpty()

    # 验证新增轮廓会清除该层的强制空掩码标志。
    def test_adding_polygon_clears_force_empty(self) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_PolygonAnnotation import (
            C_PolygonAnnotation,
        )

        from .C_AnnotationFixtures import C_AnnotationFixtures

        project = C_AnnotationFixtures().project()
        project.set_force_empty(2, True)
        project.add_polygon(
            2, C_PolygonAnnotation(points=((2, 4), (12, 4), (12, 14), (2, 14)))
        )
        assert not project.annotation(2).getForceEmpty()
        assert project.to_mask(interpolate=False)[:, :, 2].any()

    # 验证人工和机器轮廓以并集组合，保留原有来源语义。
    def test_manual_and_prototype_sources_are_combined_as_a_union(self) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_PolygonAnnotation import (
            C_PolygonAnnotation,
        )

        from .C_AnnotationFixtures import C_AnnotationFixtures

        project = C_AnnotationFixtures().project()
        project.add_polygon(
            2,
            C_PolygonAnnotation(
                points=((1, 2), (9, 2), (9, 12), (1, 12)), source="prototype"
            ),
        )
        project.add_polygon(
            2, C_PolygonAnnotation(points=((7, 2), (16, 2), (16, 12), (7, 12)))
        )
        project.add_polygon(
            2,
            C_PolygonAnnotation(
                points=((7, 4), (11, 4), (11, 10), (7, 10)), operation="erase"
            ),
        )
        plane = project.to_mask(interpolate=False)[:, :, 2]
        assert plane[8, 6] == 1
        assert plane[14, 6] == 1

    # 往返保存和加载 JSON，核验强制空层标志保留。
    def test_force_empty_round_trips_through_json(self, tmp_path: I_FilePath) -> None:
        from med_image_seg.Concrete.Storage.Projects.C_ProjectRepository import (
            C_ProjectRepository,
        )

        from .C_AnnotationFixtures import C_AnnotationFixtures

        project = C_AnnotationFixtures().project()
        project.set_force_empty(2, True)
        loaded = C_ProjectRepository().load(project.save(tmp_path / "annotations.json"))
        assert loaded.getSchemaVersion() == 4
        assert loaded.annotation(2).getForceEmpty()

    # 复核机器轮廓，验证来源仍为机器而不会改成人工。
    def test_reviewing_machine_polygon_preserves_its_source(self) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_PolygonAnnotation import (
            C_PolygonAnnotation,
        )

        from .C_AnnotationFixtures import C_AnnotationFixtures

        project = C_AnnotationFixtures().project()
        project.add_polygon(
            2,
            C_PolygonAnnotation(
                points=((2, 4), (12, 4), (12, 14), (2, 14)), source="prototype"
            ),
        )
        project.set_completed(2, True)
        assert project.annotation(2).getPolygon(0).getSource() == "prototype"

    # 逐层比较存在性结果与完整导出掩码是否含前景。
    @pytest.mark.parametrize("interpolate", [False, True])
    @pytest.mark.parametrize("seed", range(8))
    def test_mask_presence_matches_exported_mask(
        self, seed: int, interpolate: bool
    ) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_PolygonAnnotation import (
            C_PolygonAnnotation,
        )
        from med_image_seg.Concrete.Domain.Snapshots.C_ProjectCopy import C_ProjectCopy

        from .C_AnnotationFixtures import C_AnnotationFixtures

        project = C_ProjectCopy().withShape(
            C_AnnotationFixtures().project(), (20, 18, 17)
        )
        random = np.random.default_rng(seed)
        for slice_index in range(project.getShapeLps()[2]):
            for _polygon_index in range(int(random.integers(0, 4))):
                left, top = random.integers(-5, 20, size=2)
                width, height = random.integers(1, 12, size=2)
                project.add_polygon(
                    slice_index,
                    C_PolygonAnnotation(
                        points=(
                            (float(left), float(top)),
                            (float(left + width), float(top)),
                            (float(left + width), float(top + height)),
                            (float(left), float(top + height)),
                        ),
                        operation="erase" if random.random() < 0.4 else "add",
                        source="prototype" if random.random() < 0.5 else "manual",
                    ),
                )
            project.set_completed(slice_index, random.random() < 0.2)
            project.set_keyframe(slice_index, random.random() < 0.15)
            project.set_force_empty(slice_index, random.random() < 0.2)
        presence = project.mask_presence(interpolate=interpolate)
        assert presence.dtype == np.bool_
        assert presence.shape == (project.getShapeLps()[2],)
        np.testing.assert_array_equal(
            presence, project.to_mask(interpolate=interpolate).any(axis=(0, 1))
        )

    # 核验不相交关键层之间可能为空的插值不会错误高亮。
    def test_mask_presence_handles_disjoint_keyframes_with_empty_interpolation(
        self,
    ) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_PolygonAnnotation import (
            C_PolygonAnnotation,
        )

        from .C_AnnotationFixtures import C_AnnotationFixtures

        project = C_AnnotationFixtures().project()
        project.add_polygon(0, C_PolygonAnnotation(points=((1, 1), (1, 1), (1, 1))))
        project.add_polygon(
            4, C_PolygonAnnotation(points=((18, 16), (18, 16), (18, 16)))
        )
        assert project.mask_presence().tolist() == [True, False, False, False, True]
        np.testing.assert_array_equal(
            project.mask_presence(), project.to_mask().any((0, 1))
        )

    # 验证轮廓全部擦除后，存在性区间可为空而标注记录仍保留。
    def test_mask_presence_can_be_empty_despite_stored_contours(self) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_PolygonAnnotation import (
            C_PolygonAnnotation,
        )

        from .C_AnnotationFixtures import C_AnnotationFixtures

        project = C_AnnotationFixtures().project()
        points = ((2, 2), (8, 2), (5, 8))
        project.add_polygon(0, C_PolygonAnnotation(points=points))
        project.add_polygon(0, C_PolygonAnnotation(points=points, operation="erase"))
        project.add_polygon(1, C_PolygonAnnotation(points=points, operation="erase"))
        project.add_polygon(
            2, C_PolygonAnnotation(points=((-10, -10), (-8, -10), (-9, -8)))
        )
        project.add_polygon(3, C_PolygonAnnotation(points=points))
        project.set_force_empty(3, True)
        project.set_completed(4, True)
        assert not project.mask_presence().any()
        assert not project.to_mask().any()

    # 验证掩码存在性保留多个分离区间和孤立层。
    def test_mask_presence_keeps_separate_intervals_and_isolated_slices(self) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_PolygonAnnotation import (
            C_PolygonAnnotation,
        )
        from med_image_seg.Concrete.Domain.Snapshots.C_ProjectCopy import C_ProjectCopy

        from .C_AnnotationFixtures import C_AnnotationFixtures

        project = C_ProjectCopy().withShape(
            C_AnnotationFixtures().project(), (20, 18, 13)
        )
        polygon = C_PolygonAnnotation(points=((2, 2), (10, 2), (10, 10), (2, 10)))
        for slice_index in (0, 4, 6, 8, 12):
            project.add_polygon(slice_index, polygon)
        for slice_index in (5, 7):
            project.set_force_empty(slice_index, True)
        expected = [True] * 5 + [False, True, False] + [True] * 5
        assert project.mask_presence().tolist() == expected

    # 验证重叠关键层的存在性快速路径不计算距离场或分配完整体积。
    def test_mask_presence_overlapping_keyframes_avoids_distance_and_volume_allocation(
        self, monkeypatch: MonkeyPatch
    ) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_AnnotationProject import (
            C_AnnotationProject,
        )
        from med_image_seg.Concrete.Domain.Annotations.C_PolygonAnnotation import (
            C_PolygonAnnotation,
        )

        from .C_AnnotationFixtures import C_AnnotationFixtures

        project = C_AnnotationFixtures().project()
        polygon = C_PolygonAnnotation(points=((2, 2), (10, 2), (10, 10), (2, 10)))
        project.add_polygon(0, polygon)
        project.add_polygon(4, polygon)

        # 拦截不应发生的距离场或三维掩码计算，调用即判定测试失败。
        def unexpected_computation(*_args, **_kwargs) -> None:
            pytest.fail(
                "overlapping keyframes need neither a distance field nor a volume"
            )

        monkeypatch.setattr(
            C_AnnotationProject, "_signed_distance", unexpected_computation
        )
        monkeypatch.setattr(C_AnnotationProject, "to_mask", unexpected_computation)
        assert project.mask_presence().tolist() == [True] * 5

    # 验证复核等非轮廓状态不会阻止空编号文件删除。
    @pytest.mark.parametrize("state", ["empty", "completed", "keyframe", "force_empty"])
    def test_empty_project_removal_ignores_non_polygon_state(
        self, tmp_path: I_FilePath, state: str
    ) -> None:
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath
        from med_image_seg.Concrete.Storage.Projects.C_ProjectRepository import (
            C_ProjectRepository,
        )

        from .C_AnnotationFixtures import C_AnnotationFixtures

        project = C_AnnotationFixtures().project()
        if state == "completed":
            project.set_completed(2, True)
        elif state == "keyframe":
            project.set_keyframe(2, True)
        elif state == "force_empty":
            project.set_force_empty(2, True)
        path = project.save(tmp_path / "scan.med-image-seg-1.json")
        project.save(path)
        assert C_FilePath(f"{path}.bak").is_file()
        for suffix in (".tmp", ".bak.tmp"):
            C_FilePath(f"{path}{suffix}").write_text(
                "interrupted write", encoding="utf-8"
            )
        assert not project.getHasPolygons()
        assert project.save(path, delete_if_empty=True) == path
        assert all(
            not C_FilePath(f"{path}{suffix}").exists()
            for suffix in ("", ".bak", ".tmp", ".bak.tmp")
        )
        with pytest.raises(FileNotFoundError):
            C_ProjectRepository().load(path)

    # 验证 0 号项目即使没有轮廓仍保留主文件和备份。
    def test_default_save_keeps_empty_project_and_backup(
        self, tmp_path: I_FilePath
    ) -> None:
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath
        from med_image_seg.Concrete.Storage.Projects.C_ProjectRepository import (
            C_ProjectRepository,
        )

        from .C_AnnotationFixtures import C_AnnotationFixtures

        project = C_AnnotationFixtures().project()
        project.set_completed(2, True)
        path = project.save(tmp_path / "scan.med-image-seg.json")
        project.save(path)
        assert path.is_file()
        assert C_FilePath(f"{path}.bak").is_file()
        assert C_ProjectRepository().load(path).annotation(2).getCompleted()

    # 验证空项目删除策略依据已存轮廓数量，而非最终前景体素数量。
    @pytest.mark.parametrize(
        "operation, forced", [("add", False), ("erase", False), ("add", True)]
    )
    def test_delete_if_empty_counts_stored_polygons_not_nonzero_mask(
        self, tmp_path: I_FilePath, operation: str, forced: bool
    ) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_PolygonAnnotation import (
            C_PolygonAnnotation,
        )
        from med_image_seg.Concrete.Storage.Projects.C_ProjectRepository import (
            C_ProjectRepository,
        )

        from .C_AnnotationFixtures import C_AnnotationFixtures

        project = C_AnnotationFixtures().project()
        project.add_polygon(
            4, C_PolygonAnnotation(points=((2, 2), (8, 2), (5, 8)), operation=operation)
        )
        project.set_force_empty(4, forced)
        assert project.getHasPolygons()
        path = project.save(
            tmp_path / "scan.med-image-seg-2.json", delete_if_empty=True
        )
        assert path.is_file()
        assert C_ProjectRepository().load(path).getHasPolygons()

    # 验证删除从未保存的空项目不会创建多余目录。
    def test_deleting_absent_empty_project_does_not_create_directories(
        self, tmp_path: I_FilePath
    ) -> None:
        from .C_AnnotationFixtures import C_AnnotationFixtures

        path = tmp_path / "not-created" / "scan.med-image-seg-9.json"
        C_AnnotationFixtures().project().save(path, delete_if_empty=True)
        assert not path.getParent().exists()

    # 验证备份删除失败时不会继续删除主标注文件。
    def test_backup_removal_failure_does_not_delete_primary_annotation(
        self, tmp_path: I_FilePath, monkeypatch: MonkeyPatch
    ) -> None:
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath

        from .C_AnnotationFixtures import C_AnnotationFixtures

        project = C_AnnotationFixtures().project()
        path = project.save(tmp_path / "scan.med-image-seg-2.json")
        project.save(path)
        original = C_FilePath.unlink

        # 模拟备份文件被占用，核验删除失败不会破坏主标注文件。
        def fail_backup(candidate: I_FilePath, *args, **kwargs):
            assert isinstance(candidate, C_FilePath)
            if candidate == C_FilePath(f"{path}.bak"):
                raise PermissionError("backup is locked")
            return original(candidate, *args, **kwargs)

        with monkeypatch.context() as patch:
            patch.setattr(C_FilePath, "unlink", fail_backup)
            with pytest.raises(PermissionError, match="backup is locked"):
                project.save(path, delete_if_empty=True)
        assert path.is_file()
        assert C_FilePath(f"{path}.bak").is_file()

    # 把 pytest 临时目录转换为路径接口，供业务测试复用。
    @pytest.fixture(name="tmp_path")
    def _adapt_path(self, tmp_path: Path) -> I_FilePath:
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath

        return C_FilePath(tmp_path)
