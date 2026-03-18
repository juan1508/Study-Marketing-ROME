"""ESTUDIO DE MERCADO ROME — Calculadora de Precios Colombia"""

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Estudio de Mercado ROME",
    page_icon="🔵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500&display=swap');
.stApp{background:linear-gradient(135deg,#0A1628,#0D2137);}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;color:#DDE8F5;}
h1,h2,h3{font-family:'Syne',sans-serif;font-weight:800;}
#MainMenu,footer,header{visibility:hidden;}
div[data-testid="metric-container"]{
    background:linear-gradient(135deg,#1A3A5CCC,#1E5FAD33)!important;
    border:1px solid #54A0FF40!important;border-radius:12px!important;padding:16px!important;}
div[data-testid="metric-container"] label{color:#A8D8F0!important;font-size:.8rem!important;text-transform:uppercase;}
[data-testid="stMetricValue"]{color:#EEF6FF!important;font-family:'Syne',sans-serif!important;font-weight:800!important;}
.stDataFrame{border-radius:12px!important;}
thead tr th{background:#1A3A5C!important;color:#A8D8F0!important;font-weight:600!important;}
</style>
""", unsafe_allow_html=True)

# ── CONSTANTES DE COSTOS COLOMBIA ────────────────────────────────
# TRM promedio 2025
TRM = 4200

# Costo envío proveedor → Colombia (promedio por producto pequeño/mediano)
# Incluye: flete internacional + aduana estimada + última milla
ENVIO_USD = 8.50

# Impuestos importación Colombia (arancel promedio belleza ~15% + IVA 19%)
ARANCEL_PCT = 0.15
IVA_PCT = 0.19

# Margen mínimo objetivo
MARGEN_MIN = 0.35

# ── BASE DE PRODUCTOS ────────────────────────────────────────────
PRODUCTOS = [
    # PIEL
    ("The Ordinary Niacinamide 10% + Zinc","The Ordinary","Piel",6.90,"Amazon/ASOS","Poros, manchas, acné"),
    ("Paula's Choice BHA 2% Liquid Exfoliant","Paula's Choice","Piel",34.00,"Paula's Choice","Poros, acné, opacidad"),
    ("SkinCeuticals C E Ferulic","SkinCeuticals","Piel",182.00,"Dermstore/Sephora","Manchas, envejecimiento"),
    ("Differin Adapalene Gel 0.1%","Differin","Piel",15.50,"Amazon/Walmart","Acné, cicatrices, arrugas"),
    ("CeraVe Moisturizing Cream 250ml","CeraVe","Piel",19.00,"Amazon/Walmart","Sequedad, barrera cutánea"),
    ("Good Molecules Discoloration Serum","Good Molecules","Piel",12.00,"Ulta/Amazon","Hiperpigmentación, manchas"),
    ("Sol de Janeiro Brazilian Bum Bum Cream","Sol de Janeiro","Piel",48.00,"Sephora/Amazon","Celulitis, flacidez"),
    ("Bio-Oil Skincare Oil 125ml","Bio-Oil","Piel",14.00,"Amazon/Walmart","Estrías, cicatrices"),
    ("La Roche-Posay Effaclar Duo+","La Roche-Posay","Piel",30.00,"Amazon/Dermstore","Acné, poros, grasa"),
    ("EltaMD UV Clear SPF 46","EltaMD","Piel",39.00,"Amazon/Dermstore","Daño solar, manchas"),
    ("Neutrogena Rapid Wrinkle Repair Eye Cream","Neutrogena","Piel",22.00,"Amazon/Walmart","Bolsas, ojeras, arrugas"),
    ("RoC Retinol Correxion Line Smoothing Cream","RoC","Piel",25.99,"Amazon/Walmart","Arrugas, líneas expresión"),
    ("Some By Mi AHA BHA PHA 30 Days Toner","Some By Mi","Piel",22.00,"Amazon/YesStyle","Poros, textura, manchas"),
    ("Drunk Elephant C-Firma Fresh Day Serum","Drunk Elephant","Piel",90.00,"Sephora/Amazon","Opacidad, manchas"),
    ("GlamGlow Supermud Clearing Treatment","GlamGlow","Piel",69.00,"Sephora/Amazon","Acné, poros, impurezas"),
    # CABELLO
    ("Viviscal Extra Strength Hair Growth Supplement","Viviscal","Cabello",49.99,"Amazon/Ulta","Caída del cabello"),
    ("Minoxidil 5% Kirkland Foam 6 meses","Kirkland","Cabello",29.00,"Amazon/Costco","Calvicie, entradas"),
    ("Olaplex No.3 Hair Perfector 100ml","Olaplex","Cabello",30.00,"Sephora/Amazon","Cabello quebradizo"),
    ("Nizoral Anti-Dandruff Shampoo","Nizoral","Cabello",15.00,"Amazon/CVS","Caspa, dermatitis"),
    ("Madison Reed Root Touch Up Kit","Madison Reed","Cabello",26.00,"Amazon/Ulta","Canas prematuras"),
    # ENVEJECIMIENTO
    ("Vital Proteins Collagen Peptides 283g","Vital Proteins","Envejecimiento",43.00,"Amazon/Target","Arrugas, cabello, uñas"),
    ("StriVectin-TL Tightening Neck Cream","StriVectin","Envejecimiento",89.00,"Sephora/Amazon","Flacidez cuello"),
    ("Murad Rapid Age Spot Correcting Serum","Murad","Envejecimiento",86.00,"Sephora/Amazon","Manchas edad"),
    # MAQUILLAJE
    ("Fenty Beauty Pro Filt'r Foundation","Fenty Beauty","Maquillaje",40.00,"Sephora","Tono desigual, manchas"),
    ("Charlotte Tilbury Pillow Talk Lip Liner","Charlotte Tilbury","Maquillaje",28.00,"Sephora/Nordstrom","Labios finos"),
    ("Benefit Gimme Brow+ Volumizing Gel","Benefit","Maquillaje",24.00,"Sephora/Ulta","Cejas escasas"),
    ("L'Oreal Voluminous Original Mascara","L'Oreal","Maquillaje",10.99,"Amazon/Walmart","Pestañas cortas"),
    ("NYX Professional Makeup Wonder Stick","NYX","Maquillaje",14.00,"Amazon/Ulta","Definición facial"),
    ("e.l.f. Poreless Putty Primer","e.l.f.","Maquillaje",10.00,"Amazon/Target","Poros visibles"),
    ("Charlotte Tilbury Flawless Filter","Charlotte Tilbury","Maquillaje",46.00,"Sephora/Nordstrom","Base luminosa natural"),
    ("NARS Radiant Creamy Concealer","NARS","Maquillaje",32.00,"Sephora/Ulta","Ojeras, imperfecciones"),
    ("Too Faced Better Than Sex Mascara","Too Faced","Maquillaje",27.00,"Sephora/Ulta","Pestañas volumen"),
    ("Urban Decay All Nighter Setting Spray","Urban Decay","Maquillaje",33.00,"Sephora/Ulta","Maquillaje duradero"),
    # CUERPO
    ("Optimum Nutrition Gold Standard Whey 908g","Optimum Nutrition","Cuerpo",58.00,"Amazon/GNC","Masa muscular"),
    ("Bliss Fat Girl Slim Arm Candy Cream","Bliss","Cuerpo",38.00,"Amazon/Ulta","Flacidez brazos"),
    # VELLO
    ("Ulike Air 3 IPL Hair Removal Device","Ulike","Vello",219.00,"Amazon/ulike.com","Vello facial, corporal"),
    ("Tend Skin Solution 236ml","Tend Skin","Vello",24.00,"Amazon/Ulta","Vello encarnado"),
    # SUDORACIÓN
    ("Native Natural Deodorant","Native","Sudoración",13.00,"Amazon/Target","Mal olor, transpiración"),
    ("Carpe Antiperspirant Hand Lotion","Carpe","Sudoración",14.95,"Amazon/Target","Sudoración excesiva"),
    # MANOS Y UÑAS
    ("OPI Nail Envy Original Formula","OPI","Manos y Uñas",19.99,"Amazon/Ulta","Uñas frágiles"),
    ("L'Occitane Shea Butter Hand Cream 150ml","L'Occitane","Manos y Uñas",32.00,"Sephora/Amazon","Manos resecas"),
    ("Baby Foot Exfoliant Foot Peel","Baby Foot","Pies",25.00,"Amazon/Ulta","Pies agrietados, callos"),
    # CUIDADO MASCULINO
    ("Beardbrand Gold Beard Oil 30ml","Beardbrand","Cuidado Masculino",25.00,"beardbrand.com","Barba áspera"),
    ("Jack Black Pure Clean Facial Cleanser","Jack Black","Cuidado Masculino",24.00,"Amazon/Sephora","Piel grasa, acné"),
    # BIENESTAR
    ("HUM Nutrition Daily Cleanse Supplement","HUM Nutrition","Bienestar",40.00,"Sephora/Amazon","Acné interno, piel opaca"),
    ("Leanbean Fat Burner for Women","Leanbean","Bienestar",59.99,"leanbean.com","Control de peso"),
    # MIRADA
    ("RapidLash Eyelash Enhancing Serum","RapidLash","Mirada",49.99,"Amazon/Ulta","Pestañas cortas"),
    # SKINCARE PREMIUM
    ("Crest 3D Whitestrips Professional Effects","Crest","Sonrisa",49.99,"Amazon/Walmart","Dientes amarillos"),
    ("Native Natural Lip Balm 3-Pack","Native","Labios",12.00,"Amazon/Target","Labios secos"),
    ("Herbivore Bakuchiol Retinol Alternative Serum","Herbivore","Skincare Premium",54.00,"Sephora/Amazon","Arrugas, poros"),
]


def calcular_precio(precio_proveedor_usd, margen=MARGEN_MIN):
    """
    Calcula precio de venta sugerido en COP para Colombia.
    
    Flujo de costos:
    1. Precio proveedor (USD)
    2. + Envío estimado a Colombia
    3. + Arancel (15% sobre valor + envío)
    4. + IVA (19% sobre valor + envío + arancel)
    5. Convertir a COP con TRM
    6. Aplicar margen mínimo 35%
    """
    costo_usd = precio_proveedor_usd + ENVIO_USD
    arancel   = costo_usd * ARANCEL_PCT
    base_iva  = costo_usd + arancel
    iva       = base_iva * IVA_PCT
    costo_total_usd = base_iva + iva
    costo_cop = costo_total_usd * TRM

    # Precio de venta con margen objetivo
    precio_venta = costo_cop / (1 - margen)

    # Redondear al múltiplo de 1000 más cercano hacia arriba
    import math
    precio_venta_redondeado = math.ceil(precio_venta / 1000) * 1000

    margen_real = (precio_venta_redondeado - costo_cop) / precio_venta_redondeado * 100

    return {
        "costo_proveedor_usd": precio_proveedor_usd,
        "costo_envio_usd":     ENVIO_USD,
        "arancel_usd":         round(arancel, 2),
        "iva_usd":             round(iva, 2),
        "costo_total_usd":     round(costo_total_usd, 2),
        "costo_total_cop":     round(costo_cop),
        "precio_venta_cop":    precio_venta_redondeado,
        "ganancia_cop":        precio_venta_redondeado - round(costo_cop),
        "margen_pct":          round(margen_real, 1),
    }


# ── HEADER ────────────────────────────────────────────────────────
st.markdown(f"""
<div style="padding:24px 0 8px;">
  <h1 style="margin:0;font-size:2.2rem;background:linear-gradient(90deg,#EEF6FF,#54A0FF);
     -webkit-background-clip:text;-webkit-text-fill-color:transparent;font-family:'Syne',sans-serif;">
     🔬 ESTUDIO DE MERCADO ROME
  </h1>
  <p style="margin:4px 0 0;color:#A8D8F0;font-size:.95rem;">
     Calculadora de Precios para Venta en Colombia · Margen mínimo 35% · {len(PRODUCTOS)} productos
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr style='border-color:#1E5FAD30;margin:8px 0 20px;'>", unsafe_allow_html=True)

# ── PARÁMETROS AJUSTABLES ─────────────────────────────────────────
with st.expander("⚙️ Ajustar parámetros de cálculo", expanded=False):
    pc1, pc2, pc3, pc4 = st.columns(4)
    with pc1:
        trm_val = st.number_input("TRM (USD a COP)", value=4200, step=50,
                                   help="Tasa de cambio actual")
    with pc2:
        envio_val = st.number_input("Envio a Colombia (USD)", value=8.50, step=0.50,
                                     help="Costo promedio envio internacional + ultima milla")
    with pc3:
        arancel_pct = st.number_input("Arancel importacion (%)", value=15.0, step=1.0,
                                       help="Arancel promedio productos belleza Colombia")
        arancel_val = arancel_pct / 100
    with pc4:
        margen_pct = st.number_input("Margen minimo objetivo (%)", value=35.0, step=5.0,
                                      help="Porcentaje de ganancia sobre precio de venta")
        margen_val = margen_pct / 100

# Recalcular con parámetros actuales
import math

def calcular(precio_prov, margen=None):
    m = margen if margen else margen_val
    costo   = precio_prov + envio_val
    arancel = costo * arancel_val
    base    = costo + arancel
    iva     = base * IVA_PCT
    total_usd = base + iva
    total_cop = total_usd * trm_val
    venta   = math.ceil((total_cop / (1 - m)) / 1000) * 1000
    ganancia = venta - round(total_cop)
    margen_r = (venta - total_cop) / venta * 100
    return total_cop, venta, ganancia, margen_r, total_usd

# ── CONSTRUIR TABLA ───────────────────────────────────────────────
filas = []
for nombre, marca, cat, precio_prov, fuente, problema in PRODUCTOS:
    costo_cop, venta_cop, ganancia_cop, margen_r, total_usd = calcular(precio_prov)
    filas.append({
        "Producto":          nombre,
        "Marca":             marca,
        "Categoría":         cat,
        "Precio Proveedor":  f"${precio_prov:.2f} USD",
        "Costo Total USD":   f"${total_usd:.2f}",
        "Costo Total COP":   f"${costo_cop:,.0f}",
        "💰 Precio Venta COP": f"${venta_cop:,.0f}",
        "Ganancia COP":      f"${ganancia_cop:,.0f}",
        "Margen %":          f"{margen_r:.1f}%",
        "Plataforma Compra": fuente,
        "Problema Atacado":  problema,
        # valores numéricos para métricas
        "_precio_prov":      precio_prov,
        "_venta_cop":        venta_cop,
        "_ganancia":         ganancia_cop,
        "_margen":           margen_r,
    })

df_full = pd.DataFrame(filas)

# ── KPIs ─────────────────────────────────────────────────────────
k1,k2,k3,k4 = st.columns(4)
with k1:
    st.metric("📦 Productos", len(df_full))
with k2:
    avg_venta = df_full["_venta_cop"].mean()
    st.metric("💰 Precio Venta Prom.", f"${avg_venta:,.0f} COP")
with k3:
    avg_margen = df_full["_margen"].mean()
    st.metric("📈 Margen Promedio", f"{avg_margen:.1f}%")
with k4:
    mejor = df_full.loc[df_full["_margen"].idxmax(), "Producto"]
    st.metric("🏆 Mayor Margen", mejor[:30]+"..." if len(mejor)>30 else mejor)

st.markdown("<br>", unsafe_allow_html=True)

# ── FILTRO RÁPIDO ─────────────────────────────────────────────────
col_f1, col_f2, col_f3 = st.columns([2, 2, 2])
with col_f1:
    buscar = st.text_input("🔎 Buscar producto...", placeholder="Ej: retinol, mascara, colágeno")
with col_f2:
    cats_list = ["Todas"] + sorted(df_full["Categoría"].unique().tolist())
    cat_filtro = st.selectbox("📂 Categoría", cats_list)
with col_f3:
    precio_max = st.slider("Precio venta máx. (COP millones)", 0.0, 5.0, 5.0, 0.1)

# Aplicar filtros
df_show = df_full.copy()
if buscar:
    q = buscar.lower()
    df_show = df_show[
        df_show["Producto"].str.lower().str.contains(q, na=False) |
        df_show["Marca"].str.lower().str.contains(q, na=False) |
        df_show["Problema Atacado"].str.lower().str.contains(q, na=False)
    ]
if cat_filtro != "Todas":
    df_show = df_show[df_show["Categoría"] == cat_filtro]
df_show = df_show[df_show["_venta_cop"] <= precio_max * 1_000_000]

st.caption(f"Mostrando {len(df_show)} de {len(df_full)} productos")

# ── TABLA PRINCIPAL ───────────────────────────────────────────────
cols_display = [
    "Producto", "Marca", "Categoría",
    "Precio Proveedor", "Costo Total USD", "Costo Total COP",
    "💰 Precio Venta COP", "Ganancia COP", "Margen %",
    "Plataforma Compra", "Problema Atacado"
]

st.dataframe(
    df_show[cols_display],
    use_container_width=True,
    hide_index=True,
    height=600,
    column_config={
        "Producto":           st.column_config.TextColumn("Producto", width=220),
        "Marca":              st.column_config.TextColumn("Marca", width=120),
        "Categoría":          st.column_config.TextColumn("Categoría", width=120),
        "Precio Proveedor":   st.column_config.TextColumn("Precio Proveedor", width=120),
        "Costo Total USD":    st.column_config.TextColumn("Costo Total USD", width=110),
        "Costo Total COP":    st.column_config.TextColumn("Costo Total COP", width=120),
        "💰 Precio Venta COP":st.column_config.TextColumn("💰 Precio Venta COP", width=150),
        "Ganancia COP":       st.column_config.TextColumn("Ganancia COP", width=120),
        "Margen %":           st.column_config.TextColumn("Margen %", width=80),
        "Plataforma Compra":  st.column_config.TextColumn("Plataforma", width=140),
        "Problema Atacado":   st.column_config.TextColumn("Problema", width=200),
    }
)

# ── DESCARGA ─────────────────────────────────────────────────────
csv = df_show[cols_display].to_csv(index=False).encode("utf-8")
st.download_button(
    "📥 Descargar tabla completa (CSV)",
    csv,
    "rome_precios_colombia.csv",
    "text/csv",
    use_container_width=False
)

# ── NOTA METODOLÓGICA ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("📋 Cómo se calculan los precios"):
    st.markdown(f"""
**Fórmula de cálculo:**

```
Costo base        = Precio proveedor + Envío a Colombia (${envio_val:.2f} USD)
Arancel           = Costo base × {arancel_val*100:.0f}%  (arancel promedio belleza)
IVA               = (Costo base + Arancel) × 19%
Costo total USD   = Costo base + Arancel + IVA
Costo total COP   = Costo total USD × TRM ({trm_val:,})
Precio venta COP  = Costo total COP ÷ (1 - {margen_val*100:.0f}%)
                    → Redondeado al próximo múltiplo de $1,000
```

**Supuestos:**
- Precio proveedor: precio promedio en plataformas internacionales (Amazon, Sephora, etc.)
- Envío: estimado para paquetes pequeños/medianos vía operador logístico (DHL, FedEx, UPS)
- Arancel: promedio categoría cosméticos y cuidado personal según DIAN
- IVA: 19% estándar Colombia
- TRM: ${trm_val:,} COP/USD (ajustable arriba)
- Margen: sobre precio de venta (no sobre costo)
    """)

st.markdown(f"""
<div style="text-align:center;padding:20px 0;color:#A8D8F0;font-size:.78rem;">
  <span style="font-family:'Syne',sans-serif;font-size:1rem;color:#54A0FF;font-weight:700;">
    ESTUDIO DE MERCADO ROME
  </span><br>
  Precios sugeridos para Colombia · TRM ${trm_val:,} · Margen mínimo {margen_val*100:.0f}%<br>
  <span style="opacity:.5;font-size:.7rem;">
    Precios referenciales. Verificar aranceles exactos en DIAN según partida arancelaria.
  </span>
</div>
""", unsafe_allow_html=True)
