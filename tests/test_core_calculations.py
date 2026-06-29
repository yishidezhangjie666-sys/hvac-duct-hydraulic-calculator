from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_ventilation_sample_data_structure():
    from modules import ventilation_duct

    sample_path = ROOT / "sample_data.csv"
    assert hasattr(ventilation_duct, "render_ventilation_duct_module")
    assert sample_path.exists()

    df = pd.read_csv(sample_path)
    required_cols = {
        "segment_id",
        "airflow_m3h",
        "width_mm",
        "height_mm",
        "length_m",
        "friction_pa_per_m",
        "zeta",
    }
    assert not df.empty
    assert required_cols.issubset(df.columns)
    assert df["airflow_m3h"].notna().any()


def test_water_system_sample_calculation_runs():
    from modules.air_conditioning_water import (
        SAMPLE_DATA,
        calculate_flows,
        calculate_water_system,
    )

    df = pd.DataFrame(SAMPLE_DATA)
    df = calculate_flows(df, delta_t=5.0)
    result, summary = calculate_water_system(
        df,
        rho=1000,
        flow_safety_factor=1.10,
        pressure_safety_factor=1.15,
    )

    required_cols = {
        "流量 q (m³/s)",
        "截面积 A (m²)",
        "流速 v (m/s)",
        "管段总阻力 Pi (Pa)",
        "流速校核",
    }
    assert not result.empty
    assert required_cols.issubset(result.columns)
    assert result["管段总阻力 Pi (Pa)"].notna().any()
    assert summary["total_flow"] > 0
    assert summary["total_loss"] > 0


def test_terminal_equipment_sample_calculations_run():
    from modules.terminal_equipment import (
        FCU_SAMPLE_DATA,
        PAU_SAMPLE_DATA,
        calculate_fcu_selection,
        calculate_pau_selection,
    )

    fcu = calculate_fcu_selection(FCU_SAMPLE_DATA)
    pau = calculate_pau_selection(PAU_SAMPLE_DATA)

    assert not fcu.empty
    assert {"冷量余量", "热量余量", "风量余量", "选型结论"}.issubset(fcu.columns)
    assert fcu["冷量余量"].notna().any()
    assert fcu["选型结论"].notna().all()

    assert not pau.empty
    assert {"新风冷负荷 Q (kW)", "冷量余量", "风量余量", "选型结论"}.issubset(
        pau.columns
    )
    assert pau["新风冷负荷 Q (kW)"].notna().any()
    assert pau["选型结论"].notna().all()


def test_heat_cold_source_sample_calculations_run():
    from modules.heat_cold_source import (
        AIR_HEAT_PUMP_SAMPLE_DATA,
        BOILER_SAMPLE_DATA,
        CHILLER_SAMPLE_DATA,
        calculate_air_heat_pump_selection,
        calculate_boiler_selection,
        calculate_chiller_selection,
    )

    air = calculate_air_heat_pump_selection(AIR_HEAT_PUMP_SAMPLE_DATA)
    chiller = calculate_chiller_selection(CHILLER_SAMPLE_DATA)
    boiler = calculate_boiler_selection(BOILER_SAMPLE_DATA)

    assert not air.empty
    assert {"所需制冷量 (kW)", "总制冷量 (kW)", "制冷量余量", "选型结论"}.issubset(
        air.columns
    )
    assert air["制冷量余量"].notna().any()

    assert not chiller.empty
    assert {"所需制冷量 (kW)", "总制冷量 (kW)", "制冷量余量", "选型结论"}.issubset(
        chiller.columns
    )
    assert chiller["制冷量余量"].notna().any()

    assert not boiler.empty
    assert {"所需供热量 (kW)", "总供热量 (kW)", "供热量余量", "选型结论"}.issubset(
        boiler.columns
    )
    assert boiler["供热量余量"].notna().any()


def test_fan_pump_sample_calculations_run():
    from modules.fan_pump_selection import (
        FAN_SAMPLE_DATA,
        PUMP_SAMPLE_DATA,
        calculate_fan_selection,
        calculate_pump_selection,
    )

    fan = calculate_fan_selection(FAN_SAMPLE_DATA)
    pump = calculate_pump_selection(PUMP_SAMPLE_DATA)

    assert not fan.empty
    assert not pump.empty
    assert "选型结论" in fan.columns
    assert "选型结论" in pump.columns
