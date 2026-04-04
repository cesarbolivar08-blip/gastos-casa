# 💰 Gastos del Hogar

App web/mobile compartida en tiempo real entre **César**, **Etzania** y **Nala 🐾**.

**Stack:** Streamlit + Supabase + Anthropic  
**Deploy:** Streamlit Community Cloud (gratis)

---

## 🚀 Setup paso a paso

### 1 — Supabase (base de datos)

1. Cuenta gratuita en [supabase.com](https://supabase.com)
2. New project → nombre y contraseña
3. **SQL Editor → New Query** → pegá `supabase_setup.sql` y ejecutalo ▶️
4. Guardá:
   - **Project URL** → `Settings > API > Project URL`
   - **anon key** → `Settings > API > anon public`

### 2 — GitHub

```bash
git init
git add .
git commit -m "feat: gastos del hogar v2"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/gastos-casa.git
git push -u origin main
```

> ⚠️ El `.gitignore` ya excluye `secrets.toml`. Nunca subas las claves.

### 3 — Streamlit Community Cloud

1. [share.streamlit.io](https://share.streamlit.io) con tu cuenta GitHub
2. New app → repo `gastos-casa`, branch `main`, archivo `app.py`
3. **Advanced settings → Secrets**:

```toml
SUPABASE_URL      = "https://xxxxxxxxxxxx.supabase.co"
SUPABASE_KEY      = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
ANTHROPIC_API_KEY = "sk-ant-..."
```

4. Deploy → URL pública lista en ~2 minutos

### 4 — En el celular

- **iOS**: Safari → compartir → Agregar a pantalla de inicio
- **Android**: Chrome → menú → Agregar a pantalla de inicio

---

## 🗂️ Estructura

```
gastos_casa/
├── app.py                           ← Entry point
├── requirements.txt
├── supabase_setup.sql               ← Ejecutar una vez en Supabase
├── .gitignore
├── .streamlit/
│   └── secrets.toml.example         ← Plantilla (no subir el .toml real)
├── pages/
│   ├── dashboard.py                 ← Gráficos semanales y mensuales
│   ├── registro.py                  ← Manual + foto con IA
│   ├── historial.py                 ← Filtros y exportación
│   └── presupuestos.py              ← Límites por categoría
└── utils/
    ├── db.py                        ← Lógica Supabase
    └── exportar.py                  ← Excel y HTML/PDF
```

---

## ✨ Funcionalidades

| Feature | Detalle |
|---|---|
| 📝 Registro manual | Sección, categoría, monto, fecha, método |
| 📷 Foto de ticket | IA extrae datos automáticamente |
| 📊 Dashboard | Gráficos por sección, categoría, evolución temporal |
| 📋 Historial | Filtros, búsqueda y exportación |
| 🎯 Presupuestos | Límites con barra 🟢🟡🔴 |
| 📥 Excel / PDF | Exportación por sección y resumen |
| 🔄 Tiempo real | César y Etzania ven los mismos datos |
