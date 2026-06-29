"""
风机 / 水泵选型校核模块

本文件包含简化选型校核的纯计算函数、示例数据和 Streamlit 页面渲染。
"""

import pandas as pd
import streamlit as st

from utils.export_utils import export_formatted_excel, get_csv_bytes
from utils.validation_notes import build_recommendation_rows, build_status_summary_rows
from utils.word_report import build_calculation_report_docx


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


FAN_EXPORT_MAP = {
    "scheme_id": "方案编号",
    "service_system": "服务系统",
    "required_airflow_m3h": "系统所需风量（m³/h）",
    "required_pressure_pa": "系统所需风压（Pa）",
    "airflow_factor": "风量安全系数",
    "pressure_factor": "风压安全系数",
    "rated_airflow_m3h": "拟选风机额定风量（m³/h）",
    "rated_pressure_pa": "拟选风机全压（Pa）",
    "motor_power_kw": "电机功率（kW）",
    "fan_efficiency": "风机效率",
    "所需风量 (m³/h)": "所需风量（m³/h）",
    "所需风压 (Pa)": "所需风压（Pa）",
    "风量余量": "风量余量",
    "风压余量": "风压余量",
    "风机轴功率参考 (kW)": "风机轴功率参考（kW）",
    "电机功率余量": "电机功率余量",
    "风量校核": "风量校核",
    "风压校核": "风压校核",
    "电机功率校核": "电机功率校核",
    "选型结论": "选型结论",
    "复核建议": "复核建议",
    "remark": "备注",
}


PUMP_EXPORT_MAP = {
    "scheme_id": "方案编号",
    "service_system": "服务系统",
    "required_flow_m3h": "系统所需流量（m³/h）",
    "required_head_m": "系统所需扬程（m）",
    "flow_factor": "流量安全系数",
    "head_factor": "扬程安全系数",
    "rated_flow_m3h": "拟选水泵额定流量（m³/h）",
    "rated_head_m": "拟选水泵扬程（m）",
    "motor_power_kw": "电机功率（kW）",
    "pump_efficiency": "水泵效率",
    "所需流量 (m³/h)": "所需流量（m³/h）",
    "所需扬程 (m)": "所需扬程（m）",
    "流量余量": "流量余量",
    "扬程余量": "扬程余量",
    "水泵轴功率参考 (kW)": "水泵轴功率参考（kW）",
    "电机功率余量": "电机功率余量",
    "流量校核": "流量校核",
    "扬程校核": "扬程校核",
    "电机功率校核": "电机功率校核",
    "选型结论": "选型结论",
    "复核建议": "复核建议",
    "remark": "备注",
}


FAN_REPORT_INPUT_COLUMNS = [
    "方案编号",
    "服务系统",
    "系统所需风量（m³/h）",
    "系统所需风压（Pa）",
    "风量安全系数",
    "风压安全系数",
    "拟选风机额定风量（m³/h）",
    "拟选风机全压（Pa）",
    "电机功率（kW）",
    "风机效率",
]


FAN_REPORT_RESULT_COLUMNS = [
    "方案编号",
    "所需风量（m³/h）",
    "所需风压（Pa）",
    "风量余量",
    "风压余量",
    "风机轴功率参考（kW）",
    "电机功率余量",
    "风量校核",
    "风压校核",
    "电机功率校核",
    "选型结论",
    "复核建议",
]


PUMP_REPORT_INPUT_COLUMNS = [
    "方案编号",
    "服务系统",
    "系统所需流量（m³/h）",
    "系统所需扬程（m）",
    "流量安全系数",
    "扬程安全系数",
    "拟选水泵额定流量（m³/h）",
    "拟选水泵扬程（m）",
    "电机功率（kW）",
    "水泵效率",
]


PUMP_REPORT_RESULT_COLUMNS = [
    "方案编号",
    "所需流量（m³/h）",
    "所需扬程（m）",
    "流量余量",
    "扬程余量",
    "水泵轴功率参考（kW）",
    "电机功率余量",
    "流量校核",
    "扬程校核",
    "电机功率校核",
    "选型结论",
    "复核建议",
]


