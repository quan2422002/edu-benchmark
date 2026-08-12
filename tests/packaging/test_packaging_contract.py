"""Packaging, import, environment, and offline-CI contract tests for Plan 02."""

from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


def _pyproject() -> dict:
    with (ROOT / "pyproject.toml").open("rb") as handle:
        return tomllib.load(handle)


def _requirements() -> set[str]:
    return {
        line.strip()
        for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def test_pyproject_uses_src_layout_and_python_312() -> None:
    data = _pyproject()
    assert data["project"]["requires-python"] == ">=3.12,<3.13"
    package_find = data["tool"]["setuptools"]["packages"]["find"]
    assert package_find["where"] == ["src"]
    assert package_find["include"] == ["edu_benchmark*"]


def test_full_requirements_equal_core_and_optional_dependency_groups() -> None:
    project = _pyproject()["project"]
    declared = set(project["dependencies"])
    for group in ("dev", "providers"):
        declared.update(project["optional-dependencies"][group])
    assert _requirements() == declared


def test_environment_spec_installs_requirements_and_editable_project() -> None:
    data = yaml.safe_load((ROOT / "environment.yml").read_text(encoding="utf-8"))
    assert data["name"] == "benchmark_env"
    assert "python=3.12" in data["dependencies"]
    pip_section = next(
        item["pip"]
        for item in data["dependencies"]
        if isinstance(item, dict) and "pip" in item
    )
    assert pip_section == ["-r requirements.txt", "-e ."]


def test_source_and_active_python_entrypoints_do_not_mutate_import_paths() -> None:
    forbidden_import = "from " + "src."
    forbidden_path_mutation = "sys" + ".path"
    for root in (ROOT / "src", ROOT / "scripts", ROOT / "tests"):
        for path in root.rglob("*.py"):
            if path == Path(__file__):
                continue
            content = path.read_text(encoding="utf-8")
            assert forbidden_import not in content, path
            assert forbidden_path_mutation not in content, path
    assert not (ROOT / "tests" / "conftest.py").exists()


def test_installed_packages_import_outside_repository(tmp_path: Path) -> None:
    command = [
        sys.executable,
        "-I",
        "-c",
        (
            "from edu_benchmark import model_providers, requirement_scoring; "
            "print(model_providers.__file__); print(requirement_scoring.__file__)"
        ),
    ]
    result = subprocess.run(
        command,
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "src/edu_benchmark/model_providers/__init__.py" in result.stdout
    assert "src/edu_benchmark/requirement_scoring/__init__.py" in result.stdout


def test_core_import_does_not_load_optional_provider_packages(tmp_path: Path) -> None:
    script = """
import sys

class BlockOptionalProviders:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.partition(".")[0] in {"dotenv", "google", "openai", "tqdm"}:
            raise ModuleNotFoundError(f"blocked optional provider: {fullname}")
        return None

sys.meta_path.insert(0, BlockOptionalProviders())
import edu_benchmark
import edu_benchmark.requirement_scoring
print(edu_benchmark.__file__)
"""
    result = subprocess.run(
        [sys.executable, "-I", "-c", script],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "src/edu_benchmark/__init__.py" in result.stdout


def test_ci_is_offline_after_dependency_install() -> None:
    workflow = (ROOT / ".github/workflows/offline-tests.yml").read_text(
        encoding="utf-8"
    )
    assert "actions/checkout@v6" in workflow
    assert "actions/setup-python@v6" in workflow
    assert "python-version: \"3.12\"" in workflow
    assert 'python -m pip install -e ".[dev]"' in workflow
    assert "Run provider-independent offline tests" in workflow
    assert "Run self-contained offline test suite" in workflow
    assert "Install pinned dependencies and editable package" in workflow
    assert "python -m pytest -q" in workflow
    assert "validate_experiment.py" in workflow
    for secret in ("OPENAI_API_KEY", "GOOGLE_APPLICATION_CREDENTIALS", "secrets."):
        assert secret not in workflow
