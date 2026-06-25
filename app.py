import streamlit as st
import pandas as pd
import io

st.set_page_config(
    page_title="建环工程计算工具箱 — 通风风管水力计算",
    page_icon="🧰",
    layout="wide",
)

# ─── 项目说明 ─────────────────────────────────────────
st.title("建环工程计算工具箱")
st.markdown("### 模块一：通风风管水力计算")
st.markdown(
    "本工具用于通风风管系统初步水力计算，可计算风速、当量直径、动压、"
    "沿程阻力、局部阻力、系统总阻力，并给出风机风量与风压参考值。"
)

# ─── 输入参数 ──────────────────────────────────────────
with st.sidebar:
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
    st.divider()
    st.caption("本工具为学习和辅助计算用途，正式工程设计应以规范、教材和设计手册为准。")

# ─── 管段计算 ──────────────────────────────────────────
st.subheader("管段数据输入")

# 初始化 session_state（保存输入数据）
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
    load_example = st.button("加载示例数据", use_container_width=True)

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
    use_container_width=True,
    key=f"duct_editor_{st.session_state['editor_version']}",
    column_config={
        "segment_id": st.column_config.TextColumn("管段编号", help="管段唯一标识"),
        "airflow_m3h": st.column_config.NumberColumn("风量 (m³/h)", min_value=0, format="%.0f"),
        "width_mm": st.column_config.NumberColumn("宽度 (mm)", min_value=0, format="%.0f"),
        "height_mm": st.column_config.NumberColumn("高度 (mm)", min_value=0, format="%.0f"),
        "length_m": st.column_config.NumberColumn("长度 (m)", min_value=0, format="%.1f"),
        "friction_pa_per_m": st.column_config.NumberColumn("单位长度摩擦阻力 R (Pa/m)", min_value=0, format="%.2f"),
        "zeta": st.column_config.NumberColumn("局部阻力系数 ζ", min_value=0, format="%.2f"),
    },
)
# 保存用户编辑到 session_state，确保 rerun 后不丢失
st.session_state["input_df"] = edited_df

# ─── 计算逻辑 ─────────────────────────────────────
st.subheader("计算结果")

if edited_df.empty:
    st.info('请输入管段数据或点击《加载示例数据》开始计算。')
