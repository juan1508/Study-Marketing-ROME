"""ROME Market — Modelo de Precio Competitivo Colombia"""
import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="ROME — Precio Competitivo", page_icon="🔵",
                   layout="wide", initial_sidebar_state="collapsed")

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
div[data-testid="metric-container"] label{color:#A8D8F0!important;font-size:.75rem!important;text-transform:uppercase;letter-spacing:.05em;}
[data-testid="stMetricValue"]{color:#EEF6FF!important;font-family:'Syne',sans-serif!important;font-weight:800!important;font-size:1.3rem!important;}
.stDataFrame thead th{background:#1A3A5C!important;}
</style>""", unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────────
st.markdown("""
<h1 style="margin:20px 0 4px;font-size:1.9rem;
  background:linear-gradient(90deg,#EEF6FF,#54A0FF);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
  🔬 ROME — Modelo de Precio Competitivo Colombia
</h1>
<p style="margin:0 0 4px;color:#A8D8F0;font-size:.88rem;">
  Ingresa tu costo real → el modelo calcula el precio óptimo para ser competitivo y rentable
</p>
<hr style="border-color:#1E5FAD30;margin:12px 0 20px;">
""", unsafe_allow_html=True)

# ── COMO FUNCIONA ─────────────────────────────────────────────────
with st.expander("📖 Cómo funciona el modelo", expanded=False):
    st.markdown("""
**El modelo usa 3 estrategias de precio y te muestra la rentabilidad de cada una:**

| Estrategia | Descripción | Cuando usarla |
|---|---|---|
| 🥇 **Precio Ganador** | 5–10% por debajo del mercado | Para entrar al mercado y ganar volumen |
| 🥈 **Precio Mercado** | Igual al promedio de competidores | Para competir en condiciones normales |
| 🥉 **Precio Premium** | 5–10% por encima del mercado | Si tienes diferenciación o envío más rápido |

**La columna clave es "Rentabilidad %"** — si es positiva, el negocio funciona.
Si es negativa, necesitas bajar tu costo de adquisición o no es un producto viable.

**Costo real** = lo que tú pagas para tener el producto en tus manos listo para vender.
    """)

# ── PARAMETROS OPERATIVOS ─────────────────────────────────────────
st.markdown("#### ⚙️ Parámetros de operación (aplican a todos los productos)")
c1,c2,c3,c4 = st.columns(4)
with c1: flete   = st.number_input("🚚 Flete envío al cliente (COP)", value=18000, step=1000)
with c2: dev_pct = st.number_input("↩️ % Devoluciones",               value=20.0,  step=1.0) / 100
with c3: cpa_pct = st.number_input("📢 % CPA Publicidad",              value=15.0,  step=1.0) / 100
with c4: gastos  = st.number_input("🏢 Gastos fijos por unidad (COP)", value=0,     step=1000,
                                    help="Plataforma, empaque, empleados por unidad")

st.markdown("<br>", unsafe_allow_html=True)

# ── FUNCION MODELO ────────────────────────────────────────────────
def modelo(costo_real, pv_mercado):
    """
    Dado el costo real y el precio de mercado, calcula 3 estrategias.
    costo_real: lo que pagas TÚ para tener el producto (COP)
    pv_mercado: precio promedio actual en Colombia
    """
    def calcular_rent(pv):
        devs = round(pv * dev_pct)
        cpa  = round(pv * cpa_pct)
        rent = pv - costo_real - flete - gastos - devs - cpa
        pct  = round(rent / pv * 100, 1) if pv > 0 else 0
        return rent, pct, devs, cpa

    # Estrategia 1: Precio ganador (5% bajo mercado, redondeado)
    pv1 = max(math.floor(pv_mercado * 0.95 / 1000) * 1000, 1000)
    r1, p1, d1, c1_ = calcular_rent(pv1)

    # Estrategia 2: Precio mercado
    pv2 = pv_mercado
    r2, p2, d2, c2_ = calcular_rent(pv2)

    # Estrategia 3: Precio premium (10% sobre mercado)
    pv3 = math.ceil(pv_mercado * 1.10 / 1000) * 1000
    r3, p3, d3, c3_ = calcular_rent(pv3)

    # Precio sugerido = el que maximiza rentabilidad siendo viable (>0%)
    opciones = [(p1,pv1,"Ganador -5%"),(p2,pv2,"Mercado"),(p3,pv3,"Premium +10%")]
    viables  = [(p,pv,n) for p,pv,n in opciones if p > 0]
    if viables:
        mejor_pct, mejor_pv, mejor_nom = max(viables, key=lambda x: x[0])
    else:
        mejor_pct, mejor_pv, mejor_nom = p2, pv2, "Mercado"

    # Punto de equilibrio: PV mínimo para no perder
    pct_var = dev_pct + cpa_pct
    if pct_var < 1:
        pe = math.ceil((costo_real + flete + gastos) / (1 - pct_var) / 1000) * 1000
    else:
        pe = None

    return {
        "pv1":pv1,"r1":r1,"p1":p1,
        "pv2":pv2,"r2":r2,"p2":p2,
        "pv3":pv3,"r3":r3,"p3":p3,
        "mejor_pv":mejor_pv,"mejor_pct":mejor_pct,"mejor_nom":mejor_nom,
        "pe":pe,
        "devs2":d2,"cpa2":c2_,
    }

# ── BASE DE PRODUCTOS ─────────────────────────────────────────────
# (nombre, marca, cat, pv_mercado_colombia, ref, url, presentaciones, problema)
# COSTO REAL: lo ingresa el usuario en la tabla editable abajo
# pv_mercado = precio promedio verificado en Colombia (ML, Falabella, tiendas)

PRODUCTOS_BASE = [
    # nombre, marca, cat, pv_mkt_co, ref, url, presentaciones, problema
    ("The Ordinary Niacinamide 10% + Zinc 1%","The Ordinary","Piel",
     69900,"ASIN: B07M9LX9DH","https://amazon.com/dp/B07M9LX9DH",
     "30ml — unica presentacion","Poros, manchas, acne"),

    ("Paula's Choice BHA 2% Liquid Exfoliant","Paula's Choice","Piel",
     210000,"ASIN: B00949CTQQ","https://amazon.com/dp/B00949CTQQ",
     "30ml ($12) | 118ml ($34) | 950ml ($75)","Poros, acne, opacidad"),

    ("SkinCeuticals C E Ferulic Serum","SkinCeuticals","Piel",
     980000,"ASIN: B000NZUQOY","https://amazon.com/dp/B000NZUQOY",
     "30ml — unica presentacion","Manchas, envejecimiento"),

    ("Differin Adapalene Gel 0.1%","Differin","Piel",
     89000,"ASIN: B07L1PHSY9","https://amazon.com/dp/B07L1PHSY9",
     "15g ($12) | 45g ($15.50) | 2-pack ($28)","Acne, cicatrices, arrugas"),

    ("CeraVe Moisturizing Cream 250ml","CeraVe","Piel",
     109500,"ASIN: B00TTD9BRC","https://amazon.com/dp/B00TTD9BRC",
     "250ml ($19) | 453g ($25) | 544g ($28) | 1kg ($38)","Sequedad, barrera cutanea"),

    ("Good Molecules Discoloration Serum","Good Molecules","Piel",
     85000,"SKU: 810065800078","https://goodmolecules.com",
     "30ml — unica presentacion","Hiperpigmentacion, manchas"),

    ("Sol de Janeiro Bum Bum Cream 240ml","Sol de Janeiro","Piel",
     320000,"ASIN: B01N3D7DKB","https://amazon.com/dp/B01N3D7DKB",
     "75ml ($26) | 240ml ($48) | 480ml ($72)","Celulitis, flacidez"),

    ("Bio-Oil Skincare Oil 125ml","Bio-Oil","Piel",
     79900,"ASIN: B01MS3GFHK","https://amazon.com/dp/B01MS3GFHK",
     "60ml ($10) | 125ml ($14) | 200ml ($18) | 250ml ($22)","Estrias, cicatrices"),

    ("La Roche-Posay Effaclar Duo+","La Roche-Posay","Piel",
     145000,"ASIN: B014OPM4P4","https://amazon.com/dp/B014OPM4P4",
     "40ml — unica presentacion","Acne, poros, grasa"),

    ("EltaMD UV Clear SPF 46","EltaMD","Piel",
     220000,"ASIN: B002MSN3QQ","https://amazon.com/dp/B002MSN3QQ",
     "48g Untinted ($39) | 48g Tinted ($41)","Dano solar, manchas"),

    ("Neutrogena Rapid Wrinkle Repair Eye Cream","Neutrogena","Piel",
     95000,"ASIN: B00BT7BYLO","https://amazon.com/dp/B00BT7BYLO",
     "14g — unica presentacion","Bolsas, ojeras, arrugas"),

    ("RoC Retinol Correxion Line Smoothing Cream","RoC","Piel",
     130000,"ASIN: B075H4FDMZ","https://amazon.com/dp/B075H4FDMZ",
     "30ml ($26) | 48g Max Wrinkle ($30)","Arrugas, lineas expresion"),

    ("Some By Mi AHA BHA PHA 30 Days Toner","Some By Mi","Piel",
     120000,"ASIN: B07C7FQG3Z","https://amazon.com/dp/B07C7FQG3Z",
     "150ml ($22) | 300ml ($30)","Poros, textura, manchas"),

    ("Drunk Elephant C-Firma Serum 30ml","Drunk Elephant","Piel",
     520000,"ASIN: B072J74N5K","https://amazon.com/dp/B072J74N5K",
     "15ml ($50) | 30ml ($90)","Opacidad, manchas"),

    ("GlamGlow Supermud Clearing Treatment 50g","GlamGlow","Piel",
     380000,"ASIN: B00IFHPQDY","https://amazon.com/dp/B00IFHPQDY",
     "34g ($55) | 50g ($69) | 100g ($109)","Acne, poros, impurezas"),

    ("Herbivore Bakuchiol Retinol Alternative Oil","Herbivore","Piel",
     300000,"ASIN: B07YTTQKRS","https://amazon.com/dp/B07YTTQKRS",
     "15ml ($34) | 30ml ($54)","Arrugas, poros, firmeza"),

    ("Viviscal Extra Strength Hair Growth 60 tabs","Viviscal","Cabello",
     280000,"ASIN: B00BSZKETA","https://amazon.com/dp/B00BSZKETA",
     "60 tabs 1 mes ($50) | 180 tabs 3 meses ($130)","Caida, alopecia"),

    ("Minoxidil 5% Kirkland Foam supply 6 meses","Kirkland","Cabello",
     160000,"ASIN: B00GXYK4GO","https://amazon.com/dp/B00GXYK4GO",
     "6x60ml 6 meses ($29) | 1 mes ($12)","Calvicie, entradas"),

    ("Olaplex No.3 Hair Perfector 100ml","Olaplex","Cabello",
     150000,"ASIN: B013NQRZME","https://amazon.com/dp/B013NQRZME",
     "100ml ($30) | 250ml ($52) | 1000ml salon ($130)","Cabello quebradizo"),

    ("Nizoral Anti-Dandruff Shampoo 200ml","Nizoral","Cabello",
     79000,"ASIN: B00AINMFAC","https://amazon.com/dp/B00AINMFAC",
     "200ml ($15) | 400ml ($24) | 730ml ($35)","Caspa, dermatitis"),

    ("Madison Reed Root Touch Up Kit","Madison Reed","Cabello",
     148000,"ASIN: B01MUAISNV","https://amazon.com/dp/B01MUAISNV",
     "Kit — 13 tonos ($26 c/u)","Canas prematuras"),

    ("Vital Proteins Collagen Peptides 283g","Vital Proteins","Envejecimiento",
     220000,"ASIN: B00K6EM5CK","https://amazon.com/dp/B00K6EM5CK",
     "283g ($43) | 567g ($68) | sachets x20 ($25)","Arrugas, cabello, unas"),

    ("StriVectin TL Tightening Neck Cream 50ml","StriVectin","Envejecimiento",
     490000,"ASIN: B07BFKZP7W","https://amazon.com/dp/B07BFKZP7W",
     "30ml ($65) | 50ml ($89)","Flacidez cuello y escote"),

    ("Murad Rapid Age Spot Lightening Serum 30ml","Murad","Envejecimiento",
     470000,"ASIN: B001447XCK","https://amazon.com/dp/B001447XCK",
     "30ml — unica presentacion","Manchas edad"),

    ("Fenty Beauty Pro Filt'r Foundation","Fenty Beauty","Maquillaje",
     230000,"SKU: varies by shade","https://fentybeauty.com",
     "32ml — 50 tonos ($40 c/u)","Tono desigual, manchas"),

    ("Charlotte Tilbury Pillow Talk Lip Liner","Charlotte Tilbury","Maquillaje",
     165000,"ASIN: B06WVFQXF4","https://amazon.com/dp/B06WVFQXF4",
     "1.2g — 8 tonos ($28 c/u)","Labios finos"),

    ("Benefit Gimme Brow+ Volumizing Gel","Benefit","Maquillaje",
     145000,"ASIN: B0774YDJ5H","https://amazon.com/dp/B0774YDJ5H",
     "3g full ($24) | 1.5g mini ($16) — 12 tonos","Cejas escasas"),

    ("L'Oreal Paris Voluminous Original Mascara","L'Oreal","Maquillaje",
     55000,"ASIN: B000URXPKE","https://amazon.com/dp/B000URXPKE",
     "8.5ml Regular ($11) | Waterproof ($12)","Pestanas cortas"),

    ("NYX Professional Makeup Wonder Stick","NYX","Maquillaje",
     72000,"ASIN: B01LYYM7DA","https://amazon.com/dp/B01LYYM7DA",
     "7.7g — 4 tonos ($14 c/u)","Definicion facial"),

    ("e.l.f. Poreless Putty Primer 21g","e.l.f.","Maquillaje",
     60000,"ASIN: B07FKWPRT7","https://amazon.com/dp/B07FKWPRT7",
     "21g Original/Matte/Luminous ($10 c/u)","Poros visibles"),

    ("Charlotte Tilbury Hollywood Flawless Filter 30ml","Charlotte Tilbury","Maquillaje",
     260000,"ASIN: B07YP9XHQR","https://amazon.com/dp/B07YP9XHQR",
     "30ml ($46) | Mini 7.9ml ($26) — 8 tonos","Base luminosa natural"),

    ("NARS Radiant Creamy Concealer 6ml","NARS","Maquillaje",
     175000,"ASIN: B00CM4Y29G","https://amazon.com/dp/B00CM4Y29G",
     "6ml — 30 tonos ($32)","Ojeras, imperfecciones"),

    ("Too Faced Better Than Sex Mascara 8ml","Too Faced","Maquillaje",
     155000,"ASIN: B00F7NRPOK","https://amazon.com/dp/B00F7NRPOK",
     "8ml ($27) | Travel 4ml ($14) | Waterproof ($27)","Pestanas voluminosas"),

    ("Urban Decay All Nighter Setting Spray 118ml","Urban Decay","Maquillaje",
     185000,"ASIN: B008JDHEPC","https://amazon.com/dp/B008JDHEPC",
     "30ml ($18) | 118ml ($33) | 240ml ($44)","Maquillaje duradero"),

    ("Optimum Nutrition Gold Standard Whey 908g","Optimum Nutrition","Cuerpo",
     320000,"ASIN: B000QSNYGI","https://amazon.com/dp/B000QSNYGI",
     "908g 2lb ($58) | 2.27kg 5lb ($78) | 4.54kg 10lb ($140)","Masa muscular"),

    ("Bliss Fat Girl Slim Arm Candy Cream 200ml","Bliss","Cuerpo",
     210000,"ASIN: B008X80RWW","https://amazon.com/dp/B008X80RWW",
     "200ml — unica presentacion","Flacidez brazos, celulitis"),

    ("Ulike Air 3 IPL Laser Hair Removal Device","Ulike","Vello",
     1200000,"ASIN: B0BL9W6VKD","https://amazon.com/dp/B0BL9W6VKD",
     "Air 3 ($219) | Air+ ($299) | Air 10 ($329)","Vello facial y corporal"),

    ("Tend Skin Solution 236ml","Tend Skin","Vello",
     130000,"ASIN: B0010O3PEO","https://amazon.com/dp/B0010O3PEO",
     "118ml ($17) | 236ml ($24) | 473ml ($38)","Vello encarnado"),

    ("Native Natural Deodorant 75g","Native","Sudoracion",
     75000,"ASIN: B01MCVXWAO","https://amazon.com/dp/B01MCVXWAO",
     "75g Regular ($13) | Sensitive ($14) | 3-pack ($35)","Mal olor"),

    ("Carpe Antiperspirant Hand Lotion 40g","Carpe","Sudoracion",
     80000,"ASIN: B01FXNZ2H8","https://amazon.com/dp/B01FXNZ2H8",
     "40g Manos ($15) | Foot ($15) | Kit ($28)","Sudoracion excesiva"),

    ("OPI Nail Envy Original 15ml","OPI","Manos y Unas",
     105000,"ASIN: B00178579E","https://amazon.com/dp/B00178579E",
     "15ml Original/Matte/Sensitive ($20 c/u)","Unas fragiles"),

    ("L'Occitane Shea Butter Hand Cream 150ml","L'Occitane","Manos y Unas",
     175000,"ASIN: B000MWKFNQ","https://amazon.com/dp/B000MWKFNQ",
     "30ml ($16) | 75ml ($23) | 150ml ($32) | 300ml ($50)","Manos resecas"),

    ("Baby Foot Exfoliant Foot Peel Original","Baby Foot","Pies",
     135000,"ASIN: B002YL5E30","https://amazon.com/dp/B002YL5E30",
     "Original ($25) | Lavender ($26) | Moisture ($26)","Pies agrietados, callos"),

    ("Beardbrand Gold Blend Beard Oil 30ml","Beardbrand","Cuidado Masculino",
     138000,"SKU: BB-GOLD-1OZ","https://beardbrand.com",
     "30ml 1oz — 12 aromas ($25 c/u)","Barba aspera"),

    ("Jack Black Pure Clean Facial Cleanser 177ml","Jack Black","Cuidado Masculino",
     130000,"ASIN: B001AJATV2","https://amazon.com/dp/B001AJATV2",
     "88ml ($15) | 177ml ($24) | 500ml ($45)","Piel grasa masculina"),

    ("RapidLash Eyelash Enhancing Serum 3ml","RapidLash","Mirada",
     280000,"ASIN: B0013FXLJI","https://amazon.com/dp/B0013FXLJI",
     "3ml Lashes ($50) | 3ml RapidBrow ($50)","Pestanas cortas"),

    ("HUM Nutrition Daily Cleanse 60 caps","HUM Nutrition","Bienestar",
     220000,"SKU: HUM-DC-60","https://sephora.com",
     "60 caps 1 mes — unica presentacion","Acne interno, piel opaca"),

    ("Leanbean Female Fat Burner 180 caps","Leanbean","Bienestar",
     330000,"SKU: LB-1MONTH","https://leanbean.com",
     "180 caps 1 mes ($60) | 3 meses ($140)","Control de peso"),

    ("Crest 3D Whitestrips Professional Effects","Crest","Sonrisa",
     280000,"ASIN: B003AVEU4G","https://amazon.com/dp/B003AVEU4G",
     "20 strips 10 dias ($50) | Glamorous ($35) | Supreme ($65)","Dientes amarillos"),
]

# ── TABLA EDITABLE DE COSTOS ──────────────────────────────────────
st.markdown("### 📝 Ingresa tu costo real por producto")
st.caption("**Costo real** = lo que tú pagas para tener el producto en tus manos, listo para vender (incluye el producto + lo que gastaste en traerlo). Edita la columna amarilla.")

# Crear DataFrame editable
edit_data = pd.DataFrame([{
    "Producto":      nombre,
    "Marca":         marca,
    "Categoría":     cat,
    "PV Mercado COP":pv_mkt,
    "MI costo real (COP)": round(pv_mkt * 0.45),  # sugerencia inicial = 45% del PV mercado
} for nombre, marca, cat, pv_mkt, *_ in PRODUCTOS_BASE])

edited = st.data_editor(
    edit_data,
    use_container_width=True,
    hide_index=True,
    height=400,
    column_config={
        "Producto":             st.column_config.TextColumn("Producto",           width=220, disabled=True),
        "Marca":                st.column_config.TextColumn("Marca",              width=130, disabled=True),
        "Categoría":            st.column_config.TextColumn("Categoría",          width=120, disabled=True),
        "PV Mercado COP":       st.column_config.NumberColumn("PV Mercado COP",   width=140, format="$ %d", disabled=True),
        "MI costo real (COP)":  st.column_config.NumberColumn("✏️ MI COSTO REAL", width=160, format="$ %d",
                                    help="Edita este valor con lo que TÚ pagas por cada unidad"),
    }
)

st.markdown("<br>", unsafe_allow_html=True)

# ── CALCULAR MODELO ───────────────────────────────────────────────
st.markdown("### 📊 Análisis de precio competitivo")

rows = []
for i, (nombre, marca, cat, pv_mkt, ref, url, pres, prob) in enumerate(PRODUCTOS_BASE):
    try:
        costo_real = int(edited.iloc[i]["MI costo real (COP)"])
    except Exception:
        costo_real = round(pv_mkt * 0.45)

    m = modelo(costo_real, pv_mkt)

    # Indicador semaforo
    if m["p2"] >= 25:   semaforo = "🟢"
    elif m["p2"] >= 10: semaforo = "🟡"
    elif m["p2"] >= 0:  semaforo = "🟠"
    else:               semaforo = "🔴"

    rows.append({
        "":                       semaforo,
        "Producto":               nombre,
        "Marca":                  marca,
        "Cat.":                   cat,
        "Ref.":                   ref,
        "🔗":                     url,
        "Presentaciones":         pres,
        "Mi Costo Real":          f"${costo_real:,}",
        "Flete":                  f"${flete:,}",
        "PV Mercado Colombia":    f"${pv_mkt:,}",
        "🥇 Precio Ganador (-5%)": f"${m['pv1']:,}",
        "Rent. Ganador":          f"{m['p1']}%",
        "🥈 Precio Mercado":       f"${m['pv2']:,}",
        "Rent. Mercado":          f"{m['p2']}%",
        "🥉 Precio Premium (+10%)":f"${m['pv3']:,}",
        "Rent. Premium":          f"{m['p3']}%",
        "✅ Precio Sugerido":      f"${m['mejor_pv']:,}",
        "Mejor Rentabilidad":     f"{m['mejor_pct']}%",
        "Estrategia":             m['mejor_nom'],
        "Punto de Equilibrio":    f"${m['pe']:,}" if m['pe'] else "N/A",
        "Problema":               prob,
        # numericos
        "_r2": m["p2"], "_pv2": m["pv2"], "_mejor": m["mejor_pct"],
        "_costo": costo_real, "_pv_mkt": pv_mkt,
    })

DF = pd.DataFrame(rows)

# ── KPIs ─────────────────────────────────────────────────────────
verdes  = len(DF[DF["_r2"] >= 25])
amarill = len(DF[(DF["_r2"] >= 10) & (DF["_r2"] < 25)])
rojos   = len(DF[DF["_r2"] < 10])
avg_r   = DF["_mejor"].mean()

k1,k2,k3,k4,k5 = st.columns(5)
with k1: st.metric("Total Productos",    len(DF))
with k2: st.metric("🟢 Alta rentabilidad",f"{verdes} productos",   delta="+25% rent.")
with k3: st.metric("🟡 Media rentabilidad",f"{amarill} productos", delta="10–25% rent.")
with k4: st.metric("🔴 Baja / negativa",  f"{rojos} productos",    delta="<10% rent.")
with k5: st.metric("Rentabilidad prom.",  f"{avg_r:.1f}%",         delta="con precio sugerido")

st.markdown("<br>", unsafe_allow_html=True)

# ── FILTROS ───────────────────────────────────────────────────────
f1,f2,f3 = st.columns([3,2,2])
with f1: q     = st.text_input("🔎 Buscar...", placeholder="Ej: cerave, acne, olaplex")
with f2: cat_f = st.selectbox("Categoría", ["Todas"] + sorted(DF["Cat."].unique().tolist()))
with f3: filt  = st.selectbox("Mostrar",
    ["Todos","🟢 Solo rentables (+25%)","🟡 Media (10-25%)","🔴 Revisar (<10%)"])

df_s = DF.copy()
if q:
    ql = q.lower()
    df_s = df_s[df_s["Producto"].str.lower().str.contains(ql,na=False)|
                df_s["Marca"].str.lower().str.contains(ql,na=False)|
                df_s["Problema"].str.lower().str.contains(ql,na=False)]
if cat_f != "Todas":
    df_s = df_s[df_s["Cat."] == cat_f]
if filt == "🟢 Solo rentables (+25%)":
    df_s = df_s[df_s["_r2"] >= 25]
elif filt == "🟡 Media (10-25%)":
    df_s = df_s[(df_s["_r2"] >= 10) & (df_s["_r2"] < 25)]
elif filt == "🔴 Revisar (<10%)":
    df_s = df_s[df_s["_r2"] < 10]

st.caption(f"Mostrando {len(df_s)} de {len(DF)} productos")

# ── TABLA RESULTADOS ──────────────────────────────────────────────
cols = [
    "","Producto","Marca","Cat.","Ref.","🔗","Presentaciones",
    "Mi Costo Real","Flete","PV Mercado Colombia",
    "🥇 Precio Ganador (-5%)","Rent. Ganador",
    "🥈 Precio Mercado","Rent. Mercado",
    "🥉 Precio Premium (+10%)","Rent. Premium",
    "✅ Precio Sugerido","Mejor Rentabilidad","Estrategia",
    "Punto de Equilibrio","Problema"
]

st.dataframe(df_s[cols], use_container_width=True, hide_index=True, height=600,
    column_config={
        "":                        st.column_config.TextColumn("",               width=40),
        "Producto":                st.column_config.TextColumn("Producto",       width=200),
        "Marca":                   st.column_config.TextColumn("Marca",          width=120),
        "Cat.":                    st.column_config.TextColumn("Cat.",            width=100),
        "Ref.":                    st.column_config.TextColumn("Ref./SKU",       width=160),
        "🔗":                      st.column_config.LinkColumn("Link",           width=60),
        "Presentaciones":          st.column_config.TextColumn("Presentaciones", width=220),
        "Mi Costo Real":           st.column_config.TextColumn("Mi Costo Real",  width=120),
        "Flete":                   st.column_config.TextColumn("Flete",          width=80),
        "PV Mercado Colombia":     st.column_config.TextColumn("PV Mercado CO",  width=130),
        "🥇 Precio Ganador (-5%)": st.column_config.TextColumn("Precio Ganador", width=120),
        "Rent. Ganador":           st.column_config.TextColumn("Rent.%",         width=75),
        "🥈 Precio Mercado":       st.column_config.TextColumn("Precio Mercado", width=120),
        "Rent. Mercado":           st.column_config.TextColumn("Rent.%",         width=75),
        "🥉 Precio Premium (+10%)":st.column_config.TextColumn("Precio Premium", width=120),
        "Rent. Premium":           st.column_config.TextColumn("Rent.%",         width=75),
        "✅ Precio Sugerido":      st.column_config.TextColumn("PRECIO SUGERIDO",width=140),
        "Mejor Rentabilidad":      st.column_config.TextColumn("Rent. %",        width=80),
        "Estrategia":              st.column_config.TextColumn("Estrategia",     width=110),
        "Punto de Equilibrio":     st.column_config.TextColumn("P. Equilibrio",  width=120),
        "Problema":                st.column_config.TextColumn("Problema",       width=180),
    })

csv = df_s[cols].to_csv(index=False).encode("utf-8")
st.download_button("📥 Descargar CSV", csv, "rome_precio_competitivo.csv", "text/csv")

# ── LEYENDA ───────────────────────────────────────────────────────
with st.expander("📋 Leyenda y fórmula"):
    st.markdown(f"""
**Semáforo de rentabilidad** (con Precio Mercado):
- 🟢 **+25%** → Excelente, vende al precio de mercado o con descuento
- 🟡 **10–25%** → Aceptable, ajusta costos para mejorar
- 🟠 **0–10%** → Marginal, casi sin ganancia
- 🔴 **Negativo** → Estás perdiendo dinero, revisa tu costo de adquisición

**Fórmula:**
```
Rentabilidad (COP) = PV - Costo Real - Flete - Devoluciones (PV×{dev_pct:.0%}) - CPA (PV×{cpa_pct:.0%})
Rentabilidad (%)   = Rentabilidad / PV × 100

Precio Ganador     = PV Mercado × 95%  (5% menos para ganar clientes)
Precio Mercado     = PV Mercado exacto
Precio Premium     = PV Mercado × 110% (10% más, para diferenciarte)
Punto de Equilibrio = precio mínimo para no perder dinero
```
    """)

st.markdown(f"""
<div style="text-align:center;padding:20px 0;color:#A8D8F0;font-size:.75rem;">
  <span style="font-family:'Syne',sans-serif;color:#54A0FF;font-weight:700;">ESTUDIO DE MERCADO ROME</span><br>
  Modelo de precio competitivo Colombia · Flete ${flete:,} · Dev {dev_pct:.0%} · CPA {cpa_pct:.0%}
</div>
""", unsafe_allow_html=True)
