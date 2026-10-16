from typing import final

from ...Abstract.Architecture.I_ArchitectureGuide import I_ArchitectureGuide


# 生成架构说明文本，记录分层、集合封装和依赖边界约束。
@final
class C_ArchitectureGuide(I_ArchitectureGuide):
    # 返回架构说明的 Markdown 文本，供文档生成或展示使用。
    def getMarkdown(self) -> str:
        return "\n".join(
            (
                "# 架构与兼容性 / Architecture and Compatibility",
                "",
                "Abstract 定义 I_ 接口、T_ 泛型与 E_ 枚举。",
                "Concrete 定义不可派生的 C_ 实现。",
                "接口隔离外部框架，NumPy 数组是数值类型例外。",
                "可写接口继承只读接口，不使用 @property。",
                "集合只暴露计数、索引、键查询和迭代。",
                "不返回内部 list 或 dict，修改经过受控方法。",
                "顶点采用 I_PointList，字段采用 I_RecordFieldList。",
                "三个截面通过 getLP、getPS、getSL 查询。",
                "TypeVar 和 Generic 就地定义，不使用新泛型语法。",
                "C_Qt_ 适配器保留 Qt 原生事件。",
                "业务算法、版本 4 JSON 和掩码格式保持兼容。",
                "Tests 包含架构检查与十二组历史结果回归。",
                "",
            )
        )
