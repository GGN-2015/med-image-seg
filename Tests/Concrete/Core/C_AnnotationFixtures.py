from __future__ import annotations

from typing import TYPE_CHECKING

from ...Abstract.Core.I_AnnotationFixtures import I_AnnotationFixtures

if TYPE_CHECKING:
    from med_image_seg.Abstract.Domain.Annotations import (
        I_MutableAnnotationProject,
    )
    from med_image_seg.Abstract.Domain.Imaging.I_MedicalVolume import I_MedicalVolume
import json
from typing import final

import numpy as np


# 构造轮廓、关键层和项目样本，供标注算法测试复用。
@final
class C_AnnotationFixtures(I_AnnotationFixtures):
    # 构造与测试影像源对应的体素和几何信息。
    def volume(self) -> I_MedicalVolume:
        from med_image_seg.Concrete.Domain.Imaging.C_MedicalVolume import (
            C_MedicalVolume,
        )
        from med_image_seg.Concrete.Domain.Imaging.C_Metadata import C_Metadata
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath

        return C_MedicalVolume(
            data=np.zeros((20, 18, 5), dtype=np.float32),
            spacing_mm=(0.8, 0.8, 0.8),
            origin_lps_mm=(1.0, 2.0, 3.0),
            metadata=C_Metadata(json.dumps({})),
            source=C_FilePath("anonymous"),
        )

    # 构造与测试影像几何匹配的标注项目。
    def project(self) -> I_MutableAnnotationProject:
        from med_image_seg.Concrete.Application.Projects.C_ProjectFactory import (
            C_ProjectFactory,
        )

        return C_ProjectFactory().create(
            image_id="IMAGE-TEST",
            source_fingerprint="fingerprint",
            volume=C_AnnotationFixtures().volume(),
        )
