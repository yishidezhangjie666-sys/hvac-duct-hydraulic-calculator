"""
冷热源设备初步选型模块

模块四：风冷热泵、冷水机组、锅炉 / 热源设备的简化初步选型校核。
"""

import pandas as pd
import streamlit as st

from utils.export_utils import export_formatted_excel, get_csv_bytes
from utils.word_report import build_calculation_report_docx


AIR_HEAT_PUMP_SAMPLE_DATA = {
    "scheme_id": ["AHP-1", "AHP-2", "AHP-3", "AHP-4"],
    "service_area": ["办公楼低区", "办公楼高区", "综合楼", "小型附楼"],
    "cooling_load_kw": [520.0, 680.0, 600.0, 300.0],
    "heating_load_kw": [430.0, 560.0, 720.0, 250.0],
    "cooling_factor": [1.10, 1.10, 1.10, 1.10],
    "heating_factor": [1.15, 1.15, 1.20, 1.15],
    "single_cooling_kw": [300.0, 330.0, 360.0, 300.0],
    "single_heating_kw": [280.0, 360.0, 380.0, 280.0],
    "unit_count": [2, 2, 2, 3],
    "remark": ["屋面布置", "制冷容量偏小示例", "低温制热需关注", "容量余量偏大示例"],
}

CHILLER_SAMPLE_DATA = {
    "scheme_id": ["CH-1", "CH-2", "CH-3", "CH-4"],
    "service_area": ["办公楼", "商业裙房", "数据机房辅助", "展厅"],
    "cooling_load_kw": [1180.0, 1760.0, 650.0, 900.0],
    "cooling_factor": [1.10, 1.10, 1.20, 1.10],
    "single_cooling_kw": [700.0, 800.0, 600.0, 550.0],
    "unit_count": [2, 2, 2, 2],
    "supply_temp_c": [7.0, 7.0, 6.0, 8.0],
    "return_temp_c": [12.0, 12.0, 12.0, 16.0],
    "remark": ["常规冷冻水", "容量偏小示例", "容量偏大示例", "温差需复核示例"],
}

BOILER_SAMPLE_DATA = {
    "scheme_id": ["BH-1", "BH-2", "BH-3", "BH-4"],
    "service_area": ["办公楼供暖", "生活热水", "小型附属用房", "综合热源"],
    "heating_load_kw": [920.0, 680.0, 380.0, 1450.0],
    "heating_factor": [1.10, 1.15, 1.10, 1.10],
    "single_heating_kw": [550.0, 350.0, 375.0, 900.0],
    "unit_count": [2, 2, 2, 2],
    "supply_temp_c": [60.0, 55.0, 70.0, 50.0],
    "return_temp_c": [50.0, 45.0, 55.0, 48.0],
    "remark": ["常规供暖示例", "容量偏小示例", "容量偏大示例", "温差需复核示例"],
}

AIR_HEAT_PUMP_EXPORT_MAP = {
    "scheme_id": "方案编号",
    "service_area": "服务区域",
    "cooling_load_kw": "设计冷负荷 Qc（kW）",
    "heating_load_kw": "设计热负荷 Qh（kW）",
    "cooling_factor": "冷量修正系数 Kc",
    "heating_factor": "热量修正系数 Kh",
    "single_cooling_kw": "单台额定制冷量（kW）",
    "single_heating_kw": "单台额定制热量（kW）",
    "unit_count": "台数 N",
    "所需制冷量 (kW)": "所需制冷量（kW）",
    "所需制热量 (kW)": "所需制热量（kW）",
    "总制冷量 (kW)": "总制冷量（kW）",
    "总制热量 (kW)": "总制热量（kW）",
    "制冷量余量": "制冷量余量",
    "制热量余量": "制热量余量",
    "制冷校核": "制冷校核",
    "制热校核": "制热校核",
    "选型结论": "选型结论",
    "remark": "备注",
}

