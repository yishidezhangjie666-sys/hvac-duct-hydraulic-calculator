from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_v021_is_marked_as_released():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    release_notes = (ROOT / "RELEASE_NOTES_v0.2.0.md").read_text(encoding="utf-8")

    assert "当前稳定版本：`v0.2.1`" in readme
    assert "## Unreleased" in changelog
    assert "## v0.2.1 - 2026-06-30" in changelog
    assert "# v0.2.0 Release Notes" in release_notes
    assert "草稿" not in release_notes
