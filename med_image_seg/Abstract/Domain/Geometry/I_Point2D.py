from __future__ import annotations

from abc import ABC, abstractmethod


# 表示只读二维坐标，供轮廓算法在不依赖 Qt 的情况下读取顶点。
class I_Point2D(ABC):
    # 返回二维顶点的横坐标。
    @abstractmethod
    def getX(self) -> float: ...

    # 返回二维顶点的纵坐标。
    @abstractmethod
    def getY(self) -> float: ...
