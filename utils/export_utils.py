"""数据导出工具函数"""

import pandas as pd
import io


def prepare_export_dataframe(df_result):
    """从计算结果 DataFrame 中提取导出所需的列"""
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
    return df_result[export_cols].copy()


def get_csv_bytes(df):
    """返回 CSV 文件的 bytes"""
    buf = io.BytesIO()
    df.to_csv(buf, index=False, encoding="utf-8-sig")
    return buf.getvalue()


def get_excel_bytes(df, system_total):
    """返回 Excel 文件的 bytes，末尾追加系统总阻力汇总行"""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="计算结果", index=False)
        summary = pd.DataFrame(
            {"管段总阻力 P (Pa)": [f"系统总阻力 = {system_total:.2f} Pa"]}
        )
        summary.to_excel(
            writer, sheet_name="计算结果", startrow=len(df) + 2, index=False
        )
    return buf.getvalue()
