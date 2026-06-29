from pathlib import Path
import re
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_required_project_files_exist():
    required_paths = [
        "README.md",
        "AGENTS.md",
        "requirements.txt",
        "app.py",
        "modules/ventilation_duct.py",
        "modules/air_conditioning_water.py",
        "modules/terminal_equipment.py",
        "modules/heat_cold_source.py",
        "modules/fan_pump_selection.py",
        "utils",
    ]
    for rel_path in required_paths:
        assert (ROOT / rel_path).exists(), rel_path


def test_readme_screenshot_references_exist():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    refs = re.findall(r"\]\((?:\./)?(screenshots/[^)]+\.png)\)", readme)
    assert refs, "README should reference screenshots"
    missing = [ref for ref in refs if not (ROOT / ref).exists()]
    assert missing == []


def test_gitignore_keeps_local_agent_runtime_untracked():
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert ".agents/" in gitignore
    assert "skills-lock.json" in gitignore


def test_local_agent_runtime_files_are_not_tracked_by_git():
    if not (ROOT / ".git").exists():
        pytest.skip("not running inside a Git repository")

    result = subprocess.run(
        ["git", "ls-files", ".agents", "skills-lock.json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert result.stdout.strip() == ""


def test_app_includes_fan_pump_selection_entry():
    app_text = (ROOT / "app.py").read_text(encoding="utf-8")
    module_text = (ROOT / "modules" / "fan_pump_selection.py").read_text(encoding="utf-8")

    assert "render_fan_pump_selection_module" in app_text
    assert "风机 / 水泵选型校核" in app_text
    assert "render_fan_pump_selection_module" in module_text

    for module_name in [
        "通风风管水力计算",
        "空调水系统水力计算",
        "空调末端设备初步选型",
        "冷热源设备初步选型",
    ]:
        assert module_name in app_text
