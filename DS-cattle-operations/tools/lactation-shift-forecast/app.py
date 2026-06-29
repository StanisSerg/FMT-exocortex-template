"""Streamlit-приложение для прогноза сдвига лактационной кривой."""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from economics import format_rub, project_economics
from models import (
    DEFAULT_WOOD_PARAMS,
    ZENCHTC_LENINSKY_PARAMS,
    WoodParameters,
    apply_shift,
    herd_summary,
    make_default_herd,
    simulate_herd,
)

st.set_page_config(page_title="Прогнозатор сдвига лактационной кривой", layout="wide")

st.title("🐄 Прогнозатор сдвига лактационной кривой")
st.markdown(
    "Оцени, как изменится продуктивность стада при целевом улучшении кривой лактации."
)

# --- Боковая панель: параметры ---
with st.sidebar:
    st.header("⚙️ Параметры модели Wood")
    st.markdown("`y(t) = a · t^b · exp(-c·t)`")

    PRESETS = {
        "Default": DEFAULT_WOOD_PARAMS,
        "Зенченко Ленинский": ZENCHTC_LENINSKY_PARAMS,
    }

    selected_preset = st.selectbox(
        "Preset параметров",
        list(PRESETS.keys()) + ["Custom"],
        help="Выбери калиброванный preset или настрой параметры вручную (Custom).",
    )

    def _apply_preset(name: str) -> None:
        if name in PRESETS:
            for parity, params in PRESETS[name].items():
                st.session_state[f"a_{parity}"] = params.a
                st.session_state[f"b_{parity}"] = params.b
                st.session_state[f"c_{parity}"] = params.c

    # Инициализируем состояние при первой загрузке
    if "a_1" not in st.session_state:
        _apply_preset("Default")

    # При выборе готового preset обновляем значения в полях
    if selected_preset != "Custom":
        _apply_preset(selected_preset)

    params_by_parity: dict[int, WoodParameters] = {}
    for parity in [1, 2, 3]:
        with st.expander(f"Паритет {parity}", expanded=parity == 2):
            # Значения берутся из session_state через key; value не задаём,
            # чтобы избежать конфликта со Session State API.
            a = st.number_input(
                f"a (паритет {parity})",
                min_value=0.1,
                step=0.5,
                key=f"a_{parity}",
            )
            b = st.number_input(
                f"b (паритет {parity})",
                min_value=0.01,
                max_value=1.0,
                step=0.01,
                key=f"b_{parity}",
            )
            c = st.number_input(
                f"c (паритет {parity})",
                min_value=0.0001,
                max_value=0.02,
                step=0.0001,
                format="%.4f",
                key=f"c_{parity}",
            )
            params_by_parity[parity] = WoodParameters(a=a, b=b, c=c)

    st.header("💰 Экономика")
    milk_price = st.number_input(
        "Цена молока, ₽/кг", value=40.0, min_value=1.0, step=1.0
    )
    feed_cost = st.number_input(
        "Затраты на корм на литр молока, ₽/л",
        value=15.0,
        min_value=0.0,
        step=1.0,
    )
    horizon_days = st.number_input(
        "Горизонт расчёта, дней", value=365, min_value=1, step=30
    )

# --- Основная область: ввод стада ---
st.header("📊 Структура стада")
input_method = st.radio(
    "Способ ввода", ["Таблица по умолчанию", "Загрузить CSV", "Редактировать вручную"]
)

if input_method == "Таблица по умолчанию":
    herd_df = make_default_herd()
elif input_method == "Загрузить CSV":
    uploaded = st.file_uploader(
        "CSV с колонками: parity, dim, count", type=["csv"]
    )
    if uploaded is not None:
        herd_df = pd.read_csv(uploaded)
    else:
        herd_df = make_default_herd()
        st.info("CSV не загружен — используется таблица по умолчанию.")
else:
    st.markdown("Добавь группы коров: паритет, DIM, количество.")
    editor_df = pd.DataFrame(
        [{"parity": 1, "dim": 30, "count": 10}]
    )
    herd_df = st.data_editor(
        editor_df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "parity": st.column_config.NumberColumn(
                "Паритет", min_value=1, max_value=3, step=1
            ),
            "dim": st.column_config.NumberColumn(
                "DIM", min_value=0, max_value=500, step=1
            ),
            "count": st.column_config.NumberColumn(
                "Количество", min_value=0, step=1
            ),
        },
    )

