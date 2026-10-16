from abc import ABC, abstractmethod


# 以历史样本验证 JSON 结构、掩码和区间结果保持一致。
class I_TestAnnotationCompatibility(ABC):
    # 对比历史样本，核验重构前后的 JSON、掩码哈希和区间结果一致。
    @abstractmethod
    def test_original_mask_and_json_remain_compatible(self, seed: int) -> None: ...
