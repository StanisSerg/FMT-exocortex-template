"""Валидация модели Wood на реальных данных фермы Зенченко МТК Ленинский."""

from __future__ import annotations

import os

import numpy as np
import pandas as pd

from models import DEFAULT_WOOD_PARAMS, WoodParameters, simulate_herd, herd_summary

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "zenchtc-leninsky-herd.csv")


def weighted_actual_yield(herd: pd.DataFrame) -> float:
    """Взвешенная средняя фактическая продуктивность по группам."""
    return float((herd["actual_yield"] * herd["count"]).sum() / herd["count"].sum())


def evaluate(herd: pd.DataFrame, params_by_parity: dict[int, WoodParameters]) -> dict:
    """Оценивает baseline-модель: считает метрики отклонения от факта."""
    result = simulate_herd(herd, params_by_parity)
    result["actual_yield"] = herd["actual_yield"].values
    result["error"] = result["base_yield_per_cow"] - result["actual_yield"]
    result["abs_error"] = result["error"].abs()

    total = int(herd["count"].sum())
    predicted_total = float(result["base_total"].sum())
    actual_total = float((herd["actual_yield"] * herd["count"]).sum())

    mae = float((result["abs_error"] * result["count"]).sum() / total)
    rmse = float(np.sqrt((result["error"] ** 2 * result["count"]).sum() / total))
    bias = predicted_total / actual_total - 1.0 if actual_total else 0.0

    return {
        "total_cows": total,
        "predicted_daily_yield_l": predicted_total,
        "actual_daily_yield_l": actual_total,
        "predicted_avg_yield_l": predicted_total / total if total else 0.0,
        "actual_avg_yield_l": actual_total / total if total else 0.0,
        "mae_l": mae,
        "rmse_l": rmse,
        "bias": bias,
        "detail": result,
    }


def calibrate_scales(herd: pd.DataFrame, exclude_groups: list[str] | None = None) -> dict[int, float]:
    """Подбирает масштабирующий множитель a для каждого паритета по факту.

    Решаем независимую задачу минимизации MSE для каждого паритета:
        scale_p = sum(actual_i * pred_i * count_i) / sum(pred_i^2 * count_i)
    где предсказание pred_i = Wood(a_p, b, c, dim_i).

    Параметры
    ----------
    exclude_groups : list[str] | None
        Список идентификаторов групп, которые не участвуют в калибровке
        (например, соматическая группа 19).
    """
    train = herd.copy()
    if exclude_groups:
        train = train[~train["group"].astype(str).isin(exclude_groups)]

    scales: dict[int, float] = {}
    for parity, params in DEFAULT_WOOD_PARAMS.items():
        sub = train[train["parity"] == parity]
        if sub.empty:
            scales[parity] = 1.0
            continue
        pred = sub.apply(lambda row: params.yield_at(row["dim"]), axis=1).values
        actual = sub["actual_yield"].values
        count = sub["count"].values
        numerator = float((actual * pred * count).sum())
        denominator = float(((pred ** 2) * count).sum())
        scales[parity] = numerator / denominator if denominator > 0 else 1.0
    return scales


def print_report(metrics: dict, title: str) -> None:
    print(f"\n{'='*60}")
    print(f"📊 {title}")
    print(f"{'='*60}")
    print(f"  Коров в стаде:        {metrics['total_cows']}")
    print(f"  Предсказано л/день:   {metrics['predicted_daily_yield_l']:,.1f}".replace(",", " "))
    print(f"  Фактически л/день:    {metrics['actual_daily_yield_l']:,.1f}".replace(",", " "))
    print(f"  Средний удой модели:  {metrics['predicted_avg_yield_l']:.2f} л")
    print(f"  Средний факт:         {metrics['actual_avg_yield_l']:.2f} л")
    print(f"  MAE:                  {metrics['mae_l']:.2f} л")
    print(f"  RMSE:                 {metrics['rmse_l']:.2f} л")
    print(f"  Смещение (bias):      {metrics['bias']*100:+.1f}%")
    print("\n  Детализация по группам:")
    detail = metrics["detail"]
    print(
        detail[
            ["group", "parity", "dim", "count", "actual_yield", "base_yield_per_cow", "error"]
        ]
        .rename(
            columns={
                "group": "Группа",
                "parity": "Паритет",
                "dim": "DIM",
                "count": "Кол-во",
                "actual_yield": "Факт, л",
                "base_yield_per_cow": "Модель, л",
                "error": "Ошибка, л",
            }
        )
        .to_string(index=False)
    )


def main() -> None:
    herd = pd.read_csv(DATA_PATH)

    # Baseline с параметрами по умолчанию
    baseline = evaluate(herd, DEFAULT_WOOD_PARAMS)
    print_report(baseline, "Baseline: параметры Wood по умолчанию")

    # Калибровка масштаба a под факт (группа 19 — соматика, исключаем)
    scales = calibrate_scales(herd, exclude_groups=["19"])
    calibrated_params = {
        parity: WoodParameters(a=params.a * scales[parity], b=params.b, c=params.c)
        for parity, params in DEFAULT_WOOD_PARAMS.items()
    }

    print("\n" + "-" * 60)
    print("Калибровочные множители (scale = a_new / a_default):")
    for parity, scale in scales.items():
        print(f"  Паритет {parity}: {scale:.3f}")

    calibrated = evaluate(herd, calibrated_params)
    print_report(calibrated, "После калибровки масштаба a по паритетам")

    # Сохраняем калиброванные параметры для использования в приложении
    print("\n" + "-" * 60)
    print("Калиброванные параметры Wood:")
    for parity, params in calibrated_params.items():
        print(f"  {parity}: WoodParameters(a={params.a:.4f}, b={params.b:.4f}, c={params.c:.4f})")


if __name__ == "__main__":
    main()