CHILLER_EXPORT_MAP = {
    "scheme_id": "方案编号",
    "service_area": "服务区域",
    "cooling_load_kw": "设计冷负荷 Qc（kW）",
    "cooling_factor": "冷量备用系数 Kc",
    "single_cooling_kw": "单台额定制冷量（kW）",
    "unit_count": "台数 N",
    "supply_temp_c": "冷冻水供水温度（℃）",
    "return_temp_c": "冷冻水回水温度（℃）",
    "所需制冷量 (kW)": "所需制冷量（kW）",
    "总制冷量 (kW)": "总制冷量（kW）",
    "制冷量余量": "制冷量余量",
    "制冷校核": "制冷校核",
    "供回水温差 Δt (℃)": "供回水温差 Δt（℃）",
    "温差校核": "温差校核",
    "选型结论": "选型结论",
    "remark": "备注",
}

BOILER_EXPORT_MAP = {
    "scheme_id": "方案编号",
    "service_area": "服务区域",
    "heating_load_kw": "设计热负荷 Qh（kW）",
    "heating_factor": "热量备用系数 Kh",
    "single_heating_kw": "单台额定供热量（kW）",
    "unit_count": "台数 N",
    "supply_temp_c": "供水温度（℃）",
    "return_temp_c": "回水温度（℃）",
    "所需供热量 (kW)": "所需供热量（kW）",
    "总供热量 (kW)": "总供热量（kW）",
    "供热量余量": "供热量余量",
    "供热校核": "供热校核",
    "供回水温差 Δt (℃)": "供回水温差 Δt（℃）",
    "温差校核": "温差校核",
    "选型结论": "选型结论",
    "remark": "备注",
}

AIR_HEAT_PUMP_INPUT_COLUMNS = [
    "方案编号",
    "服务区域",
    "设计冷负荷 Qc（kW）",
    "设计热负荷 Qh（kW）",
    "冷量修正系数 Kc",
    "热量修正系数 Kh",
    "单台额定制冷量（kW）",
    "单台额定制热量（kW）",
    "台数 N",
    "备注",
]

AIR_HEAT_PUMP_RESULT_COLUMNS = [
    "方案编号",
    "所需制冷量（kW）",
    "所需制热量（kW）",
    "总制冷量（kW）",
    "总制热量（kW）",
    "制冷量余量",
    "制热量余量",
    "制冷校核",
    "制热校核",
    "选型结论",
]

CHILLER_INPUT_COLUMNS = [
    "方案编号",
    "服务区域",
    "设计冷负荷 Qc（kW）",
    "冷量备用系数 Kc",
    "单台额定制冷量（kW）",
    "台数 N",
    "冷冻水供水温度（℃）",
    "冷冻水回水温度（℃）",
    "备注",
]

CHILLER_RESULT_COLUMNS = [
    "方案编号",
    "所需制冷量（kW）",
    "总制冷量（kW）",
    "制冷量余量",
    "制冷校核",
    "供回水温差 Δt（℃）",
    "温差校核",
    "选型结论",
]

BOILER_INPUT_COLUMNS = [
    "方案编号",
    "服务区域",
    "设计热负荷 Qh（kW）",
    "热量备用系数 Kh",
    "单台额定供热量（kW）",
    "台数 N",
    "供水温度（℃）",
    "回水温度（℃）",
    "备注",
]

BOILER_RESULT_COLUMNS = [
    "方案编号",
    "所需供热量（kW）",
    "总供热量（kW）",
    "供热量余量",
    "供热校核",
    "供回水温差 Δt（℃）",
    "温差校核",
    "选型结论",
]

SOURCE_FORMULA_ROWS = [
    ("所需容量", "Q_required = Q_load × K", "Q_required：所需容量，Q_load：设计负荷，K：备用或修正系数"),
    ("总装机容量", "Q_total = N × Q_single", "N：设备台数，Q_single：单台容量"),
    ("容量余量", "η = Q_total / Q_required - 1", "η < 0 为不足，0-20% 为合理，20%-50% 为偏大"),
]

COOLING_DELTA_FORMULA_ROW = (
    "供回水温差",
    "Δt = t_return - t_supply",
    "冷冻水按回水温度减供水温度，单位为 ℃",
)

HEATING_DELTA_FORMULA_ROW = (
    "供回水温差",
    "Δt = t_supply - t_return",
    "热源设备通常按供水温度减回水温度，单位为 ℃",
)

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


def _as_dataframe(data):
    if isinstance(data, pd.DataFrame):
        return data.copy()
    return pd.DataFrame(data)


def _empty_df(columns):
    return pd.DataFrame({col: pd.Series(dtype=dtype) for col, dtype in columns.items()})


