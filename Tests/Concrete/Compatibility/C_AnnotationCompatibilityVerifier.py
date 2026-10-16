from __future__ import annotations

import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import final

from ...Abstract.Compatibility.I_AnnotationCompatibilityVerifier import (
    I_AnnotationCompatibilityVerifier,
)


# 对比历史 JSON、掩码哈希和区间结果，检测封装重构是否改变算法。
@final
class C_AnnotationCompatibilityVerifier(I_AnnotationCompatibilityVerifier):
    # 对照历史样本核验 JSON、完整掩码哈希和逐层存在性结果。
    def verify(self, seed: int) -> None:
        from med_image_seg.Concrete.Domain.Snapshots.C_RecordSnapshot import (
            C_RecordSnapshot,
        )
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath
        from med_image_seg.Concrete.Storage.Projects.C_ProjectRepository import (
            C_ProjectRepository,
        )

        fixture = (
            Path(__file__).resolve().parents[2]
            / "Fixtures"
            / "Annotations"
            / "Golden.json"
        )
        expected = json.loads(fixture.read_text(encoding="utf-8"))[seed]
        project = C_ProjectRepository().decode(
            C_RecordSnapshot(json.dumps(expected["payload"]))
        )
        assert (
            hashlib.sha256(project.to_mask().tobytes()).hexdigest() == expected["mask"]
        )
        assert project.mask_presence().tolist() == expected["presence"]
        with TemporaryDirectory() as directory:
            output = project.save(
                C_FilePath(Path(directory) / "scan.med-image-seg.json")
            )
            actual = json.loads(output.read_text(encoding="utf-8"))
        actual.pop("updated_at")
        assert actual == expected["payload"]
