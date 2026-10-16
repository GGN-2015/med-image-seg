from __future__ import annotations

import ast
import re
from typing import final

from ...Abstract.Architecture.I_TestArchitecture import I_TestArchitecture


# 检查源码分层、类型命名和集合访问边界，防止重构规则回退。
@final
class C_TestArchitecture(I_TestArchitecture):
    # 检查类和方法的中文注释，禁止重新引入没有实际信息的模板句。
    def test_comments_explain_behavior_without_template_filler(self) -> None:
        from .C_ArchitectureSources import C_ArchitectureSources

        forbidden = (
            "为隔离变化",
            "为保持原有行为",
            "为限制状态访问",
            "为集中控制修改",
            "为防止行为漂移",
            "返回约定结果",
        )
        for path in C_ArchitectureSources().iterFiles():
            source = path.read_text(encoding="utf-8")
            lines = source.splitlines()
            for node in ast.walk(ast.parse(source)):
                if not isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                    continue
                start_lines = [node.lineno]
                start_lines.extend(
                    decorator.lineno for decorator in node.decorator_list
                )
                position = min(start_lines) - 1
                comments: list[str] = []
                while position > 0 and lines[position - 1].lstrip().startswith("#"):
                    comments.append(lines[position - 1].lstrip()[1:].strip())
                    position -= 1
                comment = "".join(reversed(comments))
                assert re.search(r"[\u4e00-\u9fff]", comment), (path, node.name)
                assert not any(text in comment for text in forbidden), (
                    path,
                    node.name,
                    comment,
                )

    # 检查目录容量、单文件单类型、类名、final 及抽象具体分层。
    def test_package_and_type_boundaries(self) -> None:
        from .C_ArchitectureSources import C_ArchitectureSources

        folders: dict[str, int] = {}
        for path in C_ArchitectureSources().iterFiles():
            parent = path.getParent()
            folders[str(parent)] = folders.get(str(parent), 0) + 1
            assert (parent / "__init__.py").is_file()
            if path.getName() in {"__init__.py", "__main__.py"}:
                continue
            classes = [
                node
                for node in ast.parse(path.read_text(encoding="utf-8")).body
                if isinstance(node, ast.ClassDef)
            ]
            assert len(classes) == 1
            name = classes[0].name
            assert path.getStem() == name
            assert re.fullmatch(r"(?:I_|T_|E_|C_)(?:Qt_)?[A-Z][A-Za-z0-9]*", name)
            if name.startswith("C_"):
                assert "Concrete" in str(path)
                assert any(
                    ast.unparse(base).startswith(("I_", "T_"))
                    for base in classes[0].bases
                )
                assert any(
                    ast.unparse(decorator) == "final"
                    for decorator in classes[0].decorator_list
                )
                assert not any(
                    ast.unparse(base).startswith("C_") for base in classes[0].bases
                )
            else:
                assert "Abstract" in str(path)
        assert all(count <= 7 for count in folders.values())

    # 检查模块不含全局函数或状态，仅允许入口、导出列表和局部泛型声明。
    def test_modules_do_not_define_global_state(self) -> None:
        from .C_ArchitectureSources import C_ArchitectureSources

        for path in C_ArchitectureSources().iterFiles():
            if path.getName() == "__main__.py":
                continue
            for node in ast.parse(path.read_text(encoding="utf-8")).body:
                assert not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                if isinstance(node, (ast.Assign, ast.AnnAssign)):
                    value = node.value
                    if path.getName() == "__init__.py":
                        assert isinstance(node, ast.Assign) and [
                            ast.unparse(target) for target in node.targets
                        ] == ["__all__"]
                    else:
                        assert (
                            isinstance(value, ast.Call)
                            and ast.unparse(value.func) == "TypeVar"
                        )

    # 检查抽象层不依赖框架，签名不含 Any、object 或具体类。
    def test_abstract_and_annotation_boundaries(self) -> None:
        from .C_ArchitectureSources import C_ArchitectureSources

        forbidden = {
            "PySide6",
            "scipy",
            "skimage",
            "SimpleITK",
            "ct_mri_dicom_nii_reader",
        }
        for path in C_ArchitectureSources().iterFiles():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if (
                    "Abstract" in str(path)
                    and isinstance(node, ast.ImportFrom)
                    and node.module
                ):
                    assert node.module.split(".")[0] not in forbidden
                    assert "Concrete" not in node.module.split(".")
                if isinstance(node, ast.FunctionDef):
                    annotations = [
                        argument.annotation
                        for argument in (*node.args.args, *node.args.kwonlyargs)
                        if argument.annotation is not None
                    ]
                    if node.returns is not None:
                        annotations.append(node.returns)
                    for annotation in annotations:
                        for value in ast.walk(annotation):
                            if isinstance(value, ast.Name):
                                assert value.id not in {"object", "Any"}
                                assert not value.id.startswith("C_")
                    assert not any(
                        ast.unparse(decorator) == "property"
                        for decorator in node.decorator_list
                    )

    # 检查业务 getter 不返回内部列表、字典或映射类型。
    def test_getters_do_not_expose_mutable_containers(self) -> None:
        from .C_ArchitectureSources import C_ArchitectureSources

        for path in C_ArchitectureSources().iterFiles():
            if "med_image_seg" not in str(path):
                continue
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if (
                    isinstance(node, ast.FunctionDef)
                    and node.name.startswith("get")
                    and node.returns
                ):
                    assert not any(
                        isinstance(value, ast.Name)
                        and value.id in {"list", "dict", "Mapping", "MutableMapping"}
                        for value in ast.walk(node.returns)
                    )
