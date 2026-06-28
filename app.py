import streamlit as st
from modules.ventilation_duct import render_ventilation_duct_module
from modules.air_conditioning_water import render_air_conditioning_water_module
from modules.terminal_equipment import render_terminal_equipment_module
from modules.heat_cold_source import render_heat_cold_source_module

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
    ],
)

if module == "通风风管水力计算":
    render_ventilation_duct_module()
elif module == "空调水系统水力计算":
    render_air_conditioning_water_module()
elif module == "空调末端设备初步选型":
    render_terminal_equipment_module()
elif module == "冷热源设备初步选型":
    render_heat_cold_source_module()
