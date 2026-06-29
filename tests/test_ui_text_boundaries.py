from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_ventilation_module_no_outdated_future_plan_text():
    text = (ROOT / "modules" / "ventilation_duct.py").read_text(encoding="utf-8")

    assert "课程设计案例模板库" not in text
    assert "本项目定位为建环工程计算工具箱，后续计划开发以下模块" not in text
    assert '"冷热源设备选型"' not in text


def test_readme_links_check_guide():
    text = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "./docs/CHECK_GUIDE.md" in text


def test_check_guide_keeps_engineering_boundary():
    text = (ROOT / "docs" / "CHECK_GUIDE.md").read_text(encoding="utf-8")

    assert "不能替代正式工程设计" in text
    assert "正式工程可直接使用" not in text