def _empty_air_heat_pump_df():
    return _empty_df(
        {
            "scheme_id": "str",
            "service_area": "str",
            "cooling_load_kw": "float64",
            "heating_load_kw": "float64",
            "cooling_factor": "float64",
            "heating_factor": "float64",
            "single_cooling_kw": "float64",
            "single_heating_kw": "float64",
            "unit_count": "float64",
            "remark": "str",
        }
    )


def _empty_chiller_df():
    return _empty_df(
        {
            "scheme_id": "str",
            "service_area": "str",
            "cooling_load_kw": "float64",
            "cooling_factor": "float64",
            "single_cooling_kw": "float64",
            "unit_count": "float64",
            "supply_temp_c": "float64",
            "return_temp_c": "float64",
            "remark": "str",
        }
    )


def _empty_boiler_df():
    return _empty_df(
        {
            "scheme_id": "str",
            "service_area": "str",
            "heating_load_kw": "float64",
            "heating_factor": "float64",
            "single_heating_kw": "float64",
            "unit_count": "float64",
            "supply_temp_c": "float64",
            "return_temp_c": "float64",
            "remark": "str",
        }
    )


def _safe_required(load, factor):
    if pd.isna(load) or pd.isna(factor) or load <= 0 or factor <= 0:
        return pd.NA
    return load * factor


def _safe_total(single_capacity, unit_count):
    if (
        pd.isna(single_capacity)
        or pd.isna(unit_count)
        or single_capacity <= 0
        or unit_count <= 0
    ):
        return pd.NA
    return single_capacity * unit_count


def _safe_margin(total_capacity, required_capacity):
    if pd.isna(total_capacity) or pd.isna(required_capacity) or required_capacity <= 0:
        return pd.NA
    return total_capacity / required_capacity - 1


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


def _temperature_delta_status(value):
    if pd.isna(value) or value <= 0:
        return "需复核"
    if 3 <= value <= 7:
        return "常见范围"
    return "需结合项目复核"


def _heating_delta_status(value):
    if pd.isna(value) or value <= 0:
        return "需复核"
    if 5 <= value <= 20:
        return "常见范围"
    return "需结合项目复核"


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
    if "需结合项目复核" in status_set:
        return "容量可用，温差需复核"
    return "建议可用"


def calculate_air_heat_pump_selection(df):
    """计算风冷热泵机组初步选型余量。"""
    result = _as_dataframe(df)
    result["所需制冷量 (kW)"] = result.apply(
        lambda row: _safe_required(row["cooling_load_kw"], row["cooling_factor"]),
        axis=1,
    )
    result["所需制热量 (kW)"] = result.apply(
        lambda row: _safe_required(row["heating_load_kw"], row["heating_factor"]),
        axis=1,
    )
    result["总制冷量 (kW)"] = result.apply(
        lambda row: _safe_total(row["single_cooling_kw"], row["unit_count"]),
        axis=1,
    )
    result["总制热量 (kW)"] = result.apply(
        lambda row: _safe_total(row["single_heating_kw"], row["unit_count"]),
        axis=1,
    )
    result["制冷量余量"] = result.apply(
        lambda row: _safe_margin(row["总制冷量 (kW)"], row["所需制冷量 (kW)"]),
        axis=1,
    )
    result["制热量余量"] = result.apply(
        lambda row: _safe_margin(row["总制热量 (kW)"], row["所需制热量 (kW)"]),
        axis=1,
    )
    result["制冷校核"] = result["制冷量余量"].apply(_capacity_status)
    result["制热校核"] = result["制热量余量"].apply(_capacity_status)
    result["选型结论"] = result[["制冷校核", "制热校核"]].apply(
        _selection_conclusion,
        axis=1,
    )
    return result


def calculate_chiller_selection(df):
    """计算冷水机组初步选型余量。"""
    result = _as_dataframe(df)
    result["所需制冷量 (kW)"] = result.apply(
        lambda row: _safe_required(row["cooling_load_kw"], row["cooling_factor"]),
        axis=1,
    )
    result["总制冷量 (kW)"] = result.apply(
        lambda row: _safe_total(row["single_cooling_kw"], row["unit_count"]),
        axis=1,
    )
    result["制冷量余量"] = result.apply(
        lambda row: _safe_margin(row["总制冷量 (kW)"], row["所需制冷量 (kW)"]),
        axis=1,
    )
    result["制冷校核"] = result["制冷量余量"].apply(_capacity_status)
    result["供回水温差 Δt (℃)"] = result["return_temp_c"] - result["supply_temp_c"]
    result["温差校核"] = result["供回水温差 Δt (℃)"].apply(_temperature_delta_status)
    result["选型结论"] = result[["制冷校核", "温差校核"]].apply(
        _selection_conclusion,
        axis=1,
    )
    return result