FAN_FORMULA_ROWS = [
    ("修正后所需风量", "L_need = L_required × K_L", "L_need：m³/h"),
    ("修正后所需风压", "P_need = P_required × K_P", "P_need：Pa"),
    ("风量余量", "η_L = L_rated / L_need - 1", "η_L：风量余量"),
    ("风压余量", "η_P = P_rated / P_need - 1", "η_P：风压余量"),
    ("轴功率参考", "N_ref = L_need × P_need / (3600 × 1000 × η_fan)", "N_ref：kW"),
    ("电机功率余量", "η_N = N_motor / N_ref - 1", "η_N：电机功率余量"),
]


PUMP_FORMULA_ROWS = [
    ("修正后所需流量", "G_need = G_required × K_G", "G_need：m³/h"),
    ("修正后所需扬程", "H_need = H_required × K_H", "H_need：m"),
    ("流量换算", "Q = G_need / 3600", "Q：m³/s"),
    ("流量余量", "η_G = G_rated / G_need - 1", "η_G：流量余量"),
    ("扬程余量", "η_H = H_rated / H_need - 1", "η_H：扬程余量"),
    ("轴功率参考", "N_ref = ρgQH_need / (1000 × η_pump)", "N_ref：kW"),
    ("电机功率余量", "η_N = N_motor / N_ref - 1", "η_N：电机功率余量"),
]


FORMULA_STYLE = """
<style>
.formula-table {
    width: 100%;
    border-collapse: collapse;
}
.formula-table th, .formula-table td {
    border: 1px solid rgba(255,255,255,0.18);
    padding: 10px 14px;
    text-align: left;
}
.formula-table th {
    font-weight: 700;
}
.formula-table sub {
    vertical-align: sub;
    font-size: 75%;
    line-height: 0;
}
.formula-table sup {
    vertical-align: super;
    font-size: 75%;
    line-height: 0;
}
</style>
"""


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


def _empty_fan_df():
    return pd.DataFrame(
        {
            "scheme_id": pd.Series(dtype="str"),
            "service_system": pd.Series(dtype="str"),
            "required_airflow_m3h": pd.Series(dtype="float64"),
            "required_pressure_pa": pd.Series(dtype="float64"),
            "airflow_factor": pd.Series(dtype="float64"),
            "pressure_factor": pd.Series(dtype="float64"),
            "rated_airflow_m3h": pd.Series(dtype="float64"),
            "rated_pressure_pa": pd.Series(dtype="float64"),
            "motor_power_kw": pd.Series(dtype="float64"),
            "fan_efficiency": pd.Series(dtype="float64"),
            "remark": pd.Series(dtype="str"),
        }
    )


def _empty_pump_df():
    return pd.DataFrame(
        {
            "scheme_id": pd.Series(dtype="str"),
            "service_system": pd.Series(dtype="str"),
            "required_flow_m3h": pd.Series(dtype="float64"),
            "required_head_m": pd.Series(dtype="float64"),
            "flow_factor": pd.Series(dtype="float64"),
            "head_factor": pd.Series(dtype="float64"),
            "rated_flow_m3h": pd.Series(dtype="float64"),
            "rated_head_m": pd.Series(dtype="float64"),
            "motor_power_kw": pd.Series(dtype="float64"),
            "pump_efficiency": pd.Series(dtype="float64"),
            "remark": pd.Series(dtype="str"),
        }
    )


def _rename_export_columns(df, col_map):
    available = {key: value for key, value in col_map.items() if key in df.columns}
    return df[list(available.keys())].rename(columns=available)


def _format_percent_columns(df, columns):
    result = df.copy()
    for column in columns:
        if column in result.columns:
            result[column] = result[column].apply(
                lambda value: "" if pd.isna(value) else f"{value:.1%}"
            )
    return result


