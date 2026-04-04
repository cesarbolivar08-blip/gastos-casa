import io
import pandas as pd
from datetime import datetime


def exportar_excel(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # Hoja general
        df_export = df.copy()
        df_export["fecha"] = df_export["fecha"].dt.strftime("%d/%m/%Y")
        df_export = df_export.drop(columns=["id", "fecha_registro"], errors="ignore")
        df_export.columns = [c.capitalize() for c in df_export.columns]
        df_export.to_excel(writer, sheet_name="Todos los gastos", index=False)

        # Hoja por sección
        for seccion in df["seccion"].unique():
            df_sec = df[df["seccion"] == seccion].copy()
            df_sec["fecha"] = df_sec["fecha"].dt.strftime("%d/%m/%Y")
            df_sec = df_sec.drop(columns=["id", "fecha_registro"], errors="ignore")
            df_sec.columns = [c.capitalize() for c in df_sec.columns]
            nombre_hoja = seccion.replace("🐾", "").strip()[:31]
            df_sec.to_excel(writer, sheet_name=nombre_hoja, index=False)

        # Hoja resumen
        resumen = df.groupby(["seccion", "categoria"])["monto"].sum().reset_index()
        resumen.columns = ["Sección", "Categoría", "Total (ARS)"]
        resumen.to_excel(writer, sheet_name="Resumen", index=False)

    return output.getvalue()


def exportar_pdf_simple(df: pd.DataFrame) -> bytes:
    """Genera un HTML que se puede imprimir como PDF desde el navegador."""
    total = df["monto"].sum()
    resumen = df.groupby("seccion")["monto"].sum().reset_index()

    filas_resumen = ""
    for _, row in resumen.iterrows():
        filas_resumen += f"<tr><td>{row['seccion']}</td><td>${row['monto']:,.2f}</td></tr>"

    filas_detalle = ""
    for _, row in df.iterrows():
        fecha = row["fecha"].strftime("%d/%m/%Y") if hasattr(row["fecha"], "strftime") else row["fecha"]
        filas_detalle += f"""
        <tr>
            <td>{fecha}</td>
            <td>{row.get('seccion','')}</td>
            <td>{row.get('categoria','')}</td>
            <td>{row.get('descripcion','')}</td>
            <td>${row.get('monto',0):,.2f}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Reporte de Gastos</title>
<style>
  body {{ font-family: 'Segoe UI', sans-serif; padding: 30px; color: #1a1a2e; }}
  h1 {{ color: #4F8EF7; border-bottom: 3px solid #4F8EF7; padding-bottom: 8px; }}
  h2 {{ color: #444; margin-top: 30px; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
  th {{ background: #1a1a2e; color: white; padding: 10px; text-align: left; }}
  td {{ padding: 8px 10px; border-bottom: 1px solid #eee; }}
  tr:nth-child(even) {{ background: #f8f9ff; }}
  .total {{ font-size: 1.3em; font-weight: bold; color: #4F8EF7; margin-top: 20px; }}
  @media print {{ body {{ padding: 10px; }} }}
</style>
</head>
<body>
<h1>💰 Reporte de Gastos del Hogar</h1>
<p>Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
<div class="total">Total general: ${total:,.2f} ARS</div>

<h2>Resumen por sección</h2>
<table>
  <tr><th>Sección</th><th>Total</th></tr>
  {filas_resumen}
</table>

<h2>Detalle de gastos</h2>
<table>
  <tr><th>Fecha</th><th>Sección</th><th>Categoría</th><th>Descripción</th><th>Monto</th></tr>
  {filas_detalle}
</table>
</body>
</html>"""
    return html.encode("utf-8")
