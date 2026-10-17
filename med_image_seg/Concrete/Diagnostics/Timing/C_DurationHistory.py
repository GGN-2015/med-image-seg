from __future__ import annotations

import math
import os
import sqlite3
import sys
from contextlib import closing
from pathlib import Path
from typing import final

from ....Abstract.Diagnostics.Timing.I_MutableDurationHistory import (
    I_MutableDurationHistory,
)
from ....Abstract.Storage.Paths.I_FilePath import I_FilePath


# 把操作类别、耗时和结果写到本机 SQLite，隔离并发写入及历史文件故障。
@final
class C_DurationHistory(I_MutableDurationHistory):
    # 选择用户状态目录，或使用显式路径和环境变量指定的 profiling 文件。
    def __init__(self, path: I_FilePath | None = None) -> None:
        from ...Storage.Paths.C_FilePath import C_FilePath

        configured = os.environ.get("MED_IMAGE_SEG_PROFILE_PATH")
        if path is not None:
            self._path = path.expanduser().resolve()
        elif configured:
            self._path = C_FilePath(configured).expanduser().resolve()
        else:
            if sys.platform == "win32":
                directory = Path(
                    os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")
                )
            elif sys.platform == "darwin":
                directory = Path.home() / "Library" / "Application Support"
            else:
                directory = Path(
                    os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state")
                )
            self._path = C_FilePath(directory / "med-image-seg" / "profiling.sqlite3")

    # 返回本机耗时数据库的位置，不暴露数据库连接。
    def getPath(self) -> I_FilePath:
        return self._path

    # 使用最近二十个同类成功样本的均值；文件缺失或损坏时退回初始估计。
    def getExpectedSeconds(self, operation: str, default_seconds: float) -> float:
        if not math.isfinite(default_seconds) or default_seconds <= 0:
            raise ValueError(
                "预估耗时必须为正有限数 / Expected duration must be finite and positive"
            )
        try:
            if not self._path.is_file():
                return default_seconds
            with closing(sqlite3.connect(str(self._path), timeout=0.1)) as connection:
                samples = connection.execute(
                    "SELECT elapsed_seconds FROM operation_samples "
                    "WHERE operation = ? AND success = 1 "
                    "ORDER BY id DESC LIMIT 20",
                    (operation,),
                ).fetchall()
            durations = [
                float(sample[0])
                for sample in samples
                if math.isfinite(float(sample[0])) and float(sample[0]) >= 0
            ]
            if not durations:
                return default_seconds
            expected = sum(durations) / len(durations)
            return max(0.05, expected) if math.isfinite(expected) else default_seconds
        except (OSError, sqlite3.Error, TypeError, ValueError):
            return default_seconds

    # 以短事务追加结果并限制每类保留 128 条；磁盘故障不能打断医学影像操作。
    def record(self, operation: str, elapsed_seconds: float, success: bool) -> None:
        if not math.isfinite(elapsed_seconds) or elapsed_seconds < 0:
            return
        try:
            self._path.getParent().mkdir(parents=True, exist_ok=True)
            with (
                closing(sqlite3.connect(str(self._path), timeout=0.1)) as connection,
                connection,
            ):
                connection.execute(
                    "CREATE TABLE IF NOT EXISTS operation_samples ("
                    "id INTEGER PRIMARY KEY, operation TEXT NOT NULL, "
                    "elapsed_seconds REAL NOT NULL, success INTEGER NOT NULL, "
                    "finished_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
                )
                connection.execute(
                    "INSERT INTO operation_samples "
                    "(operation, elapsed_seconds, success) "
                    "VALUES (?, ?, ?)",
                    (operation, elapsed_seconds, int(success)),
                )
                connection.execute(
                    "DELETE FROM operation_samples WHERE operation = ? "
                    "AND id NOT IN (SELECT id FROM operation_samples "
                    "WHERE operation = ? ORDER BY id DESC LIMIT 128)",
                    (operation, operation),
                )
        except (OSError, sqlite3.Error):
            return
