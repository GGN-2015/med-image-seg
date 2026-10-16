from __future__ import annotations

from abc import ABC, abstractmethod

from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath


# 验证启动配置、语言选择和命令行参数到界面的传递。
class I_TestApplication(ABC):
    # 验证应用接收并保留初始影像集合。
    @abstractmethod
    def test_application_accepts_initial_collection(
        self, tmp_path: I_FilePath
    ) -> None: ...

    # 验证应用接受中文配置并拒绝未知语言。
    @abstractmethod
    def test_application_accepts_chinese_and_rejects_unknown_language(self) -> None: ...

    # 验证命令行允许无初始影像或多个影像路径。
    @abstractmethod
    def test_cli_allows_empty_or_multiple_initial_images(self) -> None: ...

    # 验证重复影像选项可以传入一个或多个初始影像。
    @abstractmethod
    def test_cli_image_option_accepts_one_or_more_initial_images(self) -> None: ...

    # 验证命令行可以选择中文界面。
    @abstractmethod
    def test_cli_accepts_chinese_interface(self) -> None: ...

    # 验证命令行选择的影像传递到应用启动流程。
    @abstractmethod
    def test_cli_image_option_launches_selected_image(self) -> None: ...