def calculate_boiler_selection(df):
    """计算锅炉 / 热源设备初步选型余量。"""
    result = _as_dataframe(df)
    result["所需供热量 (kW)"] = result.apply(
        lambda row: _safe_required(row["heating_load_kw"], row["heating_factor"]),
        axis=1,
    )
    result["总供热量 (kW)"] = result.apply(
        lambda row: _safe_total(row["single_heating_kw"], row["unit_count"]),
        axis=1,
    )
    result["供热量余量"] = result.apply(
        lambda row: _safe_margin(row["总供热量 (kW)"], row["所需供热量 (kW)"]),
        axis=1,
    )
    result["供热校核"] = result["供热量余量"].apply(_capacity_status)
    result["供回水温差 Δt (℃)"] = result["supply_temp_c"] - result["return_temp_c"]
    result["温差校核"] = result["供回水温差 Δt (℃)"].apply(_heating_delta_status)
    result["选型结论"] = result[["供热校核", "温差校核"]].apply(
        _selection_conclusion,
        axis=1,
    )
    return result


def _rename_export_columns(df, col_map):
    available = {key: value for key, value in col_map.items() if key in df.columns}
    return df[list(available.keys())].rename(columns=available)


def _format_percent_columns(df, columns):
    formatted = df.copy()
    for col in columns:
        if col in formatted.columns:
            formatted[col] = formatted[col].apply(
                lambda v: "" if pd.isna(v) else f"{v:.1%}"
            )
    return formatted


def _format_number_columns(df, columns):
    formatted = df.copy()
    for col in columns:
        if col in formatted.columns:
            formatted[col] = formatted[col].apply(
                lambda v: "" if pd.isna(v) else f"{v:.2f}"
            )
    return formatted


def _select_report_columns(df, columns):
    available = [col for col in columns if col in df.columns]
    return df[available].copy()


def _build_source_word_report(
    title,
    module_name,
    description,
    df_export,
    summary_rows,
    input_columns,
    result_columns,
    formula_rows,
    notes=None,
):
    return build_calculation_report_docx(
        title=title,
        module_name=module_name,
        description=description,
        input_tables=[
            {"title": "负荷与拟选设备参数", "data": _select_report_columns(df_export, input_columns)},
        ],
        result_tables=[
            {"title": "设备选型校核结果", "data": _select_report_columns(df_export, result_columns)},
        ],
        summary_rows=summary_rows,
        formula_rows=formula_rows,
        notes=[
            "冷热源设备最终选型应结合设备样本、运行工况、效率等级、系统配置、备用原则、安装条件和现行规范进行复核。"
        ] + (notes or []),
    )


def _summary_rows(result, id_col, capacity_col, conclusion_col="选型结论"):
    total_count = len(result)
    insufficient = (result[conclusion_col] == "拟选偏小").sum()
    oversized = result[conclusion_col].isin(["余量偏大", "明显偏大"]).sum()
    review = result[conclusion_col].str.contains("复核", na=False).sum()
    total_capacity = result[capacity_col].dropna().sum()
    return [
        ("方案数量", f"{total_count} 个"),
        ("拟选偏小", f"{insufficient} 项"),
        ("余量偏大", f"{oversized} 项"),
        ("需复核", f"{review} 项"),
        ("总装机容量", f"{total_capacity:.2f} kW"),
    ]


