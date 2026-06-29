"""
风机 / 水泵选型校核模块

本文件仅包含简化选型校核的纯计算函数和示例数据。
Streamlit 页面接入将在后续步骤完成。
"""

import pandas as pd


FAN_SAMPLE_DATA = {
    "scheme_id": ["FAN-1", "FAN-2", "FAN-3", "FAN-4", "FAN-5"],
    "service_system": ["S-1 排风系统", "S-2 排风系统", "新风系统", "地下室排风", "小型排风"],
    "required_airflow_m3h": [12000.0, 8500.0, 6000.0, 18000.0, 3000.0],
    "required_pressure_pa": [650.0, 720.0, 450.0, 900.0, 300.0],
    "airflow_factor": [1.10, 1.10, 1.10, 1.10, 1.10],
    "pressure_factor": [1.15, 1.15, 1.15, 1.20, 1.15],
    "rated_airflow_m3h": [14000.0, 8500.0, 7600.0, 30000.0, 0.0],
    "rated_pressure_pa": [850.0, 1000.0, 420.0, 1600.0, 500.0],
    "motor_power_kw": [5.0, 4.0, 3.0, 15.0, 1.5],
    "fan_efficiency": [0.62, 0.58, 0.55, 0.60, 0.50],
    "remark": ["建议可用示例", "风量不足示例", "风压不足示例", "余量明显偏大示例", "需复核示例"],
}


PUMP_SAMPLE_DATA = {
    "scheme_id": ["PUMP-1", "PUMP-2", "PUMP-3", "PUMP-4", "PUMP-5"],
    "service_system": ["冷冻水泵", "热水循环泵", "冷却水泵", "补水泵", "小型循环泵"],
    "required_flow_m3h": [90.0, 60.0, 130.0, 8.0, 20.0],
    "required_head_m": [28.0, 24.0, 22.0, 18.0, 12.0],
    "flow_factor": [1.10, 1.10, 1.10, 1.05, 1.10],
    "head_factor": [1.15, 1.15, 1.10, 1.10, 1.15],
    "rated_flow_m3h": [110.0, 58.0, 160.0, 20.0, 0.0],
    "rated_head_m": [36.0, 34.0, 20.0, 40.0, 0.0],
    "motor_power_kw": [15.0, 7.5, 11.0, 5.5, 0.0],
    "pump_efficiency": [0.68, 0.62, 0.70, 0.48, 0.50],
    "remark": ["建议可用示例", "流量不足示例", "扬程不足示例", "余量偏大示例", "需复核示例"],
}


FAN_INPUT_COLUMNS = [
    "required_airflow_m3h",
    "required_pressure_pa",
    "airflow_factor",
    "pressure_factor",
    "rated_airflow_m3h",
    "rated_pressure_pa",
    "motor_power_kw",
    "fan_efficiency",
]


PUMP_INPUT_COLUMNS = [
    "required_flow_m3h",
    "required_head_m",
    "flow_factor",
    "head_factor",
    "rated_flow_m3h",
    "rated_head_m",
    "motor_power_kw",
    "pump_efficiency",
]


SELECTION_NOTES = {
    "建议可用": "当前参数在简化校核范围内，仍需结合设备样本和工程背景复核。",
    "拟选偏小": "至少有一项能力低于修正后需求，应优先复核系统需求和拟选设备参数。",
    "余量偏大": "设备能力高于需求，应关注运行调节、初投资和部分负荷效率。",
    "明显偏大": "设备能力明显高于需求，建议重点复核容量配置和运行点。",
    "需复核": "输入缺失、非正或效率参数异常，应先复核基础数据。",
}


def _as_dataframe(data):
    """Return a defensive DataFrame copy from dict-like data or a DataFrame."""
    if isinstance(data, pd.DataFrame):
        return data.copy()
    return pd.DataFrame(data).copy()


def _safe_number(value):
    if bool(pd.isna(value)):
        return pd.NA
    try:
        return float(value)
    except (TypeError, ValueError):
        return pd.NA


def _safe_required(value, factor):
    value = _safe_number(value)
    factor = _safe_number(factor)
    if pd.isna(value) or pd.isna(factor) or value <= 0 or factor <= 0:
        return pd.NA
    return value * factor


def _safe_margin(rated, required):
    rated = _safe_number(rated)
    required = _safe_number(required)
    if pd.isna(rated) or pd.isna(required) or rated <= 0 or required <= 0:
        return pd.NA
    return rated / required - 1


def _safe_fan_power(airflow_m3h, pressure_pa, efficiency):
    airflow_m3h = _safe_number(airflow_m3h)
    pressure_pa = _safe_number(pressure_pa)
    efficiency = _safe_number(efficiency)
    if (
        pd.isna(airflow_m3h)
        or pd.isna(pressure_pa)
        or pd.isna(efficiency)
        or airflow_m3h <= 0
        or pressure_pa <= 0
        or efficiency <= 0
    ):
        return pd.NA
    return airflow_m3h * pressure_pa / (3600 * 1000 * efficiency)


