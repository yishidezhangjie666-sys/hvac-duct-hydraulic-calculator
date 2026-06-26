"""
空调水系统水力计算模块

模块二：空调冷冻水、热水系统的简化水力计算。
"""

import streamlit as st
import pandas as pd

from utils.export_utils import (
    get_csv_bytes,
    rename_export_columns,
    export_formatted_excel,
    WATER_EXPORT_MAP,
)


# ─── 示例数据 ────────────────────────────────────────
SAMPLE_DATA = {
    "pipe_no": ["W-1", "W-2", "W-3", "W-4"],
    "load_kw": [5.0, 8.0, 12.0, 18.0],
    "flow_m3h": [0.0, 0.0, 0.0, 0.0],
    "diameter_mm": [25, 32, 40, 50],
    "length_m": [12, 15, 18, 20],
    "resistance_pa_per_m": [150, 120, 100, 90],
    "local_zeta": [2.0, 2.5, 3.0, 3.5],
}


# ─── 计算公式 ────────────────────────────────────────
def calculate_flows(df, delta_t):
    """根据负荷和温差估算水流量 G = 0.86 × QL / Δt"""
    df = df.copy()
    df["flow_m3h"] = round(0.86 * df["load_kw"].fillna(0) / delta_t, 2)
    return df


def calculate_water_system(df, rho, flow_safety_factor, pressure_safety_factor):
    """执行空调水系统全部水力计算，返回计算结果 DataFrame 和汇总数据"""
    df = df.copy()

    df["流量 q (m³/s)"] = df["flow_m3h"] / 3600
    df["管道内径 (m)"] = df["diameter_mm"] / 1000
    df["截面积 A (m²)"] = 3.14159 * df["管道内径 (m)"] ** 2 / 4
    df["流速 v (m/s)"] = df["流量 q (m³/s)"] / df["截面积 A (m²)"]
    df["动压 Pd (Pa)"] = rho * df["流速 v (m/s)"] ** 2 / 2
    df["沿程阻力 Py (Pa)"] = df["resistance_pa_per_m"] * df["length_m"]
    df["局部阻力 Pj (Pa)"] = df["local_zeta"] * df["动压 Pd (Pa)"]
    df["管段总阻力 Pi (Pa)"] = df["沿程阻力 Py (Pa)"] + df["局部阻力 Pj (Pa)"]

    # 流速校核
    df["流速校核"] = "合适"
    df.loc[df["流速 v (m/s)"] < 0.6, "流速校核"] = "偏低"
    df.loc[df["流速 v (m/s)"] > 2.5, "流速校核"] = "偏高"

    # 系统汇总
    total_flow = df["flow_m3h"].sum()
    total_loss = df["管段总阻力 Pi (Pa)"].sum()
    pump_flow = total_flow * flow_safety_factor
    pump_head_pa = total_loss * pressure_safety_factor
    pump_head_m = pump_head_pa / (rho * 9.81)
    pump_head_kpa = pump_head_pa / 1000

    summary = {
        "total_flow": total_flow,
        "total_loss": total_loss,
        "pump_flow": pump_flow,
        "pump_head_m": pump_head_m,
        "pump_head_kpa": pump_head_kpa,
    }

    return df, summary


