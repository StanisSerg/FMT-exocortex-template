"""Сценарии сдвига кривой на реальных данных КТ Зенченко МТК Ленинский."""

from __future__ import annotations

import os

import pandas as pd

from economics import format_rub, project_economics
from models import (
    ZENCHTC_LENINSKY_PARAMS,
    apply_shift,
    herd_summary,
    simulate_herd,
)

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "zenchtc-leninsky-herd.csv")

# Экономика (заглушки — заменить на актуальные цены фермы)
MILK_PRICE = 40.0          # ₽/кг ≈ литр
FEED_COST_PER_LITER = 15.0 # ₽/л доп. молока
HORIZON_DAYS = 365


def run_scenario(
    herd: pd.DataFrame,
    name: str,
    shift_type: str,
    delta: float,
    dim_target: float | None = None,
) -> dict:
    """Рассчитывает один сценарий и возвращает метрики."""
    shifted = {
        p: apply_shift(params, shift_type, delta, dim_target)
        for p, params in ZENCHTC_LENINSKY_PARAMS.items()
    }
    result = simulate_herd(herd, ZENCHTC_LENINSKY_PARAMS, shifted)
    summary = herd_summary(result)
    econ = project_economics(
        summary["delta_daily_yield_l"], MILK_PRICE, FEED_COST_PER_LITER, HORIZON_DAYS
    )
    return {
        "name": name,
        "summary": summary,
        "economics": econ,
        "result": result,
    }


def main() -> None:
    herd = pd.read_csv(DATA_PATH)
    # Исключаем соматическую группу 19 из прогноза (модель для здоровых коров)
    herd = herd[herd["group"] != 19].copy()
    total = int(herd["count"].sum())

    base = simulate_herd(herd, ZENCHTC_LENINSKY_PARAMS)
    base_summary = herd_summary(base)

    print("=" * 60)
    print("🐄 Сценарии для КТ Зенченко МТК Ленинский")
    print("=" * 60)
    print(f"Коров в расчёте: {total}")
    print(f"Базовый удой/день: {base_summary['base_daily_yield_l']:,.1f} л".replace(",", " "))
    print(f"Базовый удой/гол:  {base_summary['base_daily_yield_l'] / total:.2f} л")

    scenarios = [
        run_scenario(herd, "+1,5 л на DIM 100", "point", 1.5, 100),
        run_scenario(herd, "+2 л перед запуском (peak)", "peak", 2.0),
    ]

    print("\n" + "-" * 60)
    print(f"{'Сценарий':<35} {'Δ л/день':>12} {'Δ л/гол':>10} {'Прибыль/год':>15}")
    print("-" * 60)
    for s in scenarios:
        delta_day = s["summary"]["delta_daily_yield_l"]
        delta_per_cow = s["summary"]["delta_per_cow_l"]
        profit = s["economics"]["extra_profit_rub"]
        print(
            f"{s['name']:<35} {delta_day:>+12.1f} {delta_per_cow:>+10.2f} {format_rub(profit):>15}"
        )

    print("\n" + "-" * 60)
    print("Детализация по группам для сценария '+1,5 л на DIM 100':")
    detail = scenarios[0]["result"]
    print(
        detail[["group", "parity", "dim", "count", "base_yield_per_cow", "shifted_yield_per_cow", "delta_total"]]
        .rename(
            columns={
                "group": "Группа",
                "parity": "Паритет",
                "dim": "DIM",
                "count": "Кол-во",
                "base_yield_per_cow": "База, л",
                "shifted_yield_per_cow": "Сдвиг, л",
                "delta_total": "Δ всего, л",
            }
        )
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
