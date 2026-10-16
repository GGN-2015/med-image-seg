from abc import ABC, abstractmethod


# 对比历史 JSON、掩码哈希和区间结果，检测封装重构是否改变算法。
class I_AnnotationCompatibilityVerifier(ABC):
    # 对照历史样本核验 JSON、完整掩码哈希和逐层存在性结果。
    @abstractmethod
    def verify(self, seed: int) -> None: ...
