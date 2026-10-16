from __future__ import annotations

import json
from typing import final

import numpy as np
import pytest

from med_image_seg.Abstract.Domain.Imaging.I_ImageSource import I_ImageSource

from ...Abstract.Collections.I_TestCollectionContracts import I_TestCollectionContracts


# 验证影像、顶点、字段和截面集合的查询契约及数据隔离。
@final
class C_TestCollectionContracts(I_TestCollectionContracts):
    # 创建临时影像源，统一测试项目的配套文件路径和指纹。
    def _source(self, name: str, fingerprint: str) -> I_ImageSource:
        from med_image_seg.Abstract.Domain.Imaging.E_SourceKind import E_SourceKind
        from med_image_seg.Concrete.Domain.Imaging.C_ImageSource import C_ImageSource
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath

        return C_ImageSource(
            C_FilePath(f"{name}.nii"),
            E_SourceKind.NIFTI,
            name,
            fingerprint,
            C_FilePath(f"{name}.med-image-seg.json"),
            C_FilePath(f"{name}-mask.nii.gz"),
        )

    # 验证数量、索引及指纹查询保持导入顺序和去重语义。
    def test_image_queries_preserve_order_and_deduplication(self) -> None:
        from med_image_seg.Concrete.Domain.Collections.C_ImageCollection import (
            C_ImageCollection,
        )

        first, second = self._source("first", "a"), self._source("second", "b")
        collection = C_ImageCollection([first, second])
        assert collection.add(self._source("duplicate", "a")) is first
        assert collection.getCount() == len(collection) == 2
        assert collection.getSource(0) is collection[0] is first
        assert collection.getSource(-1) is second
        assert tuple(collection) == (first, second)
        assert collection.findByFingerprint("b") is second
        assert collection.findByFingerprint("missing") is None
        with pytest.raises(IndexError):
            collection.getSource(2)

    # 验证影像集合不再提供暴露内部列表或指纹字典的接口。
    def test_image_collection_does_not_expose_storage(self) -> None:
        from med_image_seg.Concrete.Domain.Collections.C_ImageCollection import (
            C_ImageCollection,
        )

        collection = C_ImageCollection()
        for name in (
            "getInternalSources",
            "setInternalSources",
            "getInternalByFingerprint",
            "setInternalByFingerprint",
        ):
            assert not hasattr(collection, name)

    # 修改原始点输入，验证只读顶点快照保持顺序和数值精度。
    def test_points_are_ordered_independent_snapshots(self) -> None:
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList

        precise = float(np.nextafter(1.0, 2.0))
        original = [(precise, 2.0), (3.0, 4.0)]
        points = C_PointList(original)
        original[0] = (99.0, 99.0)
        assert points.getCount() == len(points) == 2
        assert points.getPoint(0).getX() == precise
        assert points.getPoint(0).getY() == 2.0
        assert [point.getX() for point in points] == [precise, 3.0]
        assert points[-1].getY() == 4.0
        with pytest.raises(IndexError):
            points.getPoint(2)

    # 修改原字段列表，核验字段快照仍保持名称、顺序和索引边界。
    def test_record_fields_are_read_only_and_ordered(self) -> None:
        from med_image_seg.Concrete.Domain.Records.C_RecordFieldList import (
            C_RecordFieldList,
        )

        original = ["points", "operation", "source", "edit_order"]
        fields = C_RecordFieldList(original)
        original.clear()
        assert fields.getCount() == len(fields) == 4
        assert fields.getField(0) == "points"
        assert fields[-1] == "edit_order"
        assert tuple(fields) == ("points", "operation", "source", "edit_order")
        with pytest.raises(IndexError):
            fields.getField(4)

    # 核验顶点接口序列化后仍使用历史 JSON 字段和坐标数组。
    def test_polygon_serialization_preserves_existing_schema(self) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_PolygonAnnotation import (
            C_PolygonAnnotation,
        )
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList
        from med_image_seg.Concrete.Domain.Snapshots.C_RecordOperations import (
            C_RecordOperations,
        )

        polygon = C_PolygonAnnotation(
            C_PointList([(1.5, 2.5), (5.0, 2.0), (3.0, 7.0)]), edit_order=8
        )
        assert json.loads(C_RecordOperations().asdict(polygon).getJson()) == {
            "points": [[1.5, 2.5], [5.0, 2.0], [3.0, 7.0]],
            "operation": "add",
            "source": "manual",
            "edit_order": 8,
        }
        assert tuple(polygon.getRecordFields()) == (
            "points",
            "operation",
            "source",
            "edit_order",
        )

    # 验证封装后的多边形仍拒绝不足三个点或非有限坐标。
    def test_polygon_validation_is_preserved(self) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_PolygonAnnotation import (
            C_PolygonAnnotation,
        )

        with pytest.raises(ValueError, match="three points"):
            C_PolygonAnnotation(((0.0, 0.0), (1.0, 1.0)))
        with pytest.raises(ValueError, match="finite"):
            C_PolygonAnnotation(((0.0, 0.0), (np.inf, 1.0), (1.0, 0.0)))

    # 验证 LP、PS、SL 具名查询保留既定轴定义与配色。
    def test_planes_have_named_getters_and_original_axes(self) -> None:
        from med_image_seg.Concrete.Algorithms.Observation import (
            C_ObservationPlanes,
        )

        planes = C_ObservationPlanes().getPlanes()
        assert planes.getLP().getName() == "LP"
        assert planes.getPS().getName() == "PS"
        assert planes.getSL().getName() == "SL"
        assert planes.getLP().getFixedAxis() == 2
        assert planes.getPS().getFixedAxis() == 0
        assert planes.getSL().getFixedAxis() == 1
        assert planes.getLP().getColor() == "#00ffff"
        assert planes.getPS().getColor() == "#ff00ff"
        assert planes.getSL().getColor() == "#ffff00"
        with pytest.raises(KeyError):
            planes.getByName("invalid")

    # 验证单层轮廓通过索引读取、替换和删除，而不取得内部列表。
    def test_slice_polygons_are_accessed_and_modified_by_index(self) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_PolygonAnnotation import (
            C_PolygonAnnotation,
        )
        from med_image_seg.Concrete.Domain.Annotations.C_SliceAnnotation import (
            C_SliceAnnotation,
        )

        first = C_PolygonAnnotation(((0.0, 0.0), (2.0, 0.0), (0.0, 2.0)))
        second = C_PolygonAnnotation(((1.0, 1.0), (3.0, 1.0), (1.0, 3.0)))
        annotation = C_SliceAnnotation()
        annotation.addPolygon(first)
        assert annotation.getPolygonCount() == 1
        assert annotation.getPolygon(0) is first
        annotation.replacePolygon(0, second)
        assert tuple(annotation.iterPolygons()) == (second,)
        assert annotation.removePolygon(0) is second
        assert annotation.getPolygonCount() == 0
        assert not hasattr(annotation, "getPolygons")