def _base_formula_table(extra_rows=""):
    st.markdown(
        FORMULA_STYLE
        + f"""
<table class="formula-table">
<thead>
<tr><th>计算项目</th><th>公式</th><th>单位说明</th></tr>
</thead>
<tbody>
<tr>
<td>所需容量</td>
<td><span translate="no">Q<sub>required</sub> = Q<sub>load</sub> × K</span></td>
<td><span translate="no">Q<sub>required</sub></span>：所需容量，<span translate="no">kW</span>；<span translate="no">Q<sub>load</sub></span>：设计负荷，<span translate="no">kW</span>；<span translate="no">K</span>：备用或修正系数</td>
</tr>
<tr>
<td>总装机容量</td>
<td><span translate="no">Q<sub>total</sub> = N × Q<sub>single</sub></span></td>
<td><span translate="no">Q<sub>total</sub></span>：总装机容量，<span translate="no">kW</span>；<span translate="no">N</span>：设备台数；<span translate="no">Q<sub>single</sub></span>：单台容量，<span translate="no">kW</span></td>
</tr>
<tr>
<td>容量余量</td>
<td><span translate="no">η = Q<sub>total</sub> / Q<sub>required</sub> - 1</span></td>
<td><span translate="no">η</span>：容量余量；<span translate="no">η &lt; 0</span> 为不足，<span translate="no">0-20%</span> 为合理，<span translate="no">20%-50%</span> 为偏大</td>
</tr>
{extra_rows}
</tbody>
</table>
""",
        unsafe_allow_html=True,
    )


def _delta_formula_row():
    return """
<tr>
<td>供回水温差</td>
<td><span translate="no">Δt = t<sub>return</sub> - t<sub>supply</sub></span></td>
<td>冷冻水按回水温度减供水温度；热源设备按供水温度减回水温度，单位为 <span translate="no">℃</span></td>
</tr>
"""


def _render_export_buttons(
    df_export,
    summary_rows,
    file_stem,
    word_title,
    word_module_name,
    word_desc,
    input_columns,
    result_columns,
    formula_rows,
    notes=None,
):
    col_csv, col_xlsx = st.columns(2)
    with col_csv:
        st.download_button(
            label="📥 下载 CSV",
            data=get_csv_bytes(df_export),
            file_name=f"{file_stem}.csv",
            mime="text/csv",
            width="stretch",
        )
    with col_xlsx:
        st.download_button(
            label="📥 下载 Excel",
            data=export_formatted_excel(
                df_export,
                summary_rows,
                sheet_name="选型结果",
                summary_sheet_name="选型汇总",
            ),
            file_name=f"{file_stem}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch",
        )
    st.download_button(
        label="📄 导出 Word 计算说明书",
        data=_build_source_word_report(
            word_title,
            word_module_name,
            word_desc,
            df_export,
            summary_rows,
            input_columns,
            result_columns,
            formula_rows,
            notes,
        ),
        file_name=f"{file_stem}计算说明书.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        width="stretch",
    )


def _render_summary(summary_rows):
    cols = st.columns(len(summary_rows))
    for col_obj, (label, value) in zip(cols, summary_rows):
        col_obj.metric(label, value)