def _safe_pump_power(flow_m3h, head_m, efficiency, rho=1000.0, g=9.81):
    flow_m3h = _safe_number(flow_m3h)
    head_m = _safe_number(head_m)
    efficiency = _safe_number(efficiency)
    rho = _safe_number(rho)
    g = _safe_number(g)
    if (
        pd.isna(flow_m3h)
        or pd.isna(head_m)
        or pd.isna(efficiency)
        or pd.isna(rho)
        or pd.isna(g)
        or flow_m3h <= 0
        or head_m <= 0
        or efficiency <= 0
        or rho <= 0
        or g <= 0
    ):
        return pd.NA
    flow_m3s = flow_m3h / 3600
    return rho * g * flow_m3s * head_m / (1000 * efficiency)


def _capacity_status(value):
    if pd.isna(value):
        return "需复核"
    if value < 0:
        return "不足"
    if value <= 0.20:
        return "合理"
    if value <= 0.50:
        return "偏大"
    return "明显偏大"


def _selection_conclusion(statuses):
    status_set = set(statuses)
    if "不足" in status_set:
        return "拟选偏小"
    if "需复核" in status_set:
        return "需复核"
    if "明显偏大" in status_set:
        return "明显偏大"
    if "偏大" in status_set:
        return "余量偏大"
    return "建议可用"


def _selection_note(conclusion):
    return SELECTION_NOTES.get(conclusion, SELECTION_NOTES["需复核"])


def _ensure_columns(df, columns):
    for column in columns:
        if column not in df.columns:
            df[column] = pd.NA
    return df


def calculate_fan_selection(df):
    """计算风机简化选型校核结果。"""
    result = _ensure_columns(_as_dataframe(df), FAN_INPUT_COLUMNS)
    result["所需风量 (m³/h)"] = result.apply(
        lambda row: _safe_required(row["required_airflow_m3h"], row["airflow_factor"]),
        axis=1,
    )
    result["所需风压 (Pa)"] = result.apply(
        lambda row: _safe_required(row["required_pressure_pa"], row["pressure_factor"]),
        axis=1,
    )
    result["风量余量"] = result.apply(
        lambda row: _safe_margin(row["rated_airflow_m3h"], row["所需风量 (m³/h)"]),
        axis=1,
    )
    result["风压余量"] = result.apply(
        lambda row: _safe_margin(row["rated_pressure_pa"], row["所需风压 (Pa)"]),
        axis=1,
    )
    result["风机轴功率参考 (kW)"] = result.apply(
        lambda row: _safe_fan_power(
            row["所需风量 (m³/h)"],
            row["所需风压 (Pa)"],
            row["fan_efficiency"],
        ),
        axis=1,
    )
    result["电机功率余量"] = result.apply(
        lambda row: _safe_margin(row["motor_power_kw"], row["风机轴功率参考 (kW)"]),
        axis=1,
    )
    result["风量校核"] = result["风量余量"].apply(_capacity_status)
    result["风压校核"] = result["风压余量"].apply(_capacity_status)
    result["电机功率校核"] = result["电机功率余量"].apply(_capacity_status)
    result["选型结论"] = result[["风量校核", "风压校核", "电机功率校核"]].apply(
        _selection_conclusion,
        axis=1,
    )
    result["复核建议"] = result["选型结论"].apply(_selection_note)
    return result


def calculate_pump_selection(df, rho=1000.0, g=9.81):
    """计算水泵简化选型校核结果。"""
    result = _ensure_columns(_as_dataframe(df), PUMP_INPUT_COLUMNS)
    result["所需流量 (m³/h)"] = result.apply(
        lambda row: _safe_required(row["required_flow_m3h"], row["flow_factor"]),
        axis=1,
    )
    result["所需扬程 (m)"] = result.apply(
        lambda row: _safe_required(row["required_head_m"], row["head_factor"]),
        axis=1,
    )
    result["流量余量"] = result.apply(
        lambda row: _safe_margin(row["rated_flow_m3h"], row["所需流量 (m³/h)"]),
        axis=1,
    )
    result["扬程余量"] = result.apply(
        lambda row: _safe_margin(row["rated_head_m"], row["所需扬程 (m)"]),
        axis=1,
    )
    result["水泵轴功率参考 (kW)"] = result.apply(
        lambda row: _safe_pump_power(
            row["所需流量 (m³/h)"],
            row["所需扬程 (m)"],
            row["pump_efficiency"],
            rho=rho,
            g=g,
        ),
        axis=1,
    )
    result["电机功率余量"] = result.apply(
        lambda row: _safe_margin(row["motor_power_kw"], row["水泵轴功率参考 (kW)"]),
        axis=1,
    )
    result["流量校核"] = result["流量余量"].apply(_capacity_status)
    result["扬程校核"] = result["扬程余量"].apply(_capacity_status)
    result["电机功率校核"] = result["电机功率余量"].apply(_capacity_status)
    result["选型结论"] = result[["流量校核", "扬程校核", "电机功率校核"]].apply(
        _selection_conclusion,
        axis=1,
    )
    result["复核建议"] = result["选型结论"].apply(_selection_note)
    return result