else:
    df = edited_df.copy()

    # 检查缺失值
    required_cols = ["airflow_m3h", "width_mm", "height_mm", "length_m", "friction_pa_per_m", "zeta"]
    missing = df[required_cols].isnull().any(axis=1)
    if missing.any():
        st.warning(
            f"第 {', '.join(df.index[missing].astype(str))} 行存在缺失值，"
            f"已跳过计算。请检查输入数据。"
        )

    # 检查非正数值
    non_positive = (
        (df["airflow_m3h"] <= 0)
        | (df["width_mm"] <= 0)
        | (df["height_mm"] <= 0)
        | (df["length_m"] <= 0)
    )
    if non_positive.any():
        st.warning(
            f"管段 {', '.join(df.loc[non_positive, 'segment_id'].astype(str))} "
            f"中存在零或负值（风量/宽度/高度/长度），请核实。计算结果仅供参考。"
        )

    # 标记有效行（仅计算所有必需列 > 0 且非空的行）
    valid_mask = df["airflow_m3h"].fillna(0) > 0
    valid_mask &= df["width_mm"].fillna(0) > 0
    valid_mask &= df["height_mm"].fillna(0) > 0
    valid_mask &= df["length_m"].fillna(0) > 0
    valid_mask &= df["friction_pa_per_m"].fillna(0) >= 0
    valid_mask &= df["zeta"].fillna(0) >= 0

    # ─── 计算逻辑 ──────────────────────────
    df_result = df[valid_mask].copy()

    if df_result.empty:
        st.warning("没有有效数据可供计算。")
    else:
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

        # 系统总阻力
        system_total = df_result["管段总阻力 P (Pa)"].sum()

        # ─── 展示用结果表（精简列） ─────────
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

        # 保留两位小数
        df_display = df_result[display_cols].round(2)

        st.dataframe(df_display, use_container_width=True, hide_index=True)

        # ─── 系统汇总 ──────────────────
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.metric(
                label="系统总阻力 ΣP",
                value=f"{system_total:.2f} Pa",
                delta=f"{len(df_result)} 个管段",
            )

        # ─── 导出结果 ──────────────────────
        st.divider()
        st.subheader("导出数据")

        # 组合输入+结果用于导出
        df_export = df_result.copy()
        # 去掉中间过程列，保留完整结果
        export_cols = [
            "segment_id",
            "airflow_m3h",
            "width_mm",
            "height_mm",
            "length_m",
            "friction_pa_per_m",
            "zeta",
            "风量 Q (m³/s)",
            "截面积 A (m²)",
            "风速 v (m/s)",
            "当量直径 De (m)",
            "动压 Pd (Pa)",
            "沿程阻力 Py (Pa)",
            "局部阻力 Pj (Pa)",
            "管段总阻力 P (Pa)",
        ]
        df_export = df_export[export_cols]

        col_csv, col_xlsx = st.columns(2)

        with col_csv:
            csv_buf = io.BytesIO()
            df_export.to_csv(csv_buf, index=False, encoding="utf-8-sig")
            st.download_button(
                label="📥 下载 CSV",
                data=csv_buf.getvalue(),
                file_name="hvac_calculation_result.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with col_xlsx:
            xlsx_buf = io.BytesIO()
            with pd.ExcelWriter(xlsx_buf, engine="openpyxl") as writer:
                df_export.to_excel(writer, sheet_name="计算结果", index=False)
                # 额外写一行汇总
                summary = pd.DataFrame(
                    {"管段总阻力 P (Pa)": [f"系统总阻力 = {system_total:.2f} Pa"]}
                )
                summary.to_excel(
                    writer, sheet_name="计算结果", startrow=len(df_export) + 2, index=False
                )
            st.download_button(
                label="📥 下载 Excel",
                data=xlsx_buf.getvalue(),
                file_name="hvac_calculation_result.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

# ─── 计算公式说明 ─────────────────────────────────────────
st.divider()
st.subheader("计算公式说明")

with st.expander("查看计算公式"):
    st.markdown(
        f"当前空气密度 ρ = {rho:.2f} kg/m³，可在左侧边栏调整。"
    )
    st.markdown(
        """
| 计算项目 | 公式 | 单位说明 |
|---------|------|---------|
| 风量换算 | Q = Qh / 3600 | Q：m³/s，Qh：m³/h |
| 截面积 | A = a × b | A：m²，a、b：m |
| 风速 | v = Q / A | v：m/s |
| 水力直径 | De = 2ab / (a + b) | De：m |
| 动压 | Pd = ρv² / 2 | Pd：Pa，ρ：kg/m³ |
| 沿程阻力 | Py = R × L | Py：Pa，R：Pa/m，L：m |
| 局部阻力 | Pj = ζ × Pd | Pj：Pa |
| 管段总阻力 | P = Py + Pj | P：Pa |
| 系统总阻力 | ΣP = ΣPi | Pa |
"""
    )

# ─── 后续模块规划 ─────────────────────────────────────────
st.divider()
st.subheader("后续模块规划")
st.markdown(
    "本项目定位为建环工程计算工具箱，后续计划开发以下模块："
)
for m in [
    "空调水系统水力计算",
    "冷热源设备选型",
    "风机 / 水泵选型校核",
    "能耗与运行费用估算",
    "Word 计算说明书导出",
    "课程设计案例模板库",
]:
    st.markdown(f"- {m}")

# ─── 免责声明 ───────────────────────────────────────────────
st.divider()
st.caption(
    "计算结果仅供课程设计和工程初步校核使用，实际工程应结合规范、设备样本及最不利环路进行复核。"
)