def _render_air_heat_pump_tab():
    st.subheader("风冷热泵机组初步选型")
    st.caption(
        "余量阈值为简化建议，可按项目要求调整。风冷热泵实际选型应结合室外设计工况、"
        "低温制热衰减、融霜修正、噪声、安装位置和厂家样本复核。"
        "示例数据覆盖建议可用、拟选偏小和余量偏大等典型结果。"
    )

    if "source_air_heat_pump_df" not in st.session_state:
        st.session_state["source_air_heat_pump_df"] = _empty_air_heat_pump_df()
    if "source_air_heat_pump_editor_version" not in st.session_state:
        st.session_state["source_air_heat_pump_editor_version"] = 0

    col_load, col_clear = st.columns([2, 1])
    with col_load:
        if st.button("加载风冷热泵示例数据", width="stretch"):
            st.session_state["source_air_heat_pump_df"] = pd.DataFrame(
                AIR_HEAT_PUMP_SAMPLE_DATA
            )
            st.session_state["source_air_heat_pump_editor_version"] += 1
            st.success("已加载风冷热泵示例数据。")
    with col_clear:
        if st.button("清空", key="clear_air_heat_pump", width="stretch"):
            st.session_state["source_air_heat_pump_df"] = _empty_air_heat_pump_df()
            st.session_state["source_air_heat_pump_editor_version"] += 1

    edited_df = st.data_editor(
        st.session_state["source_air_heat_pump_df"],
        num_rows="dynamic",
        width="stretch",
        key=f"source_air_heat_pump_editor_{st.session_state['source_air_heat_pump_editor_version']}",
        column_config={
            "scheme_id": st.column_config.TextColumn("方案编号"),
            "service_area": st.column_config.TextColumn("服务区域"),
            "cooling_load_kw": st.column_config.NumberColumn("设计冷负荷 Qc (kW)", min_value=0, format="%.2f"),
            "heating_load_kw": st.column_config.NumberColumn("设计热负荷 Qh (kW)", min_value=0, format="%.2f"),
            "cooling_factor": st.column_config.NumberColumn("冷量修正系数 Kc", min_value=0, format="%.2f"),
            "heating_factor": st.column_config.NumberColumn("热量修正系数 Kh", min_value=0, format="%.2f"),
            "single_cooling_kw": st.column_config.NumberColumn("单台额定制冷量 (kW)", min_value=0, format="%.2f"),
            "single_heating_kw": st.column_config.NumberColumn("单台额定制热量 (kW)", min_value=0, format="%.2f"),
            "unit_count": st.column_config.NumberColumn("台数 N", min_value=0, step=1, format="%.0f"),
            "remark": st.column_config.TextColumn("备注"),
        },
    )
    st.session_state["source_air_heat_pump_df"] = edited_df

    st.subheader("计算结果")
    if edited_df.empty:
        st.info("请输入风冷热泵方案数据或加载示例数据开始计算。")
        return

    result = calculate_air_heat_pump_selection(edited_df)
    display_cols = [
        "scheme_id",
        "service_area",
        "所需制冷量 (kW)",
        "所需制热量 (kW)",
        "总制冷量 (kW)",
        "总制热量 (kW)",
        "制冷量余量",
        "制热量余量",
        "制冷校核",
        "制热校核",
        "选型结论",
        "remark",
    ]
    df_display = result[display_cols].copy()
    for col in ["制冷量余量", "制热量余量"]:
        df_display[col] = df_display[col].apply(lambda v: None if pd.isna(v) else v)
    st.dataframe(
        df_display,
        width="stretch",
        hide_index=True,
        column_config={
            "制冷量余量": st.column_config.NumberColumn("制冷量余量", format="%.1%"),
            "制热量余量": st.column_config.NumberColumn("制热量余量", format="%.1%"),
        },
    )

    st.divider()
    st.subheader("系统汇总")
    summary_rows = _summary_rows(result, "scheme_id", "总制冷量 (kW)")
    _render_summary(summary_rows)

    st.divider()
    st.subheader("导出数据")
    df_export = _format_percent_columns(
        _rename_export_columns(result, AIR_HEAT_PUMP_EXPORT_MAP),
        ["制冷量余量", "制热量余量"],
    )
    _render_export_buttons(
        df_export,
        summary_rows,
        "风冷热泵机组初步选型结果",
        "风冷热泵机组初步选型计算说明书",
        "风冷热泵机组初步选型",
        "用于风冷热泵机组制冷量、制热量和台数的简化初步选型校核。",
        AIR_HEAT_PUMP_INPUT_COLUMNS,
        AIR_HEAT_PUMP_RESULT_COLUMNS,
        SOURCE_FORMULA_ROWS,
    )

    st.divider()
    st.subheader("计算公式说明")
    with st.expander("查看风冷热泵计算公式"):
        _base_formula_table()


