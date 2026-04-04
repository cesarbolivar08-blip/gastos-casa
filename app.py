import streamlit as st

st.set_page_config(
    page_title="💰 Gastos del Hogar",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Estilos globales ──────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background: #0f1117;
        color: #e8eaf0;
    }

    section[data-testid="stSidebar"] {
        background: #1a1d27 !important;
        border-right: 1px solid #2a2d3e;
    }

    section[data-testid="stSidebar"] .stRadio label {
        font-size: 0.95em;
        padding: 6px 0;
    }

    h1, h2, h3 { font-weight: 700; }
    h2 { color: #c8ccdf; letter-spacing: -0.02em; }

    .stMetric {
        background: #1a1d27;
        border: 1px solid #2a2d3e;
        border-radius: 12px;
        padding: 16px;
    }

    .stMetric label { color: #888 !important; font-size: 0.8em !important; }
    .stMetric [data-testid="metric-container"] > div:nth-child(2) {
        font-size: 1.5em !important;
        font-weight: 700 !important;
        color: #e8eaf0 !important;
    }

    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #4F8EF7, #7B61FF);
        border: none;
        color: white;
    }

    .stSelectbox > div, .stNumberInput > div, .stTextInput > div {
        border-radius: 8px;
    }

    hr { border-color: #2a2d3e !important; }

    .stDownloadButton > button {
        border-radius: 8px;
        border: 1px solid #2a2d3e;
        background: #1a1d27;
        color: #c8ccdf;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:20px 0 10px;'>
        <div style='font-size:2.5em;'>💰</div>
        <div style='font-weight:700;font-size:1.1em;color:#e8eaf0;'>Gastos del Hogar</div>
        <div style='color:#555;font-size:0.8em;'>César · Etzania · Nala 🐾</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    pagina = st.radio(
        "Navegación",
        ["📊 Dashboard", "➕ Registrar gasto", "📋 Historial", "🎯 Presupuestos"],
        label_visibility="collapsed",
    )

    st.divider()

    # Mini resumen rápido
    from utils.db import gastos_a_dataframe
    from datetime import date
    df_quick = gastos_a_dataframe()
    hoy = date.today()
    if not df_quick.empty:
        df_mes = df_quick[
            (df_quick["fecha"].dt.month == hoy.month) &
            (df_quick["fecha"].dt.year == hoy.year)
        ]
        total_mes = df_mes["monto"].sum()
        st.markdown(f"""
        <div style='background:#12151e;border-radius:10px;padding:14px;'>
            <div style='color:#666;font-size:0.75em;text-transform:uppercase;letter-spacing:0.05em;'>Este mes</div>
            <div style='font-size:1.4em;font-weight:700;color:#4F8EF7;'>${total_mes:,.0f} <span style='font-size:0.55em;color:#666;'>ARS</span></div>
            <div style='color:#555;font-size:0.78em;margin-top:4px;'>{len(df_mes)} transacciones</div>
        </div>
        """, unsafe_allow_html=True)

# ── Routing ───────────────────────────────────────────────────
if pagina == "📊 Dashboard":
    from pages.dashboard import render
    render()
elif pagina == "➕ Registrar gasto":
    from pages.registro import render
    render()
elif pagina == "📋 Historial":
    from pages.historial import render
    render()
elif pagina == "🎯 Presupuestos":
    from pages.presupuestos import render
    render()
