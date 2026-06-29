from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_ventilation_sample_data_has_varied_velocity_scenarios():
    df = pd.read_csv(ROOT / "sample_data.csv")

    required_cols = {
        "segment_id",
        "airflow_m3h",
        "width_mm",
        "height_mm",
        "length_m",
        "friction_pa_per_m",
        "zeta",
    }
    assert required_cols.issubset(df.columns)
    assert len(df) >= 5

    area = (df["width_mm"] / 1000) * (df["height_mm"] / 1000)
    velocity = (df["airflow_m3h"] / 3600) / area

    assert velocity.min() < 1.0
    assert velocity.max() > 6.0
    assert df["zeta"].max() >= 2.0


def test_water_sample_data_covers_flow_check_states():
    from modules.air_conditioning_water import (
        SAMPLE_DATA,
        calculate_flows,
        calculate_water_system,
    )

    df = calculate_flows(pd.DataFrame(SAMPLE_DATA), delta_t=5.0)
    result, summary = calculate_water_system(
        df,
        rho=1000,
        flow_safety_factor=1.10,
        pressure_safety_factor=1.15,
    )

    assert not result.empty
    assert summary["total_flow"] > 0
    assert {"偏低", "合适", "偏高"}.issubset(set(result["流速校核"]))


def test_terminal_equipment_sample_data_covers_selection_states():
    from modules.terminal_equipment import (
        FCU_SAMPLE_DATA,
        PAU_SAMPLE_DATA,
        calculate_fcu_selection,
        calculate_pau_selection,
    )

    fcu = calculate_fcu_selection(FCU_SAMPLE_DATA)
    pau = calculate_pau_selection(PAU_SAMPLE_DATA)

    assert len(fcu) >= 5
    assert {"建议可用", "拟选偏小", "余量偏大"}.issubset(set(fcu["选型结论"]))

    assert len(pau) >= 4
    assert {"建议可用", "拟选偏小", "需复核"}.issubset(set(pau["选型结论"]))
    assert "焓差需复核" in set(pau["焓差校核"])


def test_pau_sample_export_handles_enthalpy_review_case():
    from modules.terminal_equipment import (
        PAU_EXPORT_MAP,
        PAU_SAMPLE_DATA,
        _blank_missing_export_values,
        _format_percent_columns,
        _rename_export_columns,
        _pau_summary_rows,
        calculate_pau_selection,
    )
    from utils.export_utils import export_formatted_excel

    result = calculate_pau_selection(PAU_SAMPLE_DATA)
    result = result.convert_dtypes(dtype_backend="pyarrow")
    df_export = _blank_missing_export_values(
        _format_percent_columns(
            _rename_export_columns(result, PAU_EXPORT_MAP),
            ["冷量余量", "风量余量"],
        )
    )

    assert "焓差需复核" in set(result["焓差校核"])
    assert df_export.isna().sum().sum() == 0
    assert export_formatted_excel(
        df_export,
        _pau_summary_rows(result),
        sheet_name="新风机组选型",
        summary_sheet_name="选型汇总",
    )


def test_heat_cold_source_sample_data_covers_selection_states():
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

    for result in (air, chiller, boiler):
        assert len(result) >= 4
        assert not result.empty

    conclusions = set(air["选型结论"]) | set(chiller["选型结论"]) | set(boiler["选型结论"])
    assert "建议可用" in conclusions
    assert "拟选偏小" in conclusions
    assert conclusions.intersection({"余量偏大", "明显偏大"})
    assert any("复核" in value for value in conclusions)