def _render_chiller_tab():
    st.subheader("冷水机组初步选型")
    st.caption(
        "冷水机组实际选型应结合冷冻水温度、冷却水条件、部分负荷性能、"
        "机房布置、能效等级和厂家样本复核。"
        "示例数据覆盖容量合理、容量不足、容量偏大和温差需复核等典型结果。"
    )

    if "source_chiller_df" not in st.session_state:
        st.session_state["source_chiller_df"] = _empty_chiller_df()
    if "source_chiller_editor_version" not in st.session_state:
        st.session_state["source_chiller_editor_version"] = 0

    col_load, col_clear = st.columns([2, 1])
    with col_load:
        if st.button("加载冷水机组示例数据", width="stretch"):
            st.session_state["source_chiller_df"] = pd.DataFrame(CHILLER_SAMPLE_DATA)
            st.session_state["source_chiller_editor_version"] += 1
            st.success("已加载冷水机组示例数据。")
    with col_clear:
        if st.button("清空", key="clear_chiller", width="stretch"):
            st.session_state["source_chiller_df"] = _empty_chiller_df()
            st.session_state["source_chiller_editor_version"] += 1

    edited_df = st.data_editor(
        st.session_state["source_chiller_df"],
        num_rows="dynamic",
        width="stretch",
        key=f"source_chiller_editor_{st.session_state['source_chiller_editor_version']}",
        column_config={
            "scheme_id": st.column_config.TextColumn("方案编号"),
            "service_area": st.column_config.TextColumn("服务区域"),
            "cooling_load_kw": st.column_config.NumberColumn("设计冷负荷 Qc (kW)", min_value=0, format="%.2f"),
            "cooling_factor": st.column_config.NumberColumn("冷量备用系数 Kc", min_value=0, format="%.2f"),
            "single_cooling_kw": st.column_config.NumberColumn("单台额定制冷量 (kW)", min_value=0, format="%.2f"),
            "unit_count": st.column_config.NumberColumn("台数 N", min_value=0, step=1, format="%.0f"),
            "supply_temp_c": st.column_config.NumberColumn("冷冻水供水温度 (℃)", format="%.1f"),
            "return_temp_c": st.column_config.NumberColumn("冷冻水回水温度 (℃)", format="%.1f"),
            "remark": st.column_config.TextColumn("备注"),
        },
    )
    st.session_state["source_chiller_df"] = edited_df

    st.subheader("计算结果")
    if edited_df.empty:
        st.info("请输入冷水机组方案数据或加载示例数据开始计算。")
        return

    result = calculate_chiller_selection(edited_df)
    display_cols = [
        "scheme_id",
        "service_area",
        "所需制冷量 (kW)",
        "总制冷量 (kW)",
        "制冷量余量",
        "制冷校核",
        "供回水温差 Δt (℃)",
        "温差校核",
        "选型结论",
        "remark",
    ]
    df_display = result[display_cols].copy()
    df_display["制冷量余量"] = df_display["制冷量余量"].apply(
        lambda v: None if pd.isna(v) else v
    )
    st.dataframe(
        df_display,
        width="stretch",
        hide_index=True,
        column_config={
            "制冷量余量": st.column_config.NumberColumn("制冷量余量", format="%.1%"),
        },
    )

    st.divider()
    st.subheader("系统汇总")
    summary_rows = _summary_rows(result, "scheme_id", "总制冷量 (kW)")
    _render_summary(summary_rows)

    st.divider()
    st.subheader("导出数据")
    df_export = _format_number_columns(
        _format_percent_columns(
            _rename_export_columns(result, CHILLER_EXPORT_MAP),
            ["制冷量余量"],
        ),
        ["供回水温差 Δt（℃）"],
    )
    _render_export_buttons(
        df_export,
        summary_rows,
        "冷水机组初步选型结果",
        "冷水机组初步选型计算说明书",
        "冷水机组初步选型",
        "用于冷水机组制冷量、台数和冷冻水温差的简化初步选型校核。",
        CHILLER_INPUT_COLUMNS,
        CHILLER_RESULT_COLUMNS,
        SOURCE_FORMULA_ROWS + [COOLING_DELTA_FORMULA_ROW],
    )

    st.divider()
    st.subheader("计算公式说明")
    with st.expander("查看冷水机组计算公式"):
        _base_formula_table(_delta_formula_row())


