"""Check that the packages in requirements.txt are installed and importable."""

from __future__ import annotations

import importlib
import importlib.metadata
import re
import sys
from pathlib import Path
from typing import Optional


IMPORT_NAMES = {
    "opencv-python": "cv2",
    "pyserial": "serial",
}

COMPARATOR_PATTERN = re.compile(r"^(==|!=|>=|<=|>|<|~=)\s*([0-9][^,;\s]*)$")


def read_requirements(path: Path) -> list[tuple[str, str]]:
    requirements: list[tuple[str, str]] = []
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        match = re.match(r"^([A-Za-z0-9_.-]+)\s*(.*)$", line)
        if not match:
            raise ValueError(f"{path}:{line_number}: 无法解析依赖: {raw_line}")
        package_name, specifier = match.groups()
        requirements.append((package_name, specifier.strip()))
    return requirements


def version_tuple(version: str) -> tuple[object, ...]:
    parts: list[object] = []
    for part in re.split(r"[.-]", version):
        parts.append(int(part) if part.isdigit() else part.lower())
    return tuple(parts)


def satisfies(version: str, specifier: str) -> bool:
    if not specifier:
        return True
    current = version_tuple(version)
    for raw_comparator in specifier.split(","):
        comparator = raw_comparator.strip()
        match = COMPARATOR_PATTERN.match(comparator)
        if not match:
            raise ValueError(f"不支持的版本约束: {specifier}")
        operator, expected_text = match.groups()
        expected = version_tuple(expected_text)
        if operator == "==" and current != expected:
            return False
        if operator == "!=" and current == expected:
            return False
        if operator == ">=" and current < expected:
            return False
        if operator == "<=" and current > expected:
            return False
        if operator == ">" and current <= expected:
            return False
        if operator == "<" and current >= expected:
            return False
        if operator == "~=" and current < expected:
            return False
    return True


def check_package(package_name: str, specifier: str) -> bool:
    import_name = IMPORT_NAMES.get(package_name, package_name.replace("-", "_"))
    try:
        installed_version = importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        print(f"[FAIL] {package_name}: 未安装")
        return False

    version_ok = satisfies(installed_version, specifier)
    version_status = "OK" if version_ok else "不符合要求"
    print(
        f"[{'PASS' if version_ok else 'FAIL'}] {package_name}: "
        f"已安装 {installed_version}，要求 {specifier or '任意版本'} "
        f"({version_status})"
    )

    try:
        importlib.import_module(import_name)
    except ImportError as error:
        print(f"       导入失败: {error}")
        return False
    except (OSError, RuntimeError) as error:
        print(f"       导入失败: {type(error).__name__}: {error}")
        return False

    print(f"       导入成功: {import_name}")
    return version_ok


def main(requirements_path: Optional[Path] = None) -> int:
    path = requirements_path or Path(__file__).with_name("requirements.txt")
    try:
        requirements = read_requirements(path)
    except (OSError, ValueError) as error:
        print(f"[FAIL] 读取 requirements.txt 失败: {error}")
        return 1

    print(f"检查文件: {path}")
    results = [check_package(name, specifier) for name, specifier in requirements]
    passed = sum(results)
    print(f"\n结果: {passed}/{len(results)} 个依赖检查通过")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())