def _format_number_columns(df, columns, digits=2):
    result = df.copy()
    for column in columns:
        if column in result.columns:
            result[column] = result[column].apply(
                lambda value: "" if pd.isna(value) else f"{value:.{digits}f}"
            )
    return result


def _blank_missing_export_values(df):
    return df.apply(
        lambda col: col.astype(object).map(lambda value: "" if pd.isna(value) else value)
    )


def _select_report_columns(df, columns):
    available = [column for column in columns if column in df.columns]
    return df[available].copy()


def _summary_rows(df):
    return [
        ("方案数量", f"{len(df)} 个"),
        ("拟选偏小", f"{(df['选型结论'] == '拟选偏小').sum()} 项"),
        ("余量偏大", f"{(df['选型结论'].isin(['余量偏大', '明显偏大'])).sum()} 项"),
        ("需复核", f"{(df['选型结论'] == '需复核').sum()} 项"),
    ]


def _unique_notes(notes):
    result = []
    seen = set()
    for note in notes:
        if note and note not in seen:
            result.append(note)
            seen.add(note)
    return result


def _render_validation_interpretation(result, status_columns, summary_items, recommendations):
    st.divider()
    st.subheader("校核结果解读")

    cols = st.columns(len(summary_items))
    for col_obj, (label, value) in zip(cols, summary_items):
        col_obj.metric(label, value)

    status_rows = build_status_summary_rows(result, status_columns)
    with st.expander("查看状态统计明细"):
        for label, value in status_rows:
            st.markdown(f"- {label}：{value}")

    st.markdown("**复核建议**")
    for note in _unique_notes(recommendations + build_recommendation_rows(result)):
        st.markdown(f"- {note}")


def _build_fan_word_report(df_export, summary_rows):
    return build_calculation_report_docx(
        title="风机选型校核计算说明书",
        module_name="风机选型校核",
        description="用于风机风量、风压和电机功率的简化初步选型校核。",
        input_tables=[
            {
                "title": "系统需求与拟选风机参数",
                "data": _select_report_columns(df_export, FAN_REPORT_INPUT_COLUMNS),
            },
        ],
        result_tables=[
            {
                "title": "风机选型校核结果",
                "data": _select_report_columns(df_export, FAN_REPORT_RESULT_COLUMNS),
            },
        ],
        summary_rows=summary_rows,
        formula_rows=FAN_FORMULA_ROWS,
        notes=[
            "风机功率为简化参考，不能作为最终电机选型依据。",
            "实际风机选型应结合厂家样本、性能曲线、运行点、效率、噪声和安装条件复核。",
        ],
    )


def _build_pump_word_report(df_export, summary_rows):
    return build_calculation_report_docx(
        title="水泵选型校核计算说明书",
        module_name="水泵选型校核",
        description="用于水泵流量、扬程和电机功率的简化初步选型校核。",
        input_tables=[
            {
                "title": "系统需求与拟选水泵参数",
                "data": _select_report_columns(df_export, PUMP_REPORT_INPUT_COLUMNS),
            },
        ],
        result_tables=[
            {
                "title": "水泵选型校核结果",
                "data": _select_report_columns(df_export, PUMP_REPORT_RESULT_COLUMNS),
            },
        ],
        summary_rows=summary_rows,
        formula_rows=PUMP_FORMULA_ROWS,
        notes=[
            "水泵功率为简化参考，不能作为最终电机选型依据。",
            "实际水泵选型应结合厂家样本、性能曲线、运行点、汽蚀余量、并联运行、变频控制和安装条件复核。",
        ],
    )


