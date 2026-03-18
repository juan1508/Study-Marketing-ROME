"""ESTUDIO DE MERCADO ROME — Precios Colombia con rentabilidad 30%"""
import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="ROME Market — Colombia", page_icon="🔵",
                   layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500&display=swap');
.stApp{background:linear-gradient(135deg,#0A1628,#0D2137);}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;color:#DDE8F5;}
h1,h2{font-family:'Syne',sans-serif;font-weight:800;}
#MainMenu,footer,header{visibility:hidden;}
div[data-testid="metric-container"]{
    background:linear-gradient(135deg,#1A3A5CCC,#1E5FAD33)!important;
    border:1px solid #54A0FF40!important;border-radius:12px!important;padding:16px!important;}
div[data-testid="metric-container"] label{color:#A8D8F0!important;font-size:.78rem!important;text-transform:uppercase;}
[data-testid="stMetricValue"]{color:#EEF6FF!important;font-family:'Syne',sans-serif!important;font-weight:800!important;font-size:1.3rem!important;}
</style>""", unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────────
st.markdown("""
<h1 style="margin:20px 0 4px;font-size:1.9rem;background:linear-gradient(90deg,#EEF6FF,#54A0FF);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
  🔬 ESTUDIO DE MERCADO ROME — Colombia
</h1>
<p style="margin:0 0 20px;color:#A8D8F0;font-size:.88rem;">
  Precio de venta real en Colombia · Tu precio sugerido para 30% de rentabilidad · 49 productos
</p>
<hr style="border-color:#1E5FAD30;margin-bottom:20px;">
""", unsafe_allow_html=True)

# ── PARAMETROS (tu tabla exacta) ──────────────────────────────────
st.markdown("**⚙️ Parametros de operacion**")
p1,p2,p3,p4,p5 = st.columns(5)
with p1: flete    = st.number_input("🚚 Flete (COP)",          value=18000, step=1000)
with p2: dev_pct  = st.number_input("↩️ % Devoluciones",       value=20.0,  step=1.0) / 100
with p3: gastos   = st.number_input("🏢 Gastos Operativos COP",value=0,     step=1000)
with p4: cpa_pct  = st.number_input("📢 CPA % Publicidad",     value=15.0,  step=1.0) / 100
with p5: rent_obj = st.number_input("🎯 Rentabilidad min %",   value=30.0,  step=5.0) / 100

st.markdown("<br>", unsafe_allow_html=True)

# ── FORMULA ───────────────────────────────────────────────────────
# Tu precio de venta ya existe. Lo que calculamos:
# Costo unitario = Precio de venta mercado Colombia - (flete + dev + CPA + gastos) - rentabilidad
# Pero el usuario TIENE el costo unitario (precio que paga al traerlo)
# y quiere saber: dado ese costo y el precio que ya existe en el mercado,
# ¿cual deberia ser SU precio de venta para tener 30% de rentabilidad?
#
# PV_sugerido = (Costo + Flete + Gastos) / (1 - Dev% - CPA% - Rent%)
# Luego comparamos con el precio de mercado real

def calcular(costo_cop, pv_mercado):
    pct_var = dev_pct + cpa_pct + rent_obj
    if pct_var >= 1: return None
    pv_raw     = (costo_cop + flete + gastos) / (1 - pct_var)
    pv_sug     = math.ceil(pv_raw / 1000) * 1000
    # Con precio sugerido
    devol_sug  = round(pv_sug * dev_pct)
    cpa_sug    = round(pv_sug * cpa_pct)
    rent_sug   = pv_sug - costo_cop - flete - gastos - devol_sug - cpa_sug
    rent_pct_s = round(rent_sug / pv_sug * 100, 1)
    # Con precio de mercado real
    devol_mkt  = round(pv_mercado * dev_pct)
    cpa_mkt    = round(pv_mercado * cpa_pct)
    rent_mkt   = pv_mercado - costo_cop - flete - gastos - devol_mkt - cpa_mkt
    rent_pct_m = round(rent_mkt / pv_mercado * 100, 1) if pv_mercado > 0 else 0
    viable     = rent_pct_m >= rent_obj * 100
    return {
        "pv_sug":      pv_sug,
        "rent_sug":    rent_sug,
        "rent_pct_s":  rent_pct_s,
        "rent_mkt":    rent_mkt,
        "rent_pct_m":  rent_pct_m,
        "viable":      viable,
        "diferencia":  pv_sug - pv_mercado,
    }

# ── PRODUCTOS CON PRECIO REAL COLOMBIA ───────────────────────────
# Columnas: nombre, marca, cat, costo_cop, pv_colombia_real, ref, url, presentaciones, problema
# costo_cop = precio USD proveedor x TRM 4200 (costo de traerlo)
# pv_colombia_real = precio promedio real en tiendas/ML Colombia (buscado arriba)
TRM = 4200

PRODUCTOS = [
    # PIEL
    ("The Ordinary Niacinamide 10% + Zinc 1%","The Ordinary","Piel",
     round(6.90*TRM), 69900,
     "ASIN: B07M9LX9DH","https://amazon.com/dp/B07M9LX9DH",
     "30ml — presentacion unica",
     "Poros, manchas, acne",
     "sweetievulgar.com / lunaurea.co / tuwa.co"),

    ("Paula's Choice BHA 2% Liquid Exfoliant","Paula's Choice","Piel",
     round(34.00*TRM), 210000,
     "ASIN: B00949CTQQ","https://amazon.com/dp/B00949CTQQ",
     "30ml travel ($12) | 118ml ($34) | 950ml jumbo ($75)",
     "Poros, acne, opacidad",
     "paulaschoice.com.co / ML Colombia"),

    ("SkinCeuticals C E Ferulic Serum","SkinCeuticals","Piel",
     round(182.00*TRM), 980000,
     "ASIN: B000NZUQOY","https://amazon.com/dp/B000NZUQOY",
     "30ml — presentacion unica",
     "Manchas, envejecimiento",
     "Dermstore importado / ML Colombia"),

    ("Differin Adapalene Gel 0.1%","Differin","Piel",
     round(15.50*TRM), 89000,
     "ASIN: B07L1PHSY9","https://amazon.com/dp/B07L1PHSY9",
     "15g ($12) | 45g ($15.50) | 2-pack ($28)",
     "Acne, cicatrices, arrugas",
     "Farmacias / ML Colombia"),

    ("CeraVe Moisturizing Cream 250ml","CeraVe","Piel",
     round(19.00*TRM), 109500,
     "ASIN: B00TTD9BRC","https://amazon.com/dp/B00TTD9BRC",
     "250ml ($19) | 453g ($25) | 544g ($28) | 1kg ($38)",
     "Sequedad, barrera cutanea",
     "Falabella $109.500 (454g) / Locatel / ML"),

    ("Good Molecules Discoloration Correcting Serum","Good Molecules","Piel",
     round(12.00*TRM), 85000,
     "SKU: 810065800078","https://goodmolecules.com",
     "30ml — presentacion unica",
     "Hiperpigmentacion, manchas",
     "ML Colombia / importadores"),

    ("Sol de Janeiro Brazilian Bum Bum Cream 240ml","Sol de Janeiro","Piel",
     round(48.00*TRM), 320000,
     "ASIN: B01N3D7DKB","https://amazon.com/dp/B01N3D7DKB",
     "75ml ($26) | 240ml ($48) | 480ml ($72)",
     "Celulitis, flacidez",
     "ML Colombia / importadores beauty"),

    ("Bio-Oil Skincare Oil 125ml","Bio-Oil","Piel",
     round(14.00*TRM), 79900,
     "ASIN: B01MS3GFHK","https://amazon.com/dp/B01MS3GFHK",
     "60ml ($10) | 125ml ($14) | 200ml ($18) | 250ml ($22)",
     "Estrias, cicatrices",
     "Exito / Farmacias / ML Colombia"),

    ("La Roche-Posay Effaclar Duo+","La Roche-Posay","Piel",
     round(30.00*TRM), 145000,
     "ASIN: B014OPM4P4","https://amazon.com/dp/B014OPM4P4",
     "40ml — presentacion unica",
     "Acne, poros, grasa",
     "Locatel / ML Colombia / importadores"),

    ("EltaMD UV Clear SPF 46","EltaMD","Piel",
     round(39.00*TRM), 220000,
     "ASIN: B002MSN3QQ","https://amazon.com/dp/B002MSN3QQ",
     "48g Untinted ($39) | 48g Tinted ($41)",
     "Dano solar, manchas",
     "ML Colombia / importadores"),

    ("Neutrogena Rapid Wrinkle Repair Eye Cream","Neutrogena","Piel",
     round(22.00*TRM), 95000,
     "ASIN: B00BT7BYLY","https://amazon.com/dp/B00BT7BYLO",
     "14g — presentacion unica",
     "Bolsas, ojeras, arrugas",
     "Farmacias / Exito / ML Colombia"),

    ("RoC Retinol Correxion Line Smoothing Cream","RoC","Piel",
     round(25.99*TRM), 130000,
     "ASIN: B075H4FDMZ","https://amazon.com/dp/B075H4FDMZ",
     "30ml ($26) | 48g Max Wrinkle ($30)",
     "Arrugas, lineas expresion",
     "Farmacias / ML Colombia"),

    ("Some By Mi AHA BHA PHA 30 Days Toner","Some By Mi","Piel",
     round(22.00*TRM), 120000,
     "ASIN: B07C7FQG3Z","https://amazon.com/dp/B07C7FQG3Z",
     "150ml ($22) | 300ml ($30)",
     "Poros, textura, manchas",
     "ML Colombia / K-beauty stores"),

    ("Drunk Elephant C-Firma Fresh Day Serum","Drunk Elephant","Piel",
     round(90.00*TRM), 520000,
     "ASIN: B072J74N5K","https://amazon.com/dp/B072J74N5K",
     "15ml mini ($50) | 30ml ($90)",
     "Opacidad, manchas",
     "ML Colombia / importadores premium"),

    ("GlamGlow Supermud Clearing Treatment 50g","GlamGlow","Piel",
     round(69.00*TRM), 380000,
     "ASIN: B00IFHPQDY","https://amazon.com/dp/B00IFHPQDY",
     "34g ($55) | 50g ($69) | 100g ($109)",
     "Acne, poros, impurezas",
     "ML Colombia / importadores"),

    ("Herbivore Bakuchiol Retinol Alternative Oil 30ml","Herbivore","Piel",
     round(54.00*TRM), 300000,
     "ASIN: B07YTTQKRS","https://amazon.com/dp/B07YTTQKRS",
     "15ml ($34) | 30ml ($54)",
     "Arrugas, poros, firmeza",
     "ML Colombia / Sephora importado"),

    # CABELLO
    ("Viviscal Extra Strength Hair Growth 60 tabs","Viviscal","Cabello",
     round(49.99*TRM), 280000,
     "ASIN: B00BSZKETA","https://amazon.com/dp/B00BSZKETA",
     "60 tabs 1 mes ($50) | 180 tabs 3 meses ($130)",
     "Caida del cabello, alopecia",
     "ML Colombia / importadores salud"),

    ("Minoxidil 5% Kirkland Foam 6 meses","Kirkland","Cabello",
     round(29.00*TRM), 160000,
     "ASIN: B00GXYK4GO","https://amazon.com/dp/B00GXYK4GO",
     "6x60ml supply 6 meses ($29) | 1 mes ($12)",
     "Calvicie, entradas",
     "ML Colombia / farmacias"),

    ("Olaplex No.3 Hair Perfector 100ml","Olaplex","Cabello",
     round(30.00*TRM), 150000,
     "ASIN: B013NQRZME","https://amazon.com/dp/B013NQRZME",
     "100ml ($30) | 250ml ($52) | 1000ml salon ($130)",
     "Cabello quebradizo, danado",
     "Falabella $124.900 / oritcolombia.com / ML $130.000-$150.000"),

    ("Nizoral A-D Anti-Dandruff Shampoo 200ml","Nizoral","Cabello",
     round(15.00*TRM), 79000,
     "ASIN: B00AINMFAC","https://amazon.com/dp/B00AINMFAC",
     "200ml ($15) | 400ml ($24) | 730ml ($35)",
     "Caspa, dermatitis seborreica",
     "Farmacias / Exito / ML Colombia"),

    ("Madison Reed Root Touch Up Kit","Madison Reed","Cabello",
     round(26.00*TRM), 148000,
     "ASIN: B01MUAISNV","https://amazon.com/dp/B01MUAISNV",
     "Kit completo — 13 tonos ($26 c/u)",
     "Canas prematuras",
     "ML Colombia / importadores"),

    # ENVEJECIMIENTO
    ("Vital Proteins Collagen Peptides 283g","Vital Proteins","Envejecimiento",
     round(43.00*TRM), 220000,
     "ASIN: B00K6EM5CK","https://amazon.com/dp/B00K6EM5CK",
     "283g ($43) | 567g ($68) | sachets x20 ($25)",
     "Arrugas, cabello, unas",
     "vitalproshop.com Colombia / ML $180.000-$250.000"),

    ("StriVectin TL Advanced Tightening Neck Cream 50ml","StriVectin","Envejecimiento",
     round(89.00*TRM), 490000,
     "ASIN: B07BFKZP7W","https://amazon.com/dp/B07BFKZP7W",
     "30ml ($65) | 50ml ($89)",
     "Flacidez cuello y escote",
     "ML Colombia / importadores premium"),

    ("Murad Rapid Age Spot Lightening Serum 30ml","Murad","Envejecimiento",
     round(86.00*TRM), 470000,
     "ASIN: B001447XCK","https://amazon.com/dp/B001447XCK",
     "30ml — presentacion unica",
     "Manchas edad, hiperpigmentacion",
     "ML Colombia / importadores"),

    # MAQUILLAJE
    ("Fenty Beauty Pro Filt'r Soft Matte Foundation","Fenty Beauty","Maquillaje",
     round(40.00*TRM), 230000,
     "SKU: varies by shade","https://fentybeauty.com",
     "32ml — 50 tonos ($40 c/u)",
     "Tono desigual, manchas",
     "ML Colombia $180.000-$250.000 / importadores"),

    ("Charlotte Tilbury Pillow Talk Lip Liner","Charlotte Tilbury","Maquillaje",
     round(28.00*TRM), 165000,
     "ASIN: B06WVFQXF4","https://amazon.com/dp/B06WVFQXF4",
     "1.2g — 8 tonos ($28 c/u)",
     "Labios finos, sin definicion",
     "ML Colombia $140.000-$180.000 / importadores beauty"),

    ("Benefit Gimme Brow+ Volumizing Eyebrow Gel","Benefit","Maquillaje",
     round(24.00*TRM), 145000,
     "ASIN: B0774YDJ5H","https://amazon.com/dp/B0774YDJ5H",
     "3g full ($24) | 1.5g mini ($16) — 12 tonos",
     "Cejas escasas, ralas",
     "ML Colombia $120.000-$150.000 / importadores"),

    ("L'Oreal Paris Voluminous Original Mascara","L'Oreal","Maquillaje",
     round(10.99*TRM), 55000,
     "ASIN: B000URXPKE","https://amazon.com/dp/B000URXPKE",
     "8.5ml Regular ($11) | Waterproof ($12)",
     "Pestanas cortas, ralas",
     "Exito / Farmacias / ML Colombia $45.000-$65.000"),

    ("NYX Professional Makeup Wonder Stick","NYX","Maquillaje",
     round(14.00*TRM), 72000,
     "ASIN: B01LYYM7DA","https://amazon.com/dp/B01LYYM7DA",
     "7.7g — 4 tonos ($14 c/u)",
     "Definicion facial, contouring",
     "ML Colombia $60.000-$80.000 / importadores"),

    ("e.l.f. Poreless Putty Primer 21g","e.l.f.","Maquillaje",
     round(10.00*TRM), 60000,
     "ASIN: B07FKWPRT7","https://amazon.com/dp/B07FKWPRT7",
     "21g Original ($10) | Matte ($10) | Luminous ($10)",
     "Poros visibles, maquillaje duradero",
     "ML Colombia $50.000-$70.000 / importadores"),

    ("Charlotte Tilbury Hollywood Flawless Filter 30ml","Charlotte Tilbury","Maquillaje",
     round(46.00*TRM), 260000,
     "ASIN: B07YP9XHQR","https://amazon.com/dp/B07YP9XHQR",
     "30ml ($46) | Mini 7.9ml ($26) — 8 tonos",
     "Base luminosa efecto natural",
     "ML Colombia $220.000-$280.000 / importadores"),

    ("NARS Radiant Creamy Concealer 6ml","NARS","Maquillaje",
     round(32.00*TRM), 175000,
     "ASIN: B00CM4Y29G","https://amazon.com/dp/B00CM4Y29G",
     "6ml — 30 tonos ($32)",
     "Ojeras, imperfecciones",
     "ML Colombia $150.000-$200.000 / importadores"),

    ("Too Faced Better Than Sex Mascara 8ml","Too Faced","Maquillaje",
     round(27.00*TRM), 155000,
     "ASIN: B00F7NRPOK","https://amazon.com/dp/B00F7NRPOK",
     "8ml ($27) | Travel 4ml ($14) | Waterproof ($27)",
     "Pestanas voluminosas",
     "ML Colombia $130.000-$170.000 / importadores"),

    ("Urban Decay All Nighter Setting Spray 118ml","Urban Decay","Maquillaje",
     round(33.00*TRM), 185000,
     "ASIN: B008JDHEPC","https://amazon.com/dp/B008JDHEPC",
     "30ml travel ($18) | 118ml ($33) | 240ml ($44)",
     "Maquillaje duradero todo el dia",
     "ML Colombia $160.000-$200.000 / importadores"),

    # CUERPO
    ("Optimum Nutrition Gold Standard Whey 908g","Optimum Nutrition","Cuerpo",
     round(58.00*TRM), 320000,
     "ASIN: B000QSNYGI","https://amazon.com/dp/B000QSNYGI",
     "908g 2lb ($58) | 2.27kg 5lb ($78) | 4.54kg 10lb ($140)",
     "Masa muscular, recuperacion",
     "GNC Colombia / ML $280.000-$350.000"),

    ("Bliss Fat Girl Slim Arm Candy Cream 200ml","Bliss","Cuerpo",
     round(38.00*TRM), 210000,
     "ASIN: B008X80RWW","https://amazon.com/dp/B008X80RWW",
     "200ml — presentacion unica",
     "Flacidez brazos, celulitis",
     "ML Colombia / importadores"),

    # VELLO
    ("Ulike Air 3 IPL Laser Hair Removal Device","Ulike","Vello",
     round(219.00*TRM), 1200000,
     "ASIN: B0BL9W6VKD","https://amazon.com/dp/B0BL9W6VKD",
     "Air 3 Azul/Blanco ($219) | Air+ ($299) | Air 10 ($329)",
     "Vello facial y corporal permanente",
     "ML Colombia $900.000-$1.300.000 / importadores"),

    ("Tend Skin Solution 236ml","Tend Skin","Vello",
     round(24.00*TRM), 130000,
     "ASIN: B0010O3PEO","https://amazon.com/dp/B0010O3PEO",
     "118ml ($17) | 236ml ($24) | 473ml ($38)",
     "Vello encarnado, irritacion",
     "ML Colombia / importadores"),

    # SUDORACION
    ("Native Natural Deodorant 75g","Native","Sudoracion",
     round(13.00*TRM), 75000,
     "ASIN: B01MCVXWAO","https://amazon.com/dp/B01MCVXWAO",
     "75g Regular ($13) | Sensitive ($14) | 3-pack ($35)",
     "Mal olor, transpiracion natural",
     "ML Colombia $60.000-$85.000 / importadores"),

    ("Carpe Antiperspirant Hand Lotion 40g","Carpe","Sudoracion",
     round(14.95*TRM), 80000,
     "ASIN: B01FXNZ2H8","https://amazon.com/dp/B01FXNZ2H8",
     "40g Manos ($15) | Foot Lotion ($15) | Kit ($28)",
     "Sudoracion excesiva manos/pies",
     "ML Colombia / importadores"),

    # MANOS Y UNAS
    ("OPI Nail Envy Original Nail Strengthener 15ml","OPI","Manos y Unas",
     round(19.99*TRM), 105000,
     "ASIN: B00178579E","https://amazon.com/dp/B00178579E",
     "15ml Original ($20) | Double Nude-y | Sensitive | Matte",
     "Unas fragiles, quebradizas",
     "Farmacias / ML Colombia $90.000-$115.000"),

    ("L'Occitane Shea Butter Hand Cream 150ml","L'Occitane","Manos y Unas",
     round(32.00*TRM), 175000,
     "ASIN: B000MWKFNQ","https://amazon.com/dp/B000MWKFNQ",
     "30ml ($16) | 75ml ($23) | 150ml ($32) | 300ml ($50)",
     "Manos resecas, envejecidas",
     "Falabella / ML Colombia $150.000-$190.000"),

    ("Baby Foot Exfoliant Foot Peel Original","Baby Foot","Pies",
     round(25.00*TRM), 135000,
     "ASIN: B002YL5E30","https://amazon.com/dp/B002YL5E30",
     "Original ($25) | Lavender ($26) | Moisture ($26)",
     "Pies agrietados, callos, durezas",
     "ML Colombia $110.000-$150.000 / importadores"),

    # CUIDADO MASCULINO
    ("Beardbrand Gold Blend Beard Oil 30ml","Beardbrand","Cuidado Masculino",
     round(25.00*TRM), 138000,
     "SKU: BB-GOLD-1OZ","https://beardbrand.com",
     "30ml 1oz — 12 aromas ($25 c/u)",
     "Barba aspera, piel irritada",
     "ML Colombia / importadores grooming"),

    ("Jack Black Pure Clean Daily Facial Cleanser 177ml","Jack Black","Cuidado Masculino",
     round(24.00*TRM), 130000,
     "ASIN: B001AJATV2","https://amazon.com/dp/B001AJATV2",
     "88ml travel ($15) | 177ml ($24) | 500ml pump ($45)",
     "Piel grasa, poros, acne masculino",
     "ML Colombia / importadores beauty men"),

    # MIRADA
    ("RapidLash Eyelash Enhancing Serum 3ml","RapidLash","Mirada",
     round(49.99*TRM), 280000,
     "ASIN: B0013FXLJI","https://amazon.com/dp/B0013FXLJI",
     "3ml Lashes ($50) | 3ml RapidBrow ($50)",
     "Pestanas cortas, ralas",
     "ML Colombia $240.000-$300.000 / importadores"),

    # BIENESTAR
    ("HUM Nutrition Daily Cleanse 60 capsulas","HUM Nutrition","Bienestar",
     round(40.00*TRM), 220000,
     "SKU: HUM-DC-60","https://sephora.com",
     "60 capsulas 1 mes — presentacion unica",
     "Acne interno, piel opaca",
     "ML Colombia / importadores suplementos"),

    ("Leanbean Female Fat Burner 180 capsulas","Leanbean","Bienestar",
     round(59.99*TRM), 330000,
     "SKU: LB-1MONTH","https://leanbean.com",
     "180 caps 1 mes ($60) | 3 meses bundle ($140)",
     "Control de peso, metabolismo",
     "ML Colombia / importadores salud"),

    # SONRISA
    ("Crest 3D Whitestrips Professional Effects","Crest","Sonrisa",
     round(49.99*TRM), 280000,
     "ASIN: B003AVEU4G","https://amazon.com/dp/B003AVEU4G",
     "20 strips 10 dias ($50) | Glamorous White ($35) | Supreme ($65)",
     "Dientes amarillos, manchados",
     "ML Colombia $240.000-$300.000 / farmacias"),
]

# ── CONSTRUIR DATAFRAME ───────────────────────────────────────────
rows = []
for nombre, marca, cat, costo, pv_mkt, ref, url, pres, prob, donde in PRODUCTOS:
    r = calcular(costo, pv_mkt)
    if r is None: continue

    estado = "✅ VIABLE" if r["viable"] else "⚠️ REVISAR"
    diff   = r["diferencia"]
    diff_s = f"+${diff:,}" if diff > 0 else f"-${abs(diff):,}"

    rows.append({
        "Producto":               nombre,
        "Marca":                  marca,
        "Cat.":                   cat,
        "Referencia":             ref,
        "Link":                   url,
        "Presentaciones":         pres,
        "Costo Unitario":         f"${costo:,}",
        "Flete":                  f"${flete:,}",
        "💰 PV Mercado Colombia":  f"${pv_mkt:,}",
        "🎯 Tu Precio Sugerido":   f"${r['pv_sug']:,}",
        "Diferencia vs Mercado":  diff_s,
        "Rentab. con PV Mercado": f"{r['rent_pct_m']}%",
        "Rentab. con Tu Precio":  f"{r['rent_pct_s']}%",
        "Ganancia con Tu Precio": f"${r['rent_sug']:,}",
        "Estado":                 estado,
        "Donde comprar en CO":    donde,
        "Problema":               prob,
        # numericos
        "_pv_mkt":   pv_mkt,
        "_pv_sug":   r["pv_sug"],
        "_rent_m":   r["rent_pct_m"],
        "_rent_s":   r["rent_pct_s"],
        "_viable":   r["viable"],
        "_gan":      r["rent_sug"],
        "_costo":    costo,
    })

DF = pd.DataFrame(rows)

# ── KPIs ─────────────────────────────────────────────────────────
viables = DF[DF["_viable"] == True]
k1,k2,k3,k4,k5 = st.columns(5)
with k1: st.metric("Total Productos",   len(DF))
with k2: st.metric("Productos Viables", f"{len(viables)} ✅")
with k3: st.metric("Precio Sug. Min",   f"${DF['_pv_sug'].min():,}")
with k4: st.metric("Precio Sug. Max",   f"${DF['_pv_sug'].max():,}")
with k5: st.metric("Ganancia Prom.",    f"${DF['_gan'].mean():,.0f}")

st.markdown("<br>", unsafe_allow_html=True)

# ── NOTA EXPLICATIVA ──────────────────────────────────────────────
st.info("""
**Como leer la tabla:**
- **PV Mercado Colombia** = precio al que ya se vende hoy en Colombia (ML, Falabella, tiendas)
- **Tu Precio Sugerido** = el precio al que TÚ debes vender para obtener el 30% de rentabilidad
- **✅ VIABLE** = el precio de mercado ya permite el 30% de margen → puedes competir
- **⚠️ REVISAR** = para lograr 30% debes cobrar MÁS que el mercado → difícil de competir
""")

# ── FILTROS ───────────────────────────────────────────────────────
f1, f2, f3 = st.columns([3, 2, 2])
with f1: q     = st.text_input("🔎 Buscar...", placeholder="Ej: acne, olaplex, mascara")
with f2: cat_f = st.selectbox("Categoria", ["Todas"] + sorted(DF["Cat."].unique().tolist()))
with f3: solo_v = st.checkbox("Mostrar solo productos VIABLES ✅", value=False)

df_s = DF.copy()
if q:
    ql = q.lower()
    df_s = df_s[df_s["Producto"].str.lower().str.contains(ql,na=False)|
                df_s["Marca"].str.lower().str.contains(ql,na=False)|
                df_s["Problema"].str.lower().str.contains(ql,na=False)]
if cat_f != "Todas":
    df_s = df_s[df_s["Cat."] == cat_f]
if solo_v:
    df_s = df_s[df_s["_viable"] == True]

st.caption(f"Mostrando {len(df_s)} de {len(DF)} productos")

# ── TABLA ─────────────────────────────────────────────────────────
cols = [
    "Producto","Marca","Cat.",
    "Referencia","Link","Presentaciones",
    "Costo Unitario","Flete",
    "💰 PV Mercado Colombia","🎯 Tu Precio Sugerido",
    "Diferencia vs Mercado",
    "Rentab. con PV Mercado","Rentab. con Tu Precio","Ganancia con Tu Precio",
    "Estado","Donde comprar en CO","Problema"
]
st.dataframe(df_s[cols], use_container_width=True, hide_index=True, height=620,
    column_config={
        "Producto":               st.column_config.TextColumn("Producto",            width=200),
        "Marca":                  st.column_config.TextColumn("Marca",               width=120),
        "Cat.":                   st.column_config.TextColumn("Cat.",                width=110),
        "Referencia":             st.column_config.TextColumn("Ref./SKU",            width=160),
        "Link":                   st.column_config.LinkColumn("Link",                width=80),
        "Presentaciones":         st.column_config.TextColumn("Presentaciones",      width=240),
        "Costo Unitario":         st.column_config.TextColumn("Costo Unitario",      width=115),
        "Flete":                  st.column_config.TextColumn("Flete",               width=80),
        "💰 PV Mercado Colombia":  st.column_config.TextColumn("PV Mercado CO",       width=135),
        "🎯 Tu Precio Sugerido":   st.column_config.TextColumn("Tu Precio Sugerido",  width=145),
        "Diferencia vs Mercado":  st.column_config.TextColumn("Dif. vs Mercado",     width=120),
        "Rentab. con PV Mercado": st.column_config.TextColumn("Rent. Mercado",       width=110),
        "Rentab. con Tu Precio":  st.column_config.TextColumn("Rent. Tu Precio",     width=110),
        "Ganancia con Tu Precio": st.column_config.TextColumn("Ganancia",            width=110),
        "Estado":                 st.column_config.TextColumn("Estado",              width=100),
        "Donde comprar en CO":    st.column_config.TextColumn("Donde en Colombia",   width=220),
        "Problema":               st.column_config.TextColumn("Problema",            width=200),
    })

csv = df_s[cols].to_csv(index=False).encode("utf-8")
st.download_button("📥 Descargar CSV", csv, "rome_precios_colombia.csv", "text/csv")

with st.expander("📋 Formula de calculo"):
    st.markdown(f"""
```
Costo unitario COP  = Precio USD proveedor × TRM {TRM:,}
Flete               = ${flete:,} COP
Gastos operativos   = ${gastos:,} COP

Tu Precio Sugerido  = (Costo + Flete + Gastos) / (1 - Dev% - CPA% - Rent%)
                      = (Costo + {flete:,}) / (1 - {dev_pct:.0%} - {cpa_pct:.0%} - {rent_obj:.0%})
                      Redondeado al proximo multiplo de $1,000

Rentabilidad con PV Mercado = PV_Mercado - Costo - Flete - Devoluciones - CPA
Viable = Rentabilidad con PV Mercado >= {rent_obj:.0%}
```
    """)

st.markdown(f"""
<div style="text-align:center;padding:20px 0;color:#A8D8F0;font-size:.75rem;">
  <span style="font-family:'Syne',sans-serif;color:#54A0FF;font-weight:700;">ESTUDIO DE MERCADO ROME</span><br>
  Precios Colombia verificados en ML, Falabella y tiendas especializadas · TRM ${TRM:,}<br>
  <span style="opacity:.5;">Precios de mercado son aproximados. Verificar antes de fijar precios finales.</span>
</div>
""", unsafe_allow_html=True)
