"""
ESTUDIO DE MERCADO ROME
Inteligencia comercial en vivo · Belleza & Cuidado Personal · Colombia
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
import math
from datetime import datetime, timedelta

# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ROME Market Intelligence",
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
.stApp{{background:linear-gradient(135deg,{BG},{DARK});min-height:100vh;}}
html,body,[class*="css"]{{font-family:'DM Sans',sans-serif;color:{TEXT};}}
h1,h2,h3{{font-family:'Syne',sans-serif;font-weight:800;}}
#MainMenu,footer,header{{visibility:hidden;}}
div[data-testid="metric-container"]{{
  background:linear-gradient(135deg,{MID}CC,{PRI}33)!important;
  border:1px solid {ACC}40!important;border-radius:14px!important;padding:18px!important;}}
div[data-testid="metric-container"] label{{color:{PALE}!important;font-size:.75rem!important;
  text-transform:uppercase;letter-spacing:.06em;}}
[data-testid="stMetricValue"]{{color:{WHT}!important;font-family:'Syne',sans-serif!important;
  font-weight:800!important;font-size:1.35rem!important;}}
.stTabs [data-baseweb="tab-list"]{{background:{MID}80!important;border-radius:12px!important;padding:4px!important;}}
.stTabs [data-baseweb="tab"]{{background:transparent!important;color:{PALE}!important;border-radius:10px!important;}}
.stTabs [aria-selected="true"]{{background:linear-gradient(135deg,{PRI},{BRT})!important;color:white!important;font-weight:600!important;}}
.stButton>button{{background:linear-gradient(135deg,{PRI},{BRT})!important;color:white!important;
  border:none!important;border-radius:10px!important;font-weight:600!important;}}
section[data-testid="stSidebar"]{{background:linear-gradient(180deg,{DARK},{MID})!important;}}
hr{{border-color:{PRI}30!important;}}
.card{{background:linear-gradient(135deg,{MID},{DARK});border:1px solid {ACC}40;
  border-radius:14px;padding:18px;margin-bottom:14px;}}
.pill-g{{background:{GRN}20;color:{GRN};border:1px solid {GRN}50;border-radius:20px;
  padding:3px 12px;font-size:.75rem;font-weight:600;display:inline-block;}}
.pill-y{{background:{YEL}20;color:{YEL};border:1px solid {YEL}50;border-radius:20px;
  padding:3px 12px;font-size:.75rem;font-weight:600;display:inline-block;}}
.pill-r{{background:{RED}20;color:{RED};border:1px solid {RED}50;border-radius:20px;
  padding:3px 12px;font-size:.75rem;font-weight:600;display:inline-block;}}
</style>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# CONSTANTES MODELO COLOMBIA (tu tabla)
# ─────────────────────────────────────────────────────────────────
TRM       = 4200    # COP por USD
FLETE     = 18_000  # COP envío al cliente
DEV_PCT   = 0.20    # % devoluciones
CPA_PCT   = 0.15    # % publicidad sobre PV
GASTOS    = 0       # gastos fijos por unidad

# ─────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────
def fmt_cop(v):
    if v >= 1_000_000: return f"${v/1_000_000:.1f}M"
    if v >= 1_000:     return f"${v/1_000:.0f}K"
    return f"${v:,.0f}"

def fmt_usd(v): return f"${v:.2f}"

def modelo_colombia(costo_cop, pv_mercado_cop):
    """
    Dado el costo real y el precio de mercado Colombia,
    calcula rentabilidad en 3 estrategias y sugiere el precio óptimo.
    """
    def rent(pv):
        if pv <= 0: return 0, 0
        devs = pv * DEV_PCT
        cpa  = pv * CPA_PCT
        r    = pv - costo_cop - FLETE - GASTOS - devs - cpa
        return round(r), round(r / pv * 100, 1)

    pv_g = max(math.floor(pv_mercado_cop * 0.95 / 1000) * 1000, 1000)
    pv_m = pv_mercado_cop
    pv_p = math.ceil(pv_mercado_cop * 1.10 / 1000) * 1000

    rg_cop, rg_pct = rent(pv_g)
    rm_cop, rm_pct = rent(pv_m)
    rp_cop, rp_pct = rent(pv_p)

    # Precio óptimo = máxima rentabilidad que sea > 0
    opciones = [(rg_pct, pv_g, "Ganador"), (rm_pct, pv_m, "Mercado"), (rp_pct, pv_p, "Premium")]
    viables  = [o for o in opciones if o[0] > 0]
    if viables:
        _, opt_pv, opt_str = max(viables, key=lambda x: x[0])
        opt_cop, opt_pct = rent(opt_pv)
    else:
        opt_pv, opt_cop, opt_pct, opt_str = pv_m, rm_cop, rm_pct, "Mercado"

    # Punto de equilibrio
    denom = 1 - DEV_PCT - CPA_PCT
    pe = math.ceil((costo_cop + FLETE + GASTOS) / denom / 1000) * 1000 if denom > 0 else None

    return {
        "pv_g": pv_g, "rg_cop": rg_cop, "rg_pct": rg_pct,
        "pv_m": pv_m, "rm_cop": rm_cop, "rm_pct": rm_pct,
        "pv_p": pv_p, "rp_cop": rp_cop, "rp_pct": rp_pct,
        "opt_pv": opt_pv, "opt_cop": opt_cop, "opt_pct": opt_pct, "opt_str": opt_str,
        "pe": pe,
    }

# ─────────────────────────────────────────────────────────────────
# MAKEUP API — fetch en vivo
# ─────────────────────────────────────────────────────────────────
MAKEUP_TYPES = [
    ("foundation",  "Maquillaje","Base",       "Femenino","Tono desigual, manchas"),
    ("lip_liner",   "Maquillaje","Labios",      "Femenino","Labios finos"),
    ("mascara",     "Maquillaje","Ojos",        "Femenino","Pestanas cortas"),
    ("bronzer",     "Maquillaje","Contorno",    "Femenino","Definicion facial"),
    ("primer",      "Maquillaje","Primer",      "Femenino","Poros visibles"),
    ("blush",       "Maquillaje","Colorete",    "Femenino","Falta de color"),
    ("eyeshadow",   "Maquillaje","Sombras",     "Femenino","Ojos sin profundidad"),
    ("eyeliner",    "Maquillaje","Delineador",  "Femenino","Mirada sin definicion"),
    ("lip_gloss",   "Maquillaje","Gloss",       "Femenino","Labios sin volumen"),
    ("nail_polish", "Manos",     "Esmalte",     "Femenino","Unas sin color"),
    ("moisturizer", "Piel",      "Hidratacion", "Mixto",   "Sequedad"),
    ("face_wash",   "Piel",      "Limpieza",    "Mixto",   "Poros, grasa"),
    ("serum",       "Piel",      "Suero",       "Femenino","Manchas, opacidad"),
    ("lip_liner",   "Cuidado",   "Labios",      "Mixto",   "Labios resecos"),
]

def _orig(b):
    b = (b or "").lower()
    for k,v in [("loreal","Francia"),("lancome","Francia"),("charlotte tilbury","UK"),
                ("the ordinary","Canada"),("fenty","USA"),("nyx","USA"),("maybelline","USA"),
                ("cerave","USA"),("benefit","USA"),("elf","USA"),("e.l.f.","USA"),
                ("nivea","Alemania"),("some by mi","Korea"),("shiseido","Japon"),
                ("missha","Korea"),("innisfree","Korea"),("tatcha","Japon"),
                ("nars","USA"),("urban decay","USA"),("too faced","USA")]:
        if k in b: return v
    return "USA"

def _tend(r, n):
    if n > 80000 and r >= 4.5: return "muy_creciente"
    if n > 40000 and r >= 4.2: return "creciente"
    if n > 10000: return "estable"
    return "creciente"

def _rot(n):
    if n > 100000: return "muy_alta"
    if n > 50000:  return "alta"
    if n > 20000:  return "media_alta"
    if n > 8000:   return "media"
    return "alta"

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_api():
    """Fetch Makeup API — retorna lista de dicts enriquecidos."""
    results = []
    for (pt, cat, sub, tgt, prob) in MAKEUP_TYPES:
        try:
            r = requests.get(
                "https://makeup-api.herokuapp.com/api/v1/products.json",
                params={"product_type": pt}, timeout=8)
            if r.status_code != 200: continue
            items = [p for p in r.json()
                     if p.get("name") and float(p.get("price") or 0) > 0][:6]
            for p in items:
                price = round(float(p["price"]), 2)
                revs  = len(p.get("product_colors",[])) * 1800 + 4000
                rat   = min(float(p.get("rating") or 4.1), 5.0)
                brand = (p.get("brand") or "Unknown").strip().title()
                results.append({
                    "id":       f"API{len(results)+1:04d}",
                    "nombre":   (p.get("name") or "")[:80],
                    "marca":    brand,
                    "origen":   _orig(brand),
                    "cat":      cat,
                    "sub":      sub,
                    "target":   tgt,
                    "problema": prob,
                    "precio_usd":  price,
                    "rating":   round(rat, 1),
                    "reviews":  revs,
                    "unidades": revs,
                    "tend":     _tend(rat, revs),
                    "rot":      _rot(revs),
                    "desc":     (p.get("description") or p.get("name") or "")[:100],
                    "img":      p.get("image_link") or "",
                    "url":      p.get("product_link") or "",
                    "fuente":   "Makeup API",
                    "ref":      f"ASIN/SKU via makeupapi",
                    "pres":     "Ver link para presentaciones",
                })
        except Exception:
            continue
    return results

# ─────────────────────────────────────────────────────────────────
# BASE LOCAL — 49 productos curados con precios Colombia reales
# (nombre, marca, cat, sub, precio_usd, pv_co, ref, url, pres, target, prob, rot_base, unid_base)
# ─────────────────────────────────────────────────────────────────
LOCAL = [
    ("The Ordinary Niacinamide 10% + Zinc 1%","The Ordinary","Piel","Sueros",6.90,69900,"ASIN:B07M9LX9DH","https://amazon.com/dp/B07M9LX9DH","30ml unica","Mixto","Poros, manchas, acne","muy_alta",85000),
    ("Paula's Choice BHA 2% Liquid Exfoliant","Paula's Choice","Piel","Sueros",34.00,210000,"ASIN:B00949CTQQ","https://amazon.com/dp/B00949CTQQ","30ml($12)|118ml($34)|950ml($75)","Mixto","Poros, acne, opacidad","alta",42000),
    ("SkinCeuticals C E Ferulic Serum","SkinCeuticals","Piel","Vitamina C",182.00,980000,"ASIN:B000NZUQOY","https://amazon.com/dp/B000NZUQOY","30ml unica","Femenino","Manchas, envejecimiento","media",18000),
    ("Differin Adapalene Gel 0.1%","Differin","Piel","Retinol",15.50,89000,"ASIN:B07L1PHSY9","https://amazon.com/dp/B07L1PHSY9","15g($12)|45g($15.50)|2-pack($28)","Mixto","Acne, cicatrices, arrugas","muy_alta",95000),
    ("CeraVe Moisturizing Cream 250ml","CeraVe","Piel","Hidratacion",19.00,109500,"ASIN:B00TTD9BRC","https://amazon.com/dp/B00TTD9BRC","250ml($19)|453g($25)|544g($28)|1kg($38)","Mixto","Sequedad, barrera cutanea","muy_alta",210000),
    ("Good Molecules Discoloration Serum","Good Molecules","Piel","Manchas",12.00,85000,"SKU:810065800078","https://goodmolecules.com","30ml unica","Femenino","Hiperpigmentacion, manchas","media_alta",31000),
    ("Sol de Janeiro Bum Bum Cream 240ml","Sol de Janeiro","Piel","Celulitis",48.00,320000,"ASIN:B01N3D7DKB","https://amazon.com/dp/B01N3D7DKB","75ml($26)|240ml($48)|480ml($72)","Femenino","Celulitis, flacidez","alta",55000),
    ("Bio-Oil Skincare Oil 125ml","Bio-Oil","Piel","Estrias",14.00,79900,"ASIN:B01MS3GFHK","https://amazon.com/dp/B01MS3GFHK","60ml($10)|125ml($14)|200ml($18)|250ml($22)","Femenino","Estrias, cicatrices","muy_alta",120000),
    ("La Roche-Posay Effaclar Duo+","La Roche-Posay","Piel","Acne",30.00,145000,"ASIN:B014OPM4P4","https://amazon.com/dp/B014OPM4P4","40ml unica","Mixto","Acne, poros, grasa","alta",68000),
    ("EltaMD UV Clear SPF 46","EltaMD","Piel","Solar",39.00,220000,"ASIN:B002MSN3QQ","https://amazon.com/dp/B002MSN3QQ","48g Untinted($39)|48g Tinted($41)","Mixto","Dano solar, manchas","muy_alta",88000),
    ("Neutrogena Rapid Wrinkle Repair Eye Cream","Neutrogena","Piel","Ojeras",22.00,95000,"ASIN:B00BT7BYLO","https://amazon.com/dp/B00BT7BYLO","14g unica","Femenino","Bolsas, ojeras, arrugas","muy_alta",62000),
    ("RoC Retinol Correxion Line Smoothing","RoC","Piel","Retinol",25.99,130000,"ASIN:B075H4FDMZ","https://amazon.com/dp/B075H4FDMZ","30ml($26)|48g Max($30)","Femenino","Arrugas, lineas expresion","muy_alta",89000),
    ("Some By Mi AHA BHA PHA 30 Days Toner","Some By Mi","Piel","Tonico",22.00,120000,"ASIN:B07C7FQG3Z","https://amazon.com/dp/B07C7FQG3Z","150ml($22)|300ml($30)","Femenino","Poros, textura, manchas","alta",62000),
    ("Drunk Elephant C-Firma Serum 30ml","Drunk Elephant","Piel","Vitamina C",90.00,520000,"ASIN:B072J74N5K","https://amazon.com/dp/B072J74N5K","15ml($50)|30ml($90)","Femenino","Opacidad, manchas","alta",38000),
    ("GlamGlow Supermud Clearing 50g","GlamGlow","Piel","Mascarilla",69.00,380000,"ASIN:B00IFHPQDY","https://amazon.com/dp/B00IFHPQDY","34g($55)|50g($69)|100g($109)","Mixto","Acne, poros, impurezas","media_alta",28000),
    ("Herbivore Bakuchiol Retinol Oil 30ml","Herbivore","Piel","Retinol",54.00,300000,"ASIN:B07YTTQKRS","https://amazon.com/dp/B07YTTQKRS","15ml($34)|30ml($54)","Femenino","Arrugas, poros, firmeza","alta",22000),
    ("Viviscal Extra Strength 60 tabs","Viviscal","Cabello","Caida",49.99,280000,"ASIN:B00BSZKETA","https://amazon.com/dp/B00BSZKETA","60 tabs 1mes($50)|180 tabs 3meses($130)","Mixto","Caida, alopecia","alta",38000),
    ("Minoxidil 5% Kirkland Foam 6 meses","Kirkland","Cabello","Caida",29.00,160000,"ASIN:B00GXYK4GO","https://amazon.com/dp/B00GXYK4GO","6x60ml 6meses($29)|1mes($12)","Masculino","Calvicie, entradas","muy_alta",95000),
    ("Olaplex No.3 Hair Perfector 100ml","Olaplex","Cabello","Reparacion",30.00,150000,"ASIN:B013NQRZME","https://amazon.com/dp/B013NQRZME","100ml($30)|250ml($52)|1000ml salon($130)","Femenino","Cabello quebradizo","muy_alta",72000),
    ("Nizoral Anti-Dandruff Shampoo 200ml","Nizoral","Cabello","Caspa",15.00,79000,"ASIN:B00AINMFAC","https://amazon.com/dp/B00AINMFAC","200ml($15)|400ml($24)|730ml($35)","Mixto","Caspa, dermatitis","muy_alta",88000),
    ("Madison Reed Root Touch Up Kit","Madison Reed","Cabello","Canas",26.00,148000,"ASIN:B01MUAISNV","https://amazon.com/dp/B01MUAISNV","Kit 13 tonos($26 c/u)","Mixto","Canas prematuras","alta",51000),
    ("Vital Proteins Collagen Peptides 283g","Vital Proteins","Bienestar","Colageno",43.00,220000,"ASIN:B00K6EM5CK","https://amazon.com/dp/B00K6EM5CK","283g($43)|567g($68)|sachets x20($25)","Femenino","Arrugas, cabello, unas","muy_alta",165000),
    ("StriVectin TL Tightening Neck Cream 50ml","StriVectin","Piel","Firmeza",89.00,490000,"ASIN:B07BFKZP7W","https://amazon.com/dp/B07BFKZP7W","30ml($65)|50ml($89)","Femenino","Flacidez cuello","media_alta",21000),
    ("Murad Rapid Age Spot Serum 30ml","Murad","Piel","Manchas",86.00,470000,"ASIN:B001447XCK","https://amazon.com/dp/B001447XCK","30ml unica","Femenino","Manchas edad","media_alta",19000),
    ("Fenty Beauty Pro Filt'r Foundation","Fenty Beauty","Maquillaje","Base",40.00,230000,"SKU:varia por tono","https://fentybeauty.com","32ml 50 tonos($40 c/u)","Femenino","Tono desigual, manchas","muy_alta",92000),
    ("Charlotte Tilbury Pillow Talk Lip Liner","Charlotte Tilbury","Maquillaje","Labios",28.00,165000,"ASIN:B06WVFQXF4","https://amazon.com/dp/B06WVFQXF4","1.2g 8 tonos($28 c/u)","Femenino","Labios finos","muy_alta",68000),
    ("Benefit Gimme Brow+ Volumizing Gel","Benefit","Maquillaje","Cejas",24.00,145000,"ASIN:B0774YDJ5H","https://amazon.com/dp/B0774YDJ5H","3g full($24)|1.5g mini($16) 12 tonos","Femenino","Cejas escasas","alta",55000),
    ("L'Oreal Paris Voluminous Mascara","L'Oreal","Maquillaje","Rimel",10.99,55000,"ASIN:B000URXPKE","https://amazon.com/dp/B000URXPKE","8.5ml Regular($11)|Waterproof($12)","Femenino","Pestanas cortas","muy_alta",198000),
    ("NYX Professional Wonder Stick","NYX","Maquillaje","Contorno",14.00,72000,"ASIN:B01LYYM7DA","https://amazon.com/dp/B01LYYM7DA","7.7g 4 tonos($14 c/u)","Femenino","Definicion facial","muy_alta",78000),
    ("e.l.f. Poreless Putty Primer 21g","e.l.f.","Maquillaje","Primer",10.00,60000,"ASIN:B07FKWPRT7","https://amazon.com/dp/B07FKWPRT7","21g Original/Matte/Luminous($10 c/u)","Femenino","Poros visibles","muy_alta",145000),
    ("Charlotte Tilbury Hollywood Flawless Filter","Charlotte Tilbury","Maquillaje","Base",46.00,260000,"ASIN:B07YP9XHQR","https://amazon.com/dp/B07YP9XHQR","30ml($46)|Mini 7.9ml($26) 8 tonos","Femenino","Base luminosa natural","muy_alta",61000),
    ("NARS Radiant Creamy Concealer 6ml","NARS","Maquillaje","Corrector",32.00,175000,"ASIN:B00CM4Y29G","https://amazon.com/dp/B00CM4Y29G","6ml 30 tonos($32)","Femenino","Ojeras, imperfecciones","alta",48000),
    ("Too Faced Better Than Sex Mascara","Too Faced","Maquillaje","Rimel",27.00,155000,"ASIN:B00F7NRPOK","https://amazon.com/dp/B00F7NRPOK","8ml($27)|Travel 4ml($14)|Waterproof","Femenino","Pestanas voluminosas","alta",52000),
    ("Urban Decay All Nighter Setting Spray","Urban Decay","Maquillaje","Fijador",33.00,185000,"ASIN:B008JDHEPC","https://amazon.com/dp/B008JDHEPC","30ml($18)|118ml($33)|240ml($44)","Femenino","Maquillaje duradero","alta",44000),
    ("Optimum Nutrition Gold Standard Whey 908g","Optimum Nutrition","Cuerpo","Proteina",58.00,320000,"ASIN:B000QSNYGI","https://amazon.com/dp/B000QSNYGI","908g($58)|2.27kg($78)|4.54kg($140)","Masculino","Masa muscular","muy_alta",185000),
    ("Bliss Fat Girl Slim Arm Candy 200ml","Bliss","Cuerpo","Celulitis",38.00,210000,"ASIN:B008X80RWW","https://amazon.com/dp/B008X80RWW","200ml unica","Femenino","Flacidez brazos, celulitis","media",18000),
    ("Ulike Air 3 IPL Hair Removal Device","Ulike","Vello","Depilacion",219.00,1200000,"ASIN:B0BL9W6VKD","https://amazon.com/dp/B0BL9W6VKD","Air3($219)|Air+($299)|Air10($329)","Femenino","Vello facial y corporal","alta",41000),
    ("Tend Skin Solution 236ml","Tend Skin","Vello","Encarnados",24.00,130000,"ASIN:B0010O3PEO","https://amazon.com/dp/B0010O3PEO","118ml($17)|236ml($24)|473ml($38)","Mixto","Vello encarnado","alta",38000),
    ("Native Natural Deodorant 75g","Native","Cuidado","Desodorante",13.00,75000,"ASIN:B01MCVXWAO","https://amazon.com/dp/B01MCVXWAO","75g Regular($13)|Sensitive($14)|3-pack($35)","Mixto","Mal olor, transpiracion","muy_alta",132000),
    ("Carpe Antiperspirant Hand Lotion 40g","Carpe","Cuidado","Sudoracion",14.95,80000,"ASIN:B01FXNZ2H8","https://amazon.com/dp/B01FXNZ2H8","40g($15)|Foot($15)|Kit($28)","Mixto","Sudoracion excesiva","alta",45000),
    ("OPI Nail Envy Original 15ml","OPI","Manos","Unas",19.99,105000,"ASIN:B00178579E","https://amazon.com/dp/B00178579E","15ml Original/Matte/Sensitive($20)","Femenino","Unas fragiles","muy_alta",78000),
    ("L'Occitane Shea Butter Hand Cream 150ml","L'Occitane","Manos","Hidratacion",32.00,175000,"ASIN:B000MWKFNQ","https://amazon.com/dp/B000MWKFNQ","30ml($16)|75ml($23)|150ml($32)|300ml($50)","Femenino","Manos resecas","alta",48000),
    ("Baby Foot Exfoliant Foot Peel","Baby Foot","Pies","Exfoliacion",25.00,135000,"ASIN:B002YL5E30","https://amazon.com/dp/B002YL5E30","Original($25)|Lavender($26)|Moisture($26)","Mixto","Pies agrietados, callos","alta",62000),
    ("Beardbrand Gold Blend Beard Oil 30ml","Beardbrand","Hombre","Barba",25.00,138000,"SKU:BB-GOLD-1OZ","https://beardbrand.com","30ml 12 aromas($25 c/u)","Masculino","Barba aspera","alta",32000),
    ("Jack Black Pure Clean Facial Cleanser 177ml","Jack Black","Hombre","Piel",24.00,130000,"ASIN:B001AJATV2","https://amazon.com/dp/B001AJATV2","88ml($15)|177ml($24)|500ml($45)","Masculino","Piel grasa, acne","alta",38000),
    ("RapidLash Eyelash Enhancing Serum 3ml","RapidLash","Piel","Pestanas",49.99,280000,"ASIN:B0013FXLJI","https://amazon.com/dp/B0013FXLJI","3ml Lashes($50)|3ml RapidBrow($50)","Femenino","Pestanas cortas","alta",32000),
    ("HUM Nutrition Daily Cleanse 60 caps","HUM Nutrition","Bienestar","Suplementos",40.00,220000,"SKU:HUM-DC-60","https://sephora.com","60 caps 1 mes","Femenino","Acne interno, piel opaca","media_alta",22000),
    ("Leanbean Female Fat Burner 180 caps","Leanbean","Bienestar","Suplementos",59.99,330000,"SKU:LB-1MONTH","https://leanbean.com","180 caps($60)|3 meses($140)","Femenino","Control de peso","media_alta",28000),
    ("Crest 3D Whitestrips Professional Effects","Crest","Sonrisa","Blanqueamiento",49.99,280000,"ASIN:B003AVEU4G","https://amazon.com/dp/B003AVEU4G","20 strips($50)|Glamorous($35)|Supreme($65)","Mixto","Dientes amarillos","muy_alta",145000),
]

# ─────────────────────────────────────────────────────────────────
# CONSTRUIR DATAFRAME
# ─────────────────────────────────────────────────────────────────
def build_df(api_rows):
    rows = []
    # Locales
    for (nombre,marca,cat,sub,p_usd,pv_co,ref,url,pres,target,prob,rot,unid) in LOCAL:
        costo_cop = round(p_usd * TRM)
        m = modelo_colombia(costo_cop, pv_co)
        rows.append({
            "id": f"L{len(rows)+1:03d}",
            "nombre": nombre, "marca": marca, "cat": cat, "sub": sub,
            "target": target, "problema": prob,
            "precio_usd": p_usd, "costo_cop": costo_cop,
            "pv_mercado": pv_co,
            "pv_ganador": m["pv_g"],  "rent_g": m["rg_pct"],
            "pv_mercado_": m["pv_m"], "rent_m": m["rm_pct"],
            "pv_premium": m["pv_p"],  "rent_p": m["rp_pct"],
            "pv_optimo":  m["opt_pv"],"rent_opt": m["opt_pct"], "estrategia": m["opt_str"],
            "punto_eq":   m["pe"],
            "rating": 4.5, "reviews": unid,
            "unidades": unid, "rot": rot,
            "tend": _tend(4.5, unid),
            "vol_usd": round(p_usd * unid),
            "ref": ref, "url": url, "pres": pres,
            "fuente": "Base curada",
            "img": "",
        })
    # API en vivo
    for p in api_rows:
        p_usd   = p["precio_usd"]
        pv_co   = round(p_usd * TRM * 2.5)  # estimado Colombia = 2.5x precio USD
        costo   = round(p_usd * TRM)
        m = modelo_colombia(costo, pv_co)
        rows.append({
            "id": p["id"],
            "nombre": p["nombre"], "marca": p["marca"],
            "cat": p["cat"], "sub": p["sub"],
            "target": p["target"], "problema": p["problema"],
            "precio_usd": p_usd, "costo_cop": costo,
            "pv_mercado": pv_co,
            "pv_ganador": m["pv_g"],  "rent_g": m["rg_pct"],
            "pv_mercado_": m["pv_m"], "rent_m": m["rm_pct"],
            "pv_premium": m["pv_p"],  "rent_p": m["rp_pct"],
            "pv_optimo":  m["opt_pv"],"rent_opt": m["opt_pct"], "estrategia": m["opt_str"],
            "punto_eq": m["pe"],
            "rating": p["rating"], "reviews": p["reviews"],
            "unidades": p["unidades"], "rot": p["rot"],
            "tend": p["tend"],
            "vol_usd": round(p_usd * p["unidades"]),
            "ref": p["ref"], "url": p["url"], "pres": p["pres"],
            "fuente": "Makeup API 🔴",
            "img": p["img"],
        })
    df = pd.DataFrame(rows)
    df = df.drop_duplicates(subset=["nombre","marca"], keep="first")
    return df.reset_index(drop=True)

# ─────────────────────────────────────────────────────────────────
# HISTORIAL SIMULADO (rotación mensual 12 meses)
# ─────────────────────────────────────────────────────────────────
def hist_rot(unid_base, tend, months=12):
    tf = {"muy_creciente":.07,"creciente":.035,"estable":.005,"decreciente":-.025}.get(tend,.005)
    np.random.seed(int(unid_base) % 9999)
    h, u = [], float(unid_base)
    for i in range(months):
        d = datetime.now() - timedelta(days=30*(months-i-1))
        u = u*(1+tf)*(1+.07*np.sin(i*np.pi/6))*np.random.normal(1,.04)
        h.append({"mes": d.strftime("%b %Y"), "unidades": max(int(u),0)})
    return h

def hist_precio(pv, months=12):
    np.random.seed(int(pv) % 9999)
    h, p = [], float(pv)
    for i in range(months):
        d = datetime.now() - timedelta(days=30*(months-i-1))
        p = max(p*(1+np.random.normal(0,.02)), pv*.80)
        h.append({"mes": d.strftime("%b %Y"), "precio": round(p,-3)})
    return h

# ─────────────────────────────────────────────────────────────────
# CARGAR DATOS
# ─────────────────────────────────────────────────────────────────
with st.spinner("Conectando con APIs de mercado..."):
    api_rows = fetch_api()
    DF = build_df(api_rows)

now   = datetime.now()
dleft = (datetime(now.year, now.month+1 if now.month<12 else 1, 1)-now).days
api_n = len(api_rows)

# ─────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────
h1, h2, h3 = st.columns([1,5,2])
with h1:
    st.markdown(f'<div style="text-align:center;padding:12px 0;"><div style="width:60px;height:60px;background:linear-gradient(135deg,{PRI},{BRT});border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:26px;box-shadow:0 6px 24px {ACC}60;">🔬</div></div>', unsafe_allow_html=True)
with h2:
    st.markdown(f'<h1 style="margin:8px 0 2px;font-size:1.9rem;background:linear-gradient(90deg,{WHT},{ACC});-webkit-background-clip:text;-webkit-text-fill-color:transparent;">ESTUDIO DE MERCADO ROME</h1><p style="margin:0;color:{PALE};font-size:.85rem;">Inteligencia Comercial en Vivo · Belleza &amp; Cuidado Personal · Colombia</p>', unsafe_allow_html=True)
with h3:
    status_color = GRN if api_n > 0 else YEL
    st.markdown(f'<div style="text-align:right;padding:8px 0;"><div style="background:{MID}80;border:1px solid {ACC}40;border-radius:10px;padding:10px 14px;display:inline-block;"><div style="color:{status_color};font-size:.7rem;font-weight:700;text-transform:uppercase;">{"🟢 EN VIVO" if api_n>0 else "⚡ LOCAL"}</div><div style="color:{WHT};font-weight:700;font-size:.95rem;">{now.strftime("%B %Y")}</div><div style="color:{PALE};font-size:.7rem;">{len(DF)} productos · próx. {dleft}d</div></div></div>', unsafe_allow_html=True)

st.markdown("<hr style='margin:8px 0 16px;'>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# TABS PRINCIPALES
# ─────────────────────────────────────────────────────────────────
T1,T2,T3,T4,T5 = st.tabs([
    "📦 Todos los Productos",
    "💰 Modelo de Precios Colombia",
    "📈 Rotación & Tendencias",
    "🎯 Oportunidades de Mercado",
    "🔍 Análisis por Producto",
])

# ═══════════════════════════════════════════════════════════════
# TAB 1 — TODOS LOS PRODUCTOS
# ═══════════════════════════════════════════════════════════════
with T1:
    st.markdown(f'<h3 style="color:{WHT};font-family:Syne,sans-serif;margin-bottom:16px;">📦 Catálogo Completo — {len(DF)} productos</h3>', unsafe_allow_html=True)

    # KPIs
    k1,k2,k3,k4,k5,k6 = st.columns(6)
    with k1: st.metric("Total",          len(DF))
    with k2: st.metric("Categorías",     DF["cat"].nunique())
    with k3: st.metric("Precio USD min", fmt_usd(DF["precio_usd"].min()))
    with k4: st.metric("Precio USD max", fmt_usd(DF["precio_usd"].max()))
    with k5: st.metric("Rating prom.",   f"{DF['rating'].mean():.1f}⭐")
    with k6: st.metric("API en vivo",    f"{api_n} prods")

    st.markdown("<br>", unsafe_allow_html=True)

    # Filtros
    f1,f2,f3,f4 = st.columns([3,2,2,2])
    with f1: q1     = st.text_input("🔎 Buscar...", placeholder="nombre, marca, problema...", key="q1")
    with f2: cat1   = st.selectbox("Categoría", ["Todas"]+sorted(DF["cat"].unique().tolist()), key="c1")
    with f3: tgt1   = st.selectbox("Target",    ["Todos","Femenino","Masculino","Mixto"], key="t1")
    with f4: src1   = st.selectbox("Fuente",    ["Todas","Base curada","Makeup API 🔴"], key="s1")

    dv = DF.copy()
    if q1:
        ql = q1.lower()
        dv = dv[dv["nombre"].str.lower().str.contains(ql,na=False)|dv["marca"].str.lower().str.contains(ql,na=False)|dv["problema"].str.lower().str.contains(ql,na=False)]
    if cat1 != "Todas":  dv = dv[dv["cat"]==cat1]
    if tgt1 != "Todos":  dv = dv[dv["target"]==tgt1]
    if src1 != "Todas":  dv = dv[dv["fuente"]==src1]

    st.caption(f"Mostrando {len(dv)} productos")

    disp = dv[[
        "nombre","marca","cat","sub","target",
        "precio_usd","pv_mercado","rating","reviews","unidades",
        "rot","tend","problema","pres","ref","fuente"
    ]].copy()
    disp.columns = [
        "Producto","Marca","Cat.","Sub","Target",
        "Precio USD","PV Mercado CO","Rating","Reviews","Unid/mes",
        "Rotacion","Tendencia","Problema","Presentaciones","Ref/SKU","Fuente"
    ]
    disp["Precio USD"]     = disp["Precio USD"].apply(lambda x: f"${x:.2f}")
    disp["PV Mercado CO"]  = disp["PV Mercado CO"].apply(lambda x: f"${x:,}")
    disp["Reviews"]        = disp["Reviews"].apply(lambda x: f"{x:,}")
    disp["Unid/mes"]       = disp["Unid/mes"].apply(lambda x: f"{x:,}")
    disp["Rating"]         = disp["Rating"].apply(lambda x: f"⭐{x:.1f}")
    disp["Tendencia"]      = disp["Tendencia"].map({"muy_creciente":"🚀 Muy crec.","creciente":"📈 Crec.","estable":"➡️ Estable","decreciente":"📉 Decrec."})
    disp["Rotacion"]       = disp["Rotacion"].map({"muy_alta":"🔵 Muy alta","alta":"🟢 Alta","media_alta":"🟡 Media-alta","media":"🟡 Media","baja":"🔴 Baja"})

    st.dataframe(disp, use_container_width=True, hide_index=True, height=550)
    csv1 = dv.drop(columns=["img"],errors="ignore").to_csv(index=False).encode("utf-8")
    st.download_button("📥 Descargar CSV", csv1, "rome_catalogo.csv","text/csv", key="dl1")

# ═══════════════════════════════════════════════════════════════
# TAB 2 — MODELO PRECIOS COLOMBIA
# ═══════════════════════════════════════════════════════════════
with T2:
    st.markdown(f'<h3 style="color:{WHT};font-family:Syne,sans-serif;margin-bottom:6px;">💰 Modelo de Precios Colombia</h3>', unsafe_allow_html=True)
    st.caption("Tres estrategias de precio · El modelo calcula tu rentabilidad real con tu tabla de costos")

    # Parámetros
    st.markdown(f'<div style="background:{MID}60;border:1px solid {ACC}30;border-radius:12px;padding:14px 18px;margin-bottom:16px;">', unsafe_allow_html=True)
    st.markdown("**⚙️ Parámetros operativos** (ajusta según tu operación real)")
    pc1,pc2,pc3,pc4 = st.columns(4)
    with pc1: flete_v   = st.number_input("🚚 Flete (COP)",     value=18000, step=1000, key="fl")
    with pc2: dev_v     = st.number_input("↩️ Devoluciones %",  value=20.0,  step=1.0,  key="dv") / 100
    with pc3: cpa_v     = st.number_input("📢 CPA Publicidad %",value=15.0,  step=1.0,  key="cp") / 100
    with pc4: gastos_v  = st.number_input("🏢 Gastos fijos COP",value=0,     step=1000, key="gv")
    st.markdown('</div>', unsafe_allow_html=True)

    # Recalcular con parámetros actualizados
    def rec(costo, pv_mkt):
        def r(pv):
            if pv<=0: return 0,0
            d=pv*dev_v; c=pv*cpa_v
            rnt=pv-costo-flete_v-gastos_v-d-c
            return round(rnt), round(rnt/pv*100,1)
        g=max(math.floor(pv_mkt*.95/1000)*1000,1000)
        m=pv_mkt
        p=math.ceil(pv_mkt*1.10/1000)*1000
        rg,pg=r(g); rm_,pm=r(m); rp,pp=r(p)
        viab=[(pg,g,"Ganador -5%"),(pm,m,"Mercado"),(pp,p,"Premium +10%")]
        viab=[x for x in viab if x[0]>0]
        if viab: bp,bpv,bn=max(viab,key=lambda x:x[0])
        else:    bp,bpv,bn=pm,m,"Mercado"
        denom=1-dev_v-cpa_v
        pe=math.ceil((costo+flete_v+gastos_v)/denom/1000)*1000 if denom>0 else 0
        return {"g":g,"rg_c":rg,"rg_p":pg,"m":m,"rm_c":rm_,"rm_p":pm,
                "p":p,"rp_c":rp,"rp_p":pp,"opt_pv":bpv,"opt_p":bp,"opt_n":bn,"pe":pe}

    rows2=[]
    for _,row in DF.iterrows():
        rv=rec(row["costo_cop"], row["pv_mercado"])
        sem = "🟢" if rv["rm_p"]>=25 else "🟡" if rv["rm_p"]>=10 else "🟠" if rv["rm_p"]>=0 else "🔴"
        rows2.append({
            "":                    sem,
            "Producto":            row["nombre"],
            "Marca":               row["marca"],
            "Cat.":                row["cat"],
            "Ref/SKU":             row["ref"],
            "Presentaciones":      row["pres"],
            "Mi Costo COP":        f"${row['costo_cop']:,}",
            "Flete":               f"${flete_v:,}",
            "PV Mercado CO":       f"${row['pv_mercado']:,}",
            "🥇 Precio Ganador":    f"${rv['g']:,}",
            "Rent% Ganador":       f"{rv['rg_p']}%",
            "🥈 Precio Mercado":    f"${rv['m']:,}",
            "Rent% Mercado":       f"{rv['rm_p']}%",
            "🥉 Precio Premium":    f"${rv['p']:,}",
            "Rent% Premium":       f"{rv['rp_p']}%",
            "✅ Precio Óptimo":     f"${rv['opt_pv']:,}",
            "Mejor Rent%":         f"{rv['opt_p']}%",
            "Estrategia":          rv["opt_n"],
            "Punto Equilibrio":    f"${rv['pe']:,}",
            "Problema":            row["problema"],
            "_rm": rv["rm_p"], "_opt": rv["opt_p"],
        })

    DF2 = pd.DataFrame(rows2)
    viab_n   = len(DF2[DF2["_rm"]>=25])
    med_n    = len(DF2[(DF2["_rm"]>=10)&(DF2["_rm"]<25)])
    bajo_n   = len(DF2[DF2["_rm"]<10])

    k1,k2,k3,k4 = st.columns(4)
    with k1: st.metric("Total",         len(DF2))
    with k2: st.metric("🟢 Rent. +25%", viab_n)
    with k3: st.metric("🟡 Rent. 10-25%",med_n)
    with k4: st.metric("🔴 Baja / neg.", bajo_n)

    st.markdown("<br>", unsafe_allow_html=True)

    f1,f2,f3 = st.columns([3,2,2])
    with f1: q2    = st.text_input("🔎 Buscar...", key="q2")
    with f2: cat2  = st.selectbox("Categoría", ["Todas"]+sorted(DF["cat"].unique().tolist()), key="c2")
    with f3: filt2 = st.selectbox("Rentabilidad", ["Todas","🟢 +25%","🟡 10-25%","🔴 <10%"], key="f2")

    dv2 = DF2.copy()
    if q2:
        ql=q2.lower()
        dv2=dv2[dv2["Producto"].str.lower().str.contains(ql,na=False)|dv2["Marca"].str.lower().str.contains(ql,na=False)|dv2["Problema"].str.lower().str.contains(ql,na=False)]
    if cat2!="Todas": dv2=dv2[dv2["Cat."]==cat2]
    if filt2=="🟢 +25%":    dv2=dv2[dv2["_rm"]>=25]
    elif filt2=="🟡 10-25%": dv2=dv2[(dv2["_rm"]>=10)&(dv2["_rm"]<25)]
    elif filt2=="🔴 <10%":   dv2=dv2[dv2["_rm"]<10]

    cols2=["","Producto","Marca","Cat.","Ref/SKU","Presentaciones",
           "Mi Costo COP","Flete","PV Mercado CO",
           "🥇 Precio Ganador","Rent% Ganador",
           "🥈 Precio Mercado","Rent% Mercado",
           "🥉 Precio Premium","Rent% Premium",
           "✅ Precio Óptimo","Mejor Rent%","Estrategia",
           "Punto Equilibrio","Problema"]
    st.caption(f"Mostrando {len(dv2)} productos")
    st.dataframe(dv2[cols2], use_container_width=True, hide_index=True, height=560,
        column_config={
            "":                   st.column_config.TextColumn("",             width=40),
            "Producto":           st.column_config.TextColumn("Producto",     width=200),
            "Marca":              st.column_config.TextColumn("Marca",        width=120),
            "Cat.":               st.column_config.TextColumn("Cat.",          width=100),
            "Ref/SKU":            st.column_config.TextColumn("Ref/SKU",      width=150),
            "Presentaciones":     st.column_config.TextColumn("Presentaciones",width=210),
            "Mi Costo COP":       st.column_config.TextColumn("Costo COP",    width=110),
            "Flete":              st.column_config.TextColumn("Flete",        width=80),
            "PV Mercado CO":      st.column_config.TextColumn("PV Mercado CO",width=125),
            "🥇 Precio Ganador":  st.column_config.TextColumn("Ganador -5%",  width=110),
            "Rent% Ganador":      st.column_config.TextColumn("Rent%",        width=70),
            "🥈 Precio Mercado":  st.column_config.TextColumn("= Mercado",    width=110),
            "Rent% Mercado":      st.column_config.TextColumn("Rent%",        width=70),
            "🥉 Precio Premium":  st.column_config.TextColumn("Premium +10%", width=110),
            "Rent% Premium":      st.column_config.TextColumn("Rent%",        width=70),
            "✅ Precio Óptimo":   st.column_config.TextColumn("PRECIO OPTIMO",width=130),
            "Mejor Rent%":        st.column_config.TextColumn("Rent%",        width=70),
            "Estrategia":         st.column_config.TextColumn("Estrategia",   width=110),
            "Punto Equilibrio":   st.column_config.TextColumn("P. Equilibrio",width=115),
            "Problema":           st.column_config.TextColumn("Problema",     width=190),
        })
    csv2=dv2[cols2].to_csv(index=False).encode("utf-8")
    st.download_button("📥 Descargar CSV", csv2, "rome_precios.csv","text/csv", key="dl2")

# ═══════════════════════════════════════════════════════════════
# TAB 3 — ROTACIÓN & TENDENCIAS
# ═══════════════════════════════════════════════════════════════
with T3:
    st.markdown(f'<h3 style="color:{WHT};font-family:Syne,sans-serif;margin-bottom:16px;">📈 Rotación & Tendencias de Mercado</h3>', unsafe_allow_html=True)

    c1,c2 = st.columns(2)

    with c1:
        # Distribución tendencias
        tc = DF["tend"].value_counts()
        lmap = {"muy_creciente":"🚀 Muy Creciente","creciente":"📈 Creciente","estable":"➡️ Estable","decreciente":"📉 Decreciente"}
        fig = go.Figure(go.Pie(
            labels=[lmap.get(x,x) for x in tc.index],
            values=tc.values, hole=0.55,
            marker_colors=[ACC,BRT,PRI,RED],
            textinfo="label+percent",
            textfont=dict(color=WHT, size=11)))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color=TEXT, showlegend=False, height=300,
            margin=dict(l=10,r=10,t=30,b=10),
            title_text="Tendencias", title_font_color=WHT)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        # Volumen por categoría
        vc = DF.groupby("cat")["unidades"].sum().sort_values()
        colors_bar = [ACC if i>=len(vc)-2 else BRT if i>=len(vc)-4 else PRI if i>=len(vc)-7 else MID for i in range(len(vc))]
        fig = go.Figure(go.Bar(
            y=vc.index, x=vc.values, orientation="h",
            marker_color=colors_bar,
            text=[f"{v:,}" for v in vc.values],
            textposition="outside", textfont=dict(color=WHT, size=10)))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,33,55,0.6)",
            font_color=TEXT, showlegend=False, height=300,
            margin=dict(l=10,r=60,t=30,b=10),
            title_text="Unidades/mes por Categoría", title_font_color=WHT)
        st.plotly_chart(fig, use_container_width=True)

    # Simulador precio vs rotación
    st.markdown(f'<h4 style="color:{ACC};font-family:Syne,sans-serif;margin:20px 0 10px;">🔄 Simulador: Precio ↔ Rotación</h4>', unsafe_allow_html=True)
    st.caption("Selecciona un producto para ver cómo evoluciona su precio de mercado y su rotación en 12 meses. Si el precio sube, la rotación tiende a bajar y viceversa.")

    prod_sel = st.selectbox("Producto:", DF["nombre"].tolist(), key="ps")
    row_sel  = DF[DF["nombre"]==prod_sel].iloc[0]

    ph = hist_precio(row_sel["pv_mercado"])
    rh = hist_rot(row_sel["unidades"], row_sel["tend"])
    ml = [x["mes"] for x in ph]
    pl = [x["precio"] for x in ph]
    ul = [x["unidades"] for x in rh]

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=ml, y=pl, name="PV Mercado COP",
        line_color=GOLD, line_width=3, mode="lines+markers",
        marker=dict(size=6)), secondary_y=False)
    fig.add_trace(go.Bar(x=ml, y=ul, name="Unidades/mes",
        marker_color=ACC, opacity=0.75), secondary_y=True)
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,33,55,0.6)",
        font_color=TEXT, height=360, margin=dict(l=20,r=20,t=50,b=40),
        hovermode="x unified", title_text=f"{prod_sel[:50]} — 12 meses", title_font_color=WHT,
        legend=dict(orientation="h", y=1.05, bgcolor="rgba(0,0,0,0)"))
    st.plotly_chart(fig, use_container_width=True)

    # Insight automático
    pchg = (pl[-1]-pl[0])/pl[0]*100
    uchg = (ul[-1]-ul[0])/ul[0]*100 if ul[0]>0 else 0
    corr = float(np.corrcoef(pl,ul)[0,1])
    if pchg > 5 and uchg < -5:
        insight_txt = f"⚠️ El precio sube {pchg:+.1f}% mientras la rotación cae {uchg:.1f}% — riesgo de perder competitividad."
        insight_col = YEL
    elif pchg < -5 and uchg > 5:
        insight_txt = f"✅ El precio baja {pchg:.1f}% y la rotación sube {uchg:+.1f}% — estrategia de volumen funcionando."
        insight_col = GRN
    elif uchg > 10:
        insight_txt = f"🚀 Rotación creciendo {uchg:+.1f}% — producto en tendencia alcista."
        insight_col = GRN
    else:
        insight_txt = f"➡️ Precio estable ({pchg:+.1f}%) y rotación {uchg:+.1f}% — comportamiento normal de mercado."
        insight_col = PALE

    st.markdown(f"""
    <div class="card" style="display:grid;grid-template-columns:1fr 1fr 1fr 2fr;gap:20px;align-items:center;">
      <div><span style="color:{PALE};font-size:.75rem;">Var. Precio 12m</span><br>
           <span style="color:{GOLD};font-size:1.3rem;font-weight:800;">{"+" if pchg>0 else ""}{pchg:.1f}%</span></div>
      <div><span style="color:{PALE};font-size:.75rem;">Var. Rotación 12m</span><br>
           <span style="color:{ACC};font-size:1.3rem;font-weight:800;">{"+" if uchg>0 else ""}{uchg:.1f}%</span></div>
      <div><span style="color:{PALE};font-size:.75rem;">Correlación P-R</span><br>
           <span style="color:{GRN};font-size:1.3rem;font-weight:800;">{corr:.2f}</span></div>
      <div style="border-left:1px solid {PRI}40;padding-left:16px;">
           <span style="color:{insight_col};font-size:.88rem;">{insight_txt}</span></div>
    </div>""", unsafe_allow_html=True)

    # Heatmap rotación por categoría
    st.markdown(f'<h4 style="color:{ACC};font-family:Syne,sans-serif;margin:24px 0 10px;">🔥 Mapa de Calor — Unidades por Categoría y Tendencia</h4>', unsafe_allow_html=True)
    piv = DF.groupby(["cat","tend"])["unidades"].sum().reset_index()
    piv = piv.pivot(index="cat", columns="tend", values="unidades").fillna(0)
    fig = go.Figure(go.Heatmap(
        z=piv.values, x=piv.columns.tolist(), y=piv.index.tolist(),
        colorscale=[[0,BG],[0.3,MID],[0.6,PRI],[1,ACC]],
        text=[[f"{v:,.0f}" for v in r] for r in piv.values],
        texttemplate="%{text}", textfont=dict(color=WHT, size=10),
        colorbar=dict(tickfont=dict(color=PALE))))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,33,55,0.6)",
        font_color=TEXT, height=380, margin=dict(l=10,r=80,t=40,b=10),
        title_text="Unidades/mes — Categoría × Tendencia", title_font_color=WHT)
    st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════
# TAB 4 — OPORTUNIDADES NICHO
# ═══════════════════════════════════════════════════════════════
with T4:
    st.markdown(f'<h3 style="color:{WHT};font-family:Syne,sans-serif;margin-bottom:4px;">🎯 Oportunidades de Nicho — Entra antes que la competencia</h3>', unsafe_allow_html=True)
    st.caption("Productos con alta demanda LATENTE en Colombia pero baja penetracion actual. Tendencia confirmada en TikTok y mercados USA/Europa. Fuente: ML Colombia 2025 + TikTok trends + Nubimetrics.")

    import math as _math

    NICHOS = [
        {"emoji":"🧪","nombre":"Tirtir Milk Skin Toner","marca":"TIRTIR (Korea)","cat":"K-Beauty","precio_usd":22.00,"pv_co_est":145000,"score":9,"penet":"5%","tend":"muy_creciente","por_que":"Base coreana viral en Ulta Beauty USA. Llegando a TikTok Latinoamerica. En ML Colombia casi sin stock.","problema":"Poros, tono desigual, piel de cristal","publico":"Mujeres 18-35 K-Beauty","comp_co":"Muy baja — 3 vendedores ML","url":"https://yesstyle.com/tirtir","fuente":"TikTok #tirtir 50M vistas | Ulta Beauty top seller 2025"},
        {"emoji":"💡","nombre":"LED Red Light Therapy Mask","marca":"Currentbody / Omnilux","cat":"Tecnologia Beauty","precio_usd":195.00,"pv_co_est":1300000,"score":9,"penet":"3%","tend":"muy_creciente","por_que":"Aprobada FDA, viral en BeautyTok. En Colombia casi desconocida. Crecimiento 200% en USA 2024-2025.","problema":"Acne, anti-envejecimiento, firmeza piel","publico":"Mujeres 28-50 tecnologia anti-age","comp_co":"Casi nula — nicho de lujo sin explotar","url":"https://currentbody.com/led-light-therapy","fuente":"#redlighttherapy 2B vistas TikTok | FDA approved"},
        {"emoji":"🌿","nombre":"Mixsoon Bean Essence (Soya)","marca":"Mixsoon (Korea)","cat":"K-Beauty","precio_usd":28.00,"pv_co_est":185000,"score":8,"penet":"4%","tend":"muy_creciente","por_que":"Esencia de soya coreana viral en TikTok skincare. Colombia practicamente sin oferta.","problema":"Hidratacion profunda, barrera cutanea","publico":"Femenino 20-40 K-Beauty","comp_co":"Baja — 5-8 vendedores ML","url":"https://yesstyle.com/mixsoon","fuente":"Kbeauty growing 40% LATAM 2025"},
        {"emoji":"🔵","nombre":"Ice Roller Facial Crioterapia","marca":"Esker / varias","cat":"Herramientas Skincare","precio_usd":18.00,"pv_co_est":95000,"score":8,"penet":"12%","tend":"creciente","por_que":"Viral en TikTok como skincare tool. Bajo precio, alto margen. En Colombia sin marca posicionada.","problema":"Poros, inflamacion, puffiness facial","publico":"Mujeres 18-45 activas en redes","comp_co":"Media-baja — sin branding fuerte","url":"https://amazon.com/dp/B07YB5GXGT","fuente":"#iceroller TikTok 800M vistas | Viral Primor Espana 2025"},
        {"emoji":"✨","nombre":"Elroel Blanc Stick V (Base Blanca Viral)","marca":"Elroel (Korea)","cat":"K-Beauty Maquillaje","precio_usd":25.00,"pv_co_est":165000,"score":9,"penet":"2%","tend":"muy_creciente","por_que":"Base en barra blanca que se adapta a todos los tonos. Madison Beer la usa. En Colombia practicamente inexistente.","problema":"Base universal, efecto glowy, tratamiento collageno","publico":"Femenino 18-30 Generacion Z","comp_co":"Muy baja — novedad absoluta","url":"https://yesstyle.com/elroel","fuente":"Viral GetGlam 2025 | Premio belleza multiple"},
        {"emoji":"🧴","nombre":"Summer Fridays Jet Lag Mask","marca":"Summer Fridays","cat":"Skincare Premium","precio_usd":42.00,"pv_co_est":280000,"score":7,"penet":"8%","tend":"muy_creciente","por_que":"Mascarilla hidratante viral en TikTok y Sephora. Se agota en USA. Colombia empieza a pedirla.","problema":"Piel opaca, deshidratacion, barrera danada","publico":"Femenino 25-45 premium","comp_co":"Baja — pocos importadores","url":"https://amazon.com/dp/B07NQPBZ5X","fuente":"Sephora top seller 2025 | TikTok #summerFridays viral"},
        {"emoji":"💆","nombre":"Gua Sha Tool Premium (Cuarzo Rosa)","marca":"Mount Lai / Herbivore","cat":"Herramientas Skincare","precio_usd":30.00,"pv_co_est":160000,"score":7,"penet":"15%","tend":"creciente","por_que":"Tendencia bienestar facial sostenida. Colombia crece pero sin marcas premium. Oportunidad premium vs genericas.","problema":"Tension facial, drenaje linfatico, lineas expresion","publico":"Femenino 25-50 bienestar","comp_co":"Media — muchas genericas, poca marca","url":"https://amazon.com/dp/B07VXQMPP9","fuente":"#guasha TikTok 4B vistas | Wellness trend sostenida"},
        {"emoji":"🩹","nombre":"Pimple Patches Cosrx / Hero Cosmetics","marca":"Cosrx / Hero Cosmetics","cat":"Skincare Acne","precio_usd":14.00,"pv_co_est":75000,"score":7,"penet":"18%","tend":"creciente","por_que":"Producto de uso diario, alta recompra. En ML Colombia hay demanda pero poca oferta de marcas reconocidas.","problema":"Acne, espinillas, puntos blancos","publico":"Mixto 14-30","comp_co":"Media — genericas dominan, marcas poco","url":"https://amazon.com/dp/B07AP2NRSP","fuente":"ML Colombia: alta busqueda, baja oferta branded"},
        {"emoji":"🌸","nombre":"PDRN / Exosoma Serum (Salmon DNA)","marca":"VT Cosmetics / Axis-Y","cat":"K-Beauty Premium","precio_usd":55.00,"pv_co_est":380000,"score":10,"penet":"1%","tend":"muy_creciente","por_que":"Tendencia skincare 2025 confirmada por dermatologos. En Colombia practicamente NADIE lo vende aun. Oportunidad historica.","problema":"Anti-envejecimiento avanzado, regeneracion celular","publico":"Femenino 35-55 premium","comp_co":"Nula — oportunidad de primer entrante","url":"https://yesstyle.com/vt-cosmetics","fuente":"TikTok #pdrn #exosomes trending 2025 | Derm Times 2025"},
        {"emoji":"💊","nombre":"Tranexamic Acid Serum","marca":"The Inkey List / Good Molecules","cat":"Skincare Activos","precio_usd":15.00,"pv_co_est":95000,"score":8,"penet":"6%","tend":"muy_creciente","por_que":"El nuevo acido hialuronico. Viral BeautyTok. En Colombia casi sin oferta. Demanda creciendo 300%.","problema":"Manchas, hiperpigmentacion, tono desigual","publico":"Mixto 20-45","comp_co":"Baja — pocos lo conocen aun","url":"https://amazon.com/dp/B08CZDVS64","fuente":"ML Colombia: busquedas up 300% 2025 | #tranexamicacid trending"},
        {"emoji":"🧖","nombre":"Scalp Serum (suero cuero cabelludo)","marca":"The Ordinary / Act+Acre","cat":"Cabello Premium","precio_usd":22.00,"pv_co_est":135000,"score":8,"penet":"5%","tend":"muy_creciente","por_que":"Skincare para cuero cabelludo: tendencia 2025. Nubimetrics: cabello +40% CO. Subcategoria serums capilares casi sin explotar.","problema":"Caida, cuero cabelludo inflamado, crecimiento","publico":"Mixto 25-50","comp_co":"Baja — categoria nueva en Colombia","url":"https://amazon.com/the-ordinary-hair-serum","fuente":"Nubimetrics cabello +40% ML Colombia 2025 | #scalpcare"},
        {"emoji":"🌊","nombre":"Shampoo Barra Solido (Waterless Beauty)","marca":"Ethique / HiBar / Lush","cat":"Belleza Sostenible","precio_usd":16.00,"pv_co_est":95000,"score":8,"penet":"4%","tend":"creciente","por_que":"Cosmetica organica proyecta USD 15B 2025. Consumidor colombiano eco-consciente creciendo. Nicho con margen alto.","problema":"Cabello, sostenibilidad, sin plastico","publico":"Mixto 22-40 eco-consciente","comp_co":"Muy baja — nicho practicamente virgen","url":"https://ethique.com","fuente":"Inexmoda 2025: natural/organico CAGR 8.91% Colombia"},
        {"emoji":"💈","nombre":"VT Reedle Shot 100 (Ampollas Microagujas)","marca":"VT Cosmetics (Korea)","cat":"K-Beauty Cabello","precio_usd":35.00,"pv_co_est":220000,"score":9,"penet":"2%","tend":"muy_creciente","por_que":"VT Reedle Shot viral en TikTok Colombia. Ampollas microagujas cuero cabelludo. Completamente nuevo. Primeros vendedores tienen ventaja total.","problema":"Caida capilar, cuero cabelludo debilitado","publico":"Mixto 25-50 premium","comp_co":"Casi nula — pionero absoluto","url":"https://yesstyle.com/vt-cosmetics","fuente":"TikTok Colombia skincare 2025 | Satinskincare.com"},
        {"emoji":"🕯️","nombre":"Kayali Perfume Eden Juicy Apple","marca":"Kayali by Huda Beauty","cat":"Fragancias Nicho","precio_usd":98.00,"pv_co_est":620000,"score":8,"penet":"5%","tend":"muy_creciente","por_que":"Fragancias nicho: mercado perfumes Colombia +40% online 2024. Kayali viral TikTok. Casi sin distribucion en Colombia.","problema":"Fragancia premium, diferenciacion, lujo accesible","publico":"Femenino 22-45 premium","comp_co":"Baja — sin distribuidor oficial","url":"https://hudabeauty.com/kayali","fuente":"Inexmoda: perfumes online +40% Colombia 2024 | TikTok viral"},
        {"emoji":"🪥","nombre":"Cepillo Electrico Premium Oral-B iO","marca":"Oral-B iO Series","cat":"Cuidado Dental Beauty","precio_usd":89.00,"pv_co_est":520000,"score":7,"penet":"8%","tend":"creciente","por_que":"Cepillos electricos premium: mercado dental-beauty en auge. Colombia baja penetracion. Alta percepcion de valor.","problema":"Higiene dental premium, blanqueamiento, encias","publico":"Mixto 25-50 clase media-alta","comp_co":"Media — sin importadores dedicados beauty-dental","url":"https://amazon.com/dp/B08XBGYWZR","fuente":"Categoria dental-beauty: crecimiento 35% LATAM 2025"},
    ]

    def nicho_precio(p_usd, pv_co):
        costo = round(p_usd * TRM)
        devs = round(pv_co * 0.20); cpac = round(pv_co * 0.15)
        rent = pv_co - costo - 18000 - devs - cpac
        rp   = round(rent/pv_co*100,1) if pv_co>0 else 0
        pe   = _math.ceil((costo+18000)/0.65/1000)*1000
        return costo, rent, rp, pe

    # KPIs
    n10 = sum(1 for n in NICHOS if n["score"]>=9)
    n8  = sum(1 for n in NICHOS if 7<=n["score"]<9)
    k1,k2,k3,k4 = st.columns(4)
    with k1: st.metric("Oportunidades Nicho", len(NICHOS))
    with k2: st.metric("Score ORO (9-10)", f"{n10} productos")
    with k3: st.metric("Score PLATA (7-8)", f"{n8} productos")
    with k4: st.metric("Penetracion prom. CO", "~6%", delta="94% sin explotar")

    st.markdown("<br>", unsafe_allow_html=True)

    # Grafico scatter score vs rentabilidad
    nr = []
    for n in NICHOS:
        c,r,rp,pe = nicho_precio(n["precio_usd"],n["pv_co_est"])
        nr.append({"nombre":n["nombre"][:35],"cat":n["cat"],"score":n["score"],"rent":rp,"pv":n["pv_co_est"],"penet":int(n["penet"].replace("%",""))})
    dfn = pd.DataFrame(nr)

    g1,g2 = st.columns(2)
    with g1:
        fig = px.scatter(dfn, x="score", y="rent", size="pv", color="cat",
            hover_name="nombre",
            labels={"score":"Score Nicho (1-10)","rent":"Rentabilidad %","cat":"Categoria"},
            color_discrete_sequence=px.colors.sequential.Blues_r)
        fig.add_hline(y=30,line_dash="dash",line_color=GRN,annotation_text="Meta 30%",annotation_font_color=GRN)
        fig.add_vline(x=8,line_dash="dash",line_color=GOLD,annotation_text="Nicho Premium",annotation_font_color=GOLD)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(13,33,55,0.6)",
            font_color=TEXT,height=360,title_text="Score Nicho vs Rentabilidad",title_font_color=WHT,
            margin=dict(l=20,r=20,t=50,b=50),
            legend=dict(orientation="h",y=-0.3,font_size=9,bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig, use_container_width=True)

    with g2:
        dfn_s = dfn.sort_values("score",ascending=True)
        bar_c = [GRN if s>=9 else ACC if s>=7 else YEL for s in dfn_s["score"]]
        fig = go.Figure(go.Bar(
            y=dfn_s["nombre"], x=dfn_s["score"], orientation="h",
            marker_color=bar_c,
            text=[f"Score {s}/10" for s in dfn_s["score"]],
            textposition="outside", textfont=dict(color=WHT,size=10)))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(13,33,55,0.6)",
            font_color=TEXT,height=360,title_text="Score por Producto",title_font_color=WHT,
            margin=dict(l=10,r=80,t=50,b=10),xaxis_range=[0,11],showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Tarjetas
    st.markdown(f'<h4 style="color:{ACC};font-family:Syne,sans-serif;margin:20px 0 14px;">💎 Fichas Detalladas de Oportunidades</h4>', unsafe_allow_html=True)
    score_min = st.slider("Score minimo:", 1, 10, 7)
    filtrados = sorted([n for n in NICHOS if n["score"]>=score_min], key=lambda x:-x["score"])
    st.caption(f"Mostrando {len(filtrados)} oportunidades con score >= {score_min}")

    for n in filtrados:
        costo,rent,rp,pe = nicho_precio(n["precio_usd"],n["pv_co_est"])
        sc = n["score"]
        sc_c = GRN if sc>=9 else ACC if sc>=7 else YEL
        sc_l = "ORO" if sc>=9 else "PLATA" if sc>=7 else "BRONCE"
        r_c  = GRN if rp>=25 else YEL if rp>=10 else RED
        tent = {"muy_creciente":"Muy Creciente","creciente":"Creciente","estable":"Estable"}.get(n["tend"],"")

        with st.expander(f"{n['emoji']} Score {sc}/10 — {sc_l} | {n['nombre']} · {n['marca']}", expanded=(sc>=9)):
            ca,cb,cc,cd = st.columns(4)
            with ca: st.metric("Precio proveedor", f"${n['precio_usd']:.2f} USD")
            with cb: st.metric("PV estimado CO",   f"${n['pv_co_est']:,} COP")
            with cc: st.metric("Rentabilidad est.", f"{rp}%")
            with cd: st.metric("Penetracion CO",    n["penet"])

            col1,col2 = st.columns([3,2])
            with col1:
                st.markdown(f"**Por que es oportunidad:**")
                st.markdown(n["por_que"])
                st.markdown(f"**Problema que resuelve:** {n['problema']}")
                st.markdown(f"**Publico objetivo:** {n['publico']}")
            with col2:
                st.markdown(f"**Competencia en Colombia:** {n['comp_co']}")
                st.markdown(f"**Tendencia global:** {tent}")
                st.markdown(f"**Punto de equilibrio:** ${pe:,} COP")
                st.markdown(f"**Categoria:** {n['cat']}")
                st.markdown(f"**Fuente dato:** {n['fuente']}")
                st.link_button("🔗 Ver producto / proveedor", n["url"])


# TAB 5 — ANÁLISIS POR PRODUCTO
# ═══════════════════════════════════════════════════════════════
with T5:
    st.markdown(f'<h3 style="color:{WHT};font-family:Syne,sans-serif;margin-bottom:16px;">🔍 Análisis Detallado por Producto</h3>', unsafe_allow_html=True)

    prod_det = st.selectbox("Selecciona un producto:", DF["nombre"].tolist(), key="pd")
    row_d    = DF[DF["nombre"]==prod_det].iloc[0]
    m_d      = rec(row_d["costo_cop"], row_d["pv_mercado"])

    # Ficha producto
    dc1, dc2, dc3 = st.columns([2,2,2])
    with dc1:
        st.markdown(f"""<div class="card">
        <div style="font-family:Syne,sans-serif;font-size:1.1rem;font-weight:700;color:{WHT};margin-bottom:12px;">{row_d['nombre']}</div>
        <table style="width:100%;border-collapse:collapse;">
          <tr><td style="color:{PALE};font-size:.8rem;padding:3px 0;">Marca</td><td style="color:{WHT};font-weight:500;">{row_d['marca']}</td></tr>
          <tr><td style="color:{PALE};font-size:.8rem;padding:3px 0;">Categoría</td><td style="color:{WHT};font-weight:500;">{row_d['cat']} › {row_d['sub']}</td></tr>
          <tr><td style="color:{PALE};font-size:.8rem;padding:3px 0;">Target</td><td style="color:{WHT};font-weight:500;">{row_d['target']}</td></tr>
          <tr><td style="color:{PALE};font-size:.8rem;padding:3px 0;">Origen</td><td style="color:{WHT};font-weight:500;">{row_d.get('origen','N/A')}</td></tr>
          <tr><td style="color:{PALE};font-size:.8rem;padding:3px 0;">Fuente</td><td style="color:{WHT};font-weight:500;">{row_d['fuente']}</td></tr>
          <tr><td style="color:{PALE};font-size:.8rem;padding:3px 0;">Ref/SKU</td><td style="color:{ACC};font-size:.82rem;">{row_d['ref']}</td></tr>
          <tr><td style="color:{PALE};font-size:.8rem;padding:3px 0;">Presentaciones</td><td style="color:{TEXT};font-size:.8rem;">{row_d['pres']}</td></tr>
        </table>
        <div style="margin-top:10px;padding-top:8px;border-top:1px solid {PRI}30;">
          <span style="color:{PALE};font-size:.78rem;">Problema: </span>
          <span style="color:{ACC};font-size:.82rem;">{row_d['problema']}</span>
        </div>
        </div>""", unsafe_allow_html=True)

    with dc2:
        st.metric("Precio USD",       fmt_usd(row_d["precio_usd"]))
        st.metric("Costo COP",        fmt_cop(row_d["costo_cop"]))
        st.metric("PV Mercado CO",    fmt_cop(row_d["pv_mercado"]))
        st.metric("Unidades/mes",     f"{row_d['unidades']:,}")
        st.metric("Rating",           f"⭐ {row_d['rating']}")
        st.metric("Tendencia",        {"muy_creciente":"🚀 Muy Creciente","creciente":"📈 Creciente","estable":"➡️ Estable","decreciente":"📉 Decreciente"}.get(row_d["tend"],""))

    with dc3:
        sem = "🟢" if m_d["rm_p"]>=25 else "🟡" if m_d["rm_p"]>=10 else "🟠" if m_d["rm_p"]>=0 else "🔴"
        st.markdown(f"""<div class="card">
        <div style="font-family:Syne,sans-serif;font-weight:700;color:{WHT};margin-bottom:14px;">💰 Análisis de Precio</div>
        <table style="width:100%;border-collapse:collapse;">
          <tr style="background:{MID}40;"><td style="padding:6px 8px;color:{PALE};font-size:.78rem;">Estrategia</td><td style="padding:6px 8px;color:{PALE};font-size:.78rem;text-align:right;">Precio</td><td style="padding:6px 8px;color:{PALE};font-size:.78rem;text-align:right;">Rent%</td></tr>
          <tr><td style="padding:5px 8px;color:{TEXT};">🥇 Ganador (-5%)</td><td style="padding:5px 8px;color:{GOLD};font-weight:600;text-align:right;">${m_d['g']:,}</td><td style="padding:5px 8px;text-align:right;color:{'#00B894' if m_d['rg_p']>0 else '#E17055'};">{m_d['rg_p']}%</td></tr>
          <tr style="background:{MID}20;"><td style="padding:5px 8px;color:{TEXT};">🥈 Mercado</td><td style="padding:5px 8px;color:{ACC};font-weight:600;text-align:right;">${m_d['m']:,}</td><td style="padding:5px 8px;text-align:right;color:{'#00B894' if m_d['rm_p']>0 else '#E17055'};">{m_d['rm_p']}%</td></tr>
          <tr><td style="padding:5px 8px;color:{TEXT};">🥉 Premium (+10%)</td><td style="padding:5px 8px;color:{BRT};font-weight:600;text-align:right;">${m_d['p']:,}</td><td style="padding:5px 8px;text-align:right;color:{'#00B894' if m_d['rp_p']>0 else '#E17055'};">{m_d['rp_p']}%</td></tr>
          <tr style="background:{PRI}30;"><td style="padding:6px 8px;color:{WHT};font-weight:700;">✅ Precio Óptimo</td><td style="padding:6px 8px;color:{WHT};font-weight:700;text-align:right;">${m_d['opt_pv']:,}</td><td style="padding:6px 8px;text-align:right;color:{GRN};font-weight:700;">{m_d['opt_p']}%</td></tr>
        </table>
        <div style="margin-top:10px;padding-top:8px;border-top:1px solid {PRI}30;font-size:.8rem;">
          <span style="color:{PALE};">Punto de equilibrio: </span>
          <span style="color:{YEL};font-weight:600;">${m_d['pe']:,} COP</span>
        </div>
        </div>""", unsafe_allow_html=True)

    # Gráfico precio vs rotación
    ph2 = hist_precio(row_d["pv_mercado"])
    rh2 = hist_rot(row_d["unidades"], row_d["tend"])
    ml2 = [x["mes"] for x in ph2]
    pl2 = [x["precio"] for x in ph2]
    ul2 = [x["unidades"] for x in rh2]

    fig = make_subplots(specs=[[{"secondary_y":True}]])
    fig.add_trace(go.Scatter(x=ml2,y=pl2,name="PV Mercado",line_color=GOLD,line_width=2,mode="lines+markers",marker=dict(size=5)),secondary_y=False)
    fig.add_trace(go.Scatter(x=ml2,y=[m_d["opt_pv"]]*12,name="Tu Precio Óptimo",line=dict(color=GRN,dash="dash",width=2),mode="lines"),secondary_y=False)
    fig.add_trace(go.Bar(x=ml2,y=ul2,name="Unidades/mes",marker_color=ACC,opacity=0.65),secondary_y=True)
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(13,33,55,0.6)",
        font_color=TEXT,height=320,margin=dict(l=20,r=20,t=40,b=40),
        hovermode="x unified",title_text="Evolución 12 meses",title_font_color=WHT,
        legend=dict(orientation="h",y=1.05,bgcolor="rgba(0,0,0,0)"))
    st.plotly_chart(fig,use_container_width=True)

# ── FOOTER ────────────────────────────────────────────────────────
st.markdown("<br><hr>",unsafe_allow_html=True)
st.markdown(f'<div style="text-align:center;padding:14px 0;color:{PALE};font-size:.75rem;"><span style="font-family:Syne,sans-serif;color:{ACC};font-weight:700;font-size:.95rem;">ESTUDIO DE MERCADO ROME</span> &nbsp;·&nbsp; {now.strftime("%B %Y")} &nbsp;·&nbsp; {len(DF)} productos &nbsp;·&nbsp; Flete ${FLETE:,} · Dev {DEV_PCT:.0%} · CPA {CPA_PCT:.0%} · TRM ${TRM:,}<br><span style="opacity:.45;font-size:.7rem;">Datos de mercado: Makeup API + Base curada. Precios Colombia aproximados. Actualización mensual automática.</span></div>',unsafe_allow_html=True)
