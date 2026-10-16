from __future__ import annotations

from typing import final

from ...Abstract.Localization.I_Localizer import I_Localizer


# 维护中英文本及语言回退规则，让业务代码通过消息键取得文案。
@final
class C_Localizer(I_Localizer):
    # 初始化中英文案表和支持的语言代码。
    def __init__(self) -> None:
        self._text_data = {
            "window_title": {
                "en": "med-image-seg - Medical Image Polygon Annotation",
                "zh": "med-image-seg - 医疗影像多边形标注",
            },
            "toolbar_annotation": {"en": "Annotation", "zh": "标注"},
            "export_mask": {
                "en": "Export interpolated 3D mask (.nii.gz)",
                "zh": "导出含插值的 3D 掩码（.nii.gz）",
            },
            "export_ubd_mask": {
                "en": "Export interpolated 3D mask (.ubd.npz)",
                "zh": "导出含插值的 3D 掩码（.ubd.npz）",
            },
            "export_annotations": {
                "en": "Export annotations (.med-image-seg.json)",
                "zh": "导出标注（.med-image-seg.json）",
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
            "previous_labeled_slice": {"en": "Prev labeled slice", "zh": "上一标注层"},
            "next_labeled_slice": {"en": "Next labeled slice", "zh": "下一标注层"},
            "labeled_slice_tooltip": {
                "en": (
                    "Jump to the nearest slice with stored polygons in this ann"
                    "otation project. Interpolation-only and empty keyframe sli"
                    "ces are skipped. Does not wrap at the volume boundaries."
                ),
                "zh": (
                    "跳转到当前编号标注中最近的有多边形的切片。跳过仅有插值或空"
                    "关键层的切片；到达边界时不循环跳转。"
                ),
            },
            "labeled_slice_title": {
                "en": "Labeled slice navigation",
                "zh": "标注层跳转",
            },
            "previous_labeled_not_found": {
                "en": "No previous labeled slice was found.",
                "zh": "未找到上一个有标注的面。",
            },
            "next_labeled_not_found": {
                "en": "No next labeled slice was found.",
                "zh": "未找到下一个有标注的面。",
            },
            "mask_coverage_name": {"en": "Mask coverage", "zh": "掩码覆盖区间"},
            "mask_coverage_tooltip": {
                "en": (
                    "Read-only coverage aligned to the slice slider. Green: non"
                    "empty mask including interpolation. Gray: no mask, includi"
                    "ng forced-empty slices."
                ),
                "zh": (
                    "与上方层号滑条对齐的只读指示器。绿色：该层最终掩码非空（含"
                    "插值）；灰色：无掩码（含强制不分割层）。"
                ),
            },
            "polygon_mode": {"en": "Polygon mode", "zh": "多边形模式"},
            "annotation_index": {"en": "Annotation number", "zh": "标注编号"},
            "annotation_index_tooltip": {
                "en": (
                    "Nonnegative integer. 0 uses the original .med-image-seg.js"
                    "on; n > 0 uses .med-image-seg-<n>.json. Switching saves th"
                    "e previous annotation. Numbered files with no polygons are"
                    " removed. Locked in read-only mode."
                ),
                "zh": (
                    "输入大于等于 0 的整数。0 使用原来的 .med-image-seg.json；n"
                    " > 0 使用 .med-image-seg-<n>.json。切换前自动保存原标注。"
                    "高编号标注没有任何多边形时不保留文件。只读模式下不可切换。"
                ),
            },
            "switching_annotation_status": {
                "en": "Loading the selected annotation and refreshing views...",
                "zh": "正在载入所选编号的标注并刷新视图…",
            },
            "annotation_switch_failed": {
                "en": "Unable to switch annotation",
                "zh": "无法切换标注编号",
            },
            "annotation_selected": {
                "en": "Annotation {index}: {path}",
                "zh": "当前标注 {index}：{path}",
            },
            "annotation_empty_status": {
                "en": (
                    "Annotation {index} has no polygons; no JSON file is kept.\n{path}"
                ),
                "zh": "标注 {index} 没有任何多边形，不保留 JSON 文件。\n{path}",
            },
            "add_region": {"en": "Add region (green)", "zh": "添加区域（绿色）"},
            "erase_region": {"en": "Erase region (red)", "zh": "擦除区域（红色）"},
            "observe_mode": {"en": "Observe (read-only)", "zh": "观察模式（只读）"},
            "preparing_observation": {
                "en": "Preparing interpolated orthogonal views...",
                "zh": "正在计算三视图插值掩码…",
            },
            "observation_failed": {
                "en": "Unable to prepare observation mode",
                "zh": "无法进入观察模式",
            },
            "observation_position": {
                "en": (
                    "Intersection: L={L}, P={P}, S={S}\nLP: cyan · PS: magenta ·"
                    " SL: yellow"
                ),
                "zh": "交点：L={L}，P={P}，S={S}\nLP：青色 · PS：品红 · SL：黄色",
            },
            "observation_hint": {
                "en": (
                    "Read-only: click any view to move the shared intersection."
                    "\nA reference line's color identifies its plane; the center"
                    " marker identifies the current plane. Wheel to zoom.\nLP re"
                    "tains control points. PS/SL show blue sections of the full"
                    " interpolated mask. Select Add/Erase to resume editing."
                ),
                "zh": (
                    "只读：点击任一视图移动三视图共享交点。\n参考线颜色对应其代"
                    "表的截面，中心十字星颜色对应当前截面；滚轮缩放。\nLP 保留控"
                    "制点；PS/SL 显示完整插值掩码的蓝色截面。选择添加或擦除可恢"
                    "复编辑。"
                ),
            },
            "observation_title": {
                "en": "{plane} · {axis}={index} · Read-only",
                "zh": "{plane} · {axis}={index} · 只读观察",
            },
            "observation_slice": {
                "en": "{axis} slice (0-based)",
                "zh": "{axis} 层号（从 0 开始）",
            },
            "observation_axes": {
                "en": "Horizontal: +{horizontal} →   Vertical: +{vertical} ↓",
                "zh": "横轴：+{horizontal} →   纵轴：+{vertical} ↓",
            },
            "finish_polygon": {
                "en": "Close current polygon [Space]",
                "zh": "闭合当前多边形 [Space]",
            },
            "cancel_polygon": {
                "en": "Cancel current polygon [Esc]",
                "zh": "取消当前多边形 [Esc]",
            },
            "closing_polygon_status": {
                "en": (
                    "Closing polygon, saving annotations, and refreshing the vi"
                    "ew... Please wait."
                ),
                "zh": "正在闭合多边形、保存标注并刷新画面，请稍候…",
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
                    "Keep this slice empty and block interpolation without dele"
                    "ting saved contours."
                ),
                "zh": "本层输出保持为空，并阻止自动插值；不会删除已保存的轮廓。",
            },
            "next_incomplete": {
                "en": "Go to next unreviewed slice",
                "zh": "跳到下一未完成层",
            },
            "review_progress": {
                "en": "Reviewed %v / %m slices",
                "zh": "已复核 %v / %m 层",
            },
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
            "load_external_mask": {"en": "Load external mask", "zh": "载入外置掩码"},
            "unload_external_mask": {
                "en": "Unload external mask",
                "zh": "卸载外置掩码",
            },
            "external_mask_title": {"en": "External mask", "zh": "外置掩码"},
            "external_mask_choose": {
                "en": "Choose an external mask",
                "zh": "选择外置掩码",
            },
            "external_mask_filter": {
                "en": "Mask files (*.nii *.nii.gz *.ubd.npz)",
                "zh": "掩码文件 (*.nii *.nii.gz *.ubd.npz)",
            },
            "external_mask_no_image": {
                "en": "Load an image before loading an external mask.",
                "zh": "请先载入影像，再载入外置掩码。",
            },
            "external_mask_loading": {
                "en": "Reading and aligning the external mask...\n{path}",
                "zh": "正在读取外置掩码并进行空间对齐…\n{path}",
            },
            "external_mask_failed": {
                "en": "Unable to load external mask",
                "zh": "无法载入外置掩码",
            },
            "external_mask_shape_error": {
                "en": "The aligned mask dimensions do not match the image.",
                "zh": "对齐后的掩码尺寸与影像不匹配。",
            },
            "external_mask_loaded": {
                "en": "External mask (read-only): {path}",
                "zh": "外置掩码（只读）：{path}",
            },
            "external_mask_unloading": {
                "en": "Unloading external mask and restoring annotations...",
                "zh": "正在卸载外置掩码并恢复原标注界面…",
            },
            "external_mask_unloaded": {
                "en": (
                    "External mask unloaded; the previous annotation view is restored."
                ),
                "zh": "外置掩码已卸载，已恢复之前的标注界面。",
            },
            "external_mask_current": {
                "en": "External mask · slice {index}\n{path}",
                "zh": "外置掩码 · 当前层 {index}\n{path}",
            },
            "external_mask_json_paused": {
                "en": "JSON saving paused; annotation {index} is locked.\n{path}",
                "zh": "JSON 保存已暂停；标注编号 {index} 已锁定。\n{path}",
            },
            "external_mask_hint": {
                "en": (
                    "External mask preview only: translucent light red regions "
                    "are not editable. All three views share the same intersect"
                    "ion.\nJSON contours and interpolation are hidden; JSON savi"
                    "ng, exports, and annotation-number changes are disabled.\nU"
                    "nload to restore the previous annotation, slice, and mode."
                ),
                "zh": (
                    "仅预览外置掩码：半透明淡红色区域不可编辑，三视图共享交点。"
                    "\nJSON 多边形及插值已隐藏，JSON 保存、导出和编号切换均已禁"
                    "用。\n卸载后恢复原来的标注、层号和模式。"
                ),
            },
            "hint": {
                "en": (
                    "Left-click to add vertices; right-click or double-click to"
                    " close. Drag colored vertices to reshape.\nOrange/purple co"
                    "ntours are machine-generated; green/red contours are manua"
                    "l.\nEvery addition, edit, deletion, or review is saved imme"
                    "diately to JSON beside the image.\nBlue regions are automat"
                    "ic interpolations between two keyframes."
                ),
                "zh": (
                    "左键添加顶点，右键或双击闭合；拖动彩色顶点可修形。\n橙色/紫"
                    "色为机器轮廓，绿色/红色为人工轮廓。\n每次新增、拖动、删除或"
                    "复核都会立即保存到影像旁的 JSON。\n中间蓝色区域为两个关键层"
                    "之间的自动插值。"
                ),
            },
            "no_images_status": {
                "en": "No images imported. Select image files or a DICOM folder.",
                "zh": "尚未导入影像。请选择影像文件或 DICOM 目录。",
            },
            "sources_added": {
                "en": (
                    "Imported {count} unique image sources. Double-click an ite"
                    "m to load it."
                ),
                "zh": "已导入 {count} 个去重影像来源。双击条目即可载入。",
            },
            "partial_import_title": {
                "en": "Some images could not be imported",
                "zh": "部分影像无法导入",
            },
            "choose_images_title": {
                "en": "Select medical images",
                "zh": "选择医学影像",
            },
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
            "state_machine": {
                "en": "machine segmentation keyframe",
                "zh": "机器分割关键层",
            },
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
                    "This slice is forced empty. Clear that option before delet"
                    "ing saved contours."
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
                    "Delete all contours and review state on this slice so neig"
                    "hboring keyframes can interpolate it again?"
                ),
                "zh": "将删除本层全部轮廓和复核状态，使其重新使用相邻关键层插值。",
            },
            "overwrite_title": {"en": "Overwrite this slice?", "zh": "覆盖本层？"},
            "overwrite_message": {
                "en": (
                    "This slice already has polygons. Replace them with the pre"
                    "vious slice annotation?"
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
            "export_annotations_complete_message": {
                "en": "{path}\n\nSaved annotation contours and review state.",
                "zh": "{path}\n\n已保存标注轮廓与审核状态。",
            },
            "export_annotations_empty_message": {
                "en": (
                    "Annotation {index} has no polygons. Its JSON and backups a"
                    "re removed instead of exporting an empty file.\n\n{path}"
                ),
                "zh": (
                    "标注 {index} 没有任何多边形，已按规则清理 JSON 及备份，不"
                    "导出空文件。\n\n{path}"
                ),
            },
            "loading_close_title": {"en": "Image is loading", "zh": "正在加载"},
            "loading_close_message": {
                "en": "Wait for the current image to finish loading.",
                "zh": "请等待当前影像加载完成。",
            },
        }

    # 返回可选的中英语言代码。
    def getSupportedLanguages(self) -> tuple[str, ...]:
        return ("en", "zh")

    # 规范中英语言代码，不支持的值按既定规则回退。
    def normalize_language(self, language: str) -> str:
        normalized = language.lower().replace("_", "-").split("-", maxsplit=1)[0]
        if normalized not in C_Localizer().getSupportedLanguages():
            choices = ", ".join(C_Localizer().getSupportedLanguages())
            raise ValueError(
                f"unsupported language {language!r}; choose one of: {choices}"
            )
        return normalized

    # 按消息键选择中英文案，缺省时回退并填入动态参数。
    def translate(
        self, key: str, language: str = "en", **values: str | int | float
    ) -> str:
        normalized = C_Localizer().normalize_language(language)
        try:
            template = self._text_data[key][normalized]
        except KeyError as exc:
            raise KeyError(f"unknown translation key: {key}") from exc
        return template.format(**values)
