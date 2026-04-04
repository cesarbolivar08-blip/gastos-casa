import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

CATEGORIAS = {
    "César": ["Alimentación", "Transporte", "Salud", "Entretenimiento", "Ropa", "Gaming", "Gimnasio", "Otros"],
    "Etzania": ["Alimentación", "Transporte", "Salud", "Entretenimiento", "Ropa", "Belleza", "Otros"],
    "Nala 🐾": ["Veterinaria", "Comida", "Accesorios", "Medicamentos", "Otros"],
    "Casa": ["Alquiler", "Servicios", "Limpieza", "Mantenimiento", "Supermercado", "Otros"],
}

COLORES = {
    "César": "#4F8EF7",
    "Etzania": "#F76B8A",
    "Nala 🐾": "#F7C948",
    "Casa": "#4FC98E",
}

MONEDA = "ARS"


@st.cache_resource
def get_client() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


# ── Gastos ────────────────────────────────────────────────────

def cargar_gastos() -> list:
    try:
        sb = get_client()
        res = sb.table("gastos").select("*").order("fecha", desc=True).execute()
        return res.data or []
    except Exception as e:
        st.error(f"Error cargando gastos: {e}")
        return []


def guardar_gasto(gasto: dict) -> dict:
    try:
        sb = get_client()
        payload = {
            "fecha": gasto["fecha"],
            "seccion": gasto["seccion"],
            "categoria": gasto["categoria"],
            "descripcion": gasto["descripcion"],
            "monto": float(gasto["monto"]),
            "metodo": gasto.get("metodo", ""),
            "notas": gasto.get("notas", ""),
        }
        res = sb.table("gastos").insert(payload).execute()
        return res.data[0] if res.data else {}
    except Exception as e:
        st.error(f"Error guardando gasto: {e}")
        return {}


def eliminar_gasto(gasto_id) -> None:
    try:
        sb = get_client()
        sb.table("gastos").delete().eq("id", gasto_id).execute()
    except Exception as e:
        st.error(f"Error eliminando gasto: {e}")


# ── Presupuestos ──────────────────────────────────────────────

def cargar_presupuestos() -> dict:
    try:
        sb = get_client()
        res = sb.table("presupuestos").select("*").execute()
        result = {}
        for row in (res.data or []):
            key = f"{row['seccion']}|{row['categoria']}|{row['periodo']}"
            result[key] = row
        return result
    except Exception as e:
        st.error(f"Error cargando presupuestos: {e}")
        return {}


def guardar_presupuesto(seccion: str, categoria: str, monto: float, periodo: str = "mensual") -> None:
    try:
        sb = get_client()
        # Upsert por seccion+categoria+periodo
        sb.table("presupuestos").upsert(
            {"seccion": seccion, "categoria": categoria, "monto": monto, "periodo": periodo},
            on_conflict="seccion,categoria,periodo"
        ).execute()
    except Exception as e:
        st.error(f"Error guardando presupuesto: {e}")


# ── Helper DataFrame ──────────────────────────────────────────

def gastos_a_dataframe() -> pd.DataFrame:
    gastos = cargar_gastos()
    if not gastos:
        return pd.DataFrame(columns=["id", "fecha", "seccion", "categoria", "descripcion", "monto", "metodo", "notas"])
    df = pd.DataFrame(gastos)
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["monto"] = pd.to_numeric(df["monto"], errors="coerce")
    return df
