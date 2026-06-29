from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_fan_pump_prestudy_doc_exists_and_has_boundaries():
    path = ROOT / "docs" / "FAN_PUMP_SELECTION_PRESTUDY.md"
    assert path.exists()

    text = path.read_text(encoding="utf-8")
    assert "风机选型校核" in text
    assert "水泵选型校核" in text
    assert "暂不计划" in text
    assert "不能替代正式工程设计" in text
    assert "正式工程可直接使用" not in text


def test_readme_links_fan_pump_prestudy():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "./docs/FAN_PUMP_SELECTION_PRESTUDY.md" in text


def test_roadmap_keeps_fan_pump_development_unfinished():
    text = (ROOT / "docs" / "ROADMAP_v0.2.0.md").read_text(encoding="utf-8")
    assert "后续开发风机 / 水泵选型校核计算函数" in text
    assert "- [ ] 后续开发风机 / 水泵选型校核计算函数" in text