def _fan_formula_table():
    st.markdown(
        FORMULA_STYLE
        + """
<table class="formula-table">
<thead>
<tr><th>计算项目</th><th>公式</th><th>单位说明</th></tr>
</thead>
<tbody>
<tr><td>修正后所需风量</td><td><span translate="no">L<sub>need</sub> = L<sub>required</sub> × K<sub>L</sub></span></td><td><span translate="no">L<sub>need</sub></span>：修正后所需风量，<span translate="no">m³/h</span></td></tr>
<tr><td>修正后所需风压</td><td><span translate="no">P<sub>need</sub> = P<sub>required</sub> × K<sub>P</sub></span></td><td><span translate="no">P<sub>need</sub></span>：修正后所需风压，<span translate="no">Pa</span>（帕）</td></tr>
<tr><td>风量余量</td><td><span translate="no">η<sub>L</sub> = L<sub>rated</sub> / L<sub>need</sub> - 1</span></td><td><span translate="no">η<sub>L</sub></span>：风量余量</td></tr>
<tr><td>风压余量</td><td><span translate="no">η<sub>P</sub> = P<sub>rated</sub> / P<sub>need</sub> - 1</span></td><td><span translate="no">η<sub>P</sub></span>：风压余量</td></tr>
<tr><td>轴功率参考</td><td><span translate="no">N<sub>ref</sub> = L<sub>need</sub> × P<sub>need</sub> / (3600 × 1000 × η<sub>fan</sub>)</span></td><td><span translate="no">N<sub>ref</sub></span>：风机轴功率参考，<span translate="no">kW</span></td></tr>
<tr><td>电机功率余量</td><td><span translate="no">η<sub>N</sub> = N<sub>motor</sub> / N<sub>ref</sub> - 1</span></td><td><span translate="no">η<sub>N</sub></span>：电机功率余量</td></tr>
</tbody>
</table>
""",
        unsafe_allow_html=True,
    )


def _pump_formula_table():
    st.markdown(
        FORMULA_STYLE
        + """
<table class="formula-table">
<thead>
<tr><th>计算项目</th><th>公式</th><th>单位说明</th></tr>
</thead>
<tbody>
<tr><td>修正后所需流量</td><td><span translate="no">G<sub>need</sub> = G<sub>required</sub> × K<sub>G</sub></span></td><td><span translate="no">G<sub>need</sub></span>：修正后所需流量，<span translate="no">m³/h</span></td></tr>
<tr><td>修正后所需扬程</td><td><span translate="no">H<sub>need</sub> = H<sub>required</sub> × K<sub>H</sub></span></td><td><span translate="no">H<sub>need</sub></span>：修正后所需扬程，<span translate="no">m</span></td></tr>
<tr><td>流量换算</td><td><span translate="no">Q = G<sub>need</sub> / 3600</span></td><td><span translate="no">Q</span>：<span translate="no">m³/s</span></td></tr>
<tr><td>流量余量</td><td><span translate="no">η<sub>G</sub> = G<sub>rated</sub> / G<sub>need</sub> - 1</span></td><td><span translate="no">η<sub>G</sub></span>：流量余量</td></tr>
<tr><td>扬程余量</td><td><span translate="no">η<sub>H</sub> = H<sub>rated</sub> / H<sub>need</sub> - 1</span></td><td><span translate="no">η<sub>H</sub></span>：扬程余量</td></tr>
<tr><td>轴功率参考</td><td><span translate="no">N<sub>ref</sub> = ρgQH<sub>need</sub> / (1000 × η<sub>pump</sub>)</span></td><td><span translate="no">N<sub>ref</sub></span>：水泵轴功率参考，<span translate="no">kW</span></td></tr>
<tr><td>电机功率余量</td><td><span translate="no">η<sub>N</sub> = N<sub>motor</sub> / N<sub>ref</sub> - 1</span></td><td><span translate="no">η<sub>N</sub></span>：电机功率余量</td></tr>
</tbody>
</table>
""",
        unsafe_allow_html=True,
    )


