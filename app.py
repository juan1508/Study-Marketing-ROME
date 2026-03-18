"""
╔══════════════════════════════════════════════════════════════════╗
║          ESTUDIO DE MERCADO ROME - APP PRINCIPAL                 ║
║          Análisis de mercado global de belleza y cuidado personal║
╚══════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sys
import os

# Garantiza que el root del proyecto esté en sys.path (necesario en Streamlit Cloud)
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import importlib.util

def _load_module(name, filepath):
    spec = importlib.util.spec_from_file_location(name, filepath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_db = _load_module("products_db", os.path.join(ROOT, "data", "products_db.py"))

get_dataframe          = _db.get_dataframe
get_top10_by_category  = _db.get_top10_by_category
get_categories         = _db.get_categories
generate_price_history = _db.generate_price_history
generate_rotation_history = _db.generate_rotation_history
PRODUCTS               = _db.PRODUCTS

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Estudio de Mercado ROME",
    page_icon="🔵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# PALETA DE COLORES AZULES
# ─────────────────────────────────────────────

COLORS = {
    "navy":     "#0A1628",
    "dark":     "#0D2137",
    "mid":      "#1A3A5C",
    "primary":  "#1E5FAD",
    "bright":   "#2E86DE",
    "accent":   "#54A0FF",
    "light":    "#74B9FF",
    "pale":     "#A8D8F0",
    "white":    "#EEF6FF",
    "gold":     "#FFC300",
    "success":  "#00B894",
    "warning":  "#FDCB6E",
    "danger":   "#E17055",
    "text":     "#DDE8F5",
}

BLUE_SCALE = [
    COLORS["navy"], COLORS["dark"], COLORS["mid"],
    COLORS["primary"], COLORS["bright"], COLORS["accent"],
    COLORS["light"], COLORS["pale"]
]

# ─────────────────────────────────────────────
# CSS GLOBAL - ESTÉTICA PREMIUM AZUL
# ─────────────────────────────────────────────

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

    /* FONDO PRINCIPAL */
    .stApp {{
        background: linear-gradient(135deg, {COLORS['navy']} 0%, {COLORS['dark']} 50%, #0B1E35 100%);
        min-height: 100vh;
    }}

    /* TIPOGRAFÍA */
    html, body, [class*="css"] {{
        font-family: 'DM Sans', sans-serif;
        color: {COLORS['text']};
    }}

    h1, h2, h3 {{
        font-family: 'Syne', sans-serif;
        font-weight: 800;
    }}

    /* SIDEBAR */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {COLORS['dark']} 0%, {COLORS['mid']} 100%);
        border-right: 1px solid {COLORS['primary']}40;
    }}

    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stRadio label,
    section[data-testid="stSidebar"] p {{
        color: {COLORS['text']} !important;
    }}

    /* MÉTRICAS */
    div[data-testid="metric-container"] {{
        background: linear-gradient(135deg, {COLORS['mid']}CC, {COLORS['primary']}33) !important;
        border: 1px solid {COLORS['accent']}40 !important;
        border-radius: 16px !important;
        padding: 20px !important;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }}

    div[data-testid="metric-container"]:hover {{
        border-color: {COLORS['accent']} !important;
        box-shadow: 0 8px 32px {COLORS['accent']}30;
        transform: translateY(-2px);
    }}

    div[data-testid="metric-container"] label {{
        color: {COLORS['pale']} !important;
        font-family: 'DM Sans', sans-serif;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    div[data-testid="metric-container"] [data-testid="stMetricValue"] {{
        color: {COLORS['white']} !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 800 !important;
        font-size: 1.8rem !important;
    }}

    div[data-testid="stMetricDelta"] {{
        color: {COLORS['success']} !important;
    }}

    /* DATAFRAME */
    .stDataFrame {{
        background: {COLORS['dark']}CC !important;
        border-radius: 12px;
        border: 1px solid {COLORS['primary']}30;
    }}

    /* SELECTBOX */
    .stSelectbox div[data-baseweb="select"] > div {{
        background: {COLORS['mid']} !important;
        border-color: {COLORS['primary']}60 !important;
        color: {COLORS['text']} !important;
        border-radius: 10px !important;
    }}

    /* BOTONES */
    .stButton > button {{
        background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['bright']}) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: 0.05em;
        transition: all 0.3s ease !important;
    }}

    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px {COLORS['bright']}50 !important;
    }}

    /* TABS */
    .stTabs [data-baseweb="tab-list"] {{
        background: {COLORS['mid']}80 !important;
        border-radius: 12px !important;
        padding: 4px !important;
    }}

    .stTabs [data-baseweb="tab"] {{
        background: transparent !important;
        color: {COLORS['pale']} !important;
        border-radius: 10px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
    }}

    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['bright']}) !important;
        color: white !important;
        font-weight: 600 !important;
    }}

    /* DIVIDER */
    hr {{
        border-color: {COLORS['primary']}30 !important;
    }}

    /* EXPANDER */
    .streamlit-expanderHeader {{
        background: {COLORS['mid']}80 !important;
        border: 1px solid {COLORS['primary']}30 !important;
        border-radius: 10px !important;
        color: {COLORS['text']} !important;
    }}

    /* RADIO */
    .stRadio label {{
        color: {COLORS['text']} !important;
    }}

    /* BADGES */
    .badge-alta {{ background: {COLORS['success']}30; color: {COLORS['success']}; border: 1px solid {COLORS['success']}60; border-radius: 20px; padding: 2px 10px; font-size: 0.75rem; font-weight: 600; }}
    .badge-media {{ background: {COLORS['warning']}30; color: {COLORS['warning']}; border: 1px solid {COLORS['warning']}60; border-radius: 20px; padding: 2px 10px; font-size: 0.75rem; font-weight: 600; }}
    .badge-baja {{ background: {COLORS['danger']}30; color: {COLORS['danger']}; border: 1px solid {COLORS['danger']}60; border-radius: 20px; padding: 2px 10px; font-size: 0.75rem; font-weight: 600; }}

    /* HIDE STREAMLIT BRANDING */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}

    /* INPUT */
    .stTextInput input {{
        background: {COLORS['mid']} !important;
        border-color: {COLORS['primary']}60 !important;
        color: {COLORS['text']} !important;
        border-radius: 10px !important;
    }}

    /* TOOLTIPS */
    .tooltip-card {{
        background: linear-gradient(135deg, {COLORS['mid']}, {COLORS['dark']});
        border: 1px solid {COLORS['accent']}40;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }}

    /* SLIDER */
    .stSlider [data-baseweb="slider"] {{
        color: {COLORS['accent']} !important;
    }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def plotly_theme():
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(13,33,55,0.6)",
        font=dict(family="DM Sans", color=COLORS["text"], size=12),
        title_font=dict(family="Syne", size=16, color=COLORS["white"]),
        xaxis=dict(gridcolor=COLORS["primary"] + "25", linecolor=COLORS["mid"]),
        yaxis=dict(gridcolor=COLORS["primary"] + "25", linecolor=COLORS["mid"]),
    )


def format_currency(val):
    if val >= 1_000_000:
        return f"${val/1_000_000:.1f}M"
    elif val >= 1_000:
        return f"${val/1_000:.0f}K"
    return f"${val:.2f}"


def rotation_badge(rot):
    mapping = {
        "muy_alta": ("🔵 Muy Alta", "alta"),
        "alta": ("🟢 Alta", "alta"),
        "media_alta": ("🟡 Media-Alta", "media"),
        "media": ("🟡 Media", "media"),
        "baja": ("🔴 Baja", "baja"),
    }
    label, cls = mapping.get(rot, ("⚪ N/A", "media"))
    return f'<span class="badge-{cls}">{label}</span>'


def trend_icon(t):
    icons = {
        "muy_creciente": "🚀 Muy Creciente",
        "creciente": "📈 Creciente",
        "estable": "➡️ Estable",
        "decreciente": "📉 Decreciente"
    }
    return icons.get(t, t)


# ─────────────────────────────────────────────
# HEADER PRINCIPAL
# ─────────────────────────────────────────────

col_logo, col_title, col_update = st.columns([1, 5, 2])

with col_logo:
    st.markdown(f"""
    <div style="text-align:center; padding: 10px 0;">
        <div style="width:64px; height:64px; background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['bright']});
             border-radius:50%; display:inline-flex; align-items:center; justify-content:center;
             box-shadow: 0 8px 32px {COLORS['accent']}60; font-size: 28px;">
            🔬
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_title:
    st.markdown(f"""
    <div style="padding: 8px 0;">
        <h1 style="margin:0; font-size: 2.2rem; background: linear-gradient(90deg, {COLORS['white']}, {COLORS['accent']});
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.02em;">
            ESTUDIO DE MERCADO ROME
        </h1>
        <p style="margin:0; color:{COLORS['pale']}; font-size: 0.95rem; letter-spacing: 0.05em;">
            Inteligencia Comercial Global · Belleza & Cuidado Personal · Mercados Internacionales
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_update:
    now = datetime.now()
    next_update = datetime(now.year, now.month + 1 if now.month < 12 else 1, 1)
    days_left = (next_update - now).days
    st.markdown(f"""
    <div style="text-align:right; padding:10px 0;">
        <div style="background: {COLORS['mid']}80; border: 1px solid {COLORS['accent']}40;
             border-radius: 10px; padding: 10px 14px; display: inline-block;">
            <div style="color:{COLORS['pale']}; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.08em;">
                📅 Última actualización
            </div>
            <div style="color:{COLORS['white']}; font-weight:700; font-size:1rem; font-family:'Syne',sans-serif;">
                {now.strftime("%B %Y")}
            </div>
            <div style="color:{COLORS['accent']}; font-size:0.75rem;">
                🔄 Próxima en {days_left} días
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='margin: 8px 0 20px 0;'>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR - FILTROS
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding: 16px 0 8px;">
        <div style="font-family:'Syne',sans-serif; font-size:1.2rem; font-weight:800;
             color:{COLORS['white']}; letter-spacing: 0.05em;">
            🎛️ FILTROS
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Categoría
    categorias = get_categories()
    cat_sel = st.selectbox("📂 Categoría", categorias, index=0)

    # Target
    target_sel = st.selectbox("👤 Target", ["Todos", "Femenino", "Masculino", "Mixto"], index=0)

    # Rango precio
    st.markdown(f"<p style='color:{COLORS['pale']}; font-size:0.85rem; margin-bottom:4px;'>💰 Rango de precio (USD)</p>", unsafe_allow_html=True)
    precio_range = st.slider("", 0, 250, (0, 250), label_visibility="collapsed")

    # Tendencia
    tend_sel = st.multiselect(
        "📈 Tendencia",
        ["muy_creciente", "creciente", "estable", "decreciente"],
        default=["muy_creciente", "creciente", "estable", "decreciente"]
    )

    # Rotación
    rot_sel = st.multiselect(
        "🔄 Rotación",
        ["muy_alta", "alta", "media_alta", "media", "baja"],
        default=["muy_alta", "alta", "media_alta", "media", "baja"]
    )

    # Rating mínimo
    rating_min = st.slider("⭐ Rating mínimo", 1.0, 5.0, 4.0, 0.1)

    st.markdown("---")

    # Ordenar por
    sort_by = st.radio(
        "📊 Ordenar por",
        ["unidades_mes", "volumen_mensual_usd", "score_oportunidad", "rating"],
        format_func=lambda x: {
            "unidades_mes": "🔢 Unidades/mes",
            "volumen_mensual_usd": "💵 Volumen USD",
            "score_oportunidad": "🎯 Score Oportunidad",
            "rating": "⭐ Rating"
        }[x]
    )

    st.markdown("---")

    # Info sistema
    df_all = get_dataframe()
    st.markdown(f"""
    <div style="text-align:center;">
        <div style="color:{COLORS['pale']}; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px;">
            Base de datos
        </div>
        <div style="color:{COLORS['accent']}; font-size:1.8rem; font-family:'Syne',sans-serif; font-weight:800;">
            {len(df_all)}
        </div>
        <div style="color:{COLORS['pale']}; font-size:0.8rem;">productos indexados</div>
        <div style="color:{COLORS['pale']}; font-size:0.75rem; margin-top:4px;">
            {len(df_all['categoria'].unique())} categorías · 6 plataformas
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# FILTRAR DATOS
# ─────────────────────────────────────────────

df = get_dataframe()

if cat_sel != "Todas":
    df = df[df["categoria"] == cat_sel]
if target_sel != "Todos":
    df = df[df["target"] == target_sel]

df = df[
    (df["precio_usd"] >= precio_range[0]) &
    (df["precio_usd"] <= precio_range[1]) &
    (df["tendencia"].isin(tend_sel)) &
    (df["rotacion"].isin(rot_sel)) &
    (df["rating"] >= rating_min)
]

df_sorted = df.sort_values(sort_by, ascending=False)


# ─────────────────────────────────────────────
# KPIs PRINCIPALES
# ─────────────────────────────────────────────

st.markdown(f"<h3 style='color:{COLORS['accent']}; font-family:Syne,sans-serif; font-size:1.1rem; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:12px;'>📊 Indicadores Clave del Mercado</h3>", unsafe_allow_html=True)

k1, k2, k3, k4, k5, k6 = st.columns(6)

total_vol = df["volumen_mensual_usd"].sum()
total_units = df["unidades_mes"].sum()
avg_price = df["precio_usd"].mean()
avg_rating = df["rating"].mean()
avg_margin = df["margen_oportunidad"].mean()
top_score = df["score_oportunidad"].max() if len(df) > 0 else 0

with k1:
    st.metric("📦 Productos", f"{len(df)}", delta=f"de {len(get_dataframe())} total")
with k2:
    st.metric("💰 Vol. Mensual", format_currency(total_vol), delta="mercado global")
with k3:
    st.metric("🔢 Unidades/mes", f"{total_units:,.0f}", delta="proyección")
with k4:
    st.metric("💵 Precio Prom.", f"${avg_price:.0f}", delta=f"USD")
with k5:
    st.metric("⭐ Rating Prom.", f"{avg_rating:.1f}/5", delta="calificación")
with k6:
    st.metric("📈 Margen Prom.", f"{avg_margin:.1f}%", delta="vs mercado")

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# TABS PRINCIPALES
# ─────────────────────────────────────────────

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏆 Top 10 por Categoría",
    "📈 Análisis de Tendencias",
    "💰 Precios & Rotación",
    "🔍 Explorador de Productos",
    "📊 Análisis Comparativo"
])


# ══════════════════════════════════════════════
# TAB 1: TOP 10
# ══════════════════════════════════════════════

with tab1:
    st.markdown(f"<h3 style='color:{COLORS['white']}; font-family:Syne,sans-serif; margin-bottom:20px;'>🏆 Top 10 Productos — Ordenado por {sort_by.replace('_', ' ').title()}</h3>", unsafe_allow_html=True)

    top10 = df_sorted.head(10).reset_index(drop=True)

    if len(top10) == 0:
        st.warning("⚠️ No hay productos con los filtros seleccionados. Ajusta los filtros en el panel lateral.")
    else:
        # Gráfico de barras horizontales
        fig_top = go.Figure()
        fig_top.add_trace(go.Bar(
            y=top10["nombre"].apply(lambda x: x[:45] + "..." if len(x) > 45 else x),
            x=top10[sort_by],
            orientation="h",
            marker=dict(
                color=top10[sort_by],
                colorscale=[[0, COLORS["mid"]], [0.5, COLORS["primary"]], [1, COLORS["accent"]]],
                showscale=False,
                line=dict(width=0)
            ),
            text=top10[sort_by].apply(lambda x: format_currency(x) if sort_by in ["volumen_mensual_usd"] else f"{x:,.0f}"),
            textposition="outside",
            textfont=dict(color=COLORS["white"], size=11),
            hovertemplate="<b>%{y}</b><br>Valor: %{x:,.0f}<extra></extra>"
        ))

        fig_top.update_layout(
            **plotly_theme(),
            height=420,
            margin=dict(l=10, r=80, t=20, b=10),
            yaxis=dict(categoryorder="total ascending", tickfont=dict(size=11)),
            xaxis_title=sort_by.replace("_", " ").title(),
            showlegend=False
        )

        st.plotly_chart(fig_top, use_container_width=True)

        # Tabla detallada
        st.markdown(f"<h4 style='color:{COLORS['accent']}; font-family:Syne,sans-serif; margin: 20px 0 10px;'>📋 Detalle del Top 10</h4>", unsafe_allow_html=True)

        for i, row in top10.iterrows():
            rank = i + 1
            color_rank = COLORS["gold"] if rank == 1 else COLORS["accent"] if rank <= 3 else COLORS["pale"]
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"

            with st.expander(f"{medal} {row['nombre']} — {row['marca']} · ${row['precio_usd']} USD", expanded=(rank <= 3)):
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.metric("💰 Precio", f"${row['precio_usd']:.2f}")
                    st.metric("📊 Precio Mercado", f"${row['precio_promedio_mercado']:.2f}")
                with c2:
                    st.metric("🔢 Unid/mes", f"{row['unidades_mes']:,}")
                    st.metric("💵 Vol. Mensual", format_currency(row["volumen_mensual_usd"]))
                with c3:
                    st.metric("⭐ Rating", f"{row['rating']}/5.0")
                    st.metric("💬 Reviews", f"{row['reviews']:,}")
                with c4:
                    st.metric("📈 Margen", f"{row['margen_oportunidad']}%")
                    st.metric("🎯 Score", f"{row['score_oportunidad']:.0f}")

                st.markdown(f"""
                <div class="tooltip-card">
                    <table style="width:100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 4px 12px; color:{COLORS['pale']}; font-size:0.85rem;">🌍 Origen</td>
                            <td style="padding: 4px 12px; color:{COLORS['white']}; font-weight:500;">{row['origen']}</td>
                            <td style="padding: 4px 12px; color:{COLORS['pale']}; font-size:0.85rem;">📂 Categoría</td>
                            <td style="padding: 4px 12px; color:{COLORS['white']}; font-weight:500;">{row['categoria']} › {row['subcategoria']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 4px 12px; color:{COLORS['pale']}; font-size:0.85rem;">👤 Target</td>
                            <td style="padding: 4px 12px; color:{COLORS['white']}; font-weight:500;">{row['target']}</td>
                            <td style="padding: 4px 12px; color:{COLORS['pale']}; font-size:0.85rem;">🏪 Plataformas</td>
                            <td style="padding: 4px 12px; color:{COLORS['white']}; font-weight:500;">{', '.join(row['plataformas'])}</td>
                        </tr>
                        <tr>
                            <td style="padding: 4px 12px; color:{COLORS['pale']}; font-size:0.85rem;">📈 Tendencia</td>
                            <td style="padding: 4px 12px;">{trend_icon(row['tendencia'])}</td>
                            <td style="padding: 4px 12px; color:{COLORS['pale']}; font-size:0.85rem;">🔄 Rotación</td>
                            <td style="padding: 4px 12px;">{rotation_badge(row['rotacion'])}</td>
                        </tr>
                    </table>
                    <div style="margin-top:10px; padding:8px 0; border-top: 1px solid {COLORS['primary']}30;">
                        <span style="color:{COLORS['pale']}; font-size:0.8rem;">🎯 Problema que ataca: </span>
                        <span style="color:{COLORS['accent']}; font-size:0.85rem; font-weight:500;">{row['problema_ataca']}</span>
                    </div>
                    <div style="margin-top:6px;">
                        <span style="color:{COLORS['pale']}; font-size:0.8rem;">📝 Descripción: </span>
                        <span style="color:{COLORS['text']}; font-size:0.85rem;">{row['descripcion']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# TAB 2: TENDENCIAS
# ══════════════════════════════════════════════

with tab2:
    st.markdown(f"<h3 style='color:{COLORS['white']}; font-family:Syne,sans-serif; margin-bottom:20px;'>📈 Análisis de Tendencias de Mercado</h3>", unsafe_allow_html=True)

    col_t1, col_t2 = st.columns(2)

    with col_t1:
        # Distribución por tendencia
        df_all = get_dataframe()
        tend_count = df_all["tendencia"].value_counts().reset_index()
        tend_count.columns = ["tendencia", "count"]
        tend_labels = {
            "muy_creciente": "🚀 Muy Creciente",
            "creciente": "📈 Creciente",
            "estable": "➡️ Estable",
            "decreciente": "📉 Decreciente"
        }
        tend_count["label"] = tend_count["tendencia"].map(tend_labels)

        fig_tend = go.Figure(go.Pie(
            labels=tend_count["label"],
            values=tend_count["count"],
            hole=0.6,
            marker=dict(
                colors=[COLORS["accent"], COLORS["bright"], COLORS["primary"], COLORS["danger"]],
                line=dict(color=COLORS["navy"], width=2)
            ),
            textinfo="label+percent",
            textfont=dict(size=11, color=COLORS["white"])
        ))

        fig_tend.update_layout(
            **plotly_theme(),
            title="Distribución por Tendencia",
            height=320,
            margin=dict(l=20, r=20, t=50, b=20),
            showlegend=False
        )
        st.plotly_chart(fig_tend, use_container_width=True)

    with col_t2:
        # Volumen por categoría
        vol_cat = df_all.groupby("categoria")["volumen_mensual_usd"].sum().sort_values(ascending=True)
        fig_vol = go.Figure(go.Bar(
            y=vol_cat.index,
            x=vol_cat.values,
            orientation="h",
            marker=dict(
                color=vol_cat.values,
                colorscale=[[0, COLORS["mid"]], [1, COLORS["accent"]]],
                showscale=False
            ),
            text=[format_currency(v) for v in vol_cat.values],
            textposition="outside",
            textfont=dict(color=COLORS["white"], size=10)
        ))
        fig_vol.update_layout(
            **plotly_theme(),
            title="Volumen Mensual por Categoría (USD)",
            height=320,
            margin=dict(l=10, r=80, t=50, b=10),
            showlegend=False
        )
        st.plotly_chart(fig_vol, use_container_width=True)

    # Simulación: precio vs rotación
    st.markdown(f"<h4 style='color:{COLORS['accent']}; font-family:Syne,sans-serif; margin: 20px 0 10px;'>🔄 Impacto del Precio en la Rotación (Simulación Mensual)</h4>", unsafe_allow_html=True)

    product_names = df_all["nombre"].tolist()
    sel_product = st.selectbox("Selecciona un producto para simular:", product_names, key="sim_product")
    product_data = df_all[df_all["nombre"] == sel_product].iloc[0]

    months_labels = [(datetime.now() - timedelta(days=30 * (11 - i))).strftime("%b %Y") for i in range(12)]
    price_hist = generate_price_history(product_data["precio_usd"], 12)
    rot_hist = generate_rotation_history(product_data["unidades_mes"], product_data["tendencia"], 12)

    prices = [p["precio"] for p in price_hist]
    units = [r["unidades"] for r in rot_hist]

    fig_sim = make_subplots(specs=[[{"secondary_y": True}]])

    fig_sim.add_trace(go.Scatter(
        x=months_labels, y=prices,
        name="💰 Precio USD",
        line=dict(color=COLORS["gold"], width=3),
        mode="lines+markers",
        marker=dict(size=7)
    ), secondary_y=False)

    fig_sim.add_trace(go.Bar(
        x=months_labels, y=units,
        name="📦 Unidades vendidas",
        marker=dict(color=COLORS["accent"], opacity=0.7),
    ), secondary_y=True)

    fig_sim.update_layout(
        **plotly_theme(),
        title=f"Evolución Precio–Rotación: {sel_product[:50]}",
        height=380,
        margin=dict(l=20, r=20, t=50, b=40),
        legend=dict(orientation="h", y=1.05, bgcolor="rgba(0,0,0,0)"),
        hovermode="x unified"
    )
    fig_sim.update_yaxes(title_text="Precio (USD)", secondary_y=False, gridcolor=COLORS["primary"] + "20")
    fig_sim.update_yaxes(title_text="Unidades/mes", secondary_y=True, gridcolor=COLORS["primary"] + "20")

    st.plotly_chart(fig_sim, use_container_width=True)

    # Insight automático
    price_change = (prices[-1] - prices[0]) / prices[0] * 100
    unit_change = (units[-1] - units[0]) / units[0] * 100
    correlation = np.corrcoef(prices, units)[0, 1]

    icon_p = "📈" if price_change > 0 else "📉"
    icon_u = "📈" if unit_change > 0 else "📉"

    st.markdown(f"""
    <div class="tooltip-card">
        <div style="font-family:'Syne',sans-serif; font-weight:700; color:{COLORS['white']}; margin-bottom:10px;">
            🤖 Insight Automático — {sel_product[:40]}
        </div>
        <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:16px;">
            <div>
                <span style="color:{COLORS['pale']}; font-size:0.8rem;">Variación precio (12 meses)</span><br>
                <span style="color:{COLORS['gold']}; font-size:1.2rem; font-weight:700;">{icon_p} {price_change:+.1f}%</span>
            </div>
            <div>
                <span style="color:{COLORS['pale']}; font-size:0.8rem;">Variación rotación (12 meses)</span><br>
                <span style="color:{COLORS['accent']}; font-size:1.2rem; font-weight:700;">{icon_u} {unit_change:+.1f}%</span>
            </div>
            <div>
                <span style="color:{COLORS['pale']}; font-size:0.8rem;">Correlación Precio-Rotación</span><br>
                <span style="color:{COLORS['success'] if abs(correlation) < 0.3 else COLORS['warning']}; font-size:1.2rem; font-weight:700;">
                    {correlation:.2f} {'(baja)' if abs(correlation) < 0.3 else '(moderada)' if abs(correlation) < 0.6 else '(alta)'}
                </span>
            </div>
        </div>
        <div style="margin-top:12px; padding-top:10px; border-top:1px solid {COLORS['primary']}30; color:{COLORS['text']}; font-size:0.85rem;">
            {'⚠️ <strong>Alerta:</strong> El precio bajó mientras la rotación no subió proporcionalmente — posible baja competitividad.' if price_change < -3 and unit_change < 5 else
             '✅ <strong>Saludable:</strong> La rotación se mantiene estable o creciente independiente de variaciones de precio.' if unit_change > 0 else
             '🔄 El producto mantiene un comportamiento normal del mercado.'}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# TAB 3: PRECIOS & ROTACIÓN
# ══════════════════════════════════════════════

with tab3:
    st.markdown(f"<h3 style='color:{COLORS['white']}; font-family:Syne,sans-serif; margin-bottom:20px;'>💰 Análisis de Precios y Comportamiento de Rotación</h3>", unsafe_allow_html=True)

    col_p1, col_p2 = st.columns(2)

    with col_p1:
        # Scatter: Precio vs Rating
        fig_scatter = px.scatter(
            df_all,
            x="precio_usd",
            y="rating",
            size="unidades_mes",
            color="categoria",
            hover_name="nombre",
            hover_data=["marca", "rotacion", "tendencia"],
            color_discrete_sequence=px.colors.sequential.Blues_r,
            labels={"precio_usd": "Precio USD", "rating": "Rating"}
        )
        fig_scatter.update_layout(
            **plotly_theme(),
            title="Precio vs Rating (tamaño = volumen)",
            height=360,
            margin=dict(l=20, r=20, t=50, b=30),
            legend=dict(orientation="h", y=-0.2, font=dict(size=9), bgcolor="rgba(0,0,0,0)")
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col_p2:
        # Box plot rotación por precio
        df_price_cat = df_all.copy()
        df_price_cat["rango_precio"] = pd.cut(
            df_price_cat["precio_usd"],
            bins=[0, 20, 50, 100, 250],
            labels=["$0-20", "$20-50", "$50-100", "$100+"]
        )
        rot_order = {"muy_alta": 4, "alta": 3, "media_alta": 2, "media": 1, "baja": 0}
        df_price_cat["rot_score"] = df_price_cat["rotacion"].map(rot_order)

        fig_box = px.box(
            df_price_cat.dropna(subset=["rango_precio"]),
            x="rango_precio",
            y="unidades_mes",
            color="rango_precio",
            color_discrete_sequence=[COLORS["mid"], COLORS["primary"], COLORS["bright"], COLORS["accent"]],
            labels={"rango_precio": "Rango de precio", "unidades_mes": "Unidades/mes"}
        )
        fig_box.update_layout(
            **plotly_theme(),
            title="Volumen por Rango de Precio",
            height=360,
            showlegend=False,
            margin=dict(l=20, r=20, t=50, b=30)
        )
        st.plotly_chart(fig_box, use_container_width=True)

    # Heatmap: Rotación por categoría
    st.markdown(f"<h4 style='color:{COLORS['accent']}; font-family:Syne,sans-serif; margin:20px 0 10px;'>🔥 Mapa de Calor — Rotación por Categoría y Tendencia</h4>", unsafe_allow_html=True)

    pivot_data = df_all.groupby(["categoria", "tendencia"])["unidades_mes"].sum().reset_index()
    pivot = pivot_data.pivot(index="categoria", columns="tendencia", values="unidades_mes").fillna(0)

    fig_heat = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=[[0, COLORS["navy"]], [0.3, COLORS["mid"]], [0.6, COLORS["primary"]], [1, COLORS["accent"]]],
        text=[[format_currency(v) for v in row] for row in pivot.values],
        texttemplate="%{text}",
        textfont=dict(size=10, color=COLORS["white"]),
        hovertemplate="Categoría: %{y}<br>Tendencia: %{x}<br>Unidades: %{z:,}<extra></extra>",
        showscale=True,
        colorbar=dict(tickfont=dict(color=COLORS["pale"]))
    ))

    fig_heat.update_layout(
        **plotly_theme(),
        title="Unidades/mes — Categoría × Tendencia",
        height=380,
        margin=dict(l=20, r=80, t=50, b=30),
        xaxis=dict(tickfont=dict(size=10)),
        yaxis=dict(tickfont=dict(size=10))
    )
    st.plotly_chart(fig_heat, use_container_width=True)


# ══════════════════════════════════════════════
# TAB 4: EXPLORADOR
# ══════════════════════════════════════════════

with tab4:
    st.markdown(f"<h3 style='color:{COLORS['white']}; font-family:Syne,sans-serif; margin-bottom:20px;'>🔍 Explorador Detallado de Productos</h3>", unsafe_allow_html=True)

    search = st.text_input("🔎 Buscar producto, marca o problema...", placeholder="Ej: acné, Sephora, retinol, caída cabello...")

    df_explore = get_dataframe()
    if search:
        mask = (
            df_explore["nombre"].str.lower().str.contains(search.lower(), na=False) |
            df_explore["marca"].str.lower().str.contains(search.lower(), na=False) |
            df_explore["problema_ataca"].str.lower().str.contains(search.lower(), na=False) |
            df_explore["descripcion"].str.lower().str.contains(search.lower(), na=False) |
            df_explore["categoria"].str.lower().str.contains(search.lower(), na=False)
        )
        df_explore = df_explore[mask]

    st.markdown(f"<p style='color:{COLORS['pale']}; font-size:0.85rem;'>Mostrando {len(df_explore)} productos</p>", unsafe_allow_html=True)

    if len(df_explore) == 0:
        st.warning("No se encontraron productos. Intenta otra búsqueda.")
    else:
        # Tabla compacta
        display_cols = {
            "id": "ID",
            "nombre": "Producto",
            "marca": "Marca",
            "categoria": "Categoría",
            "precio_usd": "Precio USD",
            "precio_promedio_mercado": "Precio Mercado",
            "margen_oportunidad": "Margen %",
            "unidades_mes": "Unid/mes",
            "rating": "Rating",
            "tendencia": "Tendencia",
            "rotacion": "Rotación",
            "target": "Target"
        }
        df_display = df_explore[list(display_cols.keys())].rename(columns=display_cols)
        df_display["Tendencia"] = df_display["Tendencia"].map({
            "muy_creciente": "🚀 Muy Creciente",
            "creciente": "📈 Creciente",
            "estable": "➡️ Estable",
            "decreciente": "📉 Decreciente"
        })
        df_display["Rotación"] = df_display["Rotación"].map({
            "muy_alta": "🔵 Muy Alta",
            "alta": "🟢 Alta",
            "media_alta": "🟡 Media-Alta",
            "media": "🟡 Media",
            "baja": "🔴 Baja"
        })
        df_display["Precio USD"] = df_display["Precio USD"].apply(lambda x: f"${x:.2f}")
        df_display["Precio Mercado"] = df_display["Precio Mercado"].apply(lambda x: f"${x:.2f}")
        df_display["Margen %"] = df_display["Margen %"].apply(lambda x: f"{x:.1f}%")
        df_display["Unid/mes"] = df_display["Unid/mes"].apply(lambda x: f"{x:,}")
        df_display["Rating"] = df_display["Rating"].apply(lambda x: f"⭐ {x:.1f}")

        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            height=450
        )

        # Exportar CSV
        csv = df_explore.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Descargar datos completos (CSV)",
            data=csv,
            file_name=f"rome_market_data_{datetime.now().strftime('%Y%m')}.csv",
            mime="text/csv"
        )


# ══════════════════════════════════════════════
# TAB 5: ANÁLISIS COMPARATIVO
# ══════════════════════════════════════════════

with tab5:
    st.markdown(f"<h3 style='color:{COLORS['white']}; font-family:Syne,sans-serif; margin-bottom:20px;'>📊 Análisis Comparativo y Oportunidades</h3>", unsafe_allow_html=True)

    col_c1, col_c2 = st.columns(2)

    with col_c1:
        # Treemap categorías
        df_tree = get_dataframe()
        fig_tree = px.treemap(
            df_tree,
            path=["categoria", "subcategoria"],
            values="volumen_mensual_usd",
            color="score_oportunidad",
            color_continuous_scale=[[0, COLORS["mid"]], [0.5, COLORS["primary"]], [1, COLORS["accent"]]],
            hover_data=["nombre", "precio_usd"]
        )
        fig_tree.update_layout(
            **plotly_theme(),
            title="Mapa de Oportunidades por Volumen (USD)",
            height=400,
            margin=dict(l=10, r=10, t=50, b=10),
            coloraxis_colorbar=dict(title="Score", tickfont=dict(color=COLORS["pale"]))
        )
        fig_tree.update_traces(
            textfont=dict(size=11, color="white"),
            marker=dict(line=dict(width=2, color=COLORS["navy"]))
        )
        st.plotly_chart(fig_tree, use_container_width=True)

    with col_c2:
        # Top oportunidades: mayor diferencia precio vs mercado
        df_opp = get_dataframe().nlargest(10, "margen_oportunidad")
        fig_opp = go.Figure()

        fig_opp.add_trace(go.Bar(
            name="Precio propio",
            x=df_opp["nombre"].apply(lambda x: x[:30] + "..." if len(x) > 30 else x),
            y=df_opp["precio_usd"],
            marker_color=COLORS["primary"],
        ))
        fig_opp.add_trace(go.Bar(
            name="Precio mercado",
            x=df_opp["nombre"].apply(lambda x: x[:30] + "..." if len(x) > 30 else x),
            y=df_opp["precio_promedio_mercado"],
            marker_color=COLORS["accent"],
        ))

        fig_opp.update_layout(
            **plotly_theme(),
            title="Top 10 — Oportunidad de Margen",
            barmode="group",
            height=400,
            margin=dict(l=10, r=10, t=50, b=80),
            legend=dict(orientation="h", y=1.05, bgcolor="rgba(0,0,0,0)"),
            xaxis=dict(tickangle=-35, tickfont=dict(size=9))
        )
        st.plotly_chart(fig_opp, use_container_width=True)

    # Radar por categoría
    st.markdown(f"<h4 style='color:{COLORS['accent']}; font-family:Syne,sans-serif; margin:20px 0 10px;'>🕸️ Radar de Competitividad por Categoría</h4>", unsafe_allow_html=True)

    df_radar = get_dataframe()
    radar_cats = df_radar.groupby("categoria").agg({
        "rating": "mean",
        "margen_oportunidad": "mean",
        "unidades_mes": lambda x: x.mean() / 1000,
        "score_oportunidad": "mean",
        "precio_usd": lambda x: 10 - (x.mean() / 30)  # Competitividad inversa de precio
    }).reset_index()

    cats_to_show = radar_cats["categoria"].head(6).tolist()
    metrics = ["rating", "margen_oportunidad", "unidades_mes", "score_oportunidad", "precio_usd"]
    metric_labels = ["Rating", "Margen %", "Vol. (x1000)", "Score", "Competitividad Precio"]

    fig_radar = go.Figure()
    colors_radar = [COLORS["accent"], COLORS["gold"], COLORS["success"], COLORS["warning"], COLORS["pale"], COLORS["bright"]]

    for i, cat in enumerate(cats_to_show):
        row = radar_cats[radar_cats["categoria"] == cat].iloc[0]
        values = [row[m] for m in metrics]
        # Normalizar 0-10
        max_vals = [5, 10, 100, 100, 10]
        values_norm = [min(v / m * 10, 10) for v, m in zip(values, max_vals)]
        values_norm.append(values_norm[0])

        fig_radar.add_trace(go.Scatterpolar(
            r=values_norm,
            theta=metric_labels + [metric_labels[0]],
            fill="toself",
            fillcolor=colors_radar[i % len(colors_radar)] + "20",
            line=dict(color=colors_radar[i % len(colors_radar)], width=2),
            name=cat
        ))

    fig_radar.update_layout(
        **plotly_theme(),
        polar=dict(
            bgcolor=COLORS["dark"] + "80",
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                tickfont=dict(color=COLORS["pale"], size=9),
                gridcolor=COLORS["primary"] + "30"
            ),
            angularaxis=dict(
                tickfont=dict(color=COLORS["text"], size=11),
                gridcolor=COLORS["primary"] + "30"
            )
        ),
        title="Radar de Competitividad — Top 6 Categorías",
        height=450,
        showlegend=True,
        legend=dict(orientation="h", y=-0.1, font=dict(size=10), bgcolor="rgba(0,0,0,0)")
    )
    st.plotly_chart(fig_radar, use_container_width=True)


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────

st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown(f"""
<div style="text-align:center; padding: 16px 0; color:{COLORS['pale']}; font-size:0.8rem;">
    <span style="font-family:'Syne',sans-serif; font-size:1rem; color:{COLORS['accent']}; font-weight:700;">
        ESTUDIO DE MERCADO ROME
    </span>
    &nbsp;·&nbsp; Datos actualizados: <strong style="color:{COLORS['white']};">{datetime.now().strftime("%B %Y")}</strong>
    &nbsp;·&nbsp; {len(get_dataframe())} productos indexados
    &nbsp;·&nbsp; Mercados: USA · UK · Francia · Japón · Korea · Global
    <br><br>
    <span style="font-size:0.72rem; opacity:0.6;">
        ⚠️ Los precios y unidades son estimaciones de mercado con fines de análisis competitivo. Actualización mensual automática.
    </span>
</div>
""", unsafe_allow_html=True)
