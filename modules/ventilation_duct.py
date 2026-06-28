"""
通风风管水力计算模块

模块一：矩形风管系统的简化水力计算。
"""

import streamlit as st
import pandas as pd

from utils.export_utils import (
    get_csv_bytes,
    rename_export_columns,
    export_formatted_excel,
    VENTILATION_EXPORT_MAP,
)
from utils.word_report import build_calculation_report_docx


VENTILATION_INPUT_COLUMNS = [
    "管段编号",
    "风量 Q（m³/h）",
    "宽度 a（mm）",
    "高度 b（mm）",
    "长度 L（m）",
    "单位长度摩擦阻力 R（Pa/m）",
    "局部阻力系数 ζ",
]

VENTILATION_RESULT_COLUMNS = [
    "管段编号",
    "风量 q（m³/s）",
    "截面积 A（m²）",
    "风速 v（m/s）",
    "当量直径 De（m）",
    "动压 Pd（Pa）",
    "沿程阻力 Py（Pa）",
    "局部阻力 Pj（Pa）",
    "管段总阻力 Pi（Pa）",
]

VENTILATION_FORMULA_ROWS = [
    ("风量换算", "Q = Q_h / 3600", "Q：m³/s，Q_h：m³/h"),
    ("截面积", "A = a × b", "A：m²，a、b：m"),
    ("风速", "v = Q / A", "v：m/s"),
    ("水力直径", "D_e = 2ab / (a + b)", "D_e：m"),
    ("动压", "P_d = ρv² / 2", "P_d：Pa，ρ：kg/m³"),
    ("沿程阻力", "P_y = R × L", "P_y：Pa，R：Pa/m，L：m"),
    ("局部阻力", "P_j = ζ × P_d", "P_j：Pa"),
    ("管段总阻力", "P_i = P_y + P_j", "P_i：Pa"),
    ("系统总阻力", "ΣP = ΣP_i", "Pa"),
]


def _select_report_columns(df, columns):
    available = [col for col in columns if col in df.columns]
    return df[available].copy()


def _build_ventilation_word_report(df_export, total_airflow, system_total, rho, summary_rows):
    report_summary = [("管段数量", f"{len(df_export)} 个")] + summary_rows
    return build_calculation_report_docx(
        title="通风风管水力计算说明书",
        module_name="通风风管水力计算",
        description=(
            "本模块用于通风风管系统初步水力计算，可计算风速、当量直径、动压、"
            "沿程阻力、局部阻力和系统总阻力，并给出风机风量与风压参考值。"
        ),
        input_tables=[
            {"title": "管段原始输入数据", "data": _select_report_columns(df_export, VENTILATION_INPUT_COLUMNS)},
            {"title": "计算参数", "data": [("空气密度 ρ", f"{rho:.2f} kg/m³")]},
        ],
        result_tables=[
            {"title": "管段计算结果", "data": _select_report_columns(df_export, VENTILATION_RESULT_COLUMNS)},
        ],
        summary_rows=report_summary,
        formula_rows=VENTILATION_FORMULA_ROWS,
        notes=[
            f"系统总风量为 {total_airflow:.2f} m³/h，系统总阻力为 {system_total:.2f} Pa。",
            "风机参考值为简化估算，实际工程应结合最不利环路、设备样本和规范要求复核。",
        ],
    )


