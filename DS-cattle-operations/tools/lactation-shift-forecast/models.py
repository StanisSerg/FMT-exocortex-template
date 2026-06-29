"""Модели лактационной кривой для прогнозатора сдвига продуктивности."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Literal

import numpy as np
import pandas as pd
from scipy import integrate


@dataclass
class WoodParameters:
    """Параметры модели Wood: y(t) = a * t^b * exp(-c*t)."""

    a: float
    b: float
    c: float

    def yield_at(self, dim: float) -> float:
        """Удой в литрах на заданный DIM (дни после отела)."""
        if dim <= 0:
            return 0.0
        return self.a * (dim ** self.b) * np.exp(-self.c * dim)

    def peak(self) -> tuple[float, float]:
        """Возвращает (DIM пика, удой в пике)."""
        if self.c <= 0:
            return 0.0, 0.0
        dim_peak = self.b / self.c
        return dim_peak, self.yield_at(dim_peak)

    def yield_305(self) -> float:
        """305-дневный удой одной коровы (литров)."""
        result, _ = integrate.quad(lambda t: self.yield_at(t), 0, 305, limit=100)
        return float(result)


# Предустановленные параметры по паритетам (подобраны вручную для реалистичной формы).
DEFAULT_WOOD_PARAMS: dict[int, WoodParameters] = {
    1: WoodParameters(a=18.0, b=0.18, c=0.0030),
    2: WoodParameters(a=21.5, b=0.18, c=0.0030),
    3: WoodParameters(a=23.5, b=0.18, c=0.0030),
}


def build_curve_from_target(
    peak_yield: float, dim_peak: float, yield_305_target: float | None = None
) -> WoodParameters:
    """Подбирает параметры Wood под заданный пик и (опционально) 305-дневный удой.

    Подбор итеративный: фиксируем b, вычисляем c = b / dim_peak,
    затем a = peak_yield / (dim_peak**b * exp(-b)).
    """
    b = 0.18
    c = b / dim_peak
    a = peak_yield / (dim_peak ** b * np.exp(-b))
    params = WoodParameters(a=a, b=b, c=c)
    if yield_305_target is not None:
        # Корректируем масштаб a, чтобы 305-дневный удой совпал
        current_305 = params.yield_305()
        if current_305 > 0:
            params.a *= yield_305_target / current_305
    return params


def apply_shift(
    params: WoodParameters,
    shift_type: Literal["point", "peak"],
    delta_liters: float,
    dim_target: float | None = None,
) -> WoodParameters:
    """Возвращает новые параметры Wood с учётом сдвига.

    - "point": масштабирует кривую так, чтобы в точке `dim_target`
      удой вырос на `delta_liters`.
    - "peak": масштабирует кривую относительно пикового удоя
      (используется для сценария "перед запуском" / стартовый потенциал).
    """
    if shift_type == "point":
        if dim_target is None or dim_target <= 0:
            raise ValueError("Для point-сдвига нужен dim_target > 0")
        base_yield = params.yield_at(dim_target)
        if base_yield <= 0:
            raise ValueError(f"Базовый удой в DIM {dim_target} равен нулю, point-сдвиг невозможен")
        scale = (base_yield + delta_liters) / base_yield
        return WoodParameters(a=params.a * scale, b=params.b, c=params.c)

    if shift_type == "peak":
        _, peak_yield = params.peak()
        if peak_yield <= 0:
            raise ValueError("Пиковый удой равен нулю, peak-сдвиг невозможен")
        scale = (peak_yield + delta_liters) / peak_yield
        return WoodParameters(a=params.a * scale, b=params.b, c=params.c)

    raise ValueError(f"Неизвестный тип сдвига: {shift_type}")


def simulate_herd(
    herd: pd.DataFrame,
    params_by_parity: dict[int, WoodParameters],
    shifted_params_by_parity: dict[int, WoodParameters] | None = None,
) -> pd.DataFrame:
    """Считает базовую и новую продуктивность для каждой группы коров.

    Ожидаемые колонки в `herd`: parity (int), dim (float), count (int).
    Возвращает DataFrame с колонками:
    parity, dim, count, base_yield_per_cow, shifted_yield_per_cow,
    base_total, shifted_total, delta_total, delta_per_cow.
    """
    required = {"parity", "dim", "count"}
    if not required.issubset(herd.columns):
        raise ValueError(f"В таблице стада не хватает колонок: {required - set(herd.columns)}")

    result = herd.copy()
    result["base_yield_per_cow"] = result.apply(
        lambda row: params_by_parity.get(int(row["parity"]), DEFAULT_WOOD_PARAMS[3]).yield_at(
            row["dim"]
        ),
        axis=1,
    )

    if shifted_params_by_parity:
        result["shifted_yield_per_cow"] = result.apply(
            lambda row: shifted_params_by_parity.get(
                int(row["parity"]), DEFAULT_WOOD_PARAMS[3]
            ).yield_at(row["dim"]),
            axis=1,
        )
    else:
        result["shifted_yield_per_cow"] = result["base_yield_per_cow"]

    result["base_total"] = result["base_yield_per_cow"] * result["count"]
    result["shifted_total"] = result["shifted_yield_per_cow"] * result["count"]
    result["delta_total"] = result["shifted_total"] - result["base_total"]
    result["delta_per_cow"] = result["delta_total"] / result["count"].replace(0, np.nan)

    return result


def herd_summary(result: pd.DataFrame) -> dict[str, float]:
    """Агрегирует результаты по стаду."""
    total_cows = int(result["count"].sum())
    base_daily = float(result["base_total"].sum())
    shifted_daily = float(result["shifted_total"].sum())
    delta_daily = shifted_daily - base_daily
    return {
        "total_cows": total_cows,
        "base_daily_yield_l": base_daily,
        "shifted_daily_yield_l": shifted_daily,
        "delta_daily_yield_l": delta_daily,
        "delta_per_cow_l": delta_daily / total_cows if total_cows else 0.0,
    }


def make_default_herd() -> pd.DataFrame:
    """Возвращает синтетическое стадо для демонстрации."""
    rows = []
    for parity in [1, 2, 3]:
        for dim_group, count in [(30, 20), (100, 30), (200, 25), (280, 15)]:
            rows.append({"parity": parity, "dim": dim_group, "count": count})
    return pd.DataFrame(rows)
