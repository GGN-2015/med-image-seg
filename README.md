# med-image-seg

独立、可编程的医疗影像多多边形标注工具，支持 DICOM 序列、NIfTI 和 `.ubd.npz`。程序使用 Python 3.12 和 uv 管理环境，医学影像读取统一由 `ct_mri_dicom_nii_reader==0.1.6` 完成。

## 安装与启动

```powershell
uv sync --frozen
uv run med-image-seg
```

无参数启动时影像列表为空。可以在 GUI 中点击“导入影像文件”选择一个或多个 NIfTI、UBD 或 DICOM 文件，也可以点击“导入 DICOM 目录”。

CLI 可以提供初始影像集合；程序会自动去重并载入第一项：

```powershell
uv run med-image-seg `
  --image "D:\dicom-series" `
  --image "D:\images\pelvis.nii.gz" `
  --image "D:\images\knee.ubd.npz" `
  --spacing 0.8
```

位置参数仍然兼容。使用 `--image PATH` 打开单个影像时，程序会自动查找下表
约定位置的 JSON，校验内容指纹和体数据几何后加载并显示已有机器/人工轮廓。

检查 `cbct-bone` 的机器结果时，可直接执行：

```powershell
uv run med-image-seg --image "D:\images\scan.nii.gz"
```

## 标注文件位置

标注始终与影像放在同一目录：

| 影像类型 | 标注 JSON | 导出掩码 |
| --- | --- | --- |
| DICOM 目录或其中一个 DICOM 文件 | `<DICOM目录>/.med-image-seg.json` | `<DICOM目录>/med-image-seg-mask.nii.gz` |
| `scan.nii` / `scan.nii.gz` | `scan.med-image-seg.json` | `scan.med-image-seg-mask.nii.gz` |
| `scan.ubd.npz` | `scan.med-image-seg.json` | `scan.med-image-seg-mask.nii.gz` |

JSON 不保存源路径或 DICOM 身份字段，只保存内容指纹、重采样几何、轮廓和复核状态。每次新增多边形、拖动顶点、删除、复制、清空或复核都会立即以原子替换方式保存；同时保留 `.json.bak` 滚动备份，另有 10 秒定时兜底。

## GUI 操作

- 加载和重采样在后台线程完成；加载期间显示模态进度条，主 GUI 不可编辑。
- 左键添加顶点，右键、双击或 `Space` 闭合多边形。
- 拖动彩色顶点可修改已有多边形。
- `Ctrl+Z` 或“删除本层最后编辑的多边形”删除当前切片最近一次新增或拖动编辑的多边形。
- `C` 复制上一层标注，`M` 标记当前层已复核。
- 勾选“本切片强制不分割”后，本层输出固定为空且不再显示蓝色插值；
  已保存轮廓不会被删除，取消勾选即可恢复；新增轮廓也会自动取消该状态。
- 两个关键层之间的空层以有符号距离场动态插值，并用蓝色半透明区域显示。
- 机器轮廓以橙色/紫色显示，人工轮廓以绿色/红色显示。同层两种来源
  分别应用各自的添加/擦除操作后取并集，因此都会进入最终掩码。
- `E` 或工具栏按钮导出包含插值的三维 NIfTI 掩码。

## Python API

无初始影像启动：

```python
from med_image_seg import AnnotationApplication

app = AnnotationApplication(spacing_mm=0.8)
app.run()
```

指定初始影像集合：

```python
from med_image_seg import AnnotationApplication

app = AnnotationApplication.from_paths(
    ["D:/dicom-series", "D:/images/pelvis.nii.gz"],
    spacing_mm=0.8,
)
app.add_image("D:/images/knee.nii.gz")
app.run()
```

数据模型、插值和导出也可独立使用：

```python
from med_image_seg import (
    AnnotationExporter,
    AnnotationProject,
    ImageSource,
    MedicalVolumeReader,
    PolygonAnnotation,
)

source = ImageSource.from_path("D:/images/pelvis.nii.gz")
volume = MedicalVolumeReader(0.8).read(source.path)
project = AnnotationProject.create(
    image_id=source.source_id,
    source_fingerprint=source.fingerprint,
    volume=volume,
)
project.add_polygon(
    10,
    PolygonAnnotation(points=((20, 20), (80, 20), (50, 90))),
)
project.save(source.annotation_path)
AnnotationExporter().export(project, volume, source.mask_path)
```

公共 API 包括 `ImageSource`、`ImageCollection`、`MedicalVolumeReader`、
`AnnotationProject`、`PolygonAnnotation`、`AnnotationExporter`、
`AnnotationApplication`、`AnnotationMainWindow`、`SliceCanvas`、
`VolumeLoadThread` 和 `launch_annotation_app`。GUI 的导入、异步加载、编辑、
保存和导出方法均可直接从 Python 调用。

## 开发检查

```powershell
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv build
```
