from __future__ import annotations

from typing import TYPE_CHECKING

from ....Abstract.Storage.Paths.I_SourceFingerprint import I_SourceFingerprint

if TYPE_CHECKING:
    from ....Abstract.Domain.Imaging.E_SourceKind import E_SourceKind
    from ....Abstract.Storage.Paths.I_FilePath import I_FilePath
import hashlib
from typing import final


# 以影像文件信息生成稳定指纹，排除软件生成的标注和掩码文件。
@final
class C_SourceFingerprint(I_SourceFingerprint):
    # 对输入影像文件信息计算摘要，忽略软件生成的标注和掩码输出。
    def fingerprint(self, path: I_FilePath, kind: E_SourceKind) -> str:
        from .C_SourcePathRules import C_SourcePathRules

        digest = hashlib.sha256()
        digest.update(kind.value.encode("ascii"))
        if path.is_file():
            stat = path.stat()
            digest.update(path.getName().encode("utf-8", errors="surrogatepass"))
            digest.update(str(stat.getSize()).encode("ascii"))
            digest.update(str(stat.getModifiedNs()).encode("ascii"))
            with path.open("rb") as handle:
                digest.update(handle.read(1024 * 1024))
            return digest.hexdigest()
        files = sorted(
            (
                item
                for item in path.iterdir()
                if C_SourcePathRules().is_dicom_candidate(item)
            ),
            key=lambda item: item.getName(),
        )
        if not files:
            raise ValueError(f"DICOM directory contains no candidate files: {path}")
        digest.update(str(len(files)).encode("ascii"))
        for item in files:
            stat = item.stat()
            digest.update(item.getName().encode("utf-8", errors="surrogatepass"))
            digest.update(str(stat.getSize()).encode("ascii"))
        for item in dict.fromkeys((files[0], files[len(files) // 2], files[-1])):
            with item.open("rb") as handle:
                digest.update(handle.read(1024 * 1024))
        return digest.hexdigest()
