from typing import final

from fake_process_estimation import C_SCurveProcessEstimation

from ....Abstract.Diagnostics.Progress.I_ProgressEstimator import I_ProgressEstimator


# 将第三方 S 曲线封装为自有契约，是项目内唯一了解该依赖的适配类。
@final
class C_FakeProcessEstimation(I_ProgressEstimator):
    # 固定显示范围为百分比，并把 100 留给真实成功事件。
    def __init__(self, expected_seconds: float) -> None:
        self._estimator = C_SCurveProcessEstimation(
            estimated_time_cost=expected_seconds,
            lowest_value=0,
            highest_value=100,
        )

    # 根据已经耗费的时间给出不超过 99 的估计进度。
    def estimate(self, elapsed_seconds: float) -> int:
        return max(0, min(99, self._estimator.estimate(elapsed_seconds)))
