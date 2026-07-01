import streamlit as st
from modules.ventilation_duct import render_ventilation_duct_module
from modules.air_conditioning_water import render_air_conditioning_water_module
from modules.terminal_equipment import render_terminal_equipment_module
from modules.heat_cold_source import render_heat_cold_source_module
from modules.fan_pump_selection import render_fan_pump_selection_module

REPO_DOCS_BASE_URL = "https://github.com/yishidezhangjie666-sys/hvac-duct-hydraulic-calculator/blob/main"

st.set_page_config(
    page_title="建环工程计算工具箱",
    page_icon="🧰",
    layout="wide",
)

st.title("建环工程计算工具箱")

module = st.sidebar.selectbox(
    "选择计算模块",
    [
        "通风风管水力计算",
        "空调水系统水力计算",
        "空调末端设备初步选型",
        "冷热源设备初步选型",
        "风机 / 水泵选型校核",
    ],
)

st.sidebar.markdown("---")
st.sidebar.markdown("当前稳定版本：`v0.2.1`")
st.sidebar.caption("本工具用于学习、课程设计辅助核算和工程初步校核，不能替代正式工程设计。")
st.sidebar.markdown(
    "\n".join(
        [
            "说明文档：",
            f"- [README]({REPO_DOCS_BASE_URL}/README.md)",
            f"- [用户使用指南]({REPO_DOCS_BASE_URL}/docs/USER_GUIDE.md)",
            f"- [Word 导出说明]({REPO_DOCS_BASE_URL}/docs/WORD_EXPORT_GUIDE.md)",
        ]
    )
)

if module == "通风风管水力计算":
    render_ventilation_duct_module()
elif module == "空调水系统水力计算":
    render_air_conditioning_water_module()
elif module == "空调末端设备初步选型":
    render_terminal_equipment_module()
elif module == "冷热源设备初步选型":
    render_heat_cold_source_module()
elif module == "风机 / 水泵选型校核":
    render_fan_pump_selection_module()
