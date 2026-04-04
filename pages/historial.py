import streamlit as st
import pandas as pd
from datetime import date, timedelta
from utils.db import gastos_a_dataframe, eliminar_gasto, COLORES
from utils.exportar import exportar_excel, exportar_pdf_simple


def render():
    st.markdown("## 📋 Historial de gastos")

    df_full = gastos_a_dataframe()

    if df_full.empty:
        st.info("No hay gastos registrados todavía.")
        return

    # ── Filtros ───────────────────────────────────────────────
    with st.expander("🔍 Filtros", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            secciones = ["Todas"] + sorted(df_full["seccion"].unique().tolist())
            sec_filtro = st.selectbox("Sección", secciones)
        with col2:
            cats = ["Todas"] + sorted(df_full["categoria"].unique().tolist())
            cat_filtro = st.selectbox("Categoría", cats)
        with col3:
            metodos = ["Todos"] + sorted(df_full["metodo"].unique().tolist())
            met_filtro = st.selectbox("Método de pago", metodos)

        col4, col5 = st.columns(2)
        with col4:
            fecha_desde = st.date_input("Desde", value=date.today() - timedelta(days=30))
        with col5:
            fecha_hasta = st.date_input("Hasta", value=date.today())

        texto_busqueda = st.text_input("🔎 Buscar en descripción", placeholder="Ej: supermercado")

    # Aplicar filtros
    df = df_full.copy()
    df = df[(df["fecha"].dt.date >= fecha_desde) & (df["fecha"].dt.date <= fecha_hasta)]

    if sec_filtro != "Todas":
        df = df[df["seccion"] == sec_filtro]
    if cat_filtro != "Todas":
        df = df[df["categoria"] == cat_filtro]
    if met_filtro != "Todos":
        df = df[df["metodo"] == met_filtro]
    if texto_busqueda:
        df = df[df["descripcion"].str.contains(texto_busqueda, case=False, na=False)]

    df = df.sort_values("fecha", ascending=False)

    # ── Exportar ──────────────────────────────────────────────
    st.markdown(f"**{len(df)} gastos** · Total: **${df['monto'].sum():,.2f} ARS**")

    col_ex1, col_ex2, col_ex3 = st.columns([1, 1, 2])
    with col_ex1:
        excel_bytes = exportar_excel(df)
        st.download_button(
            "📥 Exportar Excel",
            data=excel_bytes,
            file_name=f"gastos_{date.today().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with col_ex2:
        pdf_html = exportar_pdf_simple(df)
        st.download_button(
            "📄 Exportar HTML/PDF",
            data=pdf_html,
            file_name=f"gastos_{date.today().strftime('%Y%m%d')}.html",
            mime="text/html",
            use_container_width=True,
        )

    st.divider()

    # ── Tabla ─────────────────────────────────────────────────
    if df.empty:
        st.warning("No hay gastos con esos filtros.")
        return

    for _, row in df.iterrows():
        color = COLORES.get(row["seccion"], "#888")
        with st.container():
            col_info, col_monto, col_del = st.columns([5, 2, 1])
            with col_info:
                st.markdown(
                    f"""<div style='border-left:3px solid {color};padding-left:10px;margin-bottom:4px;'>
                    <span style='font-weight:600;'>{row['descripcion']}</span>
                    <span style='color:#888;font-size:0.85em;'> · {row['seccion']} · {row['categoria']} · {row['metodo']}</span><br>
                    <span style='color:#aaa;font-size:0.8em;'>{row['fecha'].strftime('%d/%m/%Y')}</span>
                    {f"<span style='color:#bbb;font-size:0.8em;'> · {row['notas']}</span>" if row.get('notas') else ''}
                    </div>""",
                    unsafe_allow_html=True,
                )
            with col_monto:
                st.markdown(
                    f"<div style='text-align:right;font-weight:700;font-size:1.05em;padding-top:6px;'>${row['monto']:,.2f}</div>",
                    unsafe_allow_html=True,
                )
            with col_del:
                if st.button("🗑️", key=f"del_{row['id']}", help="Eliminar este gasto"):
                    eliminar_gasto(row["id"])
                    st.rerun()
        st.divider()
