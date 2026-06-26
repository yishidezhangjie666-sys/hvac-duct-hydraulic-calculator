import streamlit as st
from modules.ventilation_duct import render_ventilation_duct_module

st.set_page_config(
    page_title="建环工程计算工具箱 — 通风风管水力计算",
    page_icon="🧰",
    layout="wide",
)

st.title("建环工程计算工具箱")

module = st.sidebar.selectbox(
    "选择计算模块",
    ["通风风管水力计算"],
)

if module == "通风风管水力计算":
    render_ventilation_duct_module()
