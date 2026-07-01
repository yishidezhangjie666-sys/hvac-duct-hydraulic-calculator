import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_new_docs_exist_and_are_linked_from_readme():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs = [
        "PROJECT_HANDOFF.md",
        "docs/PROJECT_SHOWCASE.md",
        "docs/PROJECT_FINAL_SUMMARY.md",
        "docs/NEXT_STEPS.md",
        "docs/PORTFOLIO_PITCH.md",
        "docs/FAQ.md",
        "docs/USER_GUIDE.md",
        "docs/WORD_EXPORT_GUIDE.md",
        "docs/SAMPLE_DATA_GUIDE.md",
        "docs/CHECK_GUIDE.md",
        "docs/ROADMAP_v0.2.1.md",
    ]
    for rel in docs:
        assert (ROOT / rel).exists(), rel
        assert f"./{rel}" in readme


def test_docs_do_not_overstate_engineering_use():
    forbidden_phrases = [
        "正式工程可直接使用",
        "可以替代正式工程设计",
        "可替代正式工程设计",
        "可以替代规范校核",
        "可替代规范校核",
        "完全自动设计",
        "厂家库自动选型",
        "正式施工图设计软件",
    ]
    for path in [
        ROOT / "README.md",
        ROOT / "PROJECT_HANDOFF.md",
        ROOT / "docs" / "PROJECT_SHOWCASE.md",
        ROOT / "docs" / "PROJECT_FINAL_SUMMARY.md",
        ROOT / "docs" / "NEXT_STEPS.md",
        ROOT / "docs" / "PORTFOLIO_PITCH.md",
        ROOT / "docs" / "FAQ.md",
        ROOT / "docs" / "USER_GUIDE.md",
        ROOT / "docs" / "WORD_EXPORT_GUIDE.md",
        ROOT / "docs" / "ROADMAP_v0.2.1.md",
    ]:
        text = path.read_text(encoding="utf-8")
        for phrase in forbidden_phrases:
            assert phrase not in text, f"{path}: {phrase}"


def test_readme_keeps_stable_version_v021():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "当前稳定版本：`v0.2.1`" in text


def test_documented_local_screenshots_exist():
    docs = [
        ROOT / "README.md",
        ROOT / "docs" / "PROJECT_SHOWCASE.md",
    ]
    markdown_image_pattern = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
    screenshot_text_pattern = re.compile(r"`?(?:\./)?(screenshots/[^`\s)]+\.(?:png|jpg|jpeg|webp))`?")

    for path in docs:
        text = path.read_text(encoding="utf-8")
        referenced = set()
        referenced.update(markdown_image_pattern.findall(text))
        referenced.update(screenshot_text_pattern.findall(text))

        for ref in referenced:
            normalized = ref.split("#", 1)[0].split("?", 1)[0]
            if normalized.startswith("./"):
                normalized = normalized[2:]
            if normalized.startswith("screenshots/"):
                assert (ROOT / normalized).exists(), f"{path}: {ref}"
