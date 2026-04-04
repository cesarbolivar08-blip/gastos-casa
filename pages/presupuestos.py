import streamlit as st
import pandas as pd
from utils.db import (
    CATEGORIAS, COLORES, cargar_presupuestos,
    guardar_presupuesto, gastos_a_dataframe
)
from datetime import date


def render():
    st.markdown("## 🎯 Presupuestos")
    st.caption("Definí límites de gasto por sección y categoría para controlar tu plata.")

    presupuestos = cargar_presupuestos()
    df = gastos_a_dataframe()
    hoy = date.today()

    # Filtrar gastos del mes actual
    df_mes = df[(df["fecha"].dt.month == hoy.month) & (df["fecha"].dt.year == hoy.year)]

    # ── Formulario para agregar/editar presupuesto ─────────────
    with st.expander("➕ Agregar / Editar presupuesto", expanded=not presupuestos):
        col1, col2, col3 = st.columns(3)
        with col1:
            sec = st.selectbox("Sección", list(CATEGORIAS.keys()), key="pres_sec")
        with col2:
            cat = st.selectbox("Categoría", CATEGORIAS[sec], key="pres_cat")
        with col3:
            monto = st.number_input("Límite mensual (ARS)", min_value=0.0, step=1000.0, format="%.2f")

        if st.button("💾 Guardar presupuesto", type="primary"):
            if monto <= 0:
                st.error("El monto debe ser mayor a 0.")
            else:
                guardar_presupuesto(sec, cat, monto)
                st.success(f"✅ Presupuesto guardado: {sec} · {cat} = ${monto:,.2f} ARS")
                st.rerun()

    st.divider()

    # ── Lista de presupuestos ─────────────────────────────────
    if not presupuestos:
        st.info("No tenés presupuestos definidos todavía.")
        return

    st.markdown(f"### Mes actual: {hoy.strftime('%B %Y')}")

    for key, pres in presupuestos.items():
        sec = pres["seccion"]
        cat = pres["categoria"]
        limite = pres["monto"]
        color = COLORES.get(sec, "#4F8EF7")

        gastado = df_mes[
            (df_mes["seccion"] == sec) & (df_mes["categoria"] == cat)
        ]["monto"].sum()

        restante = limite - gastado
        porcentaje = min(gastado / limite * 100, 100) if limite > 0 else 0

        if porcentaje < 70:
            estado_emoji = "🟢"
            bar_color = "#4FC98E"
        elif porcentaje < 90:
            estado_emoji = "🟡"
            bar_color = "#F7C948"
        else:
            estado_emoji = "🔴"
            bar_color = "#F76B6B"

        with st.container():
            col_info, col_nums = st.columns([3, 2])
            with col_info:
                st.markdown(
                    f"""<div style='margin-bottom:4px;'>
                    {estado_emoji} <b>{sec}</b> · {cat}
                    <span style='color:{color};font-size:0.85em;font-weight:600;'> (mensual)</span>
                    </div>""",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"""<div style='background:#eee;border-radius:6px;height:10px;margin:4px 0;'>
                    <div style='background:{bar_color};width:{porcentaje:.1f}%;height:10px;border-radius:6px;transition:width 0.3s;'></div>
                    </div>
                    <span style='font-size:0.8em;color:#888;'>{porcentaje:.1f}% usado</span>""",
                    unsafe_allow_html=True,
                )
            with col_nums:
                st.markdown(
                    f"""<div style='text-align:right;'>
                    <div style='font-size:0.8em;color:#888;'>Gastado</div>
                    <div style='font-weight:700;font-size:1.1em;'>${gastado:,.0f}</div>
                    <div style='font-size:0.8em;color:#888;margin-top:4px;'>de ${limite:,.0f}</div>
                    <div style='font-size:0.85em;color:{"#4FC98E" if restante >= 0 else "#F76B6B"};font-weight:600;'>
                    {"✅ Quedan" if restante >= 0 else "⚠️ Excedido"} ${abs(restante):,.0f}
                    </div>
                    </div>""",
                    unsafe_allow_html=True,
                )
        st.divider()
