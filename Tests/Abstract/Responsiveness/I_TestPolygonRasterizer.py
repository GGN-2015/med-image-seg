from abc import ABC, abstractmethod


# 约定栅格化替换的兼容性回归，确保解除 GIL 阻塞不会改变已有标注结果。
class I_TestPolygonRasterizer(ABC):
    # 检查凹形、自交、退化和越界轮廓在两条执行路径上保持逐像素一致。
    @abstractmethod
    def test_boundary_cases_match_original(self, case: str, size: int) -> None: ...

    # 使用包含大量顶点的随机轮廓，覆盖需要释放 GIL 的实际网格判定路径。
    @abstractmethod
    def test_random_large_polygons_match_original(self, seed: int) -> None: ...
