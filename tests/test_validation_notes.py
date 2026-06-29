from utils.validation_notes import (
    build_recommendation_rows,
    explain_selection_conclusion,
)


def test_selection_conclusion_explanations_keep_review_boundary():
    assert "复核" in explain_selection_conclusion("建议可用")
    assert any(word in explain_selection_conclusion("拟选偏小") for word in ["负荷", "容量"])
    assert any(word in explain_selection_conclusion("余量偏大") for word in ["运行调节", "初投资"])
    assert any(word in explain_selection_conclusion("需复核") for word in ["输入参数", "工况"])

    all_text = "\n".join(
        [
            explain_selection_conclusion("建议可用"),
            explain_selection_conclusion("拟选偏小"),
            explain_selection_conclusion("余量偏大"),
            explain_selection_conclusion("需复核"),
        ]
    )
    assert "正式工程可直接使用" not in all_text


def test_build_recommendation_rows_deduplicates_conclusions():
    import pandas as pd

    rows = build_recommendation_rows(
        pd.DataFrame({"选型结论": ["建议可用", "建议可用", "拟选偏小"]})
    )

    assert len(rows) == 2
    assert any("负荷" in row or "容量" in row for row in rows)
