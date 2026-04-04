import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from utils.db import gastos_a_dataframe, cargar_presupuestos, COLORES, CATEGORIAS


def _gauge_presupuesto(gastado, limite, label, color):
    porcentaje = min(gastado / limite * 100, 100) if limite > 0 else 0
    estado = "🟢" if porcentaje < 70 else "🟡" if porcentaje < 90 else "🔴"
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=gastado,
        delta={"reference": limite, "valueformat": ",.0f"},
        number={"prefix": "$", "valueformat": ",.0f"},
        title={"text": f"{estado} {label}", "font": {"size": 13}},
        gauge={
            "axis": {"range": [0, limite], "tickformat": ",.0f"},
            "bar": {"color": color},
            "bgcolor": "rgba(0,0,0,0.05)",
            "steps": [
                {"range": [0, limite * 0.7], "color": "rgba(79,201,142,0.15)"},
                {"range": [limite * 0.7, limite * 0.9], "color": "rgba(247,201,72,0.15)"},
                {"range": [limite * 0.9, limite], "color": "rgba(247,100,100,0.15)"},
            ],
        },
    ))
    fig.update_layout(height=180, margin=dict(l=10, r=10, t=40, b=10))
    return fig


def render():
    df = gastos_a_dataframe()

    st.markdown("## 📊 Dashboard")

    if df.empty:
        st.info("🕳️ No hay gastos registrados todavía. ¡Andá a **Registrar** para agregar el primero!")
        return

    # ── Filtros ──────────────────────────────────────────────
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        periodo = st.selectbox("Período", ["Esta semana", "Este mes", "Mes anterior", "Todo"])
    with col_f2:
        secciones_disp = ["Todas"] + list(COLORES.keys())
        seccion_filtro = st.selectbox("Sección", secciones_disp)
    with col_f3:
        hoy = date.today()

    # Aplicar filtro de período
    if periodo == "Esta semana":
        inicio = hoy - timedelta(days=hoy.weekday())
        df = df[df["fecha"].dt.date >= inicio]
    elif periodo == "Este mes":
        df = df[(df["fecha"].dt.month == hoy.month) & (df["fecha"].dt.year == hoy.year)]
    elif periodo == "Mes anterior":
        mes_ant = hoy.replace(day=1) - timedelta(days=1)
        df = df[(df["fecha"].dt.month == mes_ant.month) & (df["fecha"].dt.year == mes_ant.year)]

    if seccion_filtro != "Todas":
        df = df[df["seccion"] == seccion_filtro]

    if df.empty:
        st.warning("No hay gastos para el período/sección seleccionada.")
        return

    # ── Métricas top ─────────────────────────────────────────
    total = df["monto"].sum()
    cant = len(df)
    promedio = total / cant if cant > 0 else 0
    mayor = df.loc[df["monto"].idxmax()]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("💰 Total", f"${total:,.0f}")
    m2.metric("🧾 Transacciones", cant)
    m3.metric("📐 Promedio", f"${promedio:,.0f}")
    m4.metric("🔝 Mayor gasto", f"${mayor['monto']:,.0f}", delta=mayor["descripcion"])

    st.divider()

    # ── Gráfico por sección ───────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### Por sección")
        por_sec = df.groupby("seccion")["monto"].sum().reset_index()
        colores_pie = [COLORES.get(s, "#999") for s in por_sec["seccion"]]
        fig_pie = px.pie(
            por_sec, values="monto", names="seccion",
            color="seccion",
            color_discrete_map=COLORES,
            hole=0.45,
        )
        fig_pie.update_traces(textposition="outside", textinfo="label+percent")
        fig_pie.update_layout(height=300, margin=dict(l=0, r=0, t=20, b=0), showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_b:
        st.markdown("#### Por categoría (top 8)")
        por_cat = df.groupby("categoria")["monto"].sum().nlargest(8).reset_index()
        fig_bar = px.bar(
            por_cat, x="monto", y="categoria", orientation="h",
            color_discrete_sequence=["#4F8EF7"],
            labels={"monto": "ARS", "categoria": ""},
        )
        fig_bar.update_layout(height=300, margin=dict(l=0, r=20, t=20, b=0))
        st.plotly_chart(fig_bar, use_container_width=True)

    # ── Evolución temporal ────────────────────────────────────
    st.markdown("#### Evolución de gastos")
    df["semana"] = df["fecha"].dt.to_period("W").dt.start_time
    df["mes_label"] = df["fecha"].dt.strftime("%b %Y")

    if periodo == "Esta semana":
        evol = df.groupby([df["fecha"].dt.date, "seccion"])["monto"].sum().reset_index()
        evol.columns = ["periodo", "seccion", "monto"]
        x_col = "periodo"
    else:
        evol = df.groupby(["semana", "seccion"])["monto"].sum().reset_index()
        evol.columns = ["periodo", "seccion", "monto"]
        x_col = "periodo"

    fig_line = px.bar(
        evol, x=x_col, y="monto", color="seccion",
        color_discrete_map=COLORES,
        barmode="stack",
        labels={"monto": "ARS", x_col: ""},
    )
    fig_line.update_layout(height=280, margin=dict(l=0, r=0, t=10, b=0), legend_title="Sección")
    st.plotly_chart(fig_line, use_container_width=True)

    # ── Presupuestos ──────────────────────────────────────────
    presupuestos = cargar_presupuestos()
    if presupuestos:
        st.divider()
        st.markdown("#### 🎯 Presupuestos del mes")
        cols = st.columns(min(len(presupuestos), 3))
        for i, (key, pres) in enumerate(presupuestos.items()):
            sec = pres["seccion"]
            cat = pres["categoria"]
            limite = pres["monto"]
            gastado_cat = df[
                (df["seccion"] == sec) & (df["categoria"] == cat)
            ]["monto"].sum()
            with cols[i % 3]:
                st.plotly_chart(
                    _gauge_presupuesto(gastado_cat, limite, f"{sec} · {cat}", COLORES.get(sec, "#4F8EF7")),
                    use_container_width=True
                )
