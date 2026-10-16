from __future__ import annotations

from typing import TYPE_CHECKING

from ....Abstract.Domain.Annotations.I_AnnotationProject import I_AnnotationProject
from ....Abstract.Domain.Annotations.I_PolygonAnnotation import I_PolygonAnnotation
from ....Abstract.Domain.Annotations.I_SliceAnnotation import I_SliceAnnotation
from ....Abstract.Domain.Snapshots.I_RecordOperations import I_RecordOperations
from ....Abstract.Domain.Snapshots.I_RecordSnapshot import I_RecordSnapshot

if TYPE_CHECKING:
    from ....Abstract.Domain.Annotations.I_AnnotationProject import I_AnnotationProject
    from ....Abstract.Domain.Snapshots.I_RecordSnapshot import I_RecordSnapshot
import json
from typing import final


# 将项目、切片或轮廓转换为 JSON 快照，保留现有磁盘字段结构。
@final
class C_RecordOperations(I_RecordOperations):
    # 序列化为保留原有字段结构的 JSON 快照，而不是返回可变字典。
    def asdict(
        self, record: I_AnnotationProject | I_PolygonAnnotation | I_SliceAnnotation
    ) -> I_RecordSnapshot:
        from ....Abstract.Domain.Annotations.I_PolygonAnnotation import (
            I_PolygonAnnotation,
        )
        from ....Abstract.Domain.Annotations.I_SliceAnnotation import I_SliceAnnotation
        from .C_RecordSnapshot import C_RecordSnapshot

        if isinstance(record, I_PolygonAnnotation):
            payload = {
                "points": [
                    (point.getX(), point.getY()) for point in record.getPoints()
                ],
                "operation": record.getOperation(),
                "source": record.getSource(),
                "edit_order": record.getEditOrder(),
            }
        elif isinstance(record, I_SliceAnnotation):
            payload = {
                "polygons": [
                    json.loads(self.asdict(p).getJson()) for p in record.iterPolygons()
                ],
                "completed": record.getCompleted(),
                "keyframe": record.getKeyframe(),
                "force_empty": record.getForceEmpty(),
            }
        else:
            payload = {
                "image_id": record.getImageId(),
                "source_fingerprint": record.getSourceFingerprint(),
                "shape_lps": record.getShapeLps(),
                "spacing_lps_mm": record.getSpacingLpsMm(),
                "origin_lps_mm": record.getOriginLpsMm(),
                "slices": {
                    str(i): json.loads(self.asdict(a).getJson())
                    for i, a in (
                        (_entry_index, record.getSlice(_entry_index))
                        for _entry_index in record.iterSliceIndices()
                    )
                },
                "metadata": json.loads(record.getMetadata().getJson()),
                "edit_counter": record.getEditCounter(),
                "schema_version": record.getSchemaVersion(),
                "updated_at": record.getUpdatedAt(),
            }
        return C_RecordSnapshot(json.dumps(payload, ensure_ascii=False))