herd_df = herd_df[herd_df["count"] > 0].copy()
herd_df["parity"] = herd_df["parity"].clip(1, 3)

st.dataframe(herd_df, use_container_width=True)

# --- Сценарий ---
st.header("🎯 Сценарий сдвига")
scenario = st.selectbox(
    "Тип сценария",
    [
        "+Y л на DIM X",
        "+Y л перед запуском (масштабирование peak)",
    ],
)

if scenario == "+Y л на DIM X":
    shift_type = "point"
    dim_target = st.number_input(
        "Целевой DIM", value=100, min_value=1, max_value=305, step=1
    )
    delta = st.number_input(
        "Прирост удоя в точке, л", value=1.5, min_value=0.0, step=0.1
    )
else:
    shift_type = "peak"
    dim_target = None
    delta = st.number_input(
        "Прирост пикового/стартового удоя, л", value=2.0, min_value=0.0, step=0.1
    )

# --- Расчёт ---
shifted_params_by_parity = {
    parity: apply_shift(params, shift_type, delta, dim_target)
    for parity, params in params_by_parity.items()
}

result = simulate_herd(herd_df, params_by_parity, shifted_params_by_parity)
summary = herd_summary(result)
econ = project_economics(
    summary["delta_daily_yield_l"], milk_price, feed_cost, int(horizon_days)
)

# --- Результаты ---
st.header("📈 Результаты")
cols = st.columns(4)
cols[0].metric("Коров в стаде", summary["total_cows"])
cols[1].metric(
    "Базовый удой/день",
    f"{summary['base_daily_yield_l']:,.0f} л".replace(",", " "),
)
cols[2].metric(
    "Новый удой/день",
    f"{summary['shifted_daily_yield_l']:,.0f} л".replace(",", " "),
)
cols[3].metric(
    "Δ удоя/день",
    f"{summary['delta_daily_yield_l']:+.1f} л",
    delta_color="normal",
)

econ_cols = st.columns(4)
econ_cols[0].metric("Доп. молока", f"{econ['extra_milk_l']:,.0f} л".replace(",", " "))
econ_cols[1].metric("Доп. выручка", format_rub(econ["extra_revenue_rub"]))
econ_cols[2].metric("Доп. корм", format_rub(econ["extra_feed_cost_rub"]))
econ_cols[3].metric(
    "Доп. прибыль",
    format_rub(econ["extra_profit_rub"]),
    delta_color="normal",
)

st.subheader("Детализация по группам")
st.dataframe(
    result[
        [
            "parity",
            "dim",
            "count",
            "base_yield_per_cow",
            "shifted_yield_per_cow",
            "delta_per_cow",
            "delta_total",
        ]
    ].rename(
        columns={
            "parity": "Паритет",
            "dim": "DIM",
            "count": "Кол-во",
            "base_yield_per_cow": "Базовый удой/гол",
            "shifted_yield_per_cow": "Новый удой/гол",
            "delta_per_cow": "Δ/гол",
            "delta_total": "Δ всего",
        }
    ),
    use_container_width=True,
)

# --- Графики ---
st.header("📉 Графики")
fig_col1, fig_col2 = st.columns(2)

with fig_col1:
    st.subheader("Лактационные кривые")
    dim_range = np.linspace(1, 305, 200)
    chart_data = pd.DataFrame(
        {
            "DIM": dim_range,
            **{
                f"Паритет {p} (база)": [
                    params_by_parity[p].yield_at(d) for d in dim_range
                ]
                for p in [1, 2, 3]
            },
            **{
                f"Паритет {p} (сдвиг)": [
                    shifted_params_by_parity[p].yield_at(d) for d in dim_range
                ]
                for p in [1, 2, 3]
            },
        }
    )
    st.line_chart(chart_data.set_index("DIM"))

with fig_col2:
    st.subheader("Распределение стада по DIM")
    herd_chart = (
        herd_df.groupby("dim")["count"].sum().reset_index().sort_values("dim")
    )
    st.bar_chart(herd_chart.set_index("dim"))

st.markdown("---")
st.caption(
    "MVP: упрощённая модель Wood. Результат — оценка порядка величины, не замена полноценной симуляции."
)
