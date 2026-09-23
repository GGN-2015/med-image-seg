"""English and Chinese user-interface localization."""

# Chinese UI copy intentionally uses full-width Chinese punctuation.
# ruff: noqa: RUF001

from __future__ import annotations

from typing import Literal, cast

UiLanguage = Literal["en", "zh"]
SUPPORTED_LANGUAGES: tuple[UiLanguage, ...] = ("en", "zh")

_TEXT: dict[str, dict[UiLanguage, str]] = {
    "window_title": {
        "en": "med-image-seg - Medical Image Polygon Annotation",
        "zh": "med-image-seg - 医疗影像多边形标注",
    },
    "toolbar_annotation": {"en": "Annotation", "zh": "标注"},
    "export_mask": {
        "en": "Export interpolated 3D mask",
        "zh": "导出含插值的 3D 掩码",
    },
    "image_collection": {"en": "Image collection", "zh": "影像集合"},
    "import_files": {"en": "Import image files", "zh": "导入影像文件"},
    "import_dicom": {"en": "Import DICOM folder", "zh": "导入 DICOM 目录"},
    "language": {"en": "Language", "zh": "语言"},
    "imported_images": {
        "en": "Imported images (double-click to load)",
        "zh": "已导入影像（双击载入）",
    },
    "annotation_grid": {"en": "Annotation grid", "zh": "标注网格"},
    "load_selected": {"en": "Load selected image", "zh": "载入选中影像"},
    "previous_slice": {"en": "Previous slice", "zh": "上一层"},
    "next_slice": {"en": "Next slice", "zh": "下一层"},
    "polygon_mode": {"en": "Polygon mode", "zh": "多边形模式"},
    "add_region": {"en": "Add region (green)", "zh": "添加区域（绿色）"},
    "erase_region": {"en": "Erase region (red)", "zh": "擦除区域（红色）"},
    "finish_polygon": {
        "en": "Close current polygon [Space]",
        "zh": "闭合当前多边形 [Space]",
    },
    "cancel_polygon": {
        "en": "Cancel current polygon [Esc]",
        "zh": "取消当前多边形 [Esc]",
    },
    "delete_last": {
        "en": "Delete last edited polygon on this slice [Ctrl+Z]",
        "zh": "删除本层最后编辑的多边形 [Ctrl+Z]",
    },
    "copy_previous": {
        "en": "Copy previous slice annotation [C]",
        "zh": "复制上一层标注 [C]",
    },
    "clear_slice": {
        "en": "Clear slice contours and restore interpolation",
        "zh": "清空本层轮廓，恢复插值",
    },
    "completed": {
        "en": "Slice reviewed; an empty slice can be a boundary keyframe [M]",
        "zh": "本层已复核；空层可作边界关键层 [M]",
    },
    "force_empty": {
        "en": "Force no segmentation on this slice",
        "zh": "本切片强制不分割",
    },
    "force_empty_tooltip": {
        "en": (
            "Keep this slice empty and block interpolation without deleting "
            "saved contours."
        ),
        "zh": "本层输出保持为空，并阻止自动插值；不会删除已保存的轮廓。",
    },
    "next_incomplete": {"en": "Go to next unreviewed slice", "zh": "跳到下一未完成层"},
    "review_progress": {"en": "Reviewed %v / %m slices", "zh": "已复核 %v / %m 层"},
    "show_interpolation": {
        "en": "Show automatic interpolation between keyframes",
        "zh": "显示中间层自动插值",
    },
    "slice_not_loaded": {
        "en": "Current slice: no image loaded",
        "zh": "当前层：尚未载入影像",
    },
    "autosave_waiting": {
        "en": "Autosave: waiting for an image",
        "zh": "自动保存：等待载入影像",
    },
    "window": {"en": "Intensity window", "zh": "灰度窗"},
    "window_level": {"en": "Level", "zh": "窗位"},
    "window_width": {"en": "Width", "zh": "窗宽"},
    "hint": {
        "en": (
            "Left-click to add vertices; right-click or double-click to close. "
            "Drag colored vertices to reshape.\nOrange/purple contours are "
            "machine-generated; green/red contours are manual.\nEvery addition, edit, "
            "deletion, or review is "
            "saved immediately to JSON beside the image.\nBlue regions are automatic "
            "interpolations between two keyframes."
        ),
        "zh": (
            "左键添加顶点，右键或双击闭合；拖动彩色顶点可修形。\n"
            "橙色/紫色为机器轮廓，绿色/红色为人工轮廓。\n"
            "每次新增、拖动、删除或复核都会立即保存到影像旁的 JSON。\n"
            "中间蓝色区域为两个关键层之间的自动插值。"
        ),
    },
    "no_images_status": {
        "en": "No images imported. Select image files or a DICOM folder.",
        "zh": "尚未导入影像。请选择影像文件或 DICOM 目录。",
    },
    "sources_added": {
        "en": "Imported {count} unique image sources. Double-click an item to load it.",
        "zh": "已导入 {count} 个去重影像来源。双击条目即可载入。",
    },
    "partial_import_title": {
        "en": "Some images could not be imported",
        "zh": "部分影像无法导入",
    },
    "choose_images_title": {"en": "Select medical images", "zh": "选择医学影像"},
    "image_filter": {
        "en": "Medical images (*.nii *.nii.gz *.ubd.npz *.dcm);;All files (*)",
        "zh": "医学影像 (*.nii *.nii.gz *.ubd.npz *.dcm);;所有文件 (*)",
    },
    "choose_dicom_title": {
        "en": "Select DICOM series folder",
        "zh": "选择 DICOM 序列目录",
    },
    "loading_message": {
        "en": "Reading and resampling:\n{path}",
        "zh": "正在读取并重采样：\n{path}",
    },
    "loading_title": {"en": "Loading image", "zh": "正在加载影像"},
    "loading_status": {"en": "Loading {name}...", "zh": "正在加载 {name}…"},
    "load_failed_title": {"en": "Unable to load image", "zh": "无法载入影像"},
    "load_failed_status": {
        "en": "Image loading failed. Select another image to continue.",
        "zh": "影像载入失败；可选择其他影像继续。",
    },
    "autosave_path": {"en": "Autosave: {path}", "zh": "自动保存：{path}"},
    "loaded_status": {
        "en": "Loaded {name}: {shape}, spacing={spacing}, modality={modality}",
        "zh": "已载入 {name}: {shape}, spacing={spacing}, modality={modality}",
    },
    "state_force_empty": {
        "en": "forced empty (saved contours are excluded from output)",
        "zh": "强制不分割（已保存轮廓暂不参与输出）",
    },
    "state_machine": {"en": "machine segmentation keyframe", "zh": "机器分割关键层"},
    "state_manual": {"en": "manual keyframe", "zh": "人工关键层"},
    "state_union": {
        "en": "machine and manual union keyframe",
        "zh": "机器与人工联合关键层",
    },
    "state_reviewed": {"en": "reviewed", "zh": "已复核"},
    "state_unreviewed": {"en": "not reviewed", "zh": "尚未复核"},
    "state_empty_boundary": {
        "en": "empty boundary keyframe (reviewed)",
        "zh": "空边界关键层（已复核）",
    },
    "state_empty_keyframe": {
        "en": "empty keyframe (not reviewed)",
        "zh": "空关键层（尚未复核）",
    },
    "state_interpolated": {
        "en": "automatic interpolation from keyframes {lower} and {upper}",
        "zh": "自动插值，来自关键层 {lower} 和 {upper}",
    },
    "state_unannotated": {
        "en": "unannotated; interpolation requires keyframes on both sides",
        "zh": "未标注；需要位于两个关键层之间才能插值",
    },
    "current_slice": {"en": "Current slice: {state}", "zh": "当前层：{state}"},
    "force_empty_delete": {
        "en": (
            "This slice is forced empty. Clear that option before deleting "
            "saved contours."
        ),
        "zh": "本层正处于强制不分割状态；取消勾选后才能删除已保存轮廓。",
    },
    "no_polygon_delete": {
        "en": "There is no polygon to delete on the current slice.",
        "zh": "当前切片没有可删除的多边形。",
    },
    "polygon_deleted": {
        "en": "Deleted the last edited polygon on the current slice.",
        "zh": "已删除当前切片最后编辑的多边形。",
    },
    "clear_title": {"en": "Clear this slice?", "zh": "清空本层？"},
    "clear_message": {
        "en": (
            "Delete all contours and review state on this slice so neighboring "
            "keyframes can interpolate it again?"
        ),
        "zh": "将删除本层全部轮廓和复核状态，使其重新使用相邻关键层插值。",
    },
    "overwrite_title": {"en": "Overwrite this slice?", "zh": "覆盖本层？"},
    "overwrite_message": {
        "en": (
            "This slice already has polygons. Replace them with the previous "
            "slice annotation?"
        ),
        "zh": "本层已有多边形。是否用上一层标注覆盖？",
    },
    "autosave_failed": {
        "en": "Autosave failed: {error}",
        "zh": "自动保存失败：{error}",
    },
    "autosave_failed_title": {"en": "Autosave failed", "zh": "自动保存失败"},
    "autosave_success": {
        "en": "Autosaved: {time}\n{path} (including .bak)",
        "zh": "自动保存：{time}\n{path}（含 .bak）",
    },
    "export_failed_title": {"en": "Export failed", "zh": "导出失败"},
    "export_complete_title": {"en": "Export complete", "zh": "导出完成"},
    "export_complete_message": {
        "en": "{path}\n\nGenerated {count} intermediate interpolated slices.",
        "zh": "{path}\n\n已生成 {count} 个中间插值层。",
    },
    "loading_close_title": {"en": "Image is loading", "zh": "正在加载"},
    "loading_close_message": {
        "en": "Wait for the current image to finish loading.",
        "zh": "请等待当前影像加载完成。",
    },
}


def normalize_language(language: str) -> UiLanguage:
    """Validate and normalize a UI language code."""

    normalized = language.lower().replace("_", "-").split("-", maxsplit=1)[0]
    if normalized not in SUPPORTED_LANGUAGES:
        choices = ", ".join(SUPPORTED_LANGUAGES)
        raise ValueError(f"unsupported language {language!r}; choose one of: {choices}")
    return cast(UiLanguage, normalized)


def translate(key: str, language: str = "en", **values: object) -> str:
    """Return a translated UI string and interpolate named values."""

    normalized = normalize_language(language)
    try:
        template = _TEXT[key][normalized]
    except KeyError as exc:
        raise KeyError(f"unknown translation key: {key}") from exc
    return template.format(**values)


__all__ = ["SUPPORTED_LANGUAGES", "UiLanguage", "normalize_language", "translate"]
