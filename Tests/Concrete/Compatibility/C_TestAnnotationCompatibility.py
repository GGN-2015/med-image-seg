from typing import final

import pytest

from ...Abstract.Compatibility.I_TestAnnotationCompatibility import (
    I_TestAnnotationCompatibility,
)


# 以历史样本验证 JSON 结构、掩码和区间结果保持一致。
@final
class C_TestAnnotationCompatibility(I_TestAnnotationCompatibility):
    # 对比历史样本，核验重构前后的 JSON、掩码哈希和区间结果一致。
    @pytest.mark.parametrize("seed", range(12))
    def test_original_mask_and_json_remain_compatible(self, seed: int) -> None:
        from .C_AnnotationCompatibilityVerifier import C_AnnotationCompatibilityVerifier

        C_AnnotationCompatibilityVerifier().verify(seed)
