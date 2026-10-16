from abc import ABC, abstractmethod


# 检查源码分层、类型命名和集合访问边界，防止重构规则回退。
class I_TestArchitecture(ABC):
    # 检查类和方法的中文注释，禁止重新引入没有实际信息的模板句。
    @abstractmethod
    def test_comments_explain_behavior_without_template_filler(self) -> None: ...

    # 检查目录容量、单文件单类型、类名、final 及抽象具体分层。
    @abstractmethod
    def test_package_and_type_boundaries(self) -> None: ...

    # 检查模块不含全局函数或状态，仅允许入口、导出列表和局部泛型声明。
    @abstractmethod
    def test_modules_do_not_define_global_state(self) -> None: ...

    # 检查抽象层不依赖框架，签名不含 Any、object 或具体类。
    @abstractmethod
    def test_abstract_and_annotation_boundaries(self) -> None: ...

    # 检查业务 getter 不返回内部列表、字典或映射类型。
    @abstractmethod
    def test_getters_do_not_expose_mutable_containers(self) -> None: ...