def render_ventilation_duct_module():
    """渲染通风风管水力计算模块的完整页面"""

    # ─── 模块说明 ─────────────────────────────────────
    st.markdown("### 模块一：通风风管水力计算")
    st.markdown(
        "本工具用于通风风管系统初步水力计算，可计算风速、当量直径、动压、"
        "沿程阻力、局部阻力、系统总阻力，并给出风机风量与风压参考值。"
    )

    # ─── 输入参数 ─────────────────────────────────────
    with st.sidebar:
        st.divider()
        st.header("计算参数")
        rho = st.number_input(
            "空气密度 ρ (kg/m³)",
            min_value=0.1,
            max_value=10.0,
            value=1.2,
            step=0.05,
            format="%.2f",
            help="标准工况下空气密度一般取 1.2 kg/m³。",
        )
        st.caption(
            "计算结果仅供课程设计和工程初步校核使用，"
            "实际工程应结合规范、设备样本及最不利环路进行复核。"
        )

    # ─── 管段计算 ─────────────────────────────────────
    st.subheader("管段数据输入")

    # 初始化 session_state
    if "input_df" not in st.session_state:
        st.session_state["input_df"] = pd.DataFrame(
            {
                "segment_id": pd.Series(dtype="str"),
                "airflow_m3h": pd.Series(dtype="float64"),
                "width_mm": pd.Series(dtype="float64"),
                "height_mm": pd.Series(dtype="float64"),
                "length_m": pd.Series(dtype="float64"),
                "friction_pa_per_m": pd.Series(dtype="float64"),
                "zeta": pd.Series(dtype="float64"),
            }
        )
    if "editor_version" not in st.session_state:
        st.session_state["editor_version"] = 0

    # 数据加载
    col1, col2 = st.columns([6, 1])
    with col2:
        load_example = st.button("加载示例数据", width="stretch")

    if load_example:
        try:
            st.session_state["input_df"] = pd.read_csv("sample_data.csv")
            st.session_state["editor_version"] += 1
            st.success("已加载示例数据，可在此基础上编辑。")
        except FileNotFoundError:
            st.error("未找到 sample_data.csv 文件。")

    # 可编辑数据表格
    st.caption("请在表格中录入或编辑管段数据（双击单元格进行编辑）。")
    edited_df = st.data_editor(
        st.session_state["input_df"],
        num_rows="dynamic",
        width="stretch",
        key=f"duct_editor_{st.session_state['editor_version']}",
        column_config={
            "segment_id": st.column_config.TextColumn("管段编号", help="管段唯一标识"),
            "airflow_m3h": st.column_config.NumberColumn(
                "风量 (m³/h)", min_value=0, format="%.0f"
            ),
            "width_mm": st.column_config.NumberColumn(
                "宽度 (mm)", min_value=0, format="%.0f"
            ),
            "height_mm": st.column_config.NumberColumn(
                "高度 (mm)", min_value=0, format="%.0f"
            ),
            "length_m": st.column_config.NumberColumn(
                "长度 (m)", min_value=0, format="%.1f"
            ),
            "friction_pa_per_m": st.column_config.NumberColumn(
                "单位长度摩擦阻力 R (Pa/m)", min_value=0, format="%.2f"
            ),
            "zeta": st.column_config.NumberColumn(
                "局部阻力系数 ζ", min_value=0, format="%.2f"
            ),
        },
    )
    st.session_state["input_df"] = edited_df

    # ─── 计算逻辑 ─────────────────────────────────────
    st.subheader("计算结果")

    if edited_df.empty:
        st.info("请输入管段数据或点击《加载示例数据》开始计算。")
        return

    df = edited_df.copy()

    # 缺失值检查
    required_cols = [
        "airflow_m3h", "width_mm", "height_mm",
        "length_m", "friction_pa_per_m", "zeta",
    ]
    missing = df[required_cols].isnull().any(axis=1)
    if missing.any():
        st.warning(
            f"第 {', '.join(df.index[missing].astype(str))} 行存在缺失值，"
            "已跳过计算。请检查输入数据。"
        )

    # 非正数检查
    non_positive = (
        (df["airflow_m3h"] <= 0)
        | (df["width_mm"] <= 0)
        | (df["height_mm"] <= 0)
        | (df["length_m"] <= 0)
    )
    if non_positive.any():
        st.warning(
            f"管段 {', '.join(df.loc[non_positive, 'segment_id'].astype(str))} "
            "中存在零或负值（风量/宽度/高度/长度），请核实。计算结果仅供参考。"
        )

    # 有效行掩码
    valid_mask = df["airflow_m3h"].fillna(0) > 0
    valid_mask &= df["width_mm"].fillna(0) > 0
    valid_mask &= df["height_mm"].fillna(0) > 0
    valid_mask &= df["length_m"].fillna(0) > 0
    valid_mask &= df["friction_pa_per_m"].fillna(0) >= 0
    valid_mask &= df["zeta"].fillna(0) >= 0

    df_result = df[valid_mask].copy()

    if df_result.empty:
        st.warning("没有有效数据可供计算。")
        return

    # ─── 核心计算 ─────────────────────────────────────
    df_result["管段编号"] = df_result["segment_id"]
    df_result["风量 Q (m³/s)"] = df_result["airflow_m3h"] / 3600
    df_result["宽度 (m)"] = df_result["width_mm"] / 1000
    df_result["高度 (m)"] = df_result["height_mm"] / 1000
    df_result["截面积 A (m²)"] = df_result["宽度 (m)"] * df_result["高度 (m)"]
    df_result["风速 v (m/s)"] = (
        df_result["风量 Q (m³/s)"] / df_result["截面积 A (m²)"]
    )
    df_result["当量直径 De (m)"] = (
        2
        * df_result["宽度 (m)"]
        * df_result["高度 (m)"]
        / (df_result["宽度 (m)"] + df_result["高度 (m)"])
    )
    df_result["动压 Pd (Pa)"] = rho * df_result["风速 v (m/s)"] ** 2 / 2
    df_result["沿程阻力 Py (Pa)"] = (
        df_result["friction_pa_per_m"] * df_result["length_m"]
    )
    df_result["局部阻力 Pj (Pa)"] = (
        df_result["zeta"] * df_result["动压 Pd (Pa)"]
    )
    df_result["管段总阻力 P (Pa)"] = (
        df_result["沿程阻力 Py (Pa)"] + df_result["局部阻力 Pj (Pa)"]
    )

    system_total = df_result["管段总阻力 P (Pa)"].sum()

    # ─── 结果展示 ─────────────────────────────────────
    display_cols = [
        "管段编号",
        "风量 Q (m³/s)",
        "风速 v (m/s)",
        "当量直径 De (m)",
        "动压 Pd (Pa)",
        "沿程阻力 Py (Pa)",
        "局部阻力 Pj (Pa)",
        "管段总阻力 P (Pa)",
    ]
    df_display = df_result[display_cols].round(2)
    st.dataframe(df_display, width="stretch", hide_index=True)

    # ─── 系统汇总 ─────────────────────────────────────
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.metric(
            label="系统总阻力 ΣP",
            value=f"{system_total:.2f} Pa",
            delta=f"{len(df_result)} 个管段",
        )

    # ─── 导出结果 ─────────────────────────────────────
    st.divider()
    st.subheader("导出数据")

    df_export = rename_export_columns(df_result, VENTILATION_EXPORT_MAP)

    col_csv, col_xlsx = st.columns(2)

    with col_csv:
        st.download_button(
            label="📥 下载 CSV",
            data=get_csv_bytes(df_export),
            file_name="通风风管水力计算结果.csv",
            mime="text/csv",
            width="stretch",
        )

    total_airflow = df_result["airflow_m3h"].sum()
    # 风机推荐值：按系统总参数 × 1.0（当前版本未设安全系数参数）
    summary_rows = [
        ("系统总风量", f"{total_airflow:.2f} m³/h"),
        ("系统总阻力", f"{system_total:.2f} Pa"),
        ("推荐风机风量", f"{total_airflow:.2f} m³/h"),
        ("推荐风机风压", f"{system_total:.2f} Pa"),
    ]
    with col_xlsx:
        st.download_button(
            label="📥 下载 Excel",
            data=export_formatted_excel(df_export, summary_rows),
            file_name="通风风管水力计算结果.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch",
        )

    st.download_button(
        label="📄 导出 Word 计算说明书",
        data=_build_ventilation_word_report(
            df_export,
            total_airflow,
            system_total,
            rho,
            summary_rows,
        ),
        file_name="通风风管水力计算说明书.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        width="stretch",
    )

    # ─── 计算公式说明 ─────────────────────────────────
    st.divider()
    st.subheader("计算公式说明")

    with st.expander("查看计算公式"):
        st.markdown(
            f"当前空气密度 ρ = {rho:.2f} kg/m³，可在左侧边栏调整。"
        )
        st.markdown(
            """
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

<table class="formula-table">
<thead>
<tr><th>计算项目</th><th>公式</th><th>单位说明</th></tr>
</thead>
<tbody>
<tr><td>风量换算</td><td><span translate="no">Q = Q<sub>h</sub> / 3600</span></td><td><span translate="no">Q</span>：m³/s，<span translate="no">Q<sub>h</sub></span>：m³/h</td></tr>
<tr><td>截面积</td><td><span translate="no">A = a × b</span></td><td><span translate="no">A</span>：m²，<span translate="no">a</span>、<span translate="no">b</span>：m</td></tr>
<tr><td>风速</td><td><span translate="no">v = Q / A</span></td><td><span translate="no">v</span>：m/s</td></tr>
<tr><td>水力直径</td><td><span translate="no">D<sub>e</sub> = 2ab / (a + b)</span></td><td><span translate="no">D<sub>e</sub></span>：m</td></tr>
<tr><td>动压</td><td><span translate="no">P<sub>d</sub> = ρv<sup>2</sup> / 2</span></td><td><span translate="no">P<sub>d</sub></span>：<span translate="no">Pa</span>（帕），ρ：kg/m³</td></tr>
<tr><td>沿程阻力</td><td><span translate="no">P<sub>y</sub> = R × L</span></td><td><span translate="no">P<sub>y</sub></span>：<span translate="no">Pa</span>（帕），<span translate="no">R</span>：<span translate="no">Pa/m</span>（帕/米），<span translate="no">L</span>：m</td></tr>
<tr><td>局部阻力</td><td><span translate="no">P<sub>j</sub> = ζ × P<sub>d</sub></span></td><td><span translate="no">P<sub>j</sub></span>：<span translate="no">Pa</span>（帕）</td></tr>
<tr><td>管段总阻力</td><td><span translate="no">P<sub>i</sub> = P<sub>y</sub> + P<sub>j</sub></span></td><td><span translate="no">P<sub>i</sub></span>：<span translate="no">Pa</span>（帕）</td></tr>
<tr><td>系统总阻力</td><td><span translate="no">ΣP = ΣP<sub>i</sub></span></td><td><span translate="no">ΣP</span>：<span translate="no">Pa</span>（帕）</td></tr>
</tbody>
</table>
""",
            unsafe_allow_html=True,
        )

    # ─── 后续模块规划 ─────────────────────────────────
    st.divider()
    st.subheader("后续模块规划")
    st.markdown("本项目定位为建环工程计算工具箱，后续计划开发以下模块：")
    for m in [
        "空调水系统水力计算",
        "冷热源设备选型",
        "风机 / 水泵选型校核",
        "能耗与运行费用估算",
        "Word 计算说明书导出",
        "课程设计案例模板库",
    ]:
        st.markdown(f"- {m}")

    # ─── 免责声明 ─────────────────────────────────────
    st.divider()
    st.caption(
        "计算结果仅供课程设计和工程初步校核使用，"
        "实际工程应结合规范、设备样本及最不利环路进行复核。"
    )