def _render_fan_tab():
    st.subheader("风机选型校核")
    st.caption(
        "根据风量、风压、安全系数和拟选风机参数进行简化初步校核。"
        "功率仅为简化参考，实际应结合风机样本、性能曲线、运行点、噪声和电机效率复核。"
    )

    if "fan_selection_df" not in st.session_state:
        st.session_state["fan_selection_df"] = _empty_fan_df()
    if "fan_selection_editor_version" not in st.session_state:
        st.session_state["fan_selection_editor_version"] = 0

    col_load, col_calc, col_clear = st.columns([2, 1, 1])
    with col_load:
        if st.button("加载风机示例数据", width="stretch"):
            st.session_state["fan_selection_df"] = pd.DataFrame(FAN_SAMPLE_DATA)
            st.session_state["fan_selection_editor_version"] += 1
            st.success("已加载风机示例数据。")
    with col_calc:
        st.button("计算", key="calc_fan_selection", width="stretch", type="primary")
    with col_clear:
        if st.button("清空", key="clear_fan_selection", width="stretch"):
            st.session_state["fan_selection_df"] = _empty_fan_df()
            st.session_state["fan_selection_editor_version"] += 1

    edited_df = st.data_editor(
        st.session_state["fan_selection_df"],
        num_rows="dynamic",
        width="stretch",
        key=f"fan_selection_editor_{st.session_state['fan_selection_editor_version']}",
        column_config={
            "scheme_id": st.column_config.TextColumn("方案编号"),
            "service_system": st.column_config.TextColumn("服务系统"),
            "required_airflow_m3h": st.column_config.NumberColumn("系统所需风量（m³/h）", min_value=0, format="%.0f"),
            "required_pressure_pa": st.column_config.NumberColumn("系统所需风压（Pa）", min_value=0, format="%.1f"),
            "airflow_factor": st.column_config.NumberColumn("风量安全系数", min_value=0, format="%.2f"),
            "pressure_factor": st.column_config.NumberColumn("风压安全系数", min_value=0, format="%.2f"),
            "rated_airflow_m3h": st.column_config.NumberColumn("拟选风机额定风量（m³/h）", min_value=0, format="%.0f"),
            "rated_pressure_pa": st.column_config.NumberColumn("拟选风机全压（Pa）", min_value=0, format="%.1f"),
            "motor_power_kw": st.column_config.NumberColumn("电机功率（kW）", min_value=0, format="%.2f"),
            "fan_efficiency": st.column_config.NumberColumn("风机效率", min_value=0, format="%.2f"),
            "remark": st.column_config.TextColumn("备注"),
        },
    )
    st.session_state["fan_selection_df"] = edited_df

    st.subheader("计算结果")
    if edited_df.empty:
        st.info("请输入风机数据或加载示例数据开始计算。")
        return

    result = calculate_fan_selection(edited_df)
    if (result["选型结论"] == "需复核").any():
        st.warning("存在零值、负值、缺失值或效率异常项，相关结果已标记为需复核。")

    display_cols = [
        "scheme_id",
        "service_system",
        "所需风量 (m³/h)",
        "所需风压 (Pa)",
        "风量余量",
        "风压余量",
        "风机轴功率参考 (kW)",
        "电机功率余量",
        "风量校核",
        "风压校核",
        "电机功率校核",
        "选型结论",
        "复核建议",
        "remark",
    ]
    df_display = result[display_cols].copy()
    for column in ["风量余量", "风压余量", "风机轴功率参考 (kW)", "电机功率余量"]:
        df_display[column] = df_display[column].apply(lambda value: None if pd.isna(value) else value)
    st.dataframe(
        df_display,
        width="stretch",
        hide_index=True,
        column_config={
            "scheme_id": "方案编号",
            "service_system": "服务系统",
            "所需风量 (m³/h)": st.column_config.NumberColumn("所需风量 (m³/h)", format="%.0f"),
            "所需风压 (Pa)": st.column_config.NumberColumn("所需风压 (Pa)", format="%.1f"),
            "风量余量": st.column_config.NumberColumn("风量余量", format="%.1%"),
            "风压余量": st.column_config.NumberColumn("风压余量", format="%.1%"),
            "风机轴功率参考 (kW)": st.column_config.NumberColumn("风机轴功率参考 (kW)", format="%.2f"),
            "电机功率余量": st.column_config.NumberColumn("电机功率余量", format="%.1%"),
            "remark": "备注",
        },
    )

    st.divider()
    st.subheader("系统汇总")
    summary_rows = _summary_rows(result)
    cols = st.columns(4)
    for col_obj, (label, value) in zip(cols, summary_rows):
        col_obj.metric(label, value)

    airflow_insufficient = int((result["风量校核"] == "不足").sum())
    pressure_insufficient = int((result["风压校核"] == "不足").sum())
    motor_insufficient = int((result["电机功率校核"] == "不足").sum())
    oversized_count = int(result["选型结论"].isin(["余量偏大", "明显偏大"]).sum())
    review_count = int((result["选型结论"] == "需复核").sum())
    fan_recommendations = []
    if airflow_insufficient:
        fan_recommendations.append("存在风量不足项时，优先复核系统风量、安全系数和拟选风机额定风量。")
    if pressure_insufficient:
        fan_recommendations.append("存在风压不足项时，优先复核系统阻力、风压安全系数和拟选风机全压。")
    if motor_insufficient:
        fan_recommendations.append("存在电机功率不足项时，复核风机效率、轴功率估算、电机功率和样本运行点。")
    if oversized_count:
        fan_recommendations.append("存在余量偏大项时，关注初投资、运行调节、噪声和部分负荷运行效果。")
    if review_count:
        fan_recommendations.append("存在需复核项时，应先检查输入是否缺失、非正或效率参数异常。")
    fan_recommendations.append("风机实际选型应结合性能曲线、运行点、噪声、效率和厂家样本复核。")
    _render_validation_interpretation(
        result,
        ["风量校核", "风压校核", "电机功率校核"],
        [
            ("风量不足", f"{airflow_insufficient} 项"),
            ("风压不足", f"{pressure_insufficient} 项"),
            ("电机功率不足", f"{motor_insufficient} 项"),
            ("需复核", f"{review_count} 项"),
        ],
        fan_recommendations,
    )

    st.divider()
    st.subheader("导出数据")
    df_export = _blank_missing_export_values(
        _format_number_columns(
            _format_percent_columns(
                _rename_export_columns(result, FAN_EXPORT_MAP),
                ["风量余量", "风压余量", "电机功率余量"],
            ),
            ["风机轴功率参考（kW）"],
        )
    )
    col_csv, col_xlsx = st.columns(2)
    with col_csv:
        st.download_button(
            label="📥 下载 CSV",
            data=get_csv_bytes(df_export),
            file_name="风机选型校核结果.csv",
            mime="text/csv",
            width="stretch",
        )
    with col_xlsx:
        st.download_button(
            label="📥 下载 Excel",
            data=export_formatted_excel(df_export, summary_rows, sheet_name="选型结果", summary_sheet_name="选型汇总"),
            file_name="风机选型校核结果.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch",
        )
    st.download_button(
        label="📄 导出 Word 计算说明书",
        data=_build_fan_word_report(df_export, summary_rows),
        file_name="风机选型校核计算说明书.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        width="stretch",
    )

    st.divider()
    st.subheader("计算公式说明")
    with st.expander("查看风机选型校核公式"):
        _fan_formula_table()


