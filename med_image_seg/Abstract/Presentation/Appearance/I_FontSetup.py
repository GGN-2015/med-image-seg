from abc import ABC, abstractmethod


# 约定界面字体初始化，让启动提示与主界面共享设置而不暴露底层字体对象。
class I_FontSetup(ABC):
    # 在首个窗口显示前准备字体，重复执行不得重复载入同一字体文件。
    @abstractmethod
    def configure(self) -> None: ...
