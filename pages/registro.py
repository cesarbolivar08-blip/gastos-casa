import streamlit as st
from datetime import date
import base64
import json
from utils.db import CATEGORIAS, guardar_gasto, COLORES


def _icono_seccion(seccion):
    iconos = {"César": "👤", "Etzania": "👩", "Nala 🐾": "🐾", "Casa": "🏠"}
    return iconos.get(seccion, "📌")


def _analizar_ticket_con_ia(imagen_bytes: bytes, mime_type: str) -> dict:
    """Usa la API de Anthropic para extraer datos de un ticket/recibo."""
    try:
        import anthropic
        api_key = st.secrets.get("ANTHROPIC_API_KEY", None)
        client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()
        imagen_b64 = base64.standard_b64encode(imagen_bytes).decode("utf-8")
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": mime_type, "data": imagen_b64},
                    },
                    {
                        "type": "text",
                        "text": """Analizá este ticket/recibo y extraé la información. 
Respondé ÚNICAMENTE con un JSON válido sin backticks ni texto extra, con este formato exacto:
{
  "descripcion": "descripción corta del gasto",
  "monto": 1234.56,
  "fecha": "YYYY-MM-DD",
  "categoria_sugerida": "una sola palabra o concepto"
}
Si no podés leer algún campo, usá null. El monto debe ser número sin símbolo de moneda."""
                    }
                ],
            }],
        )
        texto = response.content[0].text.strip()
        return json.loads(texto)
    except Exception as e:
        st.error(f"Error al analizar la imagen: {e}")
        return {}


def render():
    st.markdown("## ➕ Registrar gasto")

    modo = st.radio(
        "¿Cómo querés registrar el gasto?",
        ["✏️ Manual", "📷 Foto de ticket (IA)"],
        horizontal=True,
    )

    datos_ia = {}

    if modo == "📷 Foto de ticket (IA)":
        st.info("📸 Sacá o subí una foto del ticket/recibo y la IA extrae los datos automáticamente.")
        archivo = st.file_uploader(
            "Subí la imagen del ticket",
            type=["jpg", "jpeg", "png", "webp"],
            key="ticket_upload"
        )
        if archivo:
            col_img, col_res = st.columns([1, 1])
            with col_img:
                st.image(archivo, caption="Ticket subido", use_container_width=True)
            with col_res:
                with st.spinner("🤖 Analizando ticket..."):
                    mime = f"image/{archivo.type.split('/')[-1]}"
                    if mime == "image/jpg":
                        mime = "image/jpeg"
                    datos_ia = _analizar_ticket_con_ia(archivo.read(), mime)
                if datos_ia:
                    st.success("✅ Datos extraídos. Revisalos y completá lo que falta.")
                    if datos_ia.get("monto"):
                        st.metric("Monto detectado", f"${datos_ia['monto']:,.2f} ARS")
                    if datos_ia.get("descripcion"):
                        st.caption(f"📝 {datos_ia['descripcion']}")

    st.divider()

    # Formulario
    col1, col2 = st.columns(2)

    with col1:
        seccion = st.selectbox(
            "Sección",
            list(CATEGORIAS.keys()),
            format_func=lambda x: f"{_icono_seccion(x)} {x}"
        )

    with col2:
        categorias_disponibles = CATEGORIAS[seccion]
        categoria_default = 0
        if datos_ia.get("categoria_sugerida"):
            sugerida = datos_ia["categoria_sugerida"].lower()
            for i, cat in enumerate(categorias_disponibles):
                if sugerida in cat.lower() or cat.lower() in sugerida:
                    categoria_default = i
                    break
        categoria = st.selectbox("Categoría", categorias_disponibles, index=categoria_default)

    descripcion_default = datos_ia.get("descripcion", "")
    descripcion = st.text_input("Descripción", value=descripcion_default, placeholder="Ej: Supermercado Coto")

    col3, col4 = st.columns(2)

    with col3:
        monto_default = float(datos_ia.get("monto") or 0.0)
        monto = st.number_input("Monto (ARS)", min_value=0.0, value=monto_default, step=100.0, format="%.2f")

    with col4:
        fecha_default = date.today()
        if datos_ia.get("fecha"):
            try:
                from datetime import datetime
                fecha_default = datetime.strptime(datos_ia["fecha"], "%Y-%m-%d").date()
            except Exception:
                pass
        fecha = st.date_input("Fecha", value=fecha_default)

    metodo = st.selectbox("Método de pago", ["Débito", "Crédito", "Efectivo", "Transferencia", "Otro"])

    notas = st.text_area("Notas adicionales (opcional)", height=80)

    st.divider()

    color = COLORES.get(seccion, "#4F8EF7")
    st.markdown(
        f"""<div style='padding:12px;border-left:4px solid {color};background:rgba(79,142,247,0.06);border-radius:6px;'>
        <b>{_icono_seccion(seccion)} {seccion}</b> · {categoria}<br>
        <span style='font-size:1.3em;font-weight:bold;'>${monto:,.2f} ARS</span>
        <span style='color:#888;font-size:0.9em;'> · {fecha.strftime('%d/%m/%Y')} · {metodo}</span>
        </div>""",
        unsafe_allow_html=True,
    )

    if st.button("💾 Guardar gasto", type="primary", use_container_width=True):
        if monto <= 0:
            st.error("⚠️ El monto debe ser mayor a 0.")
        elif not descripcion.strip():
            st.error("⚠️ Ingresá una descripción.")
        else:
            guardar_gasto({
                "fecha": fecha.isoformat(),
                "seccion": seccion,
                "categoria": categoria,
                "descripcion": descripcion.strip(),
                "monto": monto,
                "metodo": metodo,
                "notas": notas.strip(),
            })
            st.success(f"✅ Gasto guardado: {descripcion} — ${monto:,.2f} ARS")
            st.balloons()
