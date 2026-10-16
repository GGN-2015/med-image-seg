from __future__ import annotations

from typing import TYPE_CHECKING

from ....Abstract.Algorithms.Masks.I_ManualPlaneAlgorithm import I_ManualPlaneAlgorithm
from ....Abstract.Domain.Annotations.I_MutableAnnotationProject import (
    I_MutableAnnotationProject,
)

if TYPE_CHECKING:
    from ....Abstract.Domain.Annotations.I_MutableAnnotationProject import (
        I_MutableAnnotationProject,
    )
from typing import final

import numpy as np
from numpy.typing import NDArray
from skimage.draw import polygon as rasterize_polygon


# 按来源分别合成轮廓掩码，依次应用添加与擦除后取并集。
@final
class C_ManualPlaneAlgorithm(I_ManualPlaneAlgorithm):
    # 按存储顺序分别合成人工与机器轮廓，再取两者并集。
    def manual_plane(
        self, context: I_MutableAnnotationProject, slice_index: int
    ) -> NDArray[np.bool_]:
        from ...Domain.Annotations.C_SliceAnnotation import C_SliceAnnotation
        from ...Numerics.Arrays.C_ArrayFactory import C_ArrayFactory

        plane_shape = (context.getShapeLps()[1], context.getShapeLps()[0])
        annotation = context.findSlice(slice_index) or C_SliceAnnotation()
        if annotation.getForceEmpty():
            return C_ArrayFactory().wrap(np.zeros(plane_shape, dtype=bool))
        source_planes = {
            "manual": np.zeros(plane_shape, dtype=bool),
            "prototype": np.zeros(plane_shape, dtype=bool),
        }
        for item in annotation.iterPolygons():
            x = np.asarray(
                [point.getX() for point in item.getPoints()], dtype=np.float64
            )
            y = np.asarray(
                [point.getY() for point in item.getPoints()], dtype=np.float64
            )
            rows, columns = rasterize_polygon(y, x, shape=plane_shape)
            source_planes[item.getSource()][rows, columns] = (
                item.getOperation() == "add"
            )
        return C_ArrayFactory().wrap(
            source_planes["manual"] | source_planes["prototype"]
        )
