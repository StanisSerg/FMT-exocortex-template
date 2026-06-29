"""Экономический расчёт эффекта от сдвига продуктивности."""

from __future__ import annotations


def project_economics(
    delta_daily_yield_l: float,
    milk_price_rub_per_kg: float,
    feed_cost_rub_per_liter: float,
    horizon_days: int = 365,
) -> dict[str, float]:
    """Рассчитывает экономику изменения дневного удоя.

    Параметры
    ---------
    delta_daily_yield_l : float
        Изменение дневного удоя стада (литров).
    milk_price_rub_per_kg : float
        Цена молока (рублей за кг ≈ литр).
    feed_cost_rub_per_liter : float
        Дополнительные затраты на корм на литр дополнительного молока.
    horizon_days : int
        Горизонт расчёта (дней).

    Возвращает
    ----------
    dict с ключами:
        extra_milk_l, extra_revenue_rub, extra_feed_cost_rub, extra_profit_rub,
        profit_per_day_rub, feed_cost_share.
    """
    extra_milk_l = delta_daily_yield_l * horizon_days
    extra_revenue_rub = extra_milk_l * milk_price_rub_per_kg
    extra_feed_cost_rub = extra_milk_l * feed_cost_rub_per_liter
    extra_profit_rub = extra_revenue_rub - extra_feed_cost_rub
    profit_per_day_rub = extra_profit_rub / horizon_days if horizon_days else 0.0
    feed_cost_share = (
        extra_feed_cost_rub / extra_revenue_rub if extra_revenue_rub else 0.0
    )

    return {
        "extra_milk_l": extra_milk_l,
        "extra_revenue_rub": extra_revenue_rub,
        "extra_feed_cost_rub": extra_feed_cost_rub,
        "extra_profit_rub": extra_profit_rub,
        "profit_per_day_rub": profit_per_day_rub,
        "feed_cost_share": feed_cost_share,
    }


def format_rub(value: float) -> str:
    """Форматирует сумму в рублях."""
    return f"{value:,.0f} ₽".replace(",", " ")
