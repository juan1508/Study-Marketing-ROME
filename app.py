"""
ROME Market Intelligence
Calculadora · Buscador de Mercado · Portfolio de Productos
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
import math
import json
from datetime import datetime, timedelta

# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ROME Market",
    page_icon="🔵",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── COLORES ───────────────────────────────────────────────────────
BG   = "#0A1628"; DARK = "#0D2137"; MID  = "#1A3A5C"
PRI  = "#1E5FAD"; BRT  = "#2E86DE"; ACC  = "#54A0FF"
PALE = "#A8D8F0"; WHT  = "#EEF6FF"; TEXT = "#DDE8F5"
GOLD = "#FFC300"; GRN  = "#00B894"; YEL  = "#FDCB6E"; RED  = "#E17055"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500&display=swap');
.stApp{{background:linear-gradient(135deg,{BG},{DARK});}}
html,body,[class*="css"]{{font-family:'DM Sans',sans-serif;color:{TEXT};}}
h1,h2,h3{{font-family:'Syne',sans-serif;font-weight:800;}}
#MainMenu,footer,header{{visibility:hidden;}}
div[data-testid="metric-container"]{{
  background:linear-gradient(135deg,{MID}CC,{PRI}33)!important;
  border:1px solid {ACC}40!important;border-radius:14px!important;padding:18px!important;}}
div[data-testid="metric-container"] label{{color:{PALE}!important;font-size:.75rem!important;text-transform:uppercase;letter-spacing:.06em;}}
[data-testid="stMetricValue"]{{color:{WHT}!important;font-family:'Syne',sans-serif!important;font-weight:800!important;font-size:1.3rem!important;}}
.stTabs [data-baseweb="tab-list"]{{background:{MID}80!important;border-radius:12px!important;padding:4px!important;}}
.stTabs [data-baseweb="tab"]{{background:transparent!important;color:{PALE}!important;border-radius:10px!important;font-size:.9rem!important;}}
.stTabs [aria-selected="true"]{{background:linear-gradient(135deg,{PRI},{BRT})!important;color:white!important;font-weight:600!important;}}
.stButton>button{{background:linear-gradient(135deg,{PRI},{BRT})!important;color:white!important;border:none!important;border-radius:10px!important;font-weight:600!important;transition:all .2s;}}
.stTextInput input,.stNumberInput input{{background:{MID}!important;border:1px solid {ACC}40!important;color:{WHT}!important;border-radius:10px!important;font-size:1rem!important;}}
hr{{border-color:{PRI}30!important;}}
.card{{background:linear-gradient(135deg,{MID},{DARK});border:1px solid {ACC}30;border-radius:16px;padding:20px;margin-bottom:12px;}}
.card-gold{{background:linear-gradient(135deg,#2A2010,{DARK});border:1px solid {GOLD}50;border-radius:16px;padding:20px;margin-bottom:12px;}}
.card-green{{background:linear-gradient(135deg,#0A2018,{DARK});border:1px solid {GRN}50;border-radius:16px;padding:20px;margin-bottom:12px;}}
.card-red{{background:linear-gradient(135deg,#2A0A08,{DARK});border:1px solid {RED}50;border-radius:16px;padding:20px;margin-bottom:12px;}}
</style>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# STORAGE — portfolio en session_state (persiste mientras la sesión)
# ─────────────────────────────────────────────────────────────────
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {}
    # Estructura: {nombre: {costo, pv_venta, historial:[{fecha,pv,rent}], ofertas:[], notas}}

if "search_results" not in st.session_state:
    st.session_state.search_results = []

if "calc_result" not in st.session_state:
    st.session_state.calc_result = None

# ─────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────
def fmt_cop(v):
    if abs(v) >= 1_000_000: return f"${v/1_000_000:.1f}M"
    if abs(v) >= 1_000:     return f"${v/1_000:.0f}K"
    return f"${v:,.0f}"

def calcular(costo, envio, publicidad, pct_dev, cant, rent_obj):
    """
    Formula tu tabla:
    Costo real total = (costo + envio + publicidad) × cant + devolucion
    PV sugerido para la rentabilidad objetivo
    """
    dev_cop      = envio * (pct_dev / 100)
    costo_total  = (costo + envio + publicidad) * cant + dev_cop
    costo_unit   = costo_total / cant

    # PV para cada cantidad con la rentabilidad objetivo
    # Rent% = (PV×cant - costo_total) / (PV×cant)  →  PV = costo_total / (cant × (1 - rent%))
    rent_dec = rent_obj / 100
    pv_total = costo_total / (1 - rent_dec)
    pv_unit  = math.ceil(pv_total / cant / 100) * 100   # redondeo a $100

    ganancia_total = pv_unit * cant - costo_total
    ganancia_unit  = ganancia_total / cant

    return {
        "dev_cop":       round(dev_cop),
        "costo_total":   round(costo_total),
        "costo_unit":    round(costo_unit),
        "pv_unit":       round(pv_unit),
        "ganancia_total":round(ganancia_total),
        "ganancia_unit": round(ganancia_unit),
        "rent_real":     round((ganancia_total / (pv_unit * cant)) * 100, 1),
    }

def buscar_makeup_api(termino):
    """Busca en Makeup API por nombre de producto."""
    try:
        # Buscar por tipo de producto
        tipos = ["foundation","serum","moisturizer","mascara","lip_liner",
                 "bronzer","primer","blush","eyeshadow","face_wash","lip_gloss"]
        resultados = []
        for tipo in tipos:
            r = requests.get(
                "https://makeup-api.herokuapp.com/api/v1/products.json",
                params={"product_type": tipo}, timeout=6)
            if r.status_code != 200: continue
            for p in r.json():
                nombre = (p.get("name") or "").lower()
                marca  = (p.get("brand") or "").lower()
                term   = termino.lower()
                if any(t in nombre or t in marca for t in term.split()):
                    price = float(p.get("price") or 0)
                    if price > 0:
                        resultados.append({
                            "nombre":   (p.get("name") or "")[:80],
                            "marca":    (p.get("brand") or "Unknown").title(),
                            "precio_usd": round(price, 2),
                            "pv_co_est":  round(price * 4200 * 2.3 / 1000) * 1000,
                            "rating":   float(p.get("rating") or 4.0),
                            "img":      p.get("image_link") or "",
                            "url":      p.get("product_link") or "",
                            "tipo":     tipo,
                            "colores":  len(p.get("product_colors") or []),
                        })
            if len(resultados) >= 20: break
        return resultados[:15]
    except Exception:
        return []

def simular_historial(pv_base, meses=12, tend="estable"):
    """Genera historial simulado de precios de mercado para un producto."""
    tf = {"muy_creciente": 0.04, "creciente": 0.02, "estable": 0.0, "decreciente": -0.02}.get(tend, 0.0)
    np.random.seed(int(pv_base) % 9999)
    hist = []
    pv = float(pv_base)
    for i in range(meses):
        d = datetime.now() - timedelta(days=30*(meses-i-1))
        pv = max(pv * (1 + tf + np.random.normal(0, 0.025)), pv_base * 0.7)
        hist.append({"fecha": d.strftime("%b %Y"), "pv_mercado": round(pv/1000)*1000})
    return hist

now = datetime.now()

# ─────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="padding:20px 0 8px;display:flex;align-items:center;gap:16px;">
  <div style="width:52px;height:52px;background:linear-gradient(135deg,{PRI},{BRT});
    border-radius:50%;display:flex;align-items:center;justify-content:center;
    font-size:24px;box-shadow:0 6px 24px {ACC}50;flex-shrink:0;">🔬</div>
  <div>
    <h1 style="margin:0;font-size:1.8rem;background:linear-gradient(90deg,{WHT},{ACC});
      -webkit-background-clip:text;-webkit-text-fill-color:transparent;">ROME Market</h1>
    <p style="margin:0;color:{PALE};font-size:.82rem;">
      Calculadora de precios · Buscador de mercado · Tu portfolio de productos Colombia</p>
  </div>
  <div style="margin-left:auto;text-align:right;">
    <div style="background:{MID}80;border:1px solid {ACC}30;border-radius:10px;padding:8px 14px;">
      <div style="color:{PALE};font-size:.7rem;text-transform:uppercase;">Portfolio</div>
      <div style="color:{WHT};font-weight:700;font-family:Syne,sans-serif;font-size:1.1rem;">
        {len(st.session_state.portfolio)} productos</div>
    </div>
  </div>
</div>
<hr style="margin:8px 0 0;">
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────
T1, T2, T3 = st.tabs([
    "🧮 Calculadora de Precios",
    "🔍 Buscar en el Mercado",
    "📦 Mi Portfolio",
])

# ═══════════════════════════════════════════════════════════════
# TAB 1 — CALCULADORA
# ═══════════════════════════════════════════════════════════════
with T1:
    st.markdown(f'<h3 style="color:{WHT};font-family:Syne,sans-serif;margin-bottom:4px;">🧮 Calculadora de Precios</h3>', unsafe_allow_html=True)
    st.caption("Ingresa los costos y te sugiero el precio de venta para cada cantidad")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── NOMBRE DEL PRODUCTO ────────────────────────────────────────
    prod_nombre = st.text_input(
        "📦 Nombre del producto",
        placeholder="Ej: Olaplex No.3, CeraVe Crema, Suero Vitamina C...",
        key="calc_nombre"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── INPUTS COSTOS (estructura de tu tabla) ─────────────────────
    st.markdown(f"""
    <div style="background:{MID}40;border:1px solid {ACC}25;border-radius:14px;padding:20px;margin-bottom:8px;">
      <div style="font-family:Syne,sans-serif;font-size:1rem;font-weight:700;color:{WHT};margin-bottom:16px;">
        📋 Datos del Producto — ingresa los costos en Pesos Colombianos (COP)
      </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        costo_prod = st.number_input(
            "💰 Precio del Producto (COP)",
            min_value=0, value=30000, step=1000,
            help="Lo que pagas tú por el producto — costo de adquisición"
        )
        publicidad = st.number_input(
            "📢 Costo de Publicidad (COP)",
            min_value=0, value=18000, step=1000,
            help="CPA — costo promedio por venta en publicidad"
        )
    with c2:
        envio = st.number_input(
            "🚚 Costo de Envío (COP)",
            min_value=0, value=18000, step=1000,
            help="Flete que pagas para enviar al cliente"
        )
        pct_dev = st.number_input(
            "↩️ % Devoluciones",
            min_value=0.0, max_value=100.0, value=20.0, step=1.0,
            help="Porcentaje estimado de devoluciones — se aplica sobre el envío"
        )

    # Calcular devolucion en tiempo real
    dev_cop = round(envio * (pct_dev / 100))

    st.markdown(f"""
      <div style="margin-top:16px;padding-top:14px;border-top:1px solid {PRI}40;
           display:flex;justify-content:space-between;align-items:center;">
        <div style="color:{PALE};font-size:.88rem;">
          Costo por Devolución ({pct_dev:.0f}% del envío):
          <span style="color:{YEL};font-weight:600;margin-left:8px;">${dev_cop:,}</span>
        </div>
        <div style="color:{PALE};font-size:.88rem;">
          Costo Real Total por Pedido (1 unidad):
          <span style="color:{WHT};font-weight:700;font-size:1.1rem;margin-left:8px;">
            ${costo_prod + envio + publicidad + dev_cop:,}
          </span>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── CALCULAR ──────────────────────────────────────────────────
    if st.button("⚡ Calcular precios de venta", use_container_width=True, type="primary"):
        if prod_nombre.strip() == "":
            st.warning("Escribe el nombre del producto primero")
        else:
            # Calcular para 1, 2, 3 unidades con diferentes rentabilidades
            escenarios = [
                {"cant": 1, "rent": 30, "label": "1 Unidad",    "recomendado": False},
                {"cant": 2, "rent": 35, "label": "2 Unidades",  "recomendado": True},
                {"cant": 3, "rent": 40, "label": "3 Unidades",  "recomendado": False},
            ]
            resultados = []
            for e in escenarios:
                r = calcular(costo_prod, envio, publicidad, pct_dev, e["cant"], e["rent"])
                r.update(e)
                resultados.append(r)

            st.session_state.calc_result = {
                "nombre":    prod_nombre,
                "costo":     costo_prod,
                "envio":     envio,
                "publicidad":publicidad,
                "pct_dev":   pct_dev,
                "resultados":resultados,
                "fecha":     now.strftime("%d %b %Y %H:%M"),
            }

    # ── RESULTADO ─────────────────────────────────────────────────
    if st.session_state.calc_result:
        cr = st.session_state.calc_result

        st.markdown(f"""
        <div style="background:{MID}40;border:1px solid {GRN}50;border-radius:14px;
             padding:20px;margin-top:4px;">
          <div style="font-family:Syne,sans-serif;font-size:1rem;font-weight:700;color:{WHT};margin-bottom:16px;">
            💵 Precio de Venta Sugerido
            <span style="color:{PALE};font-size:.8rem;font-weight:400;margin-left:10px;">
              Precios calculados automáticamente para garantizar tu rentabilidad
            </span>
          </div>
        """, unsafe_allow_html=True)

        # Tabla de escenarios estilo la imagen
        hdr = f"""
        <table style="width:100%;border-collapse:collapse;">
          <tr style="border-bottom:1px solid {PRI}40;">
            <th style="text-align:left;padding:10px 8px;color:{PALE};font-size:.8rem;font-weight:600;">Cantidad</th>
            <th style="text-align:center;padding:10px 8px;color:{PALE};font-size:.8rem;font-weight:600;">Rentabilidad</th>
            <th style="text-align:right;padding:10px 8px;color:{PALE};font-size:.8rem;font-weight:600;">Precio de Venta</th>
            <th style="text-align:right;padding:10px 8px;color:{PALE};font-size:.8rem;font-weight:600;">Ganancia</th>
          </tr>
        """
        rows_html = ""
        for r in cr["resultados"]:
            rec_badge = f'<span style="background:{ACC}25;color:{ACC};border:1px solid {ACC}50;border-radius:20px;padding:2px 10px;font-size:.72rem;margin-left:8px;">⭐ Recomendado</span>' if r["recomendado"] else ""
            rows_html += f"""
          <tr style="border-bottom:1px solid {MID}80;">
            <td style="padding:14px 8px;color:{WHT};font-weight:500;">
              {r['label']}{rec_badge}
            </td>
            <td style="padding:14px 8px;text-align:center;color:{ACC};font-weight:700;font-size:1.05rem;">{r['rent']}%</td>
            <td style="padding:14px 8px;text-align:right;color:{WHT};font-weight:700;font-size:1.15rem;">${r['pv_unit']:,}</td>
            <td style="padding:14px 8px;text-align:right;">
              <div style="color:{GRN};font-weight:700;font-size:1.05rem;">${r['ganancia_total']:,}</div>
              <div style="color:{PALE};font-size:.78rem;">(${r['ganancia_unit']:,} por unidad)</div>
            </td>
          </tr>"""
        st.markdown(hdr + rows_html + "</table></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Desglose de costos por escenario recomendado
        rec = next(r for r in cr["resultados"] if r["recomendado"])
        st.markdown(f"""
        <div class="card">
          <div style="font-family:Syne,sans-serif;font-weight:700;color:{WHT};margin-bottom:14px;">
            📊 Desglose — Escenario Recomendado ({rec['label']} · {rec['rent']}% rentabilidad)
          </div>
          <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;text-align:center;">
            <div style="background:{MID}80;border-radius:10px;padding:12px;">
              <div style="color:{PALE};font-size:.72rem;text-transform:uppercase;margin-bottom:4px;">Costo Producto</div>
              <div style="color:{YEL};font-size:1.1rem;font-weight:700;">${cr['costo']:,}</div>
            </div>
            <div style="background:{MID}80;border-radius:10px;padding:12px;">
              <div style="color:{PALE};font-size:.72rem;text-transform:uppercase;margin-bottom:4px;">Envío + Publicidad</div>
              <div style="color:{YEL};font-size:1.1rem;font-weight:700;">${cr['envio']+cr['publicidad']:,}</div>
            </div>
            <div style="background:{MID}80;border-radius:10px;padding:12px;">
              <div style="color:{PALE};font-size:.72rem;text-transform:uppercase;margin-bottom:4px;">Costo Devolución</div>
              <div style="color:{YEL};font-size:1.1rem;font-weight:700;">${round(cr['envio']*cr['pct_dev']/100):,}</div>
            </div>
            <div style="background:{GRN}20;border:1px solid {GRN}40;border-radius:10px;padding:12px;">
              <div style="color:{GRN};font-size:.72rem;text-transform:uppercase;margin-bottom:4px;">Tu Ganancia neta</div>
              <div style="color:{GRN};font-size:1.1rem;font-weight:700;">${rec['ganancia_total']:,}</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

        # ── GUARDAR AL PORTFOLIO ───────────────────────────────────
        st.markdown(f'<div style="color:{PALE};font-size:.85rem;margin-bottom:8px;">¿Quieres vender este producto? Guárdalo en tu portfolio para hacer seguimiento de precios.</div>', unsafe_allow_html=True)

        col_g1, col_g2 = st.columns([3,1])
        with col_g1:
            pv_elegido = st.selectbox(
                "Precio de venta con el que vas a trabajar:",
                options=[f"${r['pv_unit']:,} COP ({r['rent']}% rent. · {r['label']})" for r in cr["resultados"]],
                key="pv_elegir"
            )
        with col_g2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("💾 Guardar en Portfolio", use_container_width=True):
                idx = ["${:,} COP ({}% rent. · {})".format(r["pv_unit"],r["rent"],r["label"]) for r in cr["resultados"]].index(pv_elegido)
                r_sel = cr["resultados"][idx]
                nombre_k = cr["nombre"].strip()
                entrada = {
                    "nombre":      nombre_k,
                    "costo":       cr["costo"],
                    "envio":       cr["envio"],
                    "publicidad":  cr["publicidad"],
                    "pct_dev":     cr["pct_dev"],
                    "pv_venta":    r_sel["pv_unit"],
                    "rent_obj":    r_sel["rent"],
                    "ganancia":    r_sel["ganancia_unit"],
                    "fecha_inicio":now.strftime("%d %b %Y"),
                    "historial":   [{
                        "fecha":     now.strftime("%d %b %Y"),
                        "pv":        r_sel["pv_unit"],
                        "costo":     cr["costo"],
                        "ganancia":  r_sel["ganancia_unit"],
                        "rent":      r_sel["rent"],
                        "evento":    "Precio inicial",
                    }],
                    "alertas":     [],
                    "notas":       "",
                    "estado":      "activo",
                }
                st.session_state.portfolio[nombre_k] = entrada
                st.success(f"✅ **{nombre_k}** guardado en tu portfolio · PV ${r_sel['pv_unit']:,} · {r_sel['rent']}% rentabilidad")
                st.balloons()

# ═══════════════════════════════════════════════════════════════
# TAB 2 — BUSCADOR DE MERCADO
# ═══════════════════════════════════════════════════════════════
with T2:
    st.markdown(f'<h3 style="color:{WHT};font-family:Syne,sans-serif;margin-bottom:4px;">🔍 Buscar en el Mercado</h3>', unsafe_allow_html=True)
    st.caption("Busca el producto, analiza su precio en el mercado internacional y decide si lo incluyes en tu portafolio")

    st.markdown("<br>", unsafe_allow_html=True)

    # Búsqueda
    sc1, sc2 = st.columns([4,1])
    with sc1:
        search_q = st.text_input(
            "Buscar producto:",
            placeholder="Ej: cerave, olaplex, niacinamide, retinol, mascara...",
            key="search_q"
        )
    with sc2:
        st.markdown("<br>", unsafe_allow_html=True)
        do_search = st.button("🔍 Buscar", use_container_width=True)

    if do_search and search_q.strip():
        with st.spinner(f"Buscando '{search_q}' en bases de datos de productos..."):
            st.session_state.search_results = buscar_makeup_api(search_q)

    if st.session_state.search_results:
        results = st.session_state.search_results
        st.caption(f"Se encontraron {len(results)} productos para '{search_q}'")
        st.markdown("<br>", unsafe_allow_html=True)

        for i, p in enumerate(results):
            pv_co = p["pv_co_est"]
            pv_display = fmt_cop(pv_co)
            rating_stars = "⭐" * int(p["rating"])

            with st.expander(f"**{p['nombre']}** — {p['marca']} · ${p['precio_usd']:.2f} USD → {pv_display} COP est.", expanded=(i==0)):
                ec1, ec2, ec3 = st.columns([2,2,2])

                with ec1:
                    st.markdown(f"""
                    <div style="background:{MID}60;border-radius:10px;padding:14px;">
                      <div style="color:{PALE};font-size:.72rem;text-transform:uppercase;margin-bottom:8px;">Datos del producto</div>
                      <div style="color:{WHT};font-weight:600;font-size:.95rem;margin-bottom:4px;">{p['nombre']}</div>
                      <div style="color:{PALE};font-size:.82rem;">Marca: <span style="color:{TEXT};">{p['marca']}</span></div>
                      <div style="color:{PALE};font-size:.82rem;">Tipo: <span style="color:{TEXT};">{p['tipo'].replace('_',' ').title()}</span></div>
                      <div style="color:{PALE};font-size:.82rem;">Colores/variantes: <span style="color:{TEXT};">{p['colores']}</span></div>
                      <div style="color:{PALE};font-size:.82rem;">Rating: <span style="color:{GOLD};">{p['rating']:.1f}/5</span></div>
                    </div>""", unsafe_allow_html=True)

                with ec2:
                    st.markdown(f"""
                    <div style="background:{MID}60;border-radius:10px;padding:14px;">
                      <div style="color:{PALE};font-size:.72rem;text-transform:uppercase;margin-bottom:8px;">Precios estimados Colombia</div>
                      <div style="color:{PALE};font-size:.8rem;">Precio proveedor (USD)</div>
                      <div style="color:{GOLD};font-weight:700;font-size:1.15rem;margin-bottom:8px;">${p['precio_usd']:.2f} USD</div>
                      <div style="color:{PALE};font-size:.8rem;">Tu costo aprox. COP (×TRM 4.200)</div>
                      <div style="color:{WHT};font-weight:600;font-size:1rem;margin-bottom:8px;">${round(p['precio_usd']*4200):,} COP</div>
                      <div style="color:{PALE};font-size:.8rem;">PV estimado mercado Colombia</div>
                      <div style="color:{ACC};font-weight:700;font-size:1.15rem;">{pv_display} COP</div>
                    </div>""", unsafe_allow_html=True)

                with ec3:
                    # Calcular rápido con parámetros base
                    costo_q = round(p["precio_usd"] * 4200)
                    r_quick = calcular(costo_q, 18000, 18000, 20.0, 1, 30)
                    viable  = pv_co >= r_quick["pv_unit"]
                    v_color = GRN if viable else RED
                    v_text  = "VIABLE ✅" if viable else "REVISAR ⚠️"

                    st.markdown(f"""
                    <div style="background:{MID}60;border-radius:10px;padding:14px;">
                      <div style="color:{PALE};font-size:.72rem;text-transform:uppercase;margin-bottom:8px;">Análisis rápido (30% rent.)</div>
                      <div style="color:{PALE};font-size:.8rem;">PV mínimo para 30%</div>
                      <div style="color:{WHT};font-weight:600;font-size:1rem;margin-bottom:6px;">${r_quick['pv_unit']:,} COP</div>
                      <div style="color:{PALE};font-size:.8rem;">PV mercado Colombia</div>
                      <div style="color:{ACC};font-weight:600;font-size:1rem;margin-bottom:10px;">{pv_display} COP</div>
                      <div style="background:{v_color}20;border:1px solid {v_color}50;border-radius:8px;padding:6px 10px;text-align:center;">
                        <span style="color:{v_color};font-weight:700;font-size:.9rem;">{v_text}</span>
                      </div>
                    </div>""", unsafe_allow_html=True)

                # Acciones
                ba1, ba2, ba3 = st.columns(3)
                with ba1:
                    if st.button(f"🧮 Calcular precio", key=f"calc_{i}"):
                        st.session_state["calc_nombre"] = p["nombre"]
                        # Pre-llenar cálculo
                        costo_pre = round(p["precio_usd"] * 4200)
                        esc = []
                        for cant, rent in [(1,30),(2,35),(3,40)]:
                            rv = calcular(costo_pre, 18000, 18000, 20.0, cant, rent)
                            rv.update({"cant":cant,"rent":rent,"label":f"{cant} Unidad{'es' if cant>1 else ''}","recomendado":(cant==2)})
                            esc.append(rv)
                        st.session_state.calc_result = {
                            "nombre":p["nombre"],"costo":costo_pre,
                            "envio":18000,"publicidad":18000,"pct_dev":20.0,
                            "resultados":esc,"fecha":now.strftime("%d %b %Y %H:%M"),
                        }
                        st.info(f"✅ Cálculo listo para **{p['nombre']}** — ve a la pestaña Calculadora")

                with ba2:
                    if p["url"]:
                        st.link_button("🔗 Ver producto", p["url"])
                with ba3:
                    if st.button(f"💾 Agregar al Portfolio", key=f"port_{i}"):
                        costo_p = round(p["precio_usd"] * 4200)
                        r_p = calcular(costo_p, 18000, 18000, 20.0, 2, 35)
                        nombre_k = p["nombre"].strip()
                        st.session_state.portfolio[nombre_k] = {
                            "nombre":p["nombre"],"costo":costo_p,
                            "envio":18000,"publicidad":18000,"pct_dev":20.0,
                            "pv_venta":r_p["pv_unit"],"rent_obj":35,
                            "ganancia":r_p["ganancia_unit"],
                            "fecha_inicio":now.strftime("%d %b %Y"),
                            "historial":[{"fecha":now.strftime("%d %b %Y"),
                                          "pv":r_p["pv_unit"],"costo":costo_p,
                                          "ganancia":r_p["ganancia_unit"],"rent":35,
                                          "evento":"Agregado desde búsqueda"}],
                            "alertas":[],"notas":"","estado":"activo",
                        }
                        st.success(f"✅ **{nombre_k}** agregado al portfolio")

    elif do_search:
        st.warning("No se encontraron resultados. Intenta con otro término (en inglés funciona mejor: 'niacinamide', 'retinol', 'foundation'...)")

    # Tips de búsqueda
    if not st.session_state.search_results:
        st.markdown(f"""
        <div class="card" style="margin-top:20px;">
          <div style="font-family:Syne,sans-serif;font-weight:700;color:{WHT};margin-bottom:12px;">💡 Tips de búsqueda</div>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;font-size:.85rem;">
            <div><span style="color:{ACC};font-weight:600;">Skincare:</span><br>
              <span style="color:{TEXT};">serum, retinol, niacinamide, moisturizer, sunscreen, toner</span></div>
            <div><span style="color:{ACC};font-weight:600;">Maquillaje:</span><br>
              <span style="color:{TEXT};">foundation, mascara, lip liner, blush, bronzer, primer</span></div>
            <div><span style="color:{ACC};font-weight:600;">Marcas:</span><br>
              <span style="color:{TEXT};">cerave, olaplex, fenty, charlotte tilbury, nars, benefit</span></div>
          </div>
        </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# TAB 3 — PORTFOLIO
# ═══════════════════════════════════════════════════════════════
with T3:
    st.markdown(f'<h3 style="color:{WHT};font-family:Syne,sans-serif;margin-bottom:4px;">📦 Mi Portfolio de Productos</h3>', unsafe_allow_html=True)
    st.caption("Seguimiento de precios, historial, alertas de oferta y análisis de tus productos activos")

    if len(st.session_state.portfolio) == 0:
        st.markdown(f"""
        <div class="card" style="text-align:center;padding:40px;">
          <div style="font-size:3rem;margin-bottom:12px;">📭</div>
          <div style="font-family:Syne,sans-serif;font-size:1.1rem;color:{WHT};margin-bottom:8px;">
            Tu portfolio está vacío</div>
          <div style="color:{PALE};font-size:.88rem;">
            Calcula el precio de un producto y guárdalo, o búscalo en el mercado y agrégalo.</div>
        </div>""", unsafe_allow_html=True)

    else:
        # ── KPIs PORTFOLIO ─────────────────────────────────────────
        port_list = list(st.session_state.portfolio.values())
        gan_total = sum(p["ganancia"] for p in port_list)
        costo_avg = sum(p["costo"] for p in port_list) / len(port_list)
        rent_avg  = sum(p["rent_obj"] for p in port_list) / len(port_list)

        k1,k2,k3,k4 = st.columns(4)
        with k1: st.metric("Productos activos", len(port_list))
        with k2: st.metric("Ganancia prom/unidad", fmt_cop(gan_total/len(port_list)))
        with k3: st.metric("Costo prom. producto", fmt_cop(costo_avg))
        with k4: st.metric("Rentabilidad prom.", f"{rent_avg:.0f}%")

        st.markdown("<br>", unsafe_allow_html=True)

        # ── ACTUALIZAR PRECIOS ─────────────────────────────────────
        with st.expander("⚙️ Actualizar precio de un producto (nueva entrada de historial)", expanded=False):
            st.caption("Cuando cambies el costo o el precio de venta de un producto, regístralo aquí para llevar el seguimiento")
            upd_prod = st.selectbox("Producto:", list(st.session_state.portfolio.keys()), key="upd_prod")
            if upd_prod:
                p_upd = st.session_state.portfolio[upd_prod]
                uc1, uc2, uc3, uc4 = st.columns(4)
                with uc1: nuevo_costo = st.number_input("Nuevo costo COP", value=p_upd["costo"], step=1000, key="u_costo")
                with uc2: nuevo_pv    = st.number_input("Nuevo PV venta COP", value=p_upd["pv_venta"], step=1000, key="u_pv")
                with uc3: evento_txt  = st.text_input("Motivo del cambio", placeholder="Ej: bajó precio proveedor, oferta especial...", key="u_evento")
                with uc4:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("💾 Registrar cambio", use_container_width=True, key="u_save"):
                        nuevo_dev   = round(p_upd["envio"] * p_upd["pct_dev"] / 100)
                        costo_total = nuevo_costo + p_upd["envio"] + p_upd["publicidad"] + nuevo_dev
                        nueva_gan   = nuevo_pv - costo_total
                        nueva_rent  = round(nueva_gan / nuevo_pv * 100, 1) if nuevo_pv > 0 else 0
                        entrada_hist = {
                            "fecha":    now.strftime("%d %b %Y"),
                            "pv":       nuevo_pv,
                            "costo":    nuevo_costo,
                            "ganancia": round(nueva_gan),
                            "rent":     nueva_rent,
                            "evento":   evento_txt or "Actualización manual",
                        }
                        st.session_state.portfolio[upd_prod]["historial"].append(entrada_hist)
                        st.session_state.portfolio[upd_prod]["costo"]     = nuevo_costo
                        st.session_state.portfolio[upd_prod]["pv_venta"]  = nuevo_pv
                        st.session_state.portfolio[upd_prod]["ganancia"]  = round(nueva_gan)
                        st.success(f"✅ Cambio registrado — {now.strftime('%d %b %Y')}")

        st.markdown("<br>", unsafe_allow_html=True)

        # ── TARJETAS DE PRODUCTOS ──────────────────────────────────
        for nombre_k, prod in st.session_state.portfolio.items():
            hist = prod["historial"]
            pv_actual  = prod["pv_venta"]
            pv_inicial = hist[0]["pv"] if hist else pv_actual
            gan_actual  = prod["ganancia"]
            rent_actual = prod["rent_obj"]

            # Detectar cambios
            pv_cambio = pv_actual - pv_inicial
            pv_pct    = (pv_cambio / pv_inicial * 100) if pv_inicial > 0 else 0
            cambio_color = GRN if pv_cambio > 0 else RED if pv_cambio < 0 else PALE
            cambio_icon  = "▲" if pv_cambio > 0 else "▼" if pv_cambio < 0 else "—"

            # Alertas de oferta
            pv_oferta_30 = round(pv_actual * 0.70 / 100) * 100  # -30%
            pv_oferta_20 = round(pv_actual * 0.80 / 100) * 100  # -20%

            with st.expander(
                f"**{prod['nombre']}** · PV ${pv_actual:,} COP · {rent_actual}% rent. · {len(hist)} entradas",
                expanded=True
            ):
                pc1, pc2, pc3 = st.columns([2,2,2])

                with pc1:
                    st.markdown(f"""
                    <div style="background:{MID}60;border-radius:12px;padding:14px;">
                      <div style="color:{PALE};font-size:.72rem;text-transform:uppercase;margin-bottom:10px;">Estado Actual</div>
                      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
                        <div><div style="color:{PALE};font-size:.72rem;">Costo producto</div>
                             <div style="color:{WHT};font-weight:600;">${prod['costo']:,}</div></div>
                        <div><div style="color:{PALE};font-size:.72rem;">Envío</div>
                             <div style="color:{WHT};font-weight:600;">${prod['envio']:,}</div></div>
                        <div><div style="color:{PALE};font-size:.72rem;">Publicidad</div>
                             <div style="color:{WHT};font-weight:600;">${prod['publicidad']:,}</div></div>
                        <div><div style="color:{PALE};font-size:.72rem;">% Devoluciones</div>
                             <div style="color:{WHT};font-weight:600;">{prod['pct_dev']:.0f}%</div></div>
                      </div>
                      <div style="margin-top:10px;padding-top:10px;border-top:1px solid {PRI}30;">
                        <div style="color:{PALE};font-size:.72rem;">PV de venta actual</div>
                        <div style="color:{ACC};font-weight:700;font-size:1.3rem;">${pv_actual:,}</div>
                      </div>
                      <div style="margin-top:6px;">
                        <div style="color:{PALE};font-size:.72rem;">Ganancia por unidad</div>
                        <div style="color:{GRN};font-weight:700;font-size:1.1rem;">${gan_actual:,}</div>
                      </div>
                    </div>""", unsafe_allow_html=True)

                with pc2:
                    st.markdown(f"""
                    <div style="background:{MID}60;border-radius:12px;padding:14px;">
                      <div style="color:{PALE};font-size:.72rem;text-transform:uppercase;margin-bottom:10px;">Variación de Precio</div>
                      <div style="color:{PALE};font-size:.8rem;">Precio inicial: <span style="color:{TEXT};">${pv_inicial:,}</span></div>
                      <div style="color:{PALE};font-size:.8rem;margin-top:4px;">Precio actual: <span style="color:{ACC};font-weight:700;">${pv_actual:,}</span></div>
                      <div style="margin-top:10px;background:{cambio_color}20;border:1px solid {cambio_color}40;
                           border-radius:8px;padding:8px 12px;text-align:center;">
                        <span style="color:{cambio_color};font-weight:700;font-size:1.1rem;">
                          {cambio_icon} ${abs(pv_cambio):,} ({pv_pct:+.1f}%)</span>
                        <div style="color:{PALE};font-size:.72rem;margin-top:2px;">vs. precio inicial</div>
                      </div>
                      <div style="margin-top:12px;padding-top:10px;border-top:1px solid {PRI}30;">
                        <div style="color:{PALE};font-size:.72rem;text-transform:uppercase;margin-bottom:6px;">Sugerencias de Oferta</div>
                        <div style="display:flex;gap:8px;">
                          <div style="background:{YEL}20;border:1px solid {YEL}40;border-radius:8px;
                               padding:6px 8px;text-align:center;flex:1;">
                            <div style="color:{YEL};font-size:.7rem;">Oferta -20%</div>
                            <div style="color:{YEL};font-weight:700;">${pv_oferta_20:,}</div>
                          </div>
                          <div style="background:{RED}20;border:1px solid {RED}40;border-radius:8px;
                               padding:6px 8px;text-align:center;flex:1;">
                            <div style="color:{RED};font-size:.7rem;">Oferta -30%</div>
                            <div style="color:{RED};font-weight:700;">${pv_oferta_30:,}</div>
                          </div>
                        </div>
                        <div style="color:{PALE};font-size:.7rem;margin-top:6px;">
                          Con oferta -20% aun ganas: ${round(pv_oferta_20 - (prod['costo']+prod['envio']+prod['publicidad'])):,}/unidad</div>
                      </div>
                    </div>""", unsafe_allow_html=True)

                with pc3:
                    st.markdown(f"""
                    <div style="background:{MID}60;border-radius:12px;padding:14px;">
                      <div style="color:{PALE};font-size:.72rem;text-transform:uppercase;margin-bottom:10px;">Cuando Hacer Oferta</div>
                      <div style="font-size:.82rem;color:{TEXT};line-height:1.6;">
                        <div style="margin-bottom:8px;">
                          <span style="color:{GRN};font-weight:600;">✅ Buen momento:</span><br>
                          Cuando tu costo bajó más del 10% y tienes stock. Ofrece -15% y aumenta volumen.
                        </div>
                        <div style="margin-bottom:8px;">
                          <span style="color:{YEL};font-weight:600;">🕐 Temporadas:</span><br>
                          Nov-Dic (Navidad), Feb (San Valentín), May (Dia Madre), Sep (regreso clases.
                        </div>
                        <div>
                          <span style="color:{ACC};font-weight:600;">📊 Señal de precio:</span><br>
                          Si llevas 2+ meses sin ventas o competencia baja precio → hacer oferta temporal.
                        </div>
                      </div>
                    </div>""", unsafe_allow_html=True)

                # Historial grafico
                if len(hist) >= 2:
                    fechas_h  = [h["fecha"] for h in hist]
                    pvs_h     = [h["pv"] for h in hist]
                    gans_h    = [h["ganancia"] for h in hist]
                    eventos_h = [h.get("evento","") for h in hist]

                    fig = make_subplots(specs=[[{"secondary_y": True}]])
                    fig.add_trace(go.Scatter(
                        x=fechas_h, y=pvs_h, name="PV Venta",
                        line_color=ACC, line_width=2, mode="lines+markers+text",
                        text=[f"${v:,}" for v in pvs_h], textposition="top center",
                        textfont=dict(color=WHT, size=10),
                        marker=dict(size=8),
                        hovertext=eventos_h,
                    ), secondary_y=False)
                    fig.add_trace(go.Bar(
                        x=fechas_h, y=gans_h, name="Ganancia/unidad",
                        marker_color=GRN, opacity=0.65,
                    ), secondary_y=True)
                    fig.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,33,55,0.5)",
                        font_color=TEXT, height=260, margin=dict(l=20,r=20,t=30,b=40),
                        legend=dict(orientation="h", y=1.0, bgcolor="rgba(0,0,0,0)"),
                        hovermode="x unified",
                        title_text=f"Historial de precios — {prod['nombre'][:40]}",
                        title_font_color=WHT, title_font_size=13,
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # Tabla historial
                    df_hist = pd.DataFrame(hist)
                    df_hist_display = df_hist[["fecha","pv","costo","ganancia","rent","evento"]].copy()
                    df_hist_display.columns = ["Fecha","PV Venta","Costo","Ganancia","Rent%","Motivo"]
                    for col in ["PV Venta","Costo","Ganancia"]:
                        df_hist_display[col] = df_hist_display[col].apply(lambda x: f"${x:,}")
                    df_hist_display["Rent%"] = df_hist_display["Rent%"].apply(lambda x: f"{x}%")
                    st.dataframe(df_hist_display, use_container_width=True, hide_index=True)

                elif len(hist) == 1:
                    st.info("Solo hay un registro. Cuando actualices el precio verás el historial y la gráfica aquí.")

                # Notas y eliminar
                nn1, nn2 = st.columns([4,1])
                with nn1:
                    nota = st.text_input(
                        "📝 Nota rápida:", value=prod.get("notas",""),
                        placeholder="Ej: proveedor da descuento en 5 unidades...",
                        key=f"nota_{nombre_k}"
                    )
                    if nota != prod.get("notas",""):
                        st.session_state.portfolio[nombre_k]["notas"] = nota
                with nn2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🗑️ Eliminar", key=f"del_{nombre_k}", type="secondary"):
                        del st.session_state.portfolio[nombre_k]
                        st.rerun()

        # ── RESUMEN PORTFOLIO ──────────────────────────────────────
        if len(st.session_state.portfolio) >= 2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f'<h4 style="color:{ACC};font-family:Syne,sans-serif;margin-bottom:14px;">📊 Comparativa del Portfolio</h4>', unsafe_allow_html=True)

            port_df = pd.DataFrame([{
                "Producto": p["nombre"][:30],
                "Costo":    p["costo"],
                "PV Venta": p["pv_venta"],
                "Ganancia": p["ganancia"],
                "Rent%":    p["rent_obj"],
            } for p in st.session_state.portfolio.values()])

            fig = go.Figure()
            fig.add_trace(go.Bar(
                name="Costo", x=port_df["Producto"], y=port_df["Costo"],
                marker_color=RED, opacity=0.8))
            fig.add_trace(go.Bar(
                name="Ganancia", x=port_df["Producto"], y=port_df["Ganancia"],
                marker_color=GRN, opacity=0.8))
            fig.add_trace(go.Scatter(
                name="PV Venta", x=port_df["Producto"], y=port_df["PV Venta"],
                mode="markers+lines", marker_color=ACC, marker_size=10,
                line=dict(dash="dash", width=1.5), yaxis="y2"))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,33,55,0.5)",
                font_color=TEXT, height=340, barmode="group",
                margin=dict(l=10,r=10,t=40,b=60),
                legend=dict(orientation="h", y=1.05, bgcolor="rgba(0,0,0,0)"),
                yaxis=dict(title="COP", gridcolor=PRI+"20"),
                yaxis2=dict(title="PV Venta", overlaying="y", side="right", gridcolor=PRI+"10"),
                title_text="Costo vs Ganancia vs PV por Producto",
                title_font_color=WHT,
            )
            st.plotly_chart(fig, use_container_width=True)

# ── FOOTER ────────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(f"""
<div style="text-align:center;padding:12px 0;color:{PALE};font-size:.72rem;">
  <span style="font-family:Syne,sans-serif;color:{ACC};font-weight:700;">ROME Market</span>
  &nbsp;·&nbsp; Calculadora · Mercado · Portfolio
  &nbsp;·&nbsp; {now.strftime("%B %Y")}
  &nbsp;·&nbsp; Los datos del portfolio se guardan durante la sesión
</div>""", unsafe_allow_html=True)