def _render_pump_tab():
    st.subheader("水泵选型校核")
    st.caption(
        "根据流量、扬程、安全系数和拟选水泵参数进行简化初步校核。"
        "功率仅为简化参考，实际应结合水泵样本曲线、运行点、汽蚀余量、并联运行、变频控制和电机效率复核。"
    )

    if "pump_selection_df" not in st.session_state:
        st.session_state["pump_selection_df"] = _empty_pump_df()
    if "pump_selection_editor_version" not in st.session_state:
        st.session_state["pump_selection_editor_version"] = 0

    col_load, col_calc, col_clear = st.columns([2, 1, 1])
    with col_load:
        if st.button("加载水泵示例数据", width="stretch"):
            st.session_state["pump_selection_df"] = pd.DataFrame(PUMP_SAMPLE_DATA)
            st.session_state["pump_selection_editor_version"] += 1
            st.success("已加载水泵示例数据。")
    with col_calc:
        st.button("计算", key="calc_pump_selection", width="stretch", type="primary")
    with col_clear:
        if st.button("清空", key="clear_pump_selection", width="stretch"):
            st.session_state["pump_selection_df"] = _empty_pump_df()
            st.session_state["pump_selection_editor_version"] += 1

    edited_df = st.data_editor(
        st.session_state["pump_selection_df"],
        num_rows="dynamic",
        width="stretch",
        key=f"pump_selection_editor_{st.session_state['pump_selection_editor_version']}",
        column_config={
            "scheme_id": st.column_config.TextColumn("方案编号"),
            "service_system": st.column_config.TextColumn("服务系统"),
            "required_flow_m3h": st.column_config.NumberColumn("系统所需流量（m³/h）", min_value=0, format="%.2f"),
            "required_head_m": st.column_config.NumberColumn("系统所需扬程（m）", min_value=0, format="%.2f"),
            "flow_factor": st.column_config.NumberColumn("流量安全系数", min_value=0, format="%.2f"),
            "head_factor": st.column_config.NumberColumn("扬程安全系数", min_value=0, format="%.2f"),
            "rated_flow_m3h": st.column_config.NumberColumn("拟选水泵额定流量（m³/h）", min_value=0, format="%.2f"),
            "rated_head_m": st.column_config.NumberColumn("拟选水泵扬程（m）", min_value=0, format="%.2f"),
            "motor_power_kw": st.column_config.NumberColumn("电机功率（kW）", min_value=0, format="%.2f"),
            "pump_efficiency": st.column_config.NumberColumn("水泵效率", min_value=0, format="%.2f"),
            "remark": st.column_config.TextColumn("备注"),
        },
    )
    st.session_state["pump_selection_df"] = edited_df

    st.subheader("计算结果")
    if edited_df.empty:
        st.info("请输入水泵数据或加载示例数据开始计算。")
        return

    result = calculate_pump_selection(edited_df)
    if (result["选型结论"] == "需复核").any():
        st.warning("存在零值、负值、缺失值或效率异常项，相关结果已标记为需复核。")

    display_cols = [
        "scheme_id",
        "service_system",
        "所需流量 (m³/h)",
        "所需扬程 (m)",
        "流量余量",
        "扬程余量",
        "水泵轴功率参考 (kW)",
        "电机功率余量",
        "流量校核",
        "扬程校核",
        "电机功率校核",
        "选型结论",
        "复核建议",
        "remark",
    ]
    df_display = result[display_cols].copy()
    for column in ["流量余量", "扬程余量", "水泵轴功率参考 (kW)", "电机功率余量"]:
        df_display[column] = df_display[column].apply(lambda value: None if pd.isna(value) else value)
    st.dataframe(
        df_display,
        width="stretch",
        hide_index=True,
        column_config={
            "scheme_id": "方案编号",
            "service_system": "服务系统",
            "所需流量 (m³/h)": st.column_config.NumberColumn("所需流量 (m³/h)", format="%.2f"),
            "所需扬程 (m)": st.column_config.NumberColumn("所需扬程 (m)", format="%.2f"),
            "流量余量": st.column_config.NumberColumn("流量余量", format="%.1%"),
            "扬程余量": st.column_config.NumberColumn("扬程余量", format="%.1%"),
            "水泵轴功率参考 (kW)": st.column_config.NumberColumn("水泵轴功率参考 (kW)", format="%.2f"),
            "电机功率余量": st.column_config.NumberColumn("电机功率余量", format="%.1%"),
            "remark": "备注",
        },
    )

    st.divider()
    st.subheader("系统汇总")
    summary_rows = _summary_rows(result)
    cols = st.columns(4)
    for col_obj, (label, value) in zip(cols, summary_rows):
        col_obj.metric(label, value)

    flow_insufficient = int((result["流量校核"] == "不足").sum())
    head_insufficient = int((result["扬程校核"] == "不足").sum())
    motor_insufficient = int((result["电机功率校核"] == "不足").sum())
    oversized_count = int(result["选型结论"].isin(["余量偏大", "明显偏大"]).sum())
    review_count = int((result["选型结论"] == "需复核").sum())
    pump_recommendations = []
    if flow_insufficient:
        pump_recommendations.append("存在流量不足项时，优先复核系统流量、安全系数和拟选水泵额定流量。")
    if head_insufficient:
        pump_recommendations.append("存在扬程不足项时，优先复核系统阻力、扬程安全系数和拟选水泵扬程。")
    if motor_insufficient:
        pump_recommendations.append("存在电机功率不足项时，复核水泵效率、轴功率估算、电机功率和样本运行点。")
    if oversized_count:
        pump_recommendations.append("存在余量偏大项时，关注初投资、运行调节、变频控制和低负荷运行。")
    if review_count:
        pump_recommendations.append("存在需复核项时，应先检查输入是否缺失、非正或效率参数异常。")
    pump_recommendations.append("水泵实际选型应结合性能曲线、运行点、汽蚀余量、并联运行和厂家样本复核。")
    _render_validation_interpretation(
        result,
        ["流量校核", "扬程校核", "电机功率校核"],
        [
            ("流量不足", f"{flow_insufficient} 项"),
            ("扬程不足", f"{head_insufficient} 项"),
            ("电机功率不足", f"{motor_insufficient} 项"),
            ("需复核", f"{review_count} 项"),
        ],
        pump_recommendations,
    )

    st.divider()
    st.subheader("导出数据")
    df_export = _blank_missing_export_values(
        _format_number_columns(
            _format_percent_columns(
                _rename_export_columns(result, PUMP_EXPORT_MAP),
                ["流量余量", "扬程余量", "电机功率余量"],
            ),
            ["水泵轴功率参考（kW）"],
        )
    )
    col_csv, col_xlsx = st.columns(2)
    with col_csv:
        st.download_button(
            label="📥 下载 CSV",
            data=get_csv_bytes(df_export),
            file_name="水泵选型校核结果.csv",
            mime="text/csv",
            width="stretch",
        )
    with col_xlsx:
        st.download_button(
            label="📥 下载 Excel",
            data=export_formatted_excel(df_export, summary_rows, sheet_name="选型结果", summary_sheet_name="选型汇总"),
            file_name="水泵选型校核结果.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch",
        )
    st.download_button(
        label="📄 导出 Word 计算说明书",
        data=_build_pump_word_report(df_export, summary_rows),
        file_name="水泵选型校核计算说明书.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        width="stretch",
    )

    st.divider()
    st.subheader("计算公式说明")
    with st.expander("查看水泵选型校核公式"):
        _pump_formula_table()


def render_fan_pump_selection_module():
    """渲染风机 / 水泵选型校核模块。"""

    st.markdown("### 模块五：风机 / 水泵选型校核")
    st.markdown(
        "本模块用于风机和水泵的简化初步选型校核，可根据系统所需风量/风压或流量/扬程，"
        "以及拟选设备参数，计算余量、功率参考和选型结论。"
        "结果仅用于学习、课程设计辅助核算和工程初步校核，不能替代正式工程设计、设备样本选型或规范校核。"
    )

    fan_tab, pump_tab = st.tabs(["风机选型校核", "水泵选型校核"])
    with fan_tab:
        _render_fan_tab()
    with pump_tab:
        _render_pump_tab()

    st.divider()
    st.caption(
        "风机 / 水泵选型校核结果仅供学习、课程设计辅助核算和工程初步校核使用，"
        "实际工程应结合设备样本、性能曲线、运行点、噪声、汽蚀余量、控制方式和规范要求复核。"
    )
