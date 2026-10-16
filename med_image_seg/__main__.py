from __future__ import annotations

from .Concrete.CommandLine.C_CommandLine import C_CommandLine


# 把进程参数交给命令行对象，并将启动结果作为退出码返回。
def main(argv: list[str] | None = None) -> int:
    return C_CommandLine().run(argv)


if __name__ == "__main__":
    raise SystemExit(main())
