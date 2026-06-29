from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_fan_selection_sample_data_calculates_expected_columns():
    from modules.fan_pump_selection import FAN_SAMPLE_DATA, calculate_fan_selection

    result = calculate_fan_selection(FAN_SAMPLE_DATA)
    required_cols = {
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
    }

    assert not result.empty
    assert required_cols.issubset(result.columns)
    assert result.loc[0, "所需风量 (m³/h)"] > 0
    assert result.loc[0, "风机轴功率参考 (kW)"] > 0
    assert result["复核建议"].notna().all()
    assert not result.astype(str).apply(lambda col: col.str.contains("正式工程可直接使用")).any().any()

    conclusions = set(result["选型结论"])
    assert "建议可用" in conclusions
    assert "拟选偏小" in conclusions
    assert {"余量偏大", "明显偏大"} & conclusions
    assert "需复核" in conclusions


def test_pump_selection_sample_data_calculates_expected_columns():
    from modules.fan_pump_selection import PUMP_SAMPLE_DATA, calculate_pump_selection

    result = calculate_pump_selection(PUMP_SAMPLE_DATA)
    required_cols = {
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
    }

    assert not result.empty
    assert required_cols.issubset(result.columns)
    assert result.loc[0, "所需流量 (m³/h)"] > 0
    assert result.loc[0, "水泵轴功率参考 (kW)"] > 0
    assert result["复核建议"].notna().all()
    assert not result.astype(str).apply(lambda col: col.str.contains("正式工程可直接使用")).any().any()

    conclusions = set(result["选型结论"])
    assert "建议可用" in conclusions
    assert "拟选偏小" in conclusions
    assert {"余量偏大", "明显偏大"} & conclusions
    assert "需复核" in conclusions


def test_fan_pump_invalid_inputs_need_review():
    from modules.fan_pump_selection import (
        calculate_fan_selection,
        calculate_pump_selection,
    )

    fan = calculate_fan_selection(
        {
            "required_airflow_m3h": [0.0],
            "required_pressure_pa": [650.0],
            "airflow_factor": [1.10],
            "pressure_factor": [1.15],
            "rated_airflow_m3h": [0.0],
            "rated_pressure_pa": [850.0],
            "motor_power_kw": [5.5],
            "fan_efficiency": [0.0],
        }
    )
    pump = calculate_pump_selection(
        {
            "required_flow_m3h": [0.0],
            "required_head_m": [28.0],
            "flow_factor": [1.10],
            "head_factor": [1.15],
            "rated_flow_m3h": [0.0],
            "rated_head_m": [36.0],
            "motor_power_kw": [15.0],
            "pump_efficiency": [0.0],
        }
    )

    assert pd.isna(fan.loc[0, "风量余量"])
    assert pd.isna(fan.loc[0, "风机轴功率参考 (kW)"])
    assert fan.loc[0, "选型结论"] == "需复核"

    assert pd.isna(pump.loc[0, "流量余量"])
    assert pd.isna(pump.loc[0, "水泵轴功率参考 (kW)"])
    assert pump.loc[0, "选型结论"] == "需复核"
