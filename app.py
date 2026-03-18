"""ESTUDIO DE MERCADO ROME — Referencias y Precios Colombia"""
import streamlit as st
import pandas as pd
import math

st.set_page_config(
    page_title="ROME Market — Precios Colombia",
    page_icon="🔵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500&display=swap');
.stApp { background: linear-gradient(135deg, #0A1628, #0D2137); }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: #DDE8F5; }
h1, h2, h3 { font-family: 'Syne', sans-serif; font-weight: 800; }
#MainMenu, footer, header { visibility: hidden; }
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #1A3A5CCC, #1E5FAD33) !important;
    border: 1px solid #54A0FF40 !important;
    border-radius: 12px !important;
    padding: 16px !important;
}
div[data-testid="metric-container"] label {
    color: #A8D8F0 !important;
    font-size: .8rem !important;
    text-transform: uppercase;
}
[data-testid="stMetricValue"] {
    color: #EEF6FF !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
}
.stDataFrame { border-radius: 12px !important; }
</style>
""", unsafe_allow_html=True)

# ── PARAMETROS ────────────────────────────────────────────────────
TRM    = 4200
ENVIO  = 8.50
ARANC  = 0.15
IVA    = 0.19
MARGEN = 0.35

def precio(p, envio=ENVIO, trm=TRM, aranc=ARANC, margen=MARGEN):
    costo     = p + envio
    ar        = costo * aranc
    base      = costo + ar
    iva_v     = base * IVA
    total_usd = round(base + iva_v, 2)
    total_cop = round(total_usd * trm)
    venta     = math.ceil((total_cop / (1 - margen)) / 1000) * 1000
    gan       = venta - total_cop
    mr        = round((venta - total_cop) / venta * 100, 1)
    return total_usd, total_cop, venta, gan, mr

# ── PRODUCTOS CON REFERENCIAS COMPLETAS ──────────────────────────
# (nombre, marca, cat, precio_usd, asin_o_sku, url, presentaciones, problema)
PRODUCTOS = [
    # ── PIEL ──────────────────────────────────────────────────────
    ("The Ordinary Niacinamide 10% + Zinc 1%",
     "The Ordinary", "Piel", 6.90,
     "ASIN: B07M9LX9DH",
     "amazon.com/dp/B07M9LX9DH",
     "30ml — presentacion unica",
     "Poros, manchas, acne"),

    ("Paula's Choice Skin Perfecting 2% BHA Liquid Exfoliant",
     "Paula's Choice", "Piel", 34.00,
     "ASIN: B00949CTQQ",
     "amazon.com/dp/B00949CTQQ",
     "118ml ($34) | 30ml travel ($12) | 950ml jumbo ($75)",
     "Poros, acne, opacidad"),

    ("SkinCeuticals C E Ferulic Serum",
     "SkinCeuticals", "Piel", 182.00,
     "ASIN: B000NZUQOY",
     "amazon.com/dp/B000NZUQOY",
     "30ml — presentacion unica",
     "Manchas, envejecimiento"),

    ("Differin Adapalene Gel 0.1%",
     "Differin", "Piel", 15.50,
     "ASIN: B07L1PHSY9",
     "amazon.com/dp/B07L1PHSY9",
     "45g ($15.50) | 15g ($12) | 2-pack ($28)",
     "Acne, cicatrices, arrugas"),

    ("CeraVe Moisturizing Cream",
     "CeraVe", "Piel", 19.00,
     "ASIN: B00TTD9BRC",
     "amazon.com/dp/B00TTD9BRC",
     "250ml ($19) | 453g ($25) | 544g ($28) | 1kg ($38)",
     "Sequedad, barrera cutanea"),

    ("Good Molecules Discoloration Correcting Serum",
     "Good Molecules", "Piel", 12.00,
     "SKU: 810065800078",
     "goodmolecules.com / ulta.com",
     "30ml — presentacion unica",
     "Hiperpigmentacion, manchas"),

    ("Sol de Janeiro Brazilian Bum Bum Cream",
     "Sol de Janeiro", "Piel", 48.00,
     "ASIN: B01N3D7DKB",
     "amazon.com/dp/B01N3D7DKB",
     "75ml ($26) | 240ml ($48) | 480ml ($72)",
     "Celulitis, flacidez"),

    ("Bio-Oil Skincare Oil",
     "Bio-Oil", "Piel", 14.00,
     "ASIN: B01MS3GFHK",
     "amazon.com/dp/B01MS3GFHK",
     "60ml ($10) | 125ml ($14) | 200ml ($18) | 250ml ($22)",
     "Estrias, cicatrices"),

    ("La Roche-Posay Effaclar Duo+",
     "La Roche-Posay", "Piel", 30.00,
     "ASIN: B014OPM4P4",
     "amazon.com/dp/B014OPM4P4",
     "40ml — presentacion unica",
     "Acne, poros, grasa"),

    ("EltaMD UV Clear Broad-Spectrum SPF 46",
     "EltaMD", "Piel", 39.00,
     "ASIN: B002MSN3QQ",
     "amazon.com/dp/B002MSN3QQ",
     "48g Untinted ($39) | 48g Tinted ($41)",
     "Dano solar, manchas"),

    ("Neutrogena Rapid Wrinkle Repair Eye Cream",
     "Neutrogena", "Piel", 22.00,
     "ASIN: B00BT7BYLY",
     "amazon.com/dp/B00BT7BYLY",
     "14g/0.5oz — presentacion unica",
     "Bolsas, ojeras, arrugas"),

    ("RoC Retinol Correxion Line Smoothing Cream",
     "RoC", "Piel", 25.99,
     "ASIN: B075H4FDMZ",
     "amazon.com/dp/B075H4FDMZ",
     "30ml ($26) | 48g Max Wrinkle ($30) | Eye cream ($22)",
     "Arrugas, lineas expresion"),

    ("Some By Mi AHA BHA PHA 30 Days Miracle Toner",
     "Some By Mi", "Piel", 22.00,
     "ASIN: B07C7FQG3Z",
     "amazon.com/dp/B07C7FQG3Z",
     "150ml ($22) | 300ml ($30)",
     "Poros, textura, manchas"),

    ("Drunk Elephant C-Firma Fresh Day Serum",
     "Drunk Elephant", "Piel", 90.00,
     "ASIN: B072J74N5K",
     "amazon.com/dp/B072J74N5K",
     "15ml mini ($50) | 30ml ($90)",
     "Opacidad, manchas"),

    ("GlamGlow Supermud Clearing Treatment",
     "GlamGlow", "Piel", 69.00,
     "ASIN: B00IFHPQDY",
     "amazon.com/dp/B00IFHPQDY",
     "34g ($55) | 50g ($69) | 100g ($109)",
     "Acne, poros, impurezas"),

    ("Herbivore Bakuchiol Retinol Alternative Face Oil",
     "Herbivore", "Piel", 54.00,
     "ASIN: B07YTTQKRS",
     "amazon.com/dp/B07YTTQKRS",
     "15ml ($34) | 30ml ($54)",
     "Arrugas, poros, firmeza"),

    # ── CABELLO ───────────────────────────────────────────────────
    ("Viviscal Extra Strength Hair Growth Supplement",
     "Viviscal", "Cabello", 49.99,
     "ASIN: B00BSZKETA",
     "amazon.com/dp/B00BSZKETA",
     "60 tabs/1 mes ($50) | 180 tabs/3 meses ($130)",
     "Caida del cabello, alopecia"),

    ("Minoxidil 5% Foam Kirkland Signature",
     "Kirkland", "Cabello", 29.00,
     "ASIN: B00GXYK4GO",
     "amazon.com/dp/B00GXYK4GO",
     "6x60ml/6 meses ($29) | 1 mes ($12)",
     "Calvicie, entradas"),

    ("Olaplex No.3 Hair Perfector",
     "Olaplex", "Cabello", 30.00,
     "ASIN: B013NQRZME",
     "amazon.com/dp/B013NQRZME",
     "100ml ($30) | 250ml ($52) | 1000ml salon ($130)",
     "Cabello quebradizo, danado"),

    ("Nizoral A-D Anti-Dandruff Shampoo 1%",
     "Nizoral", "Cabello", 15.00,
     "ASIN: B00AINMFAC",
     "amazon.com/dp/B00AINMFAC",
     "200ml ($15) | 400ml ($24) | 730ml ($35)",
     "Caspa, dermatitis seborreica"),

    ("Madison Reed Root Touch Up Kit",
     "Madison Reed", "Cabello", 26.00,
     "ASIN: B01MUAISNV",
     "amazon.com/dp/B01MUAISNV",
     "Kit ($26) — 13 tonos disponibles",
     "Canas prematuras"),

    # ── ENVEJECIMIENTO ────────────────────────────────────────────
    ("Vital Proteins Collagen Peptides Powder",
     "Vital Proteins", "Envejecimiento", 43.00,
     "ASIN: B00K6EM5CK",
     "amazon.com/dp/B00K6EM5CK",
     "283g ($43) | 567g ($68) | sachets x20 ($25)",
     "Arrugas, cabello, unas"),

    ("StriVectin TL Advanced Tightening Neck Cream Plus",
     "StriVectin", "Envejecimiento", 89.00,
     "ASIN: B07BFKZP7W",
     "amazon.com/dp/B07BFKZP7W",
     "30ml ($65) | 50ml ($89)",
     "Flacidez cuello, escote"),

    ("Murad Rapid Age Spot and Pigment Lightening Serum",
     "Murad", "Envejecimiento", 86.00,
     "ASIN: B001447XCK",
     "amazon.com/dp/B001447XCK",
     "30ml — presentacion unica",
     "Manchas edad, hiperpigmentacion"),

    # ── MAQUILLAJE ────────────────────────────────────────────────
    ("Fenty Beauty Pro Filt'r Soft Matte Longwear Foundation",
     "Fenty Beauty", "Maquillaje", 40.00,
     "SKU: varies by shade — 50 tonos",
     "fentybeauty.com / sephora.com",
     "32ml — 50 tonos ($40 c/u)",
     "Tono desigual, manchas"),

    ("Charlotte Tilbury Lip Cheat Pillow Talk Lip Liner",
     "Charlotte Tilbury", "Maquillaje", 28.00,
     "ASIN: B06WVFQXF4",
     "amazon.com/dp/B06WVFQXF4",
     "1.2g — 8 tonos disponibles ($28)",
     "Labios finos, sin definicion"),

    ("Benefit Cosmetics Gimme Brow+ Volumizing Eyebrow Gel",
     "Benefit", "Maquillaje", 24.00,
     "ASIN: B0774YDJ5H",
     "amazon.com/dp/B0774YDJ5H",
     "3g full ($24) | 1.5g mini ($16) — 12 tonos",
     "Cejas escasas, ralas"),

    ("L'Oreal Paris Voluminous Original Mascara",
     "L'Oreal", "Maquillaje", 10.99,
     "ASIN: B000URXPKE",
     "amazon.com/dp/B000URXPKE",
     "8.5ml Regular ($11) | Waterproof ($12) | Carbon Black ($11)",
     "Pestanas cortas, ralas"),

    ("NYX Professional Makeup Wonder Stick Highlight & Contour",
     "NYX", "Maquillaje", 14.00,
     "ASIN: B01LYYM7DA",
     "amazon.com/dp/B01LYYM7DA",
     "7.7g — 4 tonos ($14 c/u)",
     "Definicion facial, contouring"),

    ("e.l.f. Poreless Putty Primer",
     "e.l.f.", "Maquillaje", 10.00,
     "ASIN: B07FKWPRT7",
     "amazon.com/dp/B07FKWPRT7",
     "21g Original ($10) | Matte ($10) | Luminous ($10)",
     "Poros visibles, maquillaje duradero"),

    ("Charlotte Tilbury Hollywood Flawless Filter",
     "Charlotte Tilbury", "Maquillaje", 46.00,
     "ASIN: B07YP9XHQR",
     "amazon.com/dp/B07YP9XHQR",
     "30ml ($46) | Mini 7.9ml ($26) — 8 tonos",
     "Base luminosa efecto natural"),

    ("NARS Radiant Creamy Concealer",
     "NARS", "Maquillaje", 32.00,
     "ASIN: B00CM4Y29G",
     "amazon.com/dp/B00CM4Y29G",
     "6ml — 30 tonos ($32)",
     "Ojeras, imperfecciones"),

    ("Too Faced Better Than Sex Mascara",
     "Too Faced", "Maquillaje", 27.00,
     "ASIN: B00F7NRPOK",
     "amazon.com/dp/B00F7NRPOK",
     "8ml ($27) | Travel 4ml ($14) | Waterproof ($27)",
     "Pestanas voluminosas"),

    ("Urban Decay All Nighter Long-Lasting Makeup Setting Spray",
     "Urban Decay", "Maquillaje", 33.00,
     "ASIN: B008JDHEPC",
     "amazon.com/dp/B008JDHEPC",
     "30ml travel ($18) | 118ml ($33) | 240ml ($44)",
     "Maquillaje duradero todo el dia"),

    # ── CUERPO ────────────────────────────────────────────────────
    ("Optimum Nutrition Gold Standard 100% Whey Protein",
     "Optimum Nutrition", "Cuerpo", 58.00,
     "ASIN: B000QSNYGI",
     "amazon.com/dp/B000QSNYGI",
     "908g/2lb ($58) | 2.27kg/5lb ($78) | 4.54kg/10lb ($140)",
     "Masa muscular, recuperacion"),

    ("Bliss Spa Fat Girl Slim Arm Candy Cream",
     "Bliss", "Cuerpo", 38.00,
     "ASIN: B008X80RWW",
     "amazon.com/dp/B008X80RWW",
     "200ml — presentacion unica",
     "Flacidez brazos, celulitis"),

    # ── VELLO ─────────────────────────────────────────────────────
    ("Ulike Air 3 IPL Laser Hair Removal Device",
     "Ulike", "Vello", 219.00,
     "ASIN: B0BL9W6VKD",
     "amazon.com/dp/B0BL9W6VKD",
     "Air 3 Azul ($219) | Air 3 Blanco ($219) | Air+ ($299) | Air 10 ($329)",
     "Vello facial y corporal"),

    ("Tend Skin The Skin Care Solution",
     "Tend Skin", "Vello", 24.00,
     "ASIN: B0010O3PEO",
     "amazon.com/dp/B0010O3PEO",
     "118ml ($17) | 236ml ($24) | 473ml ($38)",
     "Vello encarnado, irritacion"),

    # ── SUDORACION ────────────────────────────────────────────────
    ("Native Natural Deodorant",
     "Native", "Sudoracion", 13.00,
     "ASIN: B01MCVXWAO",
     "amazon.com/dp/B01MCVXWAO",
     "75g Regular ($13) | Sensitive ($14) | Charcoal ($14) | 3-pack ($35)",
     "Mal olor, transpiracion"),

    ("Carpe Antiperspirant Hand Lotion",
     "Carpe", "Sudoracion", 14.95,
     "ASIN: B01FXNZ2H8",
     "amazon.com/dp/B01FXNZ2H8",
     "40g Manos ($15) | Kit manos+pies ($28) | Foot Lotion ($15)",
     "Sudoracion excesiva manos/pies"),

    # ── MANOS Y UNAS ──────────────────────────────────────────────
    ("OPI Nail Envy Original Nail Strengthener",
     "OPI", "Manos y Unas", 19.99,
     "ASIN: B00178579E",
     "amazon.com/dp/B00178579E",
     "15ml Original ($20) | Double Nude-y ($20) | Sensitive & Peeling ($20) | Matte ($20)",
     "Unas fragiles, quebradizas"),

    ("L'Occitane Shea Butter Hand Cream",
     "L'Occitane", "Manos y Unas", 32.00,
     "ASIN: B000MWKFNQ",
     "amazon.com/dp/B000MWKFNQ",
     "30ml ($16) | 75ml ($23) | 150ml ($32) | 300ml ($50)",
     "Manos resecas, envejecidas"),

    # ── PIES ──────────────────────────────────────────────────────
    ("Baby Foot Exfoliant Foot Peel Original",
     "Baby Foot", "Pies", 25.00,
     "ASIN: B002YL5E30",
     "amazon.com/dp/B002YL5E30",
     "Original 35ml ($25) | Lavender ($26) | Moisture ($26)",
     "Pies agrietados, callos, durezas"),

    # ── CUIDADO MASCULINO ─────────────────────────────────────────
    ("Beardbrand Gold Blend Beard Oil",
     "Beardbrand", "Cuidado Masculino", 25.00,
     "SKU: BB-GOLD-1OZ",
     "beardbrand.com / amazon.com",
     "30ml/1oz — 12 aromas disponibles ($25)",
     "Barba aspera, piel irritada"),

    ("Jack Black Pure Clean Daily Facial Cleanser",
     "Jack Black", "Cuidado Masculino", 24.00,
     "ASIN: B001AJATV2",
     "amazon.com/dp/B001AJATV2",
     "88ml travel ($15) | 177ml ($24) | 500ml pump ($45)",
     "Piel grasa, poros, acne"),

    # ── MIRADA ────────────────────────────────────────────────────
    ("RapidLash Eyelash Enhancing Serum",
     "RapidLash", "Mirada", 49.99,
     "ASIN: B0013FXLJI",
     "amazon.com/dp/B0013FXLJI",
     "3ml Lashes ($50) | 3ml RapidBrow ($50)",
     "Pestanas cortas, ralas"),

    # ── BIENESTAR ─────────────────────────────────────────────────
    ("HUM Nutrition Daily Cleanse Supplement",
     "HUM Nutrition", "Bienestar", 40.00,
     "SKU: HUM-DAILYCLEANSE-60",
     "sephora.com / huminternational.com",
     "60 capsulas/1 mes — presentacion unica",
     "Acne interno, piel opaca"),

    ("Leanbean Female Fat Burner",
     "Leanbean", "Bienestar", 59.99,
     "SKU: LB-1MONTH-180",
     "leanbean.com",
     "180 caps/1 mes ($60) | 3 meses bundle ($140)",
     "Control de peso, metabolismo"),

    # ── SONRISA ───────────────────────────────────────────────────
    ("Crest 3D Whitestrips Professional Effects",
     "Crest", "Sonrisa", 49.99,
     "ASIN: B003AVEU4G",
     "amazon.com/dp/B003AVEU4G",
     "20 strips/10 dias ($50) | Glamorous White ($35) | Supreme Bright ($65)",
     "Dientes amarillos, manchados"),
]

# ── CONSTRUIR DATAFRAME ───────────────────────────────────────────
filas = []
for nombre, marca, cat, p_prov, ref, url, presentaciones, problema in PRODUCTOS:
    t_usd, t_cop, venta, gan, mr = precio(p_prov)
    filas.append({
        "Producto":            nombre,
        "Marca":               marca,
        "Categoria":           cat,
        "Referencia / SKU":    ref,
        "Donde Comprar":       url,
        "Presentaciones":      presentaciones,
        "Precio Proveedor USD": f"${p_prov:.2f}",
        "Costo Total USD":     f"${t_usd:.2f}",
        "Costo Total COP":     f"${t_cop:,}",
        "PRECIO VENTA COP":    f"${venta:,}",
        "Ganancia x Unidad":   f"${gan:,}",
        "Margen %":            f"{mr}%",
        "Problema que Ataca":  problema,
        "_venta": venta,
        "_margen": mr,
        "_prov": p_prov,
        "_gan": gan,
    })

DF = pd.DataFrame(filas)

# ── HEADER ────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:24px 0 8px;">
  <h1 style="margin:0;font-size:2rem;background:linear-gradient(90deg,#EEF6FF,#54A0FF);
     -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
     🔬 ESTUDIO DE MERCADO ROME
  </h1>
  <p style="margin:4px 0 0;color:#A8D8F0;font-size:.9rem;">
     Referencias exactas · Precios de venta Colombia · Margen minimo 35%
  </p>
</div>
<hr style="border-color:#1E5FAD30;margin:10px 0 20px;">
""", unsafe_allow_html=True)

# ── PARAMETROS AJUSTABLES ─────────────────────────────────────────
st.markdown("**⚙️ Parametros del calculo**")
pc1, pc2, pc3, pc4 = st.columns(4)
with pc1:
    trm_v = st.number_input("TRM COP/USD", value=4200, step=50)
with pc2:
    env_v = st.number_input("Envio promedio (USD)", value=8.50, step=0.50)
with pc3:
    aran_v = st.number_input("Arancel %", value=15.0, step=1.0) / 100
with pc4:
    marg_v = st.number_input("Margen minimo %", value=35.0, step=5.0) / 100

# Recalcular si cambian los parametros
if any([trm_v != TRM, env_v != ENVIO, aran_v != ARANC, marg_v != MARGEN]):
    filas2 = []
    for nombre, marca, cat, p_prov, ref, url, presentaciones, problema in PRODUCTOS:
        t_usd, t_cop, venta, gan, mr = precio(p_prov, envio=env_v, trm=trm_v, aranc=aran_v, margen=marg_v)
        filas2.append({
            "Producto":            nombre,
            "Marca":               marca,
            "Categoria":           cat,
            "Referencia / SKU":    ref,
            "Donde Comprar":       url,
            "Presentaciones":      presentaciones,
            "Precio Proveedor USD": f"${p_prov:.2f}",
            "Costo Total USD":     f"${t_usd:.2f}",
            "Costo Total COP":     f"${t_cop:,}",
            "PRECIO VENTA COP":    f"${venta:,}",
            "Ganancia x Unidad":   f"${gan:,}",
            "Margen %":            f"{mr}%",
            "Problema que Ataca":  problema,
            "_venta": venta, "_margen": mr, "_prov": p_prov, "_gan": gan,
        })
    DF = pd.DataFrame(filas2)

st.markdown("<br>", unsafe_allow_html=True)

# ── KPIs ─────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
with k1: st.metric("Total Productos", len(DF))
with k2: st.metric("Precio Venta Min", f"${DF['_venta'].min():,} COP")
with k3: st.metric("Precio Venta Max", f"${DF['_venta'].max():,} COP")
with k4: st.metric("Ganancia Prom.", f"${DF['_gan'].mean():,.0f} COP")
with k5: st.metric("Margen Promedio", f"{DF['_margen'].mean():.1f}%")

st.markdown("<br>", unsafe_allow_html=True)

# ── BUSCADOR ─────────────────────────────────────────────────────
col1, col2 = st.columns([3, 2])
with col1:
    q = st.text_input("🔎 Buscar producto, marca, problema...",
                      placeholder="Ej: acne, olaplex, pestanas, collagen...")
with col2:
    cats = ["Todas"] + sorted(DF["Categoria"].unique().tolist())
    cat_f = st.selectbox("Filtrar por categoria", cats)

df_show = DF.copy()
if q:
    qlow = q.lower()
    df_show = df_show[
        df_show["Producto"].str.lower().str.contains(qlow, na=False) |
        df_show["Marca"].str.lower().str.contains(qlow, na=False) |
        df_show["Problema que Ataca"].str.lower().str.contains(qlow, na=False) |
        df_show["Categoria"].str.lower().str.contains(qlow, na=False)
    ]
if cat_f != "Todas":
    df_show = df_show[df_show["Categoria"] == cat_f]

st.caption(f"Mostrando {len(df_show)} de {len(DF)} productos")

# ── TABLA ─────────────────────────────────────────────────────────
cols = [
    "Producto", "Marca", "Categoria",
    "Referencia / SKU", "Donde Comprar", "Presentaciones",
    "Precio Proveedor USD", "Costo Total USD", "Costo Total COP",
    "PRECIO VENTA COP", "Ganancia x Unidad", "Margen %",
    "Problema que Ataca"
]

st.dataframe(
    df_show[cols],
    use_container_width=True,
    hide_index=True,
    height=620,
    column_config={
        "Producto":            st.column_config.TextColumn("Producto",            width=200),
        "Marca":               st.column_config.TextColumn("Marca",               width=120),
        "Categoria":           st.column_config.TextColumn("Categoria",           width=120),
        "Referencia / SKU":    st.column_config.TextColumn("Referencia / SKU",    width=180),
        "Donde Comprar":       st.column_config.LinkColumn("Donde Comprar",       width=180),
        "Presentaciones":      st.column_config.TextColumn("Presentaciones",      width=250),
        "Precio Proveedor USD":st.column_config.TextColumn("Precio Proveedor",    width=110),
        "Costo Total USD":     st.column_config.TextColumn("Costo Total USD",     width=110),
        "Costo Total COP":     st.column_config.TextColumn("Costo Total COP",     width=120),
        "PRECIO VENTA COP":    st.column_config.TextColumn("PRECIO VENTA COP",    width=140),
        "Ganancia x Unidad":   st.column_config.TextColumn("Ganancia x Unidad",   width=130),
        "Margen %":            st.column_config.TextColumn("Margen %",            width=80),
        "Problema que Ataca":  st.column_config.TextColumn("Problema",            width=200),
    }
)

# ── DESCARGA ─────────────────────────────────────────────────────
csv = df_show[cols].to_csv(index=False).encode("utf-8")
st.download_button(
    "📥 Descargar tabla completa en CSV",
    csv, "rome_referencias_colombia.csv", "text/csv"
)

# ── METODOLOGIA ───────────────────────────────────────────────────
with st.expander("📋 Como se calculan los precios"):
    st.markdown(f"""
```
Costo base (USD)  = Precio proveedor + Envio ({env_v:.2f} USD)
Arancel           = Costo base x {aran_v*100:.0f}%
IVA               = (Costo base + Arancel) x 19%
Costo total USD   = Costo base + Arancel + IVA
Costo total COP   = Costo total USD x TRM ({trm_v:,})
Precio venta COP  = Costo total COP / (1 - {marg_v*100:.0f}%)
                    Redondeado al proximo $1,000
```
- **Envio**: estimado DHL/FedEx paquete pequeno/mediano
- **Arancel**: promedio cosmeticos Colombia segun DIAN  
- **IVA**: 19% estandar Colombia
- **Margen**: calculado sobre precio de venta final
    """)

st.markdown(f"""
<div style="text-align:center;padding:20px 0;color:#A8D8F0;font-size:.78rem;">
  <span style="font-family:'Syne',sans-serif;font-size:1rem;color:#54A0FF;font-weight:700;">
    ESTUDIO DE MERCADO ROME</span><br>
  {len(DF)} productos · TRM ${trm_v:,} · Margen minimo {marg_v*100:.0f}% · Referencias verificadas<br>
  <span style="opacity:.5;font-size:.7rem;">
    Verificar ASIN en amazon.com. Precios pueden variar. Confirmar aranceles exactos en DIAN.
  </span>
</div>
""", unsafe_allow_html=True)