def _render_boiler_tab():
    st.subheader("锅炉 / 热源设备初步选型")
    st.caption(
        "锅炉或热源设备实际选型应结合燃料条件、效率、排放、运行调节、备用原则、"
        "系统压力和厂家样本复核。"
        "示例数据覆盖供热量合理、不足、偏大和供回水温差需复核等典型结果。"
    )

    if "source_boiler_df" not in st.session_state:
        st.session_state["source_boiler_df"] = _empty_boiler_df()
    if "source_boiler_editor_version" not in st.session_state:
        st.session_state["source_boiler_editor_version"] = 0

    col_load, col_clear = st.columns([2, 1])
    with col_load:
        if st.button("加载锅炉 / 热源示例数据", width="stretch"):
            st.session_state["source_boiler_df"] = pd.DataFrame(BOILER_SAMPLE_DATA)
            st.session_state["source_boiler_editor_version"] += 1
            st.success("已加载锅炉 / 热源示例数据。")
    with col_clear:
        if st.button("清空", key="clear_boiler", width="stretch"):
            st.session_state["source_boiler_df"] = _empty_boiler_df()
            st.session_state["source_boiler_editor_version"] += 1

    edited_df = st.data_editor(
        st.session_state["source_boiler_df"],
        num_rows="dynamic",
        width="stretch",
        key=f"source_boiler_editor_{st.session_state['source_boiler_editor_version']}",
        column_config={
            "scheme_id": st.column_config.TextColumn("方案编号"),
            "service_area": st.column_config.TextColumn("服务区域"),
            "heating_load_kw": st.column_config.NumberColumn("设计热负荷 Qh (kW)", min_value=0, format="%.2f"),
            "heating_factor": st.column_config.NumberColumn("热量备用系数 Kh", min_value=0, format="%.2f"),
            "single_heating_kw": st.column_config.NumberColumn("单台额定供热量 (kW)", min_value=0, format="%.2f"),
            "unit_count": st.column_config.NumberColumn("台数 N", min_value=0, step=1, format="%.0f"),
            "supply_temp_c": st.column_config.NumberColumn("供水温度 (℃)", format="%.1f"),
            "return_temp_c": st.column_config.NumberColumn("回水温度 (℃)", format="%.1f"),
            "remark": st.column_config.TextColumn("备注"),
        },
    )
    st.session_state["source_boiler_df"] = edited_df

    st.subheader("计算结果")
    if edited_df.empty:
        st.info("请输入锅炉 / 热源设备方案数据或加载示例数据开始计算。")
        return

    result = calculate_boiler_selection(edited_df)
    display_cols = [
        "scheme_id",
        "service_area",
        "所需供热量 (kW)",
        "总供热量 (kW)",
        "供热量余量",
        "供热校核",
        "供回水温差 Δt (℃)",
        "温差校核",
        "选型结论",
        "remark",
    ]
    df_display = result[display_cols].copy()
    df_display["供热量余量"] = df_display["供热量余量"].apply(
        lambda v: None if pd.isna(v) else v
    )
    st.dataframe(
        df_display,
        width="stretch",
        hide_index=True,
        column_config={
            "供热量余量": st.column_config.NumberColumn("供热量余量", format="%.1%"),
        },
    )

    st.divider()
    st.subheader("系统汇总")
    summary_rows = _summary_rows(result, "scheme_id", "总供热量 (kW)")
    _render_summary(summary_rows)

    st.divider()
    st.subheader("导出数据")
    df_export = _format_number_columns(
        _format_percent_columns(
            _rename_export_columns(result, BOILER_EXPORT_MAP),
            ["供热量余量"],
        ),
        ["供回水温差 Δt（℃）"],
    )
    _render_export_buttons(
        df_export,
        summary_rows,
        "锅炉热源设备初步选型结果",
        "锅炉 / 热源设备初步选型计算说明书",
        "锅炉 / 热源设备初步选型",
        "用于锅炉或热源设备供热量、台数和供回水温差的简化初步选型校核。",
        BOILER_INPUT_COLUMNS,
        BOILER_RESULT_COLUMNS,
        SOURCE_FORMULA_ROWS + [HEATING_DELTA_FORMULA_ROW],
        notes=["锅炉 / 热源设备温差通常按供水温度减回水温度计算。"],
    )

    st.divider()
    st.subheader("计算公式说明")
    with st.expander("查看锅炉 / 热源设备计算公式"):
        _base_formula_table(_delta_formula_row())


def render_heat_cold_source_module():
    st.markdown("### 模块四：冷热源设备初步选型")
    st.markdown(
        "本模块用于冷热源设备的简化初步选型校核，可根据建筑设计冷负荷、热负荷、"
        "备用系数和拟选设备参数，估算设备台数、总装机容量和容量余量。"
        "计算结果仅用于学习、课程设计辅助核算和工程初步校核，不能替代正式设备样本和规范校核。"
    )

    tabs = st.tabs(["风冷热泵机组", "冷水机组", "锅炉 / 热源设备"])
    with tabs[0]:
        _render_air_heat_pump_tab()
    with tabs[1]:
        _render_chiller_tab()
    with tabs[2]:
        _render_boiler_tab()
