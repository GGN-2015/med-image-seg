from typing import final

import numpy as np
import pytest
from skimage.draw import polygon

from med_image_seg.Concrete.Algorithms.Masks.C_SkimagePolygonRasterizer import (
    C_SkimagePolygonRasterizer,
)
from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList

from ...Abstract.Responsiveness.I_TestPolygonRasterizer import I_TestPolygonRasterizer


# 以原 scikit-image polygon 为参考，核验新适配器没有改变边界容差和坐标约定。
@final
class C_TestPolygonRasterizer(I_TestPolygonRasterizer):
    # 非正方形网格和非对称轮廓可暴露转置错误，并覆盖大小两种填充分支。
    @pytest.mark.parametrize("size", [12, 384])
    @pytest.mark.parametrize(
        "case",
        [
            "convex",
            "concave",
            "crossed",
            "negative",
            "outside",
            "collinear",
            "repeated",
            "fractional",
            "near_vertex",
            "near_crop",
        ],
    )
    def test_boundary_cases_match_original(self, case: str, size: int) -> None:
        width, height = size, size * 3 // 4
        cases = {
            "convex": [(0, 0), (1, 0.2), (0.8, 1), (0.1, 0.7)],
            "concave": [(0, 0), (1, 0.1), (0.3, 0.4), (0.9, 1), (0, 0.8)],
            "crossed": [(0, 0), (1, 1), (0, 1), (1, 0)],
            "negative": [(-0.7, -0.2), (1.2, 0.1), (0.3, 1.4)],
            "outside": [(-2, -2), (-1, -2), (-1, -1)],
            "collinear": [(0, 0), (0.5, 0.5), (1, 1)],
            "repeated": [(0, 0), (1, 0), (1, 1), (1, 1), (0, 0)],
            "fractional": [(0.23, 0.17), (0.91, 0.37), (0.59, 0.83)],
            "near_vertex": [(0, 0), (1, 0), (1, 1), (0, 1)],
            "near_crop": [(1, 0.2), (1.3, 0.8), (1, 1)],
        }
        vertices = np.asarray(cases[case], dtype=np.float64)
        vertices *= (width, height)
        if case in ("near_vertex", "near_crop"):
            vertices += 1e-13
        expected = np.zeros((height, width), dtype=np.bool_)
        rows, columns = polygon(vertices[:, 1], vertices[:, 0], shape=expected.shape)
        expected[rows, columns] = True
        actual = C_SkimagePolygonRasterizer().rasterize(
            C_PointList((float(x), float(y)) for x, y in vertices), width, height
        )
        np.testing.assert_array_equal(actual, expected)

    # 随机顺序保留自交、多重边和越界情况，不用排序把困难轮廓变成规则凸形。
    @pytest.mark.parametrize("seed", [2015, 20261017, 4501])
    def test_random_large_polygons_match_original(self, seed: int) -> None:
        generator = np.random.default_rng(seed)
        for index in range(12):
            width, height = 63, 47
            vertices = generator.uniform(-0.3, 1.4, size=(200, 2))
            vertices *= (width, height)
            if index % 3 == 0:
                vertices = np.round(vertices)
            if index % 4 == 0:
                vertices += 1e-13
            expected = np.zeros((height, width), dtype=np.bool_)
            rows, columns = polygon(
                vertices[:, 1], vertices[:, 0], shape=expected.shape
            )
            expected[rows, columns] = True
            actual = C_SkimagePolygonRasterizer().rasterize(
                C_PointList((float(x), float(y)) for x, y in vertices), width, height
            )
            np.testing.assert_array_equal(actual, expected)
