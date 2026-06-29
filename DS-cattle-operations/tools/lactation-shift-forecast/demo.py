"""Демонстрационный скрипт: тестовое стадо + два сценария сдвига."""

from __future__ import annotations

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from economics import format_rub, project_economics
from models import (
    DEFAULT_WOOD_PARAMS,
    WoodParameters,
    apply_shift,
    herd_summary,
    make_default_herd,
    simulate_herd,
)

# Экономика
MILK_PRICE = 40.0          # ₽/кг ≈ литр
FEED_COST_PER_LITER = 15.0 # ₽/л доп. молока
HORIZON_DAYS = 365


def print_scenario(name: str, result: pd.DataFrame, delta: float, economics: dict) -> None:
    """Красивый вывод результатов сценария."""
    print(f"\n{'='*60}")
    print(f"📊 {name}")
    print(f"{'='*60}")
    print(f"  Коров в стаде:      {int(result['count'].sum())}")
    print(f"  Базовый удой/день:  {herd_summary(result)['base_daily_yield_l']:,.1f} л".replace(",", " "))
    print(f"  Новый удой/день:    {herd_summary(result)['shifted_daily_yield_l']:,.1f} л".replace(",", " "))
    print(f"  Δ удоя/день:        {delta:+.1f} л")
    total = int(result['count'].sum())
    print(f"  Δ удоя/корову:      {delta / total:+.2f} л" if total else "  Δ удоя/корову:      —")
    print(f"  Доп. молока/год:    {economics['extra_milk_l']:,.0f} л".replace(",", " "))
    print(f"  Доп. выручка:       {format_rub(economics['extra_revenue_rub'])}")
    print(f"  Доп. корм:          {format_rub(economics['extra_feed_cost_rub'])}")
    print(f"  Доп. прибыль:       {format_rub(economics['extra_profit_rub'])}")
    print(f"  Доля корма:         {economics['feed_cost_share']*100:.1f}%")


def plot_curves(output_dir: str) -> None:
    """Строит базовые и сдвинутые лактационные кривые."""
    dim_range = np.linspace(1, 305, 300)
    fig, ax = plt.subplots(figsize=(10, 6))

    colors = {1: "#1f77b4", 2: "#ff7f0e", 3: "#2ca02c"}
    for parity in [1, 2, 3]:
        base = [DEFAULT_WOOD_PARAMS[parity].yield_at(d) for d in dim_range]
        shifted_point = [apply_shift(DEFAULT_WOOD_PARAMS[parity], "point", 1.5, 100).yield_at(d) for d in dim_range]
        shifted_peak = [apply_shift(DEFAULT_WOOD_PARAMS[parity], "peak", 2.0).yield_at(d) for d in dim_range]

        ax.plot(dim_range, base, color=colors[parity], linestyle="-", linewidth=2, label=f"П{parity} база")
        ax.plot(dim_range, shifted_point, color=colors[parity], linestyle="--", linewidth=1.5, label=f"П{parity} +1.5л@DIM100")
        ax.plot(dim_range, shifted_peak, color=colors[parity], linestyle=":", linewidth=1.5, label=f"П{parity} +2л peak")

    ax.axvline(100, color="gray", linestyle="-.", alpha=0.5, label="DIM 100")
    ax.set_xlabel("DIM, дни")
    ax.set_ylabel("Удой, л/день")
    ax.set_title("Лактационные кривые: база vs сценарии")
    ax.legend(loc="upper right", fontsize=8)
    ax.set_xlim(0, 305)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "lactation_curves.png"), dpi=150)
    plt.close(fig)


def plot_herd_distribution(herd: pd.DataFrame, output_dir: str) -> None:
    """Строит распределение стада по DIM."""
    fig, ax = plt.subplots(figsize=(8, 5))
    grouped = herd.groupby("dim")["count"].sum().sort_index()
    ax.bar(grouped.index.astype(str), grouped.values, color="steelblue")
    ax.set_xlabel("DIM-группа")
    ax.set_ylabel("Количество коров")
    ax.set_title("Распределение тестового стада по DIM")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "herd_distribution.png"), dpi=150)
    plt.close(fig)


