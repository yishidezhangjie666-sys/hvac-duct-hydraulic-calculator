"""Validation status explanations shared by equipment selection modules."""


STATUS_EXPLANATIONS = {
    "合理": "当前参数在简化校核范围内，仍需结合工程背景和设备样本复核。",
    "适合估算": "当前参数适合进行简化估算，仍需结合工程背景和设备样本复核。",
    "建议可用": "当前参数在简化校核范围内，仍需结合工程背景和设备样本复核。",
    "不足": "至少有一项能力低于需求，应优先复核负荷、风量、设备容量或台数。",
    "拟选偏小": "至少有一项能力低于需求，应优先复核负荷、风量、设备容量或台数。",
    "偏大": "设备能力高于需求，应关注初投资、运行调节、舒适性和部分负荷效率。",
    "余量偏大": "设备能力高于需求，应关注初投资、运行调节、舒适性和部分负荷效率。",
    "明显偏大": "设备能力明显高于需求，建议重点复核容量配置和分台策略。",
    "需复核": "输入参数、工况条件或温差 / 焓差条件不适合直接判断，应先复核基础数据。",
    "焓差需复核": "室外 / 室内空气焓差条件不适合直接估算，应先复核焓值和季节工况。",
    "温差需复核": "供回水温差不在常见简化范围内，应复核系统温差设定和运行工况。",
    "容量可用，温差需复核": "容量基本满足，但供回水温差不在常见简化范围内，应复核系统温差设定和运行工况。",
}

DEFAULT_EXPLANATION = "该状态为简化校核提示，应结合输入参数、设备样本和工程背景复核。"


def _status_text(status):
    if status is None:
        return ""
    text = str(status).strip()
    return "" if text in {"", "nan", "NaN", "<NA>", "None"} else text


def explain_status(status):
    """Return a concise explanation for a validation status."""
    return STATUS_EXPLANATIONS.get(_status_text(status), DEFAULT_EXPLANATION)


def explain_selection_conclusion(conclusion):
    """Return a concise explanation for an overall selection conclusion."""
    return explain_status(conclusion)


def build_status_summary_rows(df, status_columns, conclusion_column="选型结论"):
    """Build count rows for status and conclusion columns in a DataFrame."""
    rows = []
    if df is None or getattr(df, "empty", True):
        return rows

    columns = [col for col in status_columns if col in df.columns]
    if conclusion_column in df.columns and conclusion_column not in columns:
        columns.append(conclusion_column)

    for col in columns:
        counts = df[col].dropna().astype(str).value_counts()
        for status, count in counts.items():
            if _status_text(status):
                rows.append((f"{col} - {status}", f"{int(count)} 项"))
    return rows


def build_recommendation_rows(df, conclusion_column="选型结论"):
    """Build unique recommendation text from overall selection conclusions."""
    if df is None or getattr(df, "empty", True) or conclusion_column not in df.columns:
        return [DEFAULT_EXPLANATION]

    rows = []
    seen = set()
    for conclusion in df[conclusion_column].dropna().astype(str):
        explanation = explain_selection_conclusion(conclusion)
        if explanation not in seen:
            rows.append(explanation)
            seen.add(explanation)
    return rows or [DEFAULT_EXPLANATION]
