from __future__ import annotations

from typing import TYPE_CHECKING

from ....Abstract.Domain.Snapshots.I_RecordSnapshot import I_RecordSnapshot
from ....Abstract.Storage.Projects.I_ProjectRepository import I_ProjectRepository

if TYPE_CHECKING:
    from ....Abstract.Domain.Annotations.I_MutableAnnotationProject import (
        I_MutableAnnotationProject,
    )
    from ....Abstract.Domain.Annotations.I_MutableSliceAnnotation import (
        I_MutableSliceAnnotation,
    )
    from ....Abstract.Storage.Paths.I_FilePath import I_FilePath
import json
from datetime import UTC, datetime
from typing import final


# 读取项目或备份并解码旧格式 JSON，恢复轮廓和缺省字段。
@final
class C_ProjectRepository(I_ProjectRepository):
    # 先读取主标注文件，失败时尝试同编号备份；两者都不可读则报告错误。
    def load(self, path: str | I_FilePath) -> I_MutableAnnotationProject:
        from ...Domain.Snapshots.C_RecordSnapshot import C_RecordSnapshot
        from ..Paths.C_FilePath import C_FilePath

        source = C_FilePath(path).expanduser().resolve()
        backup = C_FilePath(f"{source}.bak")
        errors: list[Exception] = []
        for candidate in (source, backup):
            if not candidate.is_file():
                continue
            try:
                payload = C_RecordSnapshot(candidate.read_text(encoding="utf-8"))
                return C_ProjectRepository().decode(payload)
            except (OSError, KeyError, TypeError, ValueError) as exc:
                errors.append(exc)
        if errors:
            raise ValueError(
                f"annotation project and backup are unreadable: {source}"
            ) from errors[0]
        raise FileNotFoundError(f"annotation project not found: {source}")

    # 从 JSON 快照恢复项目，补齐旧版缺省字段和历史编辑顺序。
    def decode(self, snapshot: I_RecordSnapshot) -> I_MutableAnnotationProject:
        payload = json.loads(snapshot.getJson())
        from ...Domain.Annotations.C_AnnotationProject import C_AnnotationProject
        from ...Domain.Annotations.C_PolygonAnnotation import C_PolygonAnnotation
        from ...Domain.Annotations.C_SliceAnnotation import C_SliceAnnotation
        from ...Domain.Imaging.C_Metadata import C_Metadata

        fallback_order = 0
        slices: dict[int, I_MutableSliceAnnotation] = {}
        for index, annotation in payload.get("slices", {}).items():
            polygons = []
            for polygon in annotation.get("polygons", []):
                fallback_order += 1
                polygons.append(
                    C_PolygonAnnotation(
                        points=tuple(
                            (float(point[0]), float(point[1]))
                            for point in polygon["points"]
                        ),
                        operation=polygon.get("operation", "add"),
                        source=polygon.get("source", "manual"),
                        edit_order=int(polygon.get("edit_order", fallback_order)),
                    )
                )
            slices[int(index)] = C_SliceAnnotation(
                polygons=polygons,
                completed=bool(annotation.get("completed", False)),
                keyframe=bool(annotation.get("keyframe", False)),
                force_empty=bool(annotation.get("force_empty", False)),
            )
        maximum_order = max(
            (
                polygon.getEditOrder()
                for annotation in slices.values()
                for polygon in annotation.iterPolygons()
            ),
            default=0,
        )
        return C_AnnotationProject(
            image_id=payload.get("image_id", payload.get("series_id", "IMAGE")),
            source_fingerprint=payload["source_fingerprint"],
            shape_lps=tuple(payload["shape_lps"]),
            spacing_lps_mm=tuple(payload["spacing_lps_mm"]),
            origin_lps_mm=tuple(payload["origin_lps_mm"]),
            slices=slices,
            metadata=C_Metadata(json.dumps(dict(payload.get("metadata", {})))),
            edit_counter=max(int(payload.get("edit_counter", 0)), maximum_order),
            schema_version=int(payload.get("schema_version", 1)),
            updated_at=payload.get("updated_at", datetime.now(UTC).isoformat()),
        )
