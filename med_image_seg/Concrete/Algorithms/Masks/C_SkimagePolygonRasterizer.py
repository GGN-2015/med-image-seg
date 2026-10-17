from typing import final

import numpy as np
from numpy.typing import NDArray
from skimage.draw import polygon
from skimage.measure import grid_points_in_poly

from ....Abstract.Algorithms.Masks.I_PolygonRasterizer import I_PolygonRasterizer
from ....Abstract.Domain.Geometry.I_PointList import I_PointList


# 使用释放 GIL 的网格判定实现原有填充规则，避免后台计算饿死界面线程。
@final
class C_SkimagePolygonRasterizer(I_PolygonRasterizer):
    # 小轮廓保留有界的原填充，大轮廓释放 GIL；两条路径均保持绝对坐标和边缘判定。
    def rasterize(
        self, points: I_PointList, width: int, height: int
    ) -> NDArray[np.bool_]:
        vertices = np.asarray(
            [(point.getX(), point.getY()) for point in points], dtype=np.float64
        )
        columns = vertices[:, 0]
        rows = vertices[:, 1]
        first_row = int(max(0, rows.min()))
        last_row = min(height - 1, int(np.ceil(rows.max())))
        first_column = int(max(0, columns.min()))
        last_column = min(width - 1, int(np.ceil(columns.max())))
        mask = np.zeros((height, width), dtype=np.bool_)
        if first_row > last_row or first_column > last_column:
            return mask
        work = (
            (last_row - first_row + 1) * (last_column - first_column + 1) * len(points)
        )
        if work <= 262144:
            selected_rows, selected_columns = polygon(rows, columns, shape=mask.shape)
            mask[selected_rows, selected_columns] = True
            return mask
        grid = grid_points_in_poly((last_column + 1, last_row + 1), vertices)
        mask[first_row : last_row + 1, first_column : last_column + 1] = grid[
            first_column : last_column + 1, first_row : last_row + 1
        ].T
        return mask
