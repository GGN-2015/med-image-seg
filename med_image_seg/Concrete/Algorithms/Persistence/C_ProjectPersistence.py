from __future__ import annotations

from typing import TYPE_CHECKING

from ....Abstract.Algorithms.Persistence.I_ProjectPersistence import (
    I_ProjectPersistence,
)

if TYPE_CHECKING:
    from ....Abstract.Domain.Annotations.I_MutableAnnotationProject import (
        I_MutableAnnotationProject,
    )
    from ....Abstract.Storage.Paths.I_FilePath import I_FilePath
import json
import os
import shutil
from datetime import UTC, datetime
from typing import final


# 原子保存标注并维护备份，按编号策略删除不含多边形的文件。
@final
class C_ProjectPersistence(I_ProjectPersistence):
    # 按空文件策略删除或原子替换 JSON，并维护备份以支持异常恢复。
    def save(
        self,
        context: I_MutableAnnotationProject,
        path: str | I_FilePath,
        *,
        delete_if_empty: bool = False,
    ) -> I_FilePath:
        from ...Domain.Snapshots.C_RecordOperations import C_RecordOperations
        from ...Storage.Paths.C_FilePath import C_FilePath

        output = C_FilePath(path).expanduser().resolve()
        if delete_if_empty and (not context.getHasPolygons()):
            for suffix in (".bak.tmp", ".tmp", ".bak", ""):
                C_FilePath(f"{output}{suffix}").unlink(missing_ok=True)
            return output
        output.getParent().mkdir(parents=True, exist_ok=True)
        context.setUpdatedAt(datetime.now(UTC).isoformat())
        payload = {
            "schema_version": context.getSchemaVersion(),
            "image_id": context.getImageId(),
            "source_fingerprint": context.getSourceFingerprint(),
            "shape_lps": context.getShapeLps(),
            "spacing_lps_mm": context.getSpacingLpsMm(),
            "origin_lps_mm": context.getOriginLpsMm(),
            "updated_at": context.getUpdatedAt(),
            "edit_counter": context.getEditCounter(),
            "metadata": json.loads(context.getMetadata().getJson()),
            "slices": {
                str(index): {
                    "completed": annotation.getCompleted(),
                    "keyframe": annotation.getKeyframe(),
                    "force_empty": annotation.getForceEmpty(),
                    "polygons": [
                        json.loads(C_RecordOperations().asdict(polygon).getJson())
                        for polygon in annotation.iterPolygons()
                    ],
                }
                for index, annotation in sorted(
                    (_entry_index, context.getSlice(_entry_index))
                    for _entry_index in context.iterSliceIndices()
                )
                if annotation.getPolygonCount()
                or annotation.getCompleted()
                or annotation.getKeyframe()
                or annotation.getForceEmpty()
            },
        }
        temporary = C_FilePath(f"{output}.tmp")
        backup = C_FilePath(f"{output}.bak")
        backup_temporary = C_FilePath(f"{backup}.tmp")
        serialized = json.dumps(payload, indent=2, ensure_ascii=False)
        try:
            with temporary.open("w", encoding="utf-8") as handle:
                handle.write(serialized)
                handle.flush()
                os.fsync(handle.fileno())
            if output.is_file():
                try:
                    json.loads(output.read_text(encoding="utf-8"))
                except (OSError, TypeError, ValueError):
                    pass
                else:
                    shutil.copy2(output, backup_temporary)
                    os.replace(backup_temporary, backup)
            os.replace(temporary, output)
        finally:
            temporary.unlink(missing_ok=True)
            backup_temporary.unlink(missing_ok=True)
        return output
