from __future__ import annotations

from typing import TYPE_CHECKING

from ....Abstract.Storage.Masks.I_NiftiPathPolicy import I_NiftiPathPolicy

if TYPE_CHECKING:
    from ....Abstract.Storage.Resources.I_TemporaryDirectory import I_TemporaryDirectory
import os
from tempfile import TemporaryDirectory, gettempdir
from typing import final

import numpy as np


# 选择纯英文临时目录并修正序列化间距，规避 NIfTI 路径和精度问题。
@final
class C_NiftiPathPolicy(I_NiftiPathPolicy):
    # 将间距向下修正到可序列化的 float32，避免写盘舍入扩大体素范围。
    def nifti_safe_spacing(
        self, spacing_mm: tuple[float, float, float]
    ) -> tuple[float, ...]:
        safe: list[float] = []
        for value in spacing_mm:
            serialized = np.float32(value)
            if float(serialized) > float(value):
                serialized = np.nextafter(
                    serialized, np.float32(-np.inf), dtype=np.float32
                )
            safe.append(float(serialized))
        return tuple(safe)

    # 优先选择可写的纯英文临时目录，必要时回退并报告无可用目录。
    def ascii_temporary_directory(self) -> I_TemporaryDirectory:
        from ..Paths.C_FilePath import C_FilePath
        from ..Paths.C_PathEnvironment import C_PathEnvironment
        from ..Resources.C_TemporaryDirectory import C_TemporaryDirectory

        directories = [
            C_FilePath(gettempdir()),
            C_PathEnvironment().getWorkingDirectory(),
        ]
        if os.name == "nt":
            directories.append(
                C_FilePath(os.environ.get("SYSTEMROOT", "C:\\Windows")) / "Temp"
            )
        for directory in directories:
            try:
                directory = directory.resolve()
                if not str(directory).isascii():
                    continue
                return C_TemporaryDirectory(
                    TemporaryDirectory(prefix="med-image-seg-", dir=directory)
                )
            except OSError:
                continue
        raise OSError(
            "NIfTI I/O requires a writable ASCII-only temporary directo"
            "ry; set TMPDIR, TEMP, or TMP to an ASCII-only path."
        )