# ─── 页面渲染主函数 ──────────────────────────────────
def render_air_conditioning_water_module():
    """渲染空调水系统水力计算模块"""

    # ─── 模块说明 ─────────────────────────────────
    st.markdown("### 模块二：空调水系统水力计算")
    st.markdown(
        "本模块用于空调冷冻水、热水系统的初步水力计算，可根据负荷和供回水温差估算水流量，"
        "并进行管径、流速、沿程阻力、局部阻力、系统总阻力和水泵参数初步校核。"
    )

    # ─── 系统参数（侧边栏） ───────────────────────
    with st.sidebar:
        st.divider()
        st.header("系统参数")
        rho = st.number_input(
            "水密度 ρ (kg/m³)",
            min_value=800.0, max_value=1200.0, value=1000.0, step=10.0, format="%.0f",
            help="空调水密度一般取 1000 kg/m³。",
        )
        cp = st.number_input(
            "水比热容 c (kJ/(kg·℃))",
            min_value=1.0, max_value=10.0, value=4.186, step=0.001, format="%.3f",
            help="作为参考参数，计算中暂未直接使用。",
        )
        delta_t = st.number_input(
            "供回水温差 Δt (℃)",
            min_value=1.0, max_value=20.0, value=5.0, step=0.5, format="%.1f",
            help="空调水系统供回水温差，一般取 5 ℃。",
        )
        flow_safety_factor = st.number_input(
            "水泵流量安全系数",
            min_value=1.0, max_value=2.0, value=1.10, step=0.01, format="%.2f",
        )
        pressure_safety_factor = st.number_input(
            "水泵扬程安全系数",
            min_value=1.0, max_value=2.0, value=1.15, step=0.01, format="%.2f",
        )
        st.caption(
            "计算结果仅供课程设计和工程初步校核使用，"
            "实际工程应结合规范、设备样本及最不利环路进行复核。"
        )

    # ─── 数据输入 ─────────────────────────────────
    st.subheader("管段数据输入")

    if "water_input_df" not in st.session_state:
        st.session_state["water_input_df"] = pd.DataFrame(
            {
                "pipe_no": pd.Series(dtype="str"),
                "load_kw": pd.Series(dtype="float64"),
                "flow_m3h": pd.Series(dtype="float64"),
                "diameter_mm": pd.Series(dtype="float64"),
                "length_m": pd.Series(dtype="float64"),
                "resistance_pa_per_m": pd.Series(dtype="float64"),
                "local_zeta": pd.Series(dtype="float64"),
            }
        )
    if "water_editor_version" not in st.session_state:
        st.session_state["water_editor_version"] = 0

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        load_example = st.button("加载示例数据", use_container_width=True)
    with col2:
        if st.button("计算", use_container_width=True, type="primary"):
            pass  # calculation happens after data_editor
    with col3:
        if st.button("清空", use_container_width=True):
            st.session_state["water_input_df"] = pd.DataFrame(
                {
                    "pipe_no": pd.Series(dtype="str"),
                    "load_kw": pd.Series(dtype="float64"),
                    "flow_m3h": pd.Series(dtype="float64"),
                    "diameter_mm": pd.Series(dtype="float64"),
                    "length_m": pd.Series(dtype="float64"),
                    "resistance_pa_per_m": pd.Series(dtype="float64"),
                    "local_zeta": pd.Series(dtype="float64"),
                }
            )
            st.session_state["water_editor_version"] += 1

    if load_example:
        df = pd.DataFrame(SAMPLE_DATA)
        df = calculate_flows(df, delta_t)
        st.session_state["water_input_df"] = df
        st.session_state["water_editor_version"] += 1
        st.success("已加载示例数据，水流量已根据负荷和温差自动估算，可手动修改。")

    # 可编辑数据表格
    st.caption("双击单元格编辑，水流量可根据负荷自动估算，也支持手动修改。")
    edited_df = st.data_editor(
        st.session_state["water_input_df"],
        num_rows="dynamic",
        use_container_width=True,
        key=f"water_editor_{st.session_state['water_editor_version']}",
        column_config={
            "pipe_no": st.column_config.TextColumn("管段编号"),
            "load_kw": st.column_config.NumberColumn("负荷 (kW)", min_value=0, format="%.1f"),
            "flow_m3h": st.column_config.NumberColumn("水流量 (m³/h)", min_value=0, format="%.2f"),
            "diameter_mm": st.column_config.NumberColumn("管内径 (mm)", min_value=0, format="%.0f"),
            "length_m": st.column_config.NumberColumn("长度 (m)", min_value=0, format="%.1f"),
            "resistance_pa_per_m": st.column_config.NumberColumn(
                "比摩阻 R (Pa/m)", min_value=0, format="%.1f"
            ),
            "local_zeta": st.column_config.NumberColumn("局部阻力系数 ζ", min_value=0, format="%.1f"),
        },
    )
    st.session_state["water_input_df"] = edited_df

    # ─── 计算 ─────────────────────────────────────
    st.subheader("计算结果")

    if edited_df.empty:
        st.info("请输入管段数据或点击「加载示例数据」开始计算。")
        return

    # 校验
    df = edited_df.copy()
    required = ["load_kw", "diameter_mm", "length_m", "resistance_pa_per_m"]
    missing = df[required].isnull().any(axis=1)
    if missing.any():
        st.warning(f"第 {', '.join(df.index[missing].astype(str))} 行存在缺失值，请检查输入数据。")

    non_pos = (
        (df["load_kw"].fillna(0) <= 0)
        | (df["diameter_mm"].fillna(0) <= 0)
        | (df["length_m"].fillna(0) <= 0)
    )
    if non_pos.any():
        st.warning(
            f"管段 {', '.join(df.loc[non_pos, 'pipe_no'].astype(str))} "
            "中存在零或负值，请核实。计算结果仅供参考。"
        )

    valid = (
        (df["load_kw"].fillna(0) > 0)
        & (df["diameter_mm"].fillna(0) > 0)
        & (df["length_m"].fillna(0) > 0)
        & (df["resistance_pa_per_m"].fillna(0) >= 0)
        & (df["local_zeta"].fillna(0) >= 0)
    )
    df_valid = df[valid].copy()

    if df_valid.empty:
        st.warning("没有有效数据可供计算。")
        return

    df_result, summary = calculate_water_system(df_valid, rho, flow_safety_factor, pressure_safety_factor)

    # ─── 结果展示 ─────────────────────────────────
    display_cols = [
        "pipe_no", "load_kw", "flow_m3h", "diameter_mm",
        "截面积 A (m²)", "流速 v (m/s)", "动压 Pd (Pa)",
        "沿程阻力 Py (Pa)", "局部阻力 Pj (Pa)", "管段总阻力 Pi (Pa)",
        "流速校核",
    ]
    df_display = df_result[display_cols].round({
        "load_kw": 1, "flow_m3h": 2, "diameter_mm": 0,
        "截面积 A (m²)": 4, "流速 v (m/s)": 2,
        "动压 Pd (Pa)": 1, "沿程阻力 Py (Pa)": 1,
        "局部阻力 Pj (Pa)": 1, "管段总阻力 Pi (Pa)": 1,
    })
    st.dataframe(df_display, use_container_width=True, hide_index=True,
                 column_config={
                     "pipe_no": "管段编号",
                     "load_kw": "负荷 (kW)",
                     "flow_m3h": "水流量 (m³/h)",
                     "diameter_mm": "管内径 (mm)",
                 })

    # ─── 系统汇总 ─────────────────────────────────
    st.divider()
    st.subheader("系统汇总")

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("系统总流量", f"{summary['total_flow']:.2f} m³/h")
    with c2:
        st.metric("系统总阻力", f"{summary['total_loss']:.1f} Pa")
    with c3:
        st.metric("推荐水泵流量", f"{summary['pump_flow']:.2f} m³/h")
    with c4:
        st.metric("推荐水泵扬程", f"{summary['pump_head_m']:.2f} m")
    with c5:
        st.metric("推荐水泵扬程", f"{summary['pump_head_kpa']:.1f} kPa")

    st.caption(
        "水泵参数为简化估算，实际选型应结合设备样本、最不利环路及水力平衡要求复核。"
    )

    # ─── 流速校核说明 ─────────────────────────────
    st.caption(
        "流速校核范围 (0.6–2.5 m/s) 仅用于课程设计和初步校核，"
        "实际工程应结合系统类型、管径、噪声和规范要求复核。"
    )

    # ─── 导出结果 ─────────────────────────────────
    st.divider()
    st.subheader("导出数据")

    df_export = rename_export_columns(df_result, WATER_EXPORT_MAP)

    col_csv, col_xlsx = st.columns(2)
    with col_csv:
        st.download_button(
            label="📥 下载 CSV",
            data=get_csv_bytes(df_export),
            file_name="空调水系统水力计算结果.csv",
            mime="text/csv",
            use_container_width=True,
        )
    summary_rows = [
        ("系统总流量", f"{summary['total_flow']:.2f} m³/h"),
        ("系统总阻力", f"{summary['total_loss']:.1f} Pa"),
        ("推荐水泵流量", f"{summary['pump_flow']:.2f} m³/h"),
        ("推荐水泵扬程", f"{summary['pump_head_m']:.2f} m"),
        ("推荐水泵扬程", f"{summary['pump_head_kpa']:.1f} kPa"),
    ]
    with col_xlsx:
        st.download_button(
            label="📥 下载 Excel",
            data=export_formatted_excel(df_export, summary_rows),
            file_name="空调水系统水力计算结果.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    # ─── 计算公式说明 ─────────────────────────────
    st.divider()
    st.subheader("计算公式说明")

    with st.expander("查看计算公式"):
        st.markdown(
            f"当前水密度 ρ = {rho:.0f} kg/m³，供回水温差 Δt = {delta_t:.1f} ℃。"
        )
        st.markdown(
            """
| 计算项目 | 公式 | 单位说明 |
|---------|------|---------|
| 水流量估算 | <i>G</i> = 0.86 × <i>Q</i><sub>L</sub> / Δ<i>t</i> | <i>G</i>：m³/h，<i>Q</i><sub>L</sub>：kW，Δ<i>t</i>：℃ |
| 流量换算 | <i>q</i> = <i>G</i> / 3600 | <i>q</i>：m³/s |
| 截面积 | <i>A</i> = π<i>D</i><sup>2</sup> / 4 | <i>A</i>：m²，<i>D</i>：m |
| 流速 | <i>v</i> = <i>q</i> / <i>A</i> | <i>v</i>：m/s |
| 动压 | <i>P</i><sub>d</sub> = ρ<i>v</i><sup>2</sup> / 2 | <i>P</i><sub>d</sub>：Pa，ρ：kg/m³ |
| 沿程阻力 | <i>P</i><sub>y</sub> = <i>R</i> × <i>L</i> | <i>P</i><sub>y</sub>：Pa，<i>R</i>：Pa/m，<i>L</i>：m |
| 局部阻力 | <i>P</i><sub>j</sub> = ζ × <i>P</i><sub>d</sub> | <i>P</i><sub>j</sub>：Pa |
| 管段总阻力 | <i>P</i><sub>i</sub> = <i>P</i><sub>y</sub> + <i>P</i><sub>j</sub> | <i>P</i><sub>i</sub>：Pa |
| 系统总阻力 | Σ<i>P</i> = Σ<i>P</i><sub>i</sub> | Pa |
| 水泵流量 | <i>G</i><sub>pump</sub> = <i>G</i><sub>total</sub> × <i>k</i><sub>f</sub> | <i>G</i><sub>pump</sub>：m³/h，<i>k</i><sub>f</sub>：流量安全系数 |
| 水泵扬程 | <i>H</i> = Σ<i>P</i> × <i>k</i><sub>p</sub> / (ρ<i>g</i>) | <i>H</i>：m，<i>k</i><sub>p</sub>：扬程安全系数，<i>g</i>：9.81 m/s² |
""",
            unsafe_allow_html=True,
        )

    # ─── 免责声明 ─────────────────────────────────
    st.divider()
    st.caption(
        "计算结果仅供课程设计和工程初步校核使用，"
        "实际工程应结合规范、设备样本、最不利环路及水力平衡要求进行复核。"
    )