def plot_scenarios_comparison(results: dict, output_dir: str) -> None:
    """Столбчатая диаграмма: база vs сценарии по дневному удою."""
    fig, ax = plt.subplots(figsize=(8, 5))
    labels = ["База", "+1.5л на DIM 100", "+2л peak"]
    values = [
        results["base_daily"],
        results["point_daily"],
        results["peak_daily"],
    ]
    colors = ["#cccccc", "#1f77b4", "#2ca02c"]
    bars = ax.bar(labels, values, color=colors)
    ax.set_ylabel("Удой стада, л/день")
    ax.set_title("Сравнение дневного удоя стада")
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 50, f"{val:,.0f}".replace(",", " "), ha="center")
    ax.set_ylim(0, max(values) * 1.15)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "scenarios_comparison.png"), dpi=150)
    plt.close(fig)


def main() -> None:
    output_dir = os.path.join(os.path.dirname(__file__), "demo_output")
    os.makedirs(output_dir, exist_ok=True)

    herd = make_default_herd()
    total_cows = int(herd["count"].sum())

    print("=" * 60)
    print("🐄 Тестовый пример: прогноз сдвига лактационной кривой")
    print("=" * 60)
    print(f"Стадо: {total_cows} коров")
    print("\nСтруктура стада:")
    print(herd.to_string(index=False))

    # Базовый расчёт
    base_result = simulate_herd(herd, DEFAULT_WOOD_PARAMS)
    base_summary = herd_summary(base_result)

    # Сценарий 1: +1.5 л на DIM 100
    shifted_point = {p: apply_shift(params, "point", 1.5, 100) for p, params in DEFAULT_WOOD_PARAMS.items()}
    result_point = simulate_herd(herd, DEFAULT_WOOD_PARAMS, shifted_point)
    summary_point = herd_summary(result_point)
    econ_point = project_economics(summary_point["delta_daily_yield_l"], MILK_PRICE, FEED_COST_PER_LITER, HORIZON_DAYS)

    # Сценарий 2: +2 л peak / перед запуском
    shifted_peak = {p: apply_shift(params, "peak", 2.0) for p, params in DEFAULT_WOOD_PARAMS.items()}
    result_peak = simulate_herd(herd, DEFAULT_WOOD_PARAMS, shifted_peak)
    summary_peak = herd_summary(result_peak)
    econ_peak = project_economics(summary_peak["delta_daily_yield_l"], MILK_PRICE, FEED_COST_PER_LITER, HORIZON_DAYS)

    print(f"\n{'─'*60}")
    print("📋 Сводка")
    print(f"{'─'*60}")
    print(f"{'Показатель':<35} {'База':>12} {'+1.5л@DIM100':>14} {'+2л peak':>12}")
    print(f"{'─'*60}")
    print(f"{'Удой/день, л':<35} {base_summary['base_daily_yield_l']:>12,.1f} {summary_point['shifted_daily_yield_l']:>14,.1f} {summary_peak['shifted_daily_yield_l']:>12,.1f}".replace(",", " "))
    print(f"{'Δ удоя/день, л':<35} {'—':>12} {summary_point['delta_daily_yield_l']:>+14.1f} {summary_peak['delta_daily_yield_l']:>+12.1f}")
    print(f"{'Доп. прибыль/год':<35} {'—':>12} {format_rub(econ_point['extra_profit_rub']):>14} {format_rub(econ_peak['extra_profit_rub']):>12}")

    print_scenario("Сценарий 1: +1,5 л на DIM 100", result_point, summary_point["delta_daily_yield_l"], econ_point)
    print_scenario("Сценарий 2: +2 л перед запуском (peak)", result_peak, summary_peak["delta_daily_yield_l"], econ_peak)

    # Графики
    plot_curves(output_dir)
    plot_herd_distribution(herd, output_dir)
    plot_scenarios_comparison(
        {
            "base_daily": base_summary["base_daily_yield_l"],
            "point_daily": summary_point["shifted_daily_yield_l"],
            "peak_daily": summary_peak["shifted_daily_yield_l"],
        },
        output_dir,
    )

    print(f"\n✅ Графики сохранены в {output_dir}/")


if __name__ == "__main__":
    main()
