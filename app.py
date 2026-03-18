"""ESTUDIO DE MERCADO ROME — Calculadora Colombia"""
import streamlit as st
import pandas as pd
import math

st.set_page_config(
    page_title="ROME Market — Colombia",
    page_icon="🔵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500&display=swap');
.stApp { background: linear-gradient(135deg, #0A1628, #0D2137); }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: #DDE8F5; }
h1, h2 { font-family: 'Syne', sans-serif; font-weight: 800; }
#MainMenu, footer, header { visibility: hidden; }
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #1A3A5CCC, #1E5FAD33) !important;
    border: 1px solid #54A0FF40 !important;
    border-radius: 12px !important;
    padding: 16px !important;
}
div[data-testid="metric-container"] label {
    color: #A8D8F0 !important;
    font-size: .78rem !important;
    text-transform: uppercase;
    letter-spacing: .05em;
}
[data-testid="stMetricValue"] {
    color: #EEF6FF !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1.4rem !important;
}
</style>
""", unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:20px 0 8px;">
  <h1 style="margin:0;font-size:1.9rem;background:linear-gradient(90deg,#EEF6FF,#54A0FF);
     -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
     🔬 ESTUDIO DE MERCADO ROME — Colombia
  </h1>
  <p style="margin:4px 0 0;color:#A8D8F0;font-size:.88rem;">
     49 productos · Precios de venta sugeridos · Rentabilidad minima 30%
  </p>
</div>
<hr style="border-color:#1E5FAD30;margin:8px 0 20px;">
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# PARAMETROS GLOBALES (tu tabla de referencia)
# ══════════════════════════════════════════════════════════════════
st.markdown("### ⚙️ Parametros globales de la operacion")
st.caption("Ajusta los valores base que aplican a todos los productos")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    flete       = st.number_input("🚚 Flete promedio (COP)", value=18000, step=1000,
                                   help="Costo promedio del envio al cliente")
with col2:
    dev_pct     = st.number_input("↩️ % Devoluciones", value=20.0, step=1.0,
                                   help="Porcentaje estimado de devoluciones") / 100
with col3:
    gastos_op   = st.number_input("🏢 Gastos Operativos (COP)", value=0, step=1000,
                                   help="Costos fijos: plataforma, empleados, impuestos por unidad")
with col4:
    cpa_pct     = st.number_input("📢 CPA % (Publicidad)", value=15.0, step=1.0,
                                   help="Costo de publicidad como % del precio de venta") / 100
with col5:
    rent_min    = st.number_input("🎯 Rentabilidad minima %", value=30.0, step=5.0,
                                   help="Ganancia neta minima sobre precio de venta") / 100

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# FORMULA (basada en tu tabla)
# ══════════════════════════════════════════════════════════════════
# Precio Venta = Costo unitario + Flete + Devoluciones% + Gastos Op + CPA% + Rentabilidad%
# Despejando:
# PV = (Costo + Flete + GastosOp) / (1 - Dev% - CPA% - Rent%)

def calcular(costo_cop):
    """
    Basado en tu tabla Colombia:
    - Costo unitario producto (COP)
    - + Flete promedio (COP)
    - + % Devoluciones (sobre PV)
    - + Gastos Operativos (COP fijo)
    - + CPA % (sobre PV)
    - = Precio de Venta
    - Rentabilidad = PV - todos los costos
    """
    # Costos fijos en COP
    costos_fijos = costo_cop + flete + gastos_op

    # Costos variables como % del PV (devoluciones + CPA + rentabilidad)
    pct_sobre_pv = dev_pct + cpa_pct + rent_min

    if pct_sobre_pv >= 1.0:
        return None

    # Precio de venta mínimo
    pv_raw = costos_fijos / (1 - pct_sobre_pv)

    # Redondear al próximo múltiplo de 1000
    pv = math.ceil(pv_raw / 1000) * 1000

    # Desglose real con PV redondeado
    devoluciones = round(pv * dev_pct)
    cpa_cop      = round(pv * cpa_pct)
    rentabilidad = pv - costo_cop - flete - gastos_op - devoluciones - cpa_cop
    rent_pct     = round(rentabilidad / pv * 100, 1)

    return {
        "pv":           pv,
        "devoluciones": devoluciones,
        "cpa_cop":      cpa_cop,
        "rentabilidad": rentabilidad,
        "rent_pct":     rent_pct,
    }

# ══════════════════════════════════════════════════════════════════
# PRODUCTOS CON REFERENCIAS COMPLETAS
# (nombre, marca, cat, costo_cop_estimado, asin_ref, url, presentaciones, problema)
# Costo COP = precio_USD * TRM promedio 4200 (ya con envio internacional incluido)
# ══════════════════════════════════════════════════════════════════
TRM = 4200  # para convertir precio proveedor USD a COP

PRODUCTOS = [
    # PIEL
    ("The Ordinary Niacinamide 10% + Zinc 1%",        "The Ordinary",    "Piel",               6.90,  "ASIN: B07M9LX9DH", "amazon.com/dp/B07M9LX9DH",       "30ml — presentacion unica",                                  "Poros, manchas, acne"),
    ("Paula's Choice BHA 2% Liquid Exfoliant",         "Paula's Choice",  "Piel",               34.00, "ASIN: B00949CTQQ", "amazon.com/dp/B00949CTQQ",       "30ml ($12) | 118ml ($34) | 950ml jumbo ($75)",                "Poros, acne, opacidad"),
    ("SkinCeuticals C E Ferulic Serum",                "SkinCeuticals",   "Piel",               182.00,"ASIN: B000NZUQOY", "amazon.com/dp/B000NZUQOY",       "30ml — presentacion unica",                                  "Manchas, envejecimiento"),
    ("Differin Adapalene Gel 0.1%",                    "Differin",        "Piel",               15.50, "ASIN: B07L1PHSY9", "amazon.com/dp/B07L1PHSY9",       "15g ($12) | 45g ($15.50) | 2-pack ($28)",                    "Acne, cicatrices, arrugas"),
    ("CeraVe Moisturizing Cream",                      "CeraVe",          "Piel",               19.00, "ASIN: B00TTD9BRC", "amazon.com/dp/B00TTD9BRC",       "250ml ($19) | 453g ($25) | 544g ($28) | 1kg ($38)",          "Sequedad, barrera cutanea"),
    ("Good Molecules Discoloration Correcting Serum",  "Good Molecules",  "Piel",               12.00, "SKU: 810065800078","goodmolecules.com / ulta.com",    "30ml — presentacion unica",                                  "Hiperpigmentacion, manchas"),
    ("Sol de Janeiro Brazilian Bum Bum Cream",         "Sol de Janeiro",  "Piel",               48.00, "ASIN: B01N3D7DKB", "amazon.com/dp/B01N3D7DKB",       "75ml ($26) | 240ml ($48) | 480ml ($72)",                     "Celulitis, flacidez"),
    ("Bio-Oil Skincare Oil",                           "Bio-Oil",         "Piel",               14.00, "ASIN: B01MS3GFHK", "amazon.com/dp/B01MS3GFHK",       "60ml ($10) | 125ml ($14) | 200ml ($18) | 250ml ($22)",       "Estrias, cicatrices"),
    ("La Roche-Posay Effaclar Duo+",                   "La Roche-Posay",  "Piel",               30.00, "ASIN: B014OPM4P4", "amazon.com/dp/B014OPM4P4",       "40ml — presentacion unica",                                  "Acne, poros, grasa"),
    ("EltaMD UV Clear Broad-Spectrum SPF 46",          "EltaMD",          "Piel",               39.00, "ASIN: B002MSN3QQ", "amazon.com/dp/B002MSN3QQ",       "48g Untinted ($39) | 48g Tinted ($41)",                      "Dano solar, manchas"),
    ("Neutrogena Rapid Wrinkle Repair Eye Cream",      "Neutrogena",      "Piel",               22.00, "ASIN: B00BT7BYLY", "amazon.com/dp/B00BT7BYLY",       "14g — presentacion unica",                                   "Bolsas, ojeras, arrugas"),
    ("RoC Retinol Correxion Line Smoothing Cream",     "RoC",             "Piel",               25.99, "ASIN: B075H4FDMZ", "amazon.com/dp/B075H4FDMZ",       "30ml ($26) | 48g Max Wrinkle ($30) | Eye cream ($22)",       "Arrugas, lineas expresion"),
    ("Some By Mi AHA BHA PHA 30 Days Toner",           "Some By Mi",      "Piel",               22.00, "ASIN: B07C7FQG3Z", "amazon.com/dp/B07C7FQG3Z",       "150ml ($22) | 300ml ($30)",                                  "Poros, textura, manchas"),
    ("Drunk Elephant C-Firma Fresh Day Serum",         "Drunk Elephant",  "Piel",               90.00, "ASIN: B072J74N5K", "amazon.com/dp/B072J74N5K",       "15ml mini ($50) | 30ml ($90)",                               "Opacidad, manchas"),
    ("GlamGlow Supermud Clearing Treatment",           "GlamGlow",        "Piel",               69.00, "ASIN: B00IFHPQDY", "amazon.com/dp/B00IFHPQDY",       "34g ($55) | 50g ($69) | 100g ($109)",                        "Acne, poros, impurezas"),
    ("Herbivore Bakuchiol Retinol Alternative Oil",    "Herbivore",       "Piel",               54.00, "ASIN: B07YTTQKRS", "amazon.com/dp/B07YTTQKRS",       "15ml ($34) | 30ml ($54)",                                    "Arrugas, poros, firmeza"),
    # CABELLO
    ("Viviscal Extra Strength Hair Growth Supplement", "Viviscal",        "Cabello",            49.99, "ASIN: B00BSZKETA", "amazon.com/dp/B00BSZKETA",       "60 tabs/1 mes ($50) | 180 tabs/3 meses ($130)",              "Caida del cabello, alopecia"),
    ("Minoxidil 5% Foam Kirkland Signature",           "Kirkland",        "Cabello",            29.00, "ASIN: B00GXYK4GO", "amazon.com/dp/B00GXYK4GO",       "6x60ml supply 6 meses ($29) | 1 mes ($12)",                  "Calvicie, entradas"),
    ("Olaplex No.3 Hair Perfector",                    "Olaplex",         "Cabello",            30.00, "ASIN: B013NQRZME", "amazon.com/dp/B013NQRZME",       "100ml ($30) | 250ml ($52) | 1000ml salon ($130)",            "Cabello quebradizo, danado"),
    ("Nizoral A-D Anti-Dandruff Shampoo 1%",           "Nizoral",         "Cabello",            15.00, "ASIN: B00AINMFAC", "amazon.com/dp/B00AINMFAC",       "200ml ($15) | 400ml ($24) | 730ml ($35)",                    "Caspa, dermatitis seborreica"),
    ("Madison Reed Root Touch Up Kit",                 "Madison Reed",    "Cabello",            26.00, "ASIN: B01MUAISNV", "amazon.com/dp/B01MUAISNV",       "Kit completo — 13 tonos ($26 c/u)",                          "Canas prematuras"),
    # ENVEJECIMIENTO
    ("Vital Proteins Collagen Peptides Powder",        "Vital Proteins",  "Envejecimiento",     43.00, "ASIN: B00K6EM5CK", "amazon.com/dp/B00K6EM5CK",       "283g ($43) | 567g ($68) | sachets x20 ($25)",                "Arrugas, cabello, unas"),
    ("StriVectin TL Advanced Tightening Neck Cream",   "StriVectin",      "Envejecimiento",     89.00, "ASIN: B07BFKZP7W", "amazon.com/dp/B07BFKZP7W",       "30ml ($65) | 50ml ($89)",                                    "Flacidez cuello y escote"),
    ("Murad Rapid Age Spot Lightening Serum",          "Murad",           "Envejecimiento",     86.00, "ASIN: B001447XCK", "amazon.com/dp/B001447XCK",       "30ml — presentacion unica",                                  "Manchas edad, hiperpigmentacion"),
    # MAQUILLAJE
    ("Fenty Beauty Pro Filt'r Soft Matte Foundation",  "Fenty Beauty",    "Maquillaje",         40.00, "SKU: varia x tono","fentybeauty.com / sephora.com",   "32ml — 50 tonos disponibles ($40 c/u)",                      "Tono desigual, manchas"),
    ("Charlotte Tilbury Pillow Talk Lip Liner",        "Charlotte Tilbury","Maquillaje",         28.00, "ASIN: B06WVFQXF4", "amazon.com/dp/B06WVFQXF4",       "1.2g — 8 tonos ($28 c/u)",                                   "Labios finos, sin definicion"),
    ("Benefit Gimme Brow+ Volumizing Eyebrow Gel",     "Benefit",         "Maquillaje",         24.00, "ASIN: B0774YDJ5H", "amazon.com/dp/B0774YDJ5H",       "3g full ($24) | 1.5g mini ($16) — 12 tonos",                 "Cejas escasas, ralas"),
    ("L'Oreal Paris Voluminous Original Mascara",      "L'Oreal",         "Maquillaje",         10.99, "ASIN: B000URXPKE", "amazon.com/dp/B000URXPKE",       "8.5ml Regular ($11) | Waterproof ($12) | Carbon Black ($11)","Pestanas cortas, ralas"),
    ("NYX Professional Makeup Wonder Stick",           "NYX",             "Maquillaje",         14.00, "ASIN: B01LYYM7DA", "amazon.com/dp/B01LYYM7DA",       "7.7g — 4 tonos ($14 c/u)",                                   "Definicion facial, contouring"),
    ("e.l.f. Poreless Putty Primer",                   "e.l.f.",          "Maquillaje",         10.00, "ASIN: B07FKWPRT7", "amazon.com/dp/B07FKWPRT7",       "21g Original ($10) | Matte ($10) | Luminous ($10)",          "Poros visibles, maquillaje duradero"),
    ("Charlotte Tilbury Hollywood Flawless Filter",    "Charlotte Tilbury","Maquillaje",         46.00, "ASIN: B07YP9XHQR", "amazon.com/dp/B07YP9XHQR",       "30ml ($46) | Mini 7.9ml ($26) — 8 tonos",                    "Base luminosa efecto natural"),
    ("NARS Radiant Creamy Concealer",                  "NARS",            "Maquillaje",         32.00, "ASIN: B00CM4Y29G", "amazon.com/dp/B00CM4Y29G",       "6ml — 30 tonos ($32)",                                       "Ojeras, imperfecciones"),
    ("Too Faced Better Than Sex Mascara",              "Too Faced",       "Maquillaje",         27.00, "ASIN: B00F7NRPOK", "amazon.com/dp/B00F7NRPOK",       "8ml ($27) | Travel 4ml ($14) | Waterproof ($27)",            "Pestanas voluminosas"),
    ("Urban Decay All Nighter Setting Spray",          "Urban Decay",     "Maquillaje",         33.00, "ASIN: B008JDHEPC", "amazon.com/dp/B008JDHEPC",       "30ml travel ($18) | 118ml ($33) | 240ml ($44)",              "Maquillaje duradero todo el dia"),
    # CUERPO
    ("Optimum Nutrition Gold Standard 100% Whey",      "Optimum Nutrition","Cuerpo",            58.00, "ASIN: B000QSNYGI", "amazon.com/dp/B000QSNYGI",       "908g/2lb ($58) | 2.27kg/5lb ($78) | 4.54kg/10lb ($140)",    "Masa muscular, recuperacion"),
    ("Bliss Fat Girl Slim Arm Candy Cream",            "Bliss",           "Cuerpo",             38.00, "ASIN: B008X80RWW", "amazon.com/dp/B008X80RWW",       "200ml — presentacion unica",                                 "Flacidez brazos, celulitis"),
    # VELLO
    ("Ulike Air 3 IPL Laser Hair Removal Device",      "Ulike",           "Vello",              219.00,"ASIN: B0BL9W6VKD", "amazon.com/dp/B0BL9W6VKD",       "Air 3 Azul/Blanco ($219) | Air+ ($299) | Air 10 ($329)",     "Vello facial y corporal"),
    ("Tend Skin The Skin Care Solution",               "Tend Skin",       "Vello",              24.00, "ASIN: B0010O3PEO", "amazon.com/dp/B0010O3PEO",       "118ml ($17) | 236ml ($24) | 473ml ($38)",                    "Vello encarnado, irritacion"),
    # SUDORACION
    ("Native Natural Deodorant",                       "Native",          "Sudoracion",         13.00, "ASIN: B01MCVXWAO", "amazon.com/dp/B01MCVXWAO",       "75g Regular ($13) | Sensitive ($14) | 3-pack ($35)",         "Mal olor, transpiracion"),
    ("Carpe Antiperspirant Hand Lotion",               "Carpe",           "Sudoracion",         14.95, "ASIN: B01FXNZ2H8", "amazon.com/dp/B01FXNZ2H8",       "40g Manos ($15) | Foot Lotion ($15) | Kit manos+pies ($28)", "Sudoracion excesiva manos/pies"),
    # MANOS Y UNAS
    ("OPI Nail Envy Original Nail Strengthener",       "OPI",             "Manos y Unas",       19.99, "ASIN: B00178579E", "amazon.com/dp/B00178579E",       "15ml Original ($20) | Double Nude-y | Sensitive | Matte",    "Unas fragiles, quebradizas"),
    ("L'Occitane Shea Butter Hand Cream",              "L'Occitane",      "Manos y Unas",       32.00, "ASIN: B000MWKFNQ", "amazon.com/dp/B000MWKFNQ",       "30ml ($16) | 75ml ($23) | 150ml ($32) | 300ml ($50)",        "Manos resecas, envejecidas"),
    ("Baby Foot Exfoliant Foot Peel Original",         "Baby Foot",       "Pies",               25.00, "ASIN: B002YL5E30", "amazon.com/dp/B002YL5E30",       "Original ($25) | Lavender ($26) | Moisture ($26)",           "Pies agrietados, callos"),
    # CUIDADO MASCULINO
    ("Beardbrand Gold Blend Beard Oil",                "Beardbrand",      "Cuidado Masculino",  25.00, "SKU: BB-GOLD-1OZ", "beardbrand.com",                  "30ml/1oz — 12 aromas ($25 c/u)",                             "Barba aspera, piel irritada"),
    ("Jack Black Pure Clean Daily Facial Cleanser",    "Jack Black",      "Cuidado Masculino",  24.00, "ASIN: B001AJATV2", "amazon.com/dp/B001AJATV2",       "88ml travel ($15) | 177ml ($24) | 500ml pump ($45)",         "Piel grasa, poros, acne masculino"),
    # MIRADA
    ("RapidLash Eyelash Enhancing Serum",              "RapidLash",       "Mirada",             49.99, "ASIN: B0013FXLJI", "amazon.com/dp/B0013FXLJI",       "3ml Lashes ($50) | 3ml RapidBrow ($50)",                     "Pestanas cortas, ralas"),
    # BIENESTAR
    ("HUM Nutrition Daily Cleanse Supplement",         "HUM Nutrition",   "Bienestar",          40.00, "SKU: HUM-DC-60",   "sephora.com / huminternational.com","60 capsulas/1 mes — presentacion unica",                   "Acne interno, piel opaca"),
    ("Leanbean Female Fat Burner",                     "Leanbean",        "Bienestar",          59.99, "SKU: LB-1MONTH",   "leanbean.com",                    "180 caps/1 mes ($60) | 3 meses bundle ($140)",               "Control de peso, metabolismo"),
    # SONRISA
    ("Crest 3D Whitestrips Professional Effects",      "Crest",           "Sonrisa",            49.99, "ASIN: B003AVEU4G", "amazon.com/dp/B003AVEU4G",       "20 strips/10 dias ($50) | Glamorous White ($35) | Supreme ($65)","Dientes amarillos, manchados"),
]

# ══════════════════════════════════════════════════════════════════
# CONSTRUIR TABLA
# ══════════════════════════════════════════════════════════════════
filas = []
for nombre, marca, cat, precio_usd, ref, url, presentaciones, problema in PRODUCTOS:
    # Costo unitario en COP = precio USD * TRM (ya incluye el producto puesto en Colombia)
    costo_cop = round(precio_usd * TRM)

    r = calcular(costo_cop)
    if r is None:
        continue

    filas.append({
        "Producto":               nombre,
        "Marca":                  marca,
        "Categoria":              cat,
        "Referencia / SKU":       ref,
        "🔗 Link Compra":         f"https://{url}",
        "Presentaciones":         presentaciones,
        "Costo Unitario COP":     f"${costo_cop:,}",
        "Flete COP":              f"${flete:,}",
        "Devoluciones COP":       f"${r['devoluciones']:,}",
        "CPA Publicidad COP":     f"${r['cpa_cop']:,}",
        "Gastos Operativos COP":  f"${gastos_op:,}",
        "💰 PRECIO VENTA COP":    f"${r['pv']:,}",
        "✅ Rentabilidad COP":    f"${r['rentabilidad']:,}",
        "Rentabilidad %":         f"{r['rent_pct']}%",
        "Problema que Ataca":     problema,
        # numericos
        "_pv":      r['pv'],
        "_rent":    r['rentabilidad'],
        "_rentpct": r['rent_pct'],
        "_costo":   costo_cop,
    })

DF = pd.DataFrame(filas)

# ══════════════════════════════════════════════════════════════════
# KPIs
# ══════════════════════════════════════════════════════════════════
k1, k2, k3, k4, k5 = st.columns(5)
with k1: st.metric("Total Productos",     len(DF))
with k2: st.metric("Precio Venta Min",    f"${DF['_pv'].min():,} COP")
with k3: st.metric("Precio Venta Max",    f"${DF['_pv'].max():,} COP")
with k4: st.metric("Rentabilidad Prom.",  f"${DF['_rent'].mean():,.0f} COP")
with k5: st.metric("Margen Prom.",        f"{DF['_rentpct'].mean():.1f}%")

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# BUSCADOR Y FILTRO
# ══════════════════════════════════════════════════════════════════
col_b, col_c = st.columns([3, 2])
with col_b:
    q = st.text_input("🔎 Buscar producto, marca o problema...",
                      placeholder="Ej: acne, olaplex, pestanas, collagen...")
with col_c:
    cats = ["Todas"] + sorted(DF["Categoria"].unique().tolist())
    cat_f = st.selectbox("Filtrar por categoria", cats)

df_show = DF.copy()
if q:
    ql = q.lower()
    df_show = df_show[
        df_show["Producto"].str.lower().str.contains(ql, na=False) |
        df_show["Marca"].str.lower().str.contains(ql, na=False) |
        df_show["Problema que Ataca"].str.lower().str.contains(ql, na=False) |
        df_show["Categoria"].str.lower().str.contains(ql, na=False)
    ]
if cat_f != "Todas":
    df_show = df_show[df_show["Categoria"] == cat_f]

st.caption(f"Mostrando {len(df_show)} de {len(DF)} productos · TRM utilizado: ${TRM:,} COP/USD")

# ══════════════════════════════════════════════════════════════════
# TABLA PRINCIPAL
# ══════════════════════════════════════════════════════════════════
cols_display = [
    "Producto", "Marca", "Categoria",
    "Referencia / SKU", "🔗 Link Compra", "Presentaciones",
    "Costo Unitario COP", "Flete COP", "Devoluciones COP",
    "CPA Publicidad COP", "Gastos Operativos COP",
    "💰 PRECIO VENTA COP", "✅ Rentabilidad COP", "Rentabilidad %",
    "Problema que Ataca",
]

st.dataframe(
    df_show[cols_display],
    use_container_width=True,
    hide_index=True,
    height=600,
    column_config={
        "Producto":              st.column_config.TextColumn("Producto",          width=200),
        "Marca":                 st.column_config.TextColumn("Marca",             width=120),
        "Categoria":             st.column_config.TextColumn("Categoria",         width=110),
        "Referencia / SKU":      st.column_config.TextColumn("Referencia/SKU",    width=170),
        "🔗 Link Compra":        st.column_config.LinkColumn("Link Compra",        width=160),
        "Presentaciones":        st.column_config.TextColumn("Presentaciones",    width=240),
        "Costo Unitario COP":    st.column_config.TextColumn("Costo Unitario",    width=120),
        "Flete COP":             st.column_config.TextColumn("Flete",             width=90),
        "Devoluciones COP":      st.column_config.TextColumn("Devoluciones",      width=110),
        "CPA Publicidad COP":    st.column_config.TextColumn("CPA Publicidad",    width=110),
        "Gastos Operativos COP": st.column_config.TextColumn("Gastos Op.",        width=100),
        "💰 PRECIO VENTA COP":   st.column_config.TextColumn("PRECIO VENTA",      width=140),
        "✅ Rentabilidad COP":   st.column_config.TextColumn("Rentabilidad COP",  width=140),
        "Rentabilidad %":        st.column_config.TextColumn("Rent. %",           width=80),
        "Problema que Ataca":    st.column_config.TextColumn("Problema",          width=200),
    }
)

# ── DESCARGA CSV ──────────────────────────────────────────────────
csv = df_show[cols_display].to_csv(index=False).encode("utf-8")
st.download_button(
    "📥 Descargar tabla completa (CSV)",
    csv, "rome_precios_colombia.csv", "text/csv"
)

# ── FORMULA DETALLADA ─────────────────────────────────────────────
with st.expander("📋 Formula de calculo (basada en tu tabla Colombia)"):
    st.markdown(f"""
| Concepto | Valor | Tipo |
|---|---|---|
| Costo unitario producto | Precio USD × ${TRM:,} TRM | Fijo por producto |
| Flete promedio | **${flete:,} COP** | Fijo por envio |
| % Devoluciones | **{dev_pct*100:.0f}%** sobre PV | Variable |
| Gastos Operativos | **${gastos_op:,} COP** | Fijo por unidad |
| CPA Publicidad | **{cpa_pct*100:.0f}%** sobre PV | Variable |
| **Rentabilidad minima** | **{rent_min*100:.0f}%** sobre PV | Objetivo |

```
PV = (Costo + Flete + Gastos Op.) / (1 - Dev% - CPA% - Rent%)
PV se redondea al proximo multiplo de $1,000
```
    """)

st.markdown(f"""
<div style="text-align:center;padding:20px 0;color:#A8D8F0;font-size:.78rem;">
  <span style="font-family:'Syne',sans-serif;font-size:1rem;color:#54A0FF;font-weight:700;">
    ESTUDIO DE MERCADO ROME</span><br>
  {len(DF)} productos · TRM ${TRM:,} · Rentabilidad minima {rent_min*100:.0f}%<br>
  <span style="opacity:.5;font-size:.7rem;">Precios referenciales. TRM y costos pueden variar.</span>
</div>
""", unsafe_allow_html=True)
