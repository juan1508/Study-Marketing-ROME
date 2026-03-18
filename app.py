"""ESTUDIO DE MERCADO ROME — app.py — single file, Plotly 6 compatible"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import requests

st.set_page_config(page_title="Estudio de Mercado ROME", page_icon="🔵",
                   layout="wide", initial_sidebar_state="expanded")

# ── Colores ───────────────────────────────────────────────────────
BG    = "#0A1628"
DARK  = "#0D2137"
MID   = "#1A3A5C"
PRI   = "#1E5FAD"
BRT   = "#2E86DE"
ACC   = "#54A0FF"
PALE  = "#A8D8F0"
WHITE = "#EEF6FF"
GOLD  = "#FFC300"
GREEN = "#00B894"
YEL   = "#FDCB6E"
RED   = "#E17055"
TEXT  = "#DDE8F5"

# ── CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500&display=swap');
.stApp{background:linear-gradient(135deg,#0A1628,#0D2137,#0B1E35);}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;color:#DDE8F5;}
h1,h2,h3{font-family:'Syne',sans-serif;font-weight:800;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#0D2137,#1A3A5C);border-right:1px solid #1E5FAD40;}
div[data-testid="metric-container"]{background:linear-gradient(135deg,#1A3A5CCC,#1E5FAD33)!important;border:1px solid #54A0FF40!important;border-radius:16px!important;padding:20px!important;}
div[data-testid="metric-container"] label{color:#A8D8F0!important;font-size:.82rem!important;text-transform:uppercase;letter-spacing:.05em;}
[data-testid="stMetricValue"]{color:#EEF6FF!important;font-family:'Syne',sans-serif!important;font-weight:800!important;font-size:1.6rem!important;}
.stTabs [data-baseweb="tab-list"]{background:#1A3A5C80!important;border-radius:12px!important;padding:4px!important;}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:#A8D8F0!important;border-radius:10px!important;}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#1E5FAD,#2E86DE)!important;color:white!important;font-weight:600!important;}
.stButton>button{background:linear-gradient(135deg,#1E5FAD,#2E86DE)!important;color:white!important;border:none!important;border-radius:10px!important;font-weight:600!important;}
.stSelectbox div[data-baseweb="select"]>div{background:#1A3A5C!important;border-color:#1E5FAD60!important;color:#DDE8F5!important;border-radius:10px!important;}
.stTextInput input{background:#1A3A5C!important;border-color:#1E5FAD60!important;color:#DDE8F5!important;border-radius:10px!important;}
.stRadio label,.stMultiSelect label,section[data-testid="stSidebar"] p,section[data-testid="stSidebar"] label{color:#DDE8F5!important;}
.streamlit-expanderHeader{background:#1A3A5C80!important;border:1px solid #1E5FAD30!important;border-radius:10px!important;color:#DDE8F5!important;}
hr{border-color:#1E5FAD30!important;}
#MainMenu,footer,header{visibility:hidden;}
.card{background:linear-gradient(135deg,#1A3A5C,#0D2137);border:1px solid #54A0FF40;border-radius:12px;padding:16px;margin-bottom:12px;}
.ba{background:#00B89425;color:#00B894;border:1px solid #00B89450;border-radius:20px;padding:2px 10px;font-size:.75rem;font-weight:600;}
.bm{background:#FDCB6E25;color:#FDCB6E;border:1px solid #FDCB6E50;border-radius:20px;padding:2px 10px;font-size:.75rem;font-weight:600;}
.bb{background:#E1705525;color:#E17055;border:1px solid #E1705550;border-radius:20px;padding:2px 10px;font-size:.75rem;font-weight:600;}
</style>""", unsafe_allow_html=True)

# ── Plotly layout base — NO axis styling, fully compatible ────────
def TH(**extra):
    d = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,33,55,0.7)",
             font_color=TEXT, font_family="DM Sans",
             title_font_color=WHITE, title_font_family="Syne", title_font_size=15,
             margin=dict(l=10,r=10,t=50,b=10))
    d.update(extra)
    return d

# ── Helpers ───────────────────────────────────────────────────────
def fmt(v):
    if v>=1e6: return f"${v/1e6:.1f}M"
    if v>=1e3: return f"${v/1e3:.0f}K"
    return f"${v:.2f}"

def rbadge(r):
    m={"muy_alta":("Muy Alta","a"),"alta":("Alta","a"),"media_alta":("Media-Alta","m"),"media":("Media","m"),"baja":("Baja","b")}
    l,c=m.get(r,("N/A","m"))
    cls={"a":"ba","m":"bm","b":"bb"}[c]
    return f'<span class="{cls}">{l}</span>'

def ticon(t):
    return {"muy_creciente":"Muy Creciente","creciente":"Creciente",
            "estable":"Estable","decreciente":"Decreciente"}.get(t,t)

def gp(base,months=12):
    np.random.seed(int(base*100)%9999)
    h,p=[],float(base)
    for i in range(months):
        d=datetime.now()-timedelta(days=30*(months-i-1))
        p=max(p*(1+np.random.normal(0,.025)),base*.72)
        h.append({"mes":d.strftime("%b %Y"),"precio":round(p,2)})
    return h

def gu(base,tend,months=12):
    tf={"muy_creciente":.07,"creciente":.035,"estable":.005,"decreciente":-.025}.get(tend,.005)
    np.random.seed(int(base)%9999)
    h,u=[],float(base)
    for i in range(months):
        d=datetime.now()-timedelta(days=30*(months-i-1))
        u=u*(1+tf)*(1+.08*np.sin(i*np.pi/6))*np.random.normal(1,.04)
        h.append({"mes":d.strftime("%b %Y"),"unidades":max(int(u),0)})
    return h

# ── Productos locales ─────────────────────────────────────────────
LP=[
    {"id":"SK01","cat":"Piel","sub":"Sueros","nombre":"The Ordinary Niacinamide 10pct + Zinc","marca":"The Ordinary","origen":"Canada","precio":6.90,"mercado":8.50,"unidades":85000,"rating":4.6,"reviews":125000,"tend":"estable","rot":"muy_alta","desc":"Suero Niacinamida 10pct para poros y manchas","target":"Mixto","problema":"Poros, manchas, acne","plat":["Amazon","ASOS","Sephora"]},
    {"id":"SK02","cat":"Piel","sub":"Sueros","nombre":"Paulas Choice BHA 2pct Liquid Exfoliant","marca":"Paulas Choice","origen":"USA","precio":34.00,"mercado":36.00,"unidades":42000,"rating":4.8,"reviews":98000,"tend":"creciente","rot":"alta","desc":"Exfoliante quimico BHA para poros","target":"Mixto","problema":"Poros, acne, opacidad","plat":["Paulas Choice","Amazon","Dermstore"]},
    {"id":"SK03","cat":"Piel","sub":"Vitamina C","nombre":"SkinCeuticals C E Ferulic","marca":"SkinCeuticals","origen":"USA","precio":182.00,"mercado":185.00,"unidades":18000,"rating":4.7,"reviews":45000,"tend":"estable","rot":"media","desc":"Vitamina C profesional antioxidante premium","target":"Femenino","problema":"Manchas, envejecimiento","plat":["Dermstore","Sephora","Amazon"]},
    {"id":"SK04","cat":"Piel","sub":"Retinol","nombre":"Differin Adapalene Gel 0.1pct","marca":"Differin","origen":"USA","precio":15.50,"mercado":18.00,"unidades":95000,"rating":4.5,"reviews":187000,"tend":"muy_creciente","rot":"muy_alta","desc":"Retinoide OTC mas potente del mercado","target":"Mixto","problema":"Acne, cicatrices, arrugas","plat":["Amazon","Walmart","Target"]},
    {"id":"SK05","cat":"Piel","sub":"Hidratacion","nombre":"CeraVe Moisturizing Cream","marca":"CeraVe","origen":"USA","precio":19.00,"mercado":21.00,"unidades":210000,"rating":4.8,"reviews":320000,"tend":"estable","rot":"muy_alta","desc":"Crema hidratante con ceramidas","target":"Mixto","problema":"Sequedad, barrera cutanea","plat":["Amazon","Walmart","CVS"]},
    {"id":"SK06","cat":"Piel","sub":"Manchas","nombre":"Good Molecules Discoloration Serum","marca":"Good Molecules","origen":"USA","precio":12.00,"mercado":14.00,"unidades":31000,"rating":4.4,"reviews":22000,"tend":"creciente","rot":"media_alta","desc":"Suero despigmentante acido tranexamico","target":"Femenino","problema":"Hiperpigmentacion, manchas","plat":["Ulta","Amazon"]},
    {"id":"SK07","cat":"Piel","sub":"Celulitis","nombre":"Sol de Janeiro Brazilian Bum Bum Cream","marca":"Sol de Janeiro","origen":"Brasil","precio":48.00,"mercado":50.00,"unidades":55000,"rating":4.6,"reviews":78000,"tend":"muy_creciente","rot":"alta","desc":"Crema reafirmante con cafeina y cupuacu","target":"Femenino","problema":"Celulitis, flacidez","plat":["Sephora","Amazon","Ulta"]},
    {"id":"SK08","cat":"Piel","sub":"Estrias","nombre":"Bio-Oil Skincare Oil","marca":"Bio-Oil","origen":"Sudafrica","precio":14.00,"mercado":16.00,"unidades":120000,"rating":4.5,"reviews":145000,"tend":"estable","rot":"muy_alta","desc":"Aceite para estrias y cicatrices","target":"Femenino","problema":"Estrias, cicatrices","plat":["Amazon","Walmart","Target"]},
    {"id":"SK09","cat":"Piel","sub":"Acne","nombre":"La Roche-Posay Effaclar Duo Plus","marca":"La Roche-Posay","origen":"Francia","precio":30.00,"mercado":33.00,"unidades":68000,"rating":4.6,"reviews":89000,"tend":"creciente","rot":"alta","desc":"Tratamiento anti-imperfecciones clinico","target":"Mixto","problema":"Acne, poros, grasa","plat":["Amazon","Dermstore","Ulta"]},
    {"id":"SK10","cat":"Piel","sub":"Protector Solar","nombre":"EltaMD UV Clear SPF 46","marca":"EltaMD","origen":"USA","precio":39.00,"mercado":42.00,"unidades":88000,"rating":4.7,"reviews":112000,"tend":"muy_creciente","rot":"muy_alta","desc":"Protector solar con niacinamida","target":"Mixto","problema":"Dano solar, manchas","plat":["Amazon","Dermstore","Ulta"]},
    {"id":"CA01","cat":"Cabello","sub":"Caida","nombre":"Viviscal Extra Strength Hair Growth","marca":"Viviscal","origen":"USA","precio":49.99,"mercado":54.00,"unidades":38000,"rating":4.3,"reviews":62000,"tend":"creciente","rot":"alta","desc":"Suplemento clinico para crecimiento capilar","target":"Mixto","problema":"Caida, alopecia","plat":["Amazon","Ulta","CVS"]},
    {"id":"CA02","cat":"Cabello","sub":"Caida","nombre":"Minoxidil 5pct Kirkland Foam","marca":"Kirkland","origen":"USA","precio":29.00,"mercado":35.00,"unidades":95000,"rating":4.4,"reviews":134000,"tend":"muy_creciente","rot":"muy_alta","desc":"Minoxidil espuma 5pct para calvicie","target":"Masculino","problema":"Calvicie, entradas","plat":["Amazon","Costco","Walmart"]},
    {"id":"CA03","cat":"Cabello","sub":"Reparacion","nombre":"Olaplex No.3 Hair Perfector","marca":"Olaplex","origen":"USA","precio":30.00,"mercado":32.00,"unidades":72000,"rating":4.6,"reviews":115000,"tend":"estable","rot":"muy_alta","desc":"Reparador enlaces moleculares","target":"Femenino","problema":"Cabello quebradizo, danado","plat":["Sephora","Amazon","Ulta"]},
    {"id":"CA04","cat":"Cabello","sub":"Caspa","nombre":"Nizoral Anti-Dandruff Shampoo","marca":"Nizoral","origen":"USA","precio":15.00,"mercado":17.00,"unidades":88000,"rating":4.6,"reviews":98000,"tend":"estable","rot":"muy_alta","desc":"Champu medicado ketoconazol 1pct","target":"Mixto","problema":"Caspa, dermatitis","plat":["Amazon","CVS","Walgreens"]},
    {"id":"CA05","cat":"Cabello","sub":"Canas","nombre":"Madison Reed Root Touch Up","marca":"Madison Reed","origen":"USA","precio":26.00,"mercado":28.00,"unidades":51000,"rating":4.5,"reviews":67000,"tend":"creciente","rot":"alta","desc":"Retoque raices sin amoniaco","target":"Mixto","problema":"Canas prematuras","plat":["Amazon","Ulta","Target"]},
    {"id":"EN01","cat":"Envejecimiento","sub":"Arrugas","nombre":"RoC Retinol Correxion Line Smoothing","marca":"RoC","origen":"Francia","precio":25.99,"mercado":28.00,"unidades":89000,"rating":4.4,"reviews":118000,"tend":"estable","rot":"muy_alta","desc":"Crema retinol puro para arrugas","target":"Femenino","problema":"Arrugas, lineas expresion","plat":["Amazon","Walmart","CVS"]},
    {"id":"EN02","cat":"Envejecimiento","sub":"Colageno","nombre":"Vital Proteins Collagen Peptides","marca":"Vital Proteins","origen":"USA","precio":43.00,"mercado":48.00,"unidades":165000,"rating":4.5,"reviews":210000,"tend":"muy_creciente","rot":"muy_alta","desc":"Colageno hidrolizado bovino en polvo","target":"Femenino","problema":"Arrugas, cabello, unas","plat":["Amazon","Target","Whole Foods"]},
    {"id":"EN03","cat":"Envejecimiento","sub":"Firmeza","nombre":"StriVectin-TL Tightening Neck Cream","marca":"StriVectin","origen":"USA","precio":89.00,"mercado":95.00,"unidades":21000,"rating":4.4,"reviews":28000,"tend":"creciente","rot":"media_alta","desc":"Crema reafirmante cuello y escote","target":"Femenino","problema":"Flacidez cuello","plat":["Sephora","Amazon","Ulta"]},
    {"id":"EN04","cat":"Envejecimiento","sub":"Manchas Edad","nombre":"Murad Rapid Age Spot Correcting Serum","marca":"Murad","origen":"USA","precio":86.00,"mercado":90.00,"unidades":19000,"rating":4.5,"reviews":24000,"tend":"creciente","rot":"media_alta","desc":"Suero corrector manchas edad","target":"Femenino","problema":"Manchas edad, hiperpigmentacion","plat":["Sephora","Amazon","Murad"]},
    {"id":"MQ01","cat":"Maquillaje","sub":"Base","nombre":"Fenty Beauty Pro Filtr Foundation","marca":"Fenty Beauty","origen":"USA","precio":40.00,"mercado":42.00,"unidades":92000,"rating":4.6,"reviews":138000,"tend":"muy_creciente","rot":"muy_alta","desc":"Base 50 tonos inclusivos","target":"Femenino","problema":"Tono desigual, manchas","plat":["Sephora","Harvey Nichols"]},
    {"id":"MQ02","cat":"Maquillaje","sub":"Labios","nombre":"Charlotte Tilbury Pillow Talk Lip Liner","marca":"Charlotte Tilbury","origen":"UK","precio":28.00,"mercado":30.00,"unidades":68000,"rating":4.7,"reviews":89000,"tend":"muy_creciente","rot":"muy_alta","desc":"Delineador labial nude mas vendido","target":"Femenino","problema":"Labios finos, sin definicion","plat":["Sephora","Nordstrom"]},
    {"id":"MQ03","cat":"Maquillaje","sub":"Ojos","nombre":"Benefit Gimme Brow+ Volumizing Gel","marca":"Benefit","origen":"USA","precio":24.00,"mercado":26.00,"unidades":55000,"rating":4.5,"reviews":72000,"tend":"creciente","rot":"alta","desc":"Gel de cejas volumizador","target":"Femenino","problema":"Cejas escasas","plat":["Sephora","Ulta","Amazon"]},
    {"id":"MQ04","cat":"Maquillaje","sub":"Rimel","nombre":"LOreal Voluminous Original Mascara","marca":"LOreal","origen":"Francia","precio":10.99,"mercado":13.00,"unidades":198000,"rating":4.5,"reviews":245000,"tend":"estable","rot":"muy_alta","desc":"Mascara de pestanas voluminizadora","target":"Femenino","problema":"Pestanas cortas","plat":["Amazon","Walmart","CVS"]},
    {"id":"MQ05","cat":"Maquillaje","sub":"Contorno","nombre":"NYX Professional Makeup Wonder Stick","marca":"NYX","origen":"USA","precio":14.00,"mercado":15.00,"unidades":78000,"rating":4.4,"reviews":91000,"tend":"creciente","rot":"muy_alta","desc":"Stick contorno e iluminador 2 en 1","target":"Femenino","problema":"Definicion facial","plat":["Amazon","Ulta","Target"]},
    {"id":"MQ06","cat":"Maquillaje","sub":"Primer","nombre":"elf Poreless Putty Primer","marca":"elf","origen":"USA","precio":10.00,"mercado":12.00,"unidades":145000,"rating":4.5,"reviews":189000,"tend":"muy_creciente","rot":"muy_alta","desc":"Primer suavizante poros ultra popular","target":"Femenino","problema":"Poros visibles, maquillaje duradero","plat":["Amazon","Target","Ulta"]},
    {"id":"SP01","cat":"Skincare Premium","sub":"K-Beauty","nombre":"Some By Mi AHA BHA PHA Toner","marca":"Some By Mi","origen":"Korea","precio":22.00,"mercado":25.00,"unidades":62000,"rating":4.5,"reviews":78000,"tend":"muy_creciente","rot":"alta","desc":"Tonico triple acido K-Beauty","target":"Femenino","problema":"Poros, textura, manchas","plat":["Amazon","YesStyle","Ulta"]},
    {"id":"SP02","cat":"Skincare Premium","sub":"Serum","nombre":"Drunk Elephant C-Firma Fresh Day Serum","marca":"Drunk Elephant","origen":"USA","precio":90.00,"mercado":95.00,"unidades":38000,"rating":4.6,"reviews":52000,"tend":"muy_creciente","rot":"alta","desc":"Vitamina C 15pct + E + acido ferulico","target":"Femenino","problema":"Opacidad, manchas","plat":["Sephora","Amazon","Dermstore"]},
    {"id":"SP03","cat":"Skincare Premium","sub":"Mascarilla","nombre":"GlamGlow Supermud Clearing Treatment","marca":"GlamGlow","origen":"USA","precio":69.00,"mercado":72.00,"unidades":28000,"rating":4.4,"reviews":38000,"tend":"estable","rot":"media_alta","desc":"Mascarilla barro activado para acne","target":"Mixto","problema":"Acne, poros, impurezas","plat":["Sephora","Amazon","Ulta"]},
    {"id":"CO01","cat":"Cuerpo","sub":"Masa Muscular","nombre":"Optimum Nutrition Gold Standard Whey","marca":"Optimum Nutrition","origen":"USA","precio":58.00,"mercado":65.00,"unidades":185000,"rating":4.7,"reviews":290000,"tend":"estable","rot":"muy_alta","desc":"Proteina de suero de leche premium","target":"Masculino","problema":"Falta masa muscular","plat":["Amazon","GNC","Bodybuilding.com"]},
    {"id":"CO02","cat":"Cuerpo","sub":"Flacidez","nombre":"Bliss Fat Girl Slim Arm Candy","marca":"Bliss","origen":"USA","precio":38.00,"mercado":42.00,"unidades":18000,"rating":4.1,"reviews":12000,"tend":"creciente","rot":"media","desc":"Crema reafirmante brazos con cafeina","target":"Femenino","problema":"Flacidez brazos, celulitis","plat":["Amazon","Ulta"]},
    {"id":"VE01","cat":"Vello","sub":"Depilacion","nombre":"Ulike Air 3 IPL Hair Removal Device","marca":"Ulike","origen":"Global","precio":219.00,"mercado":250.00,"unidades":41000,"rating":4.4,"reviews":52000,"tend":"muy_creciente","rot":"alta","desc":"Dispositivo IPL depilacion laser en casa","target":"Femenino","problema":"Vello facial, corporal","plat":["Amazon","ulike.com"]},
    {"id":"VE02","cat":"Vello","sub":"Vello Encarnado","nombre":"Tend Skin Solution","marca":"Tend Skin","origen":"USA","precio":24.00,"mercado":26.00,"unidades":38000,"rating":4.5,"reviews":45000,"tend":"estable","rot":"alta","desc":"Solucion para pelos encarnados","target":"Mixto","problema":"Vello encarnado, irritacion","plat":["Amazon","Ulta","Sephora"]},
    {"id":"SU01","cat":"Sudoracion","sub":"Desodorante","nombre":"Native Natural Deodorant","marca":"Native","origen":"USA","precio":13.00,"mercado":15.00,"unidades":132000,"rating":4.4,"reviews":178000,"tend":"muy_creciente","rot":"muy_alta","desc":"Desodorante natural sin aluminio","target":"Mixto","problema":"Mal olor, transpiracion","plat":["Amazon","Target","Walmart"]},
    {"id":"SU02","cat":"Sudoracion","sub":"Hiperhidrosis","nombre":"Carpe Antiperspirant Hand Lotion","marca":"Carpe","origen":"USA","precio":14.95,"mercado":16.00,"unidades":45000,"rating":4.3,"reviews":38000,"tend":"muy_creciente","rot":"alta","desc":"Locion antitranspirante clinica","target":"Mixto","problema":"Sudoracion excesiva manos","plat":["Amazon","Target"]},
    {"id":"MA01","cat":"Manos y Unas","sub":"Unas Fragiles","nombre":"OPI Nail Envy Original","marca":"OPI","origen":"USA","precio":19.99,"mercado":22.00,"unidades":78000,"rating":4.5,"reviews":95000,"tend":"estable","rot":"muy_alta","desc":"Endurecedor de unas profesional","target":"Femenino","problema":"Unas fragiles, quebradizas","plat":["Amazon","Ulta","Sally Beauty"]},
    {"id":"MA02","cat":"Manos y Unas","sub":"Manos Envejecidas","nombre":"LOccitane Shea Butter Hand Cream","marca":"LOccitane","origen":"Francia","precio":32.00,"mercado":34.00,"unidades":48000,"rating":4.8,"reviews":72000,"tend":"estable","rot":"alta","desc":"Crema de manos con karite","target":"Femenino","problema":"Manos resecas, envejecidas","plat":["Sephora","Amazon"]},
    {"id":"PI01","cat":"Pies","sub":"Pies Agrietados","nombre":"Baby Foot Exfoliant Foot Peel","marca":"Baby Foot","origen":"Japon","precio":25.00,"mercado":28.00,"unidades":62000,"rating":4.4,"reviews":88000,"tend":"creciente","rot":"alta","desc":"Peeling quimico exfoliante para pies","target":"Mixto","problema":"Pies agrietados, callos","plat":["Amazon","Ulta","Target"]},
    {"id":"MI01","cat":"Mirada","sub":"Ojeras","nombre":"Neutrogena Rapid Wrinkle Repair Eye Cream","marca":"Neutrogena","origen":"USA","precio":22.00,"mercado":25.00,"unidades":62000,"rating":4.4,"reviews":82000,"tend":"estable","rot":"muy_alta","desc":"Contorno de ojos con retinol","target":"Femenino","problema":"Bolsas, ojeras, arrugas","plat":["Amazon","Walmart","CVS"]},
    {"id":"MI02","cat":"Mirada","sub":"Pestanas","nombre":"RapidLash Eyelash Enhancing Serum","marca":"RapidLash","origen":"USA","precio":49.99,"mercado":55.00,"unidades":32000,"rating":4.4,"reviews":28000,"tend":"creciente","rot":"alta","desc":"Suero clinico crecimiento pestanas","target":"Femenino","problema":"Pestanas cortas, ralas","plat":["Amazon","Ulta","CVS"]},
    {"id":"FM01","cat":"Cuidado Masculino","sub":"Barba","nombre":"Beardbrand Gold Beard Oil","marca":"Beardbrand","origen":"USA","precio":25.00,"mercado":28.00,"unidades":32000,"rating":4.6,"reviews":28000,"tend":"creciente","rot":"alta","desc":"Aceite de barba premium natural","target":"Masculino","problema":"Barba aspera, piel irritada","plat":["beardbrand.com","Amazon"]},
    {"id":"FM02","cat":"Cuidado Masculino","sub":"Piel","nombre":"Jack Black Pure Clean Facial Cleanser","marca":"Jack Black","origen":"USA","precio":24.00,"mercado":26.00,"unidades":38000,"rating":4.5,"reviews":42000,"tend":"creciente","rot":"alta","desc":"Limpiador facial masculino botanico","target":"Masculino","problema":"Piel grasa, poros, acne","plat":["Amazon","Sephora","Nordstrom"]},
    {"id":"BI01","cat":"Bienestar","sub":"Suplementos Piel","nombre":"HUM Nutrition Daily Cleanse","marca":"HUM Nutrition","origen":"USA","precio":40.00,"mercado":44.00,"unidades":22000,"rating":4.2,"reviews":15000,"tend":"muy_creciente","rot":"media_alta","desc":"Suplemento belleza interior piel clara","target":"Femenino","problema":"Acne interno, piel opaca","plat":["Sephora","Amazon"]},
    {"id":"BI02","cat":"Bienestar","sub":"Perdida Peso","nombre":"Leanbean Fat Burner for Women","marca":"Leanbean","origen":"UK","precio":59.99,"mercado":65.00,"unidades":28000,"rating":4.1,"reviews":19000,"tend":"creciente","rot":"media_alta","desc":"Quemador grasa femenino natural","target":"Femenino","problema":"Exceso peso, metabolismo","plat":["leanbean.com","Amazon"]},
]

# ── Makeup API ────────────────────────────────────────────────────
MSEARCHES=[("foundation","Maquillaje","Base","Femenino","Tono desigual"),
           ("lip_liner","Maquillaje","Labios","Femenino","Labios finos"),
           ("mascara","Maquillaje","Ojos","Femenino","Pestanas cortas"),
           ("bronzer","Maquillaje","Contorno","Femenino","Definicion facial"),
           ("primer","Maquillaje","Primer","Femenino","Poros visibles"),
           ("blush","Maquillaje","Colorete","Femenino","Falta de color"),
           ("eyeshadow","Maquillaje","Sombras","Femenino","Ojos sin profundidad"),
           ("moisturizer","Piel","Hidratacion","Mixto","Sequedad"),
           ("serum","Skincare Premium","Serum","Femenino","Manchas, opacidad"),
           ("nail_polish","Manos y Unas","Esmalte","Femenino","Unas sin color")]

PM={"Maquillaje":["Sephora","Ulta","Amazon"],"Piel":["Amazon","Dermstore","Ulta"],
    "Skincare Premium":["Sephora","Dermstore","Amazon"],"Cabello":["Amazon","Ulta"],
    "Envejecimiento":["Sephora","Amazon","CVS"],"Cuerpo":["Amazon","GNC"],
    "Bienestar":["Amazon","Whole Foods","iHerb"],"Vello":["Amazon","Ulta"],
    "Sudoracion":["Amazon","Target","Walmart"],"Manos y Unas":["Amazon","Ulta","CVS"],
    "Pies":["Amazon","Ulta","Target"],"Cuidado Masculino":["Amazon","Sephora"],
    "Mirada":["Sephora","Ulta","Amazon"]}

OM={"loreal":"Francia","lancome":"Francia","nuxe":"Francia","la roche":"Francia",
    "charlotte tilbury":"UK","the ordinary":"Canada","deciem":"Canada",
    "fenty":"USA","nyx":"USA","maybelline":"USA","revlon":"USA","neutrogena":"USA",
    "cerave":"USA","benefit":"USA","urban decay":"USA","tarte":"USA","elf":"USA",
    "nivea":"Alemania","eucerin":"Alemania","some by mi":"Korea","innisfree":"Korea",
    "shiseido":"Japon","tatcha":"Japon"}

def _orig(b):
    bl=(b or "").lower()
    for k,v in OM.items():
        if k in bl: return v
    return "USA"

def _tend(r,n):
    if n>80000 and r>=4.5: return "muy_creciente"
    if n>40000 and r>=4.2: return "creciente"
    if n>10000: return "estable"
    return "creciente"

def _rot(n):
    if n>100000: return "muy_alta"
    if n>50000:  return "alta"
    if n>20000:  return "media_alta"
    if n>8000:   return "media"
    return "alta"

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_makeup():
    out=[]
    try:
        for (pt,cat,sub,tgt,prob) in MSEARCHES:
            try:
                r=requests.get("https://makeup-api.herokuapp.com/api/v1/products.json",
                                params={"product_type":pt},timeout=8)
                if r.status_code!=200: continue
                items=[p for p in r.json() if p.get("name") and float(p.get("price") or 0)>0][:5]
                for p in items:
                    price=round(float(p["price"]),2)
                    revs=len(p.get("product_colors",[]))*1800+4000
                    rat=min(float(p.get("rating") or 4.1),5.0)
                    brand=(p.get("brand") or "Unknown").strip().title()
                    out.append({"id":f"API{len(out)+1:04d}","cat":cat,"sub":sub,
                        "nombre":(p.get("name") or "")[:80],"marca":brand,
                        "origen":_orig(brand),"precio":price,"mercado":round(price*1.12,2),
                        "unidades":revs,"rating":round(rat,1),"reviews":revs,
                        "tend":_tend(rat,revs),"rot":_rot(revs),
                        "desc":(p.get("description") or p.get("name") or "")[:100],
                        "target":tgt,"problema":prob,"plat":PM.get(cat,["Amazon","Sephora"]),
                        "fuente":"Makeup API Live","img":p.get("image_link") or "",
                        "url":p.get("product_link") or ""})
            except Exception: continue
    except Exception: pass
    return out

def build_df(api=[]):
    rows=[{**p,"fuente":"Base Local","img":"","url":""} for p in LP]+list(api)
    df=pd.DataFrame(rows)
    for c in ["precio","mercado"]:
        df[c]=pd.to_numeric(df[c],errors="coerce").fillna(0)
    df["unidades"]=pd.to_numeric(df["unidades"],errors="coerce").fillna(0).astype(int)
    df["rating"]=pd.to_numeric(df["rating"],errors="coerce").clip(1,5).fillna(4.0)
    df["reviews"]=pd.to_numeric(df["reviews"],errors="coerce").fillna(0).astype(int)
    df=df[(df["precio"]>0)&(df["nombre"].str.strip()!="")]
    df=df.drop_duplicates(subset=["nombre","marca"],keep="first")
    df["margen"]=((df["mercado"]-df["precio"])/df["mercado"].replace(0,1)*100).round(1)
    df["vol_usd"]=(df["precio"]*df["unidades"]).round(0)
    df["score"]=(df["rating"]*10+df["margen"]+df["unidades"]/10000).round(1)
    return df.reset_index(drop=True)

# ── Cargar datos ──────────────────────────────────────────────────
with st.spinner("Cargando datos..."):
    api_rows=fetch_makeup()
    DF=build_df(api_rows)

now=datetime.now()
dleft=(datetime(now.year,now.month+1 if now.month<12 else 1,1)-now).days

# ── Header ────────────────────────────────────────────────────────
c1,c2,c3=st.columns([1,5,2])
with c1:
    st.markdown(f'<div style="text-align:center;padding:10px 0;"><div style="width:64px;height:64px;background:linear-gradient(135deg,{PRI},{BRT});border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:28px;">🔬</div></div>',unsafe_allow_html=True)
with c2:
    st.markdown(f'<h1 style="margin:0;font-size:2rem;background:linear-gradient(90deg,{WHITE},{ACC});-webkit-background-clip:text;-webkit-text-fill-color:transparent;">ESTUDIO DE MERCADO ROME</h1><p style="margin:0;color:{PALE};font-size:.9rem;">Inteligencia Comercial Global &middot; Belleza &amp; Cuidado Personal &middot; Mercados Internacionales</p>',unsafe_allow_html=True)
with c3:
    st.markdown(f'<div style="text-align:right;padding:10px 0;"><div style="background:{MID}80;border:1px solid {ACC}40;border-radius:10px;padding:10px 14px;display:inline-block;"><div style="color:{PALE};font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;">Ultima actualizacion</div><div style="color:{WHITE};font-weight:700;font-size:1rem;font-family:Syne,sans-serif;">{now.strftime("%B %Y")}</div><div style="color:{ACC};font-size:.72rem;">Proxima en {dleft} dias</div></div></div>',unsafe_allow_html=True)
st.markdown("<hr style='margin:8px 0 20px 0;'>",unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f'<div style="text-align:center;font-family:Syne,sans-serif;font-size:1.1rem;font-weight:800;color:{WHITE};padding:16px 0 8px;">FILTROS</div>',unsafe_allow_html=True)
    st.markdown("---")
    cats=["Todas"]+sorted(DF["cat"].dropna().unique().tolist())
    cat_s=st.selectbox("Categoria",cats)
    tgt_s=st.selectbox("Target",["Todos","Femenino","Masculino","Mixto"])
    pr=st.slider("Precio USD",0,250,(0,250))
    ts=st.multiselect("Tendencia",["muy_creciente","creciente","estable","decreciente"],
                      default=["muy_creciente","creciente","estable","decreciente"])
    rs=st.multiselect("Rotacion",["muy_alta","alta","media_alta","media","baja"],
                      default=["muy_alta","alta","media_alta","media","baja"])
    rm=st.slider("Rating min",1.0,5.0,4.0,0.1)
    st.markdown("---")
    sb=st.radio("Ordenar por",["unidades","vol_usd","score","rating"],
                format_func=lambda x:{"unidades":"Unidades/mes","vol_usd":"Volumen USD","score":"Score","rating":"Rating"}[x])
    st.markdown("---")
    ac=len(api_rows)
    clr=GREEN if ac>0 else YEL
    st.markdown(f'<div style="background:{clr}18;border:1px solid {clr}60;border-radius:10px;padding:10px;text-align:center;"><div style="color:{clr};font-weight:700;font-size:.75rem;">{"En vivo" if ac>0 else "Datos locales"}</div><div style="color:{TEXT};font-size:.8rem;margin-top:4px;">Local: {len(LP)} | API: {ac}</div><div style="color:{PALE};font-size:.72rem;margin-top:2px;">{len(DF)} productos</div></div>',unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    if st.button("Recargar",use_container_width=True):
        st.cache_data.clear(); st.rerun()

# ── Filtrar ───────────────────────────────────────────────────────
df=DF.copy()
if cat_s!="Todas": df=df[df["cat"]==cat_s]
if tgt_s!="Todos": df=df[df["target"]==tgt_s]
df=df[(df["precio"]>=pr[0])&(df["precio"]<=pr[1])&df["tend"].isin(ts)&df["rot"].isin(rs)&(df["rating"]>=rm)]
dfs=df.sort_values(sb,ascending=False)

# ── KPIs ──────────────────────────────────────────────────────────
st.markdown(f'<h3 style="color:{ACC};font-family:Syne,sans-serif;font-size:.95rem;text-transform:uppercase;letter-spacing:.08em;margin-bottom:12px;">Indicadores Clave del Mercado</h3>',unsafe_allow_html=True)
k1,k2,k3,k4,k5,k6=st.columns(6)
with k1: st.metric("Productos",   str(len(df)),                   delta=f"de {len(DF)}")
with k2: st.metric("Vol Mensual", fmt(df["vol_usd"].sum()),        delta="USD")
with k3: st.metric("Unid/mes",    f"{df['unidades'].sum():,.0f}",  delta="total")
with k4: st.metric("Precio Prom.",f"${df['precio'].mean():.0f}",   delta="USD")
with k5: st.metric("Rating Prom.",f"{df['rating'].mean():.1f}/5",  delta="avg")
with k6: st.metric("Margen Prom.",f"{df['margen'].mean():.1f}%",   delta="vs mercado")
st.markdown("<br>",unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────
t1,t2,t3,t4,t5=st.tabs(["Top 10","Tendencias","Precios y Rotacion","Explorador","Comparativo"])

# ═══ TAB 1 ════════════════════════════════════════════════════════
with t1:
    top=dfs.head(10).reset_index(drop=True)
    if len(top)==0:
        st.warning("Sin productos con los filtros actuales.")
    else:
        names=top["nombre"].apply(lambda x:x[:45]+"..." if len(x)>45 else x)
        fig=go.Figure(go.Bar(
            y=names, x=top[sb], orientation="h",
            marker_color=top[sb].tolist(),
            marker_colorscale=[[0,MID],[0.5,PRI],[1,ACC]],
            marker_showscale=False,
            text=top[sb].apply(lambda x:fmt(x) if sb=="vol_usd" else f"{x:,.0f}"),
            textposition="outside",
            textfont_color=WHITE,
        ))
        fig.update_layout(**TH(height=400,showlegend=False,
            margin=dict(l=10,r=100,t=20,b=10),
            yaxis_categoryorder="total ascending",
            xaxis_title=sb.replace("_"," ").title()))
        st.plotly_chart(fig,use_container_width=True)

        for i,row in top.iterrows():
            rk=i+1
            md="🥇" if rk==1 else "🥈" if rk==2 else "🥉" if rk==3 else f"#{rk}"
            with st.expander(f"{md} {row['nombre']} — {row['marca']} · ${row['precio']:.2f}",expanded=(rk<=2)):
                ca,cb,cc,cd=st.columns(4)
                with ca:
                    st.metric("Precio",  f"${row['precio']:.2f}")
                    st.metric("Mercado", f"${row['mercado']:.2f}")
                with cb:
                    st.metric("Unid/mes",f"{row['unidades']:,}")
                    st.metric("Vol USD", fmt(row["vol_usd"]))
                with cc:
                    st.metric("Rating",  f"{row['rating']}/5")
                    st.metric("Reviews", f"{row['reviews']:,}")
                with cd:
                    st.metric("Margen",  f"{row['margen']}%")
                    st.metric("Score",   f"{row['score']:.0f}")
                plat=", ".join(row["plat"]) if isinstance(row["plat"],list) else str(row["plat"])
                st.markdown(f"""<div class="card">
                  <table style="width:100%;border-collapse:collapse;">
                    <tr><td style="padding:4px 10px;color:{PALE};font-size:.82rem;">Origen</td><td style="padding:4px 10px;color:{WHITE};">{row["origen"]}</td>
                        <td style="padding:4px 10px;color:{PALE};font-size:.82rem;">Categoria</td><td style="padding:4px 10px;color:{WHITE};">{row["cat"]} &rsaquo; {row["sub"]}</td></tr>
                    <tr><td style="padding:4px 10px;color:{PALE};font-size:.82rem;">Target</td><td style="padding:4px 10px;color:{WHITE};">{row["target"]}</td>
                        <td style="padding:4px 10px;color:{PALE};font-size:.82rem;">Plataformas</td><td style="padding:4px 10px;color:{WHITE};">{plat}</td></tr>
                    <tr><td style="padding:4px 10px;color:{PALE};font-size:.82rem;">Tendencia</td><td style="padding:4px 10px;color:{WHITE};">{ticon(row["tend"])}</td>
                        <td style="padding:4px 10px;color:{PALE};font-size:.82rem;">Rotacion</td><td style="padding:4px 10px;">{rbadge(row["rot"])}</td></tr>
                  </table>
                  <div style="margin-top:8px;padding-top:8px;border-top:1px solid {PRI}30;font-size:.82rem;"><span style="color:{PALE};">Problema: </span><span style="color:{ACC};">{row["problema"]}</span></div>
                  <div style="margin-top:4px;font-size:.8rem;color:{TEXT};">{row["desc"]}</div>
                  <div style="margin-top:4px;font-size:.72rem;color:{PALE}90;">Fuente: {row["fuente"]}</div>
                </div>""",unsafe_allow_html=True)

# ═══ TAB 2 ════════════════════════════════════════════════════════
with t2:
    c1,c2=st.columns(2)
    with c1:
        tc=DF["tend"].value_counts().reset_index()
        tc.columns=["tend","n"]
        tc["label"]=tc["tend"].map({"muy_creciente":"Muy Creciente","creciente":"Creciente","estable":"Estable","decreciente":"Decreciente"})
        fig=go.Figure(go.Pie(labels=tc["label"],values=tc["n"],hole=0.6,
            marker_colors=[ACC,BRT,PRI,RED],
            textinfo="label+percent",textfont_color=WHITE))
        fig.update_layout(**TH(title_text="Distribucion por Tendencia",height=300,showlegend=False))
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        vc=DF.groupby("cat")["vol_usd"].sum().sort_values()
        fig=go.Figure(go.Bar(y=vc.index,x=vc.values,orientation="h",
            marker_color=list(vc.values),marker_colorscale=[[0,MID],[1,ACC]],marker_showscale=False,
            text=[fmt(v) for v in vc.values],textposition="outside",textfont_color=WHITE))
        fig.update_layout(**TH(title_text="Volumen Mensual por Categoria",height=300,showlegend=False,margin=dict(l=10,r=90,t=50,b=10)))
        st.plotly_chart(fig,use_container_width=True)

    st.markdown(f'<h4 style="color:{ACC};font-family:Syne,sans-serif;margin:20px 0 10px;">Simulador Precio-Rotacion (12 meses)</h4>',unsafe_allow_html=True)
    sel=st.selectbox("Producto:",DF["nombre"].tolist(),key="sim")
    row=DF[DF["nombre"]==sel].iloc[0]
    ph=gp(row["precio"]); rh=gu(row["unidades"],row["tend"])
    ml=[x["mes"] for x in ph]; pl=[x["precio"] for x in ph]; ul=[x["unidades"] for x in rh]
    fig=make_subplots(specs=[[{"secondary_y":True}]])
    fig.add_trace(go.Scatter(x=ml,y=pl,name="Precio USD",line_color=GOLD,line_width=3,mode="lines+markers"),secondary_y=False)
    fig.add_trace(go.Bar(x=ml,y=ul,name="Unidades",marker_color=ACC,opacity=0.7),secondary_y=True)
    fig.update_layout(**TH(title_text=f"Precio vs Rotacion — {sel[:45]}",height=350,
        margin=dict(l=20,r=20,t=50,b=40),hovermode="x unified",
        legend=dict(orientation="h",y=1.05,bgcolor="rgba(0,0,0,0)")))
    st.plotly_chart(fig,use_container_width=True)
    pchg=(pl[-1]-pl[0])/pl[0]*100; uchg=(ul[-1]-ul[0])/ul[0]*100 if ul[0]>0 else 0
    corr=float(np.corrcoef(pl,ul)[0,1])
    insight="Alerta: Precio baja sin que la rotacion suba." if pchg<-3 and uchg<5 else "Saludable: Rotacion creciente." if uchg>0 else "Comportamiento normal de mercado."
    st.markdown(f"""<div class="card"><div style="font-family:Syne,sans-serif;font-weight:700;color:{WHITE};margin-bottom:10px;">Insight Automatico</div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;">
        <div><span style="color:{PALE};font-size:.78rem;">Variacion precio 12m</span><br><span style="color:{GOLD};font-size:1.2rem;font-weight:700;">{"+" if pchg>0 else ""}{pchg:.1f}%</span></div>
        <div><span style="color:{PALE};font-size:.78rem;">Variacion rotacion 12m</span><br><span style="color:{ACC};font-size:1.2rem;font-weight:700;">{"+" if uchg>0 else ""}{uchg:.1f}%</span></div>
        <div><span style="color:{PALE};font-size:.78rem;">Correlacion P-R</span><br><span style="color:{GREEN};font-size:1.2rem;font-weight:700;">{corr:.2f}</span></div>
      </div>
      <div style="margin-top:10px;padding-top:8px;border-top:1px solid {PRI}30;color:{TEXT};font-size:.84rem;">{insight}</div>
    </div>""",unsafe_allow_html=True)

# ═══ TAB 3 ════════════════════════════════════════════════════════
with t3:
    c1,c2=st.columns(2)
    with c1:
        fig=px.scatter(DF,x="precio",y="rating",size="unidades",color="cat",hover_name="nombre",
            color_discrete_sequence=px.colors.sequential.Blues_r,
            labels={"precio":"Precio USD","rating":"Rating","cat":"Categoria"})
        fig.update_layout(**TH(title_text="Precio vs Rating (tamano=volumen)",height=360,
            margin=dict(l=20,r=20,t=50,b=30),
            legend=dict(orientation="h",y=-0.28,font_size=9,bgcolor="rgba(0,0,0,0)")))
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        dfc=DF.copy()
        dfc["rango"]=pd.cut(dfc["precio"],bins=[0,20,50,100,250],labels=["$0-20","$20-50","$50-100","$100+"])
        fig=px.box(dfc.dropna(subset=["rango"]),x="rango",y="unidades",color="rango",
            color_discrete_sequence=[MID,PRI,BRT,ACC],
            labels={"rango":"Rango precio","unidades":"Unidades/mes"})
        fig.update_layout(**TH(title_text="Volumen por Rango de Precio",height=360,showlegend=False,margin=dict(l=20,r=20,t=50,b=30)))
        st.plotly_chart(fig,use_container_width=True)

    st.markdown(f'<h4 style="color:{ACC};font-family:Syne,sans-serif;margin:20px 0 10px;">Heatmap Rotacion — Categoria x Tendencia</h4>',unsafe_allow_html=True)
    piv=DF.groupby(["cat","tend"])["unidades"].sum().reset_index().pivot(index="cat",columns="tend",values="unidades").fillna(0)
    fig=go.Figure(go.Heatmap(z=piv.values,x=piv.columns.tolist(),y=piv.index.tolist(),
        colorscale=[[0,BG],[0.3,MID],[0.6,PRI],[1,ACC]],
        text=[[fmt(v) for v in r] for r in piv.values],
        texttemplate="%{text}",textfont_color=WHITE))
    fig.update_layout(**TH(title_text="Unidades/mes — Categoria x Tendencia",height=380,margin=dict(l=20,r=80,t=50,b=30)))
    st.plotly_chart(fig,use_container_width=True)

# ═══ TAB 4 ════════════════════════════════════════════════════════
with t4:
    search=st.text_input("Buscar por nombre, marca o problema...",placeholder="Ej: acne, retinol, caida cabello...")
    dfe=DF.copy()
    if search:
        q=search.lower()
        dfe=dfe[dfe["nombre"].str.lower().str.contains(q,na=False)|dfe["marca"].str.lower().str.contains(q,na=False)|dfe["problema"].str.lower().str.contains(q,na=False)|dfe["cat"].str.lower().str.contains(q,na=False)|dfe["desc"].str.lower().str.contains(q,na=False)]
    st.markdown(f'<p style="color:{PALE};font-size:.84rem;">Mostrando {len(dfe)} productos</p>',unsafe_allow_html=True)
    if len(dfe)==0:
        st.warning("Sin resultados.")
    else:
        disp=dfe[["id","nombre","marca","cat","precio","mercado","margen","unidades","rating","tend","rot","target","fuente"]].copy()
        disp.columns=["ID","Producto","Marca","Categoria","Precio","Mercado","Margen%","Unid/mes","Rating","Tendencia","Rotacion","Target","Fuente"]
        disp["Tendencia"]=disp["Tendencia"].map({"muy_creciente":"Muy Creciente","creciente":"Creciente","estable":"Estable","decreciente":"Decreciente"})
        disp["Rotacion"]=disp["Rotacion"].map({"muy_alta":"Muy Alta","alta":"Alta","media_alta":"Media-Alta","media":"Media","baja":"Baja"})
        disp["Precio"]=disp["Precio"].apply(lambda x:f"${x:.2f}")
        disp["Mercado"]=disp["Mercado"].apply(lambda x:f"${x:.2f}")
        disp["Margen%"]=disp["Margen%"].apply(lambda x:f"{x:.1f}%")
        disp["Unid/mes"]=disp["Unid/mes"].apply(lambda x:f"{x:,}")
        disp["Rating"]=disp["Rating"].apply(lambda x:f"{x:.1f}")
        st.dataframe(disp,use_container_width=True,hide_index=True,height=460)
        csv=dfe.drop(columns=["plat","img","url"],errors="ignore").to_csv(index=False).encode("utf-8")
        st.download_button("Descargar CSV",csv,f"rome_market_{now.strftime('%Y%m')}.csv","text/csv")

# ═══ TAB 5 ════════════════════════════════════════════════════════
with t5:
    c1,c2=st.columns(2)
    with c1:
        fig=px.treemap(DF,path=["cat","sub"],values="vol_usd",color="score",
            color_continuous_scale=[[0,MID],[0.5,PRI],[1,ACC]])
        fig.update_layout(**TH(title_text="Mapa de Oportunidades por Volumen USD",height=400,margin=dict(l=10,r=10,t=50,b=10)))
        fig.update_traces(textfont_color=WHITE,marker_line_color=BG,marker_line_width=2)
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        dfo=DF.nlargest(10,"margen")
        nm=dfo["nombre"].apply(lambda x:x[:26]+"..." if len(x)>26 else x)
        fig=go.Figure()
        fig.add_trace(go.Bar(name="Precio propio", x=nm,y=dfo["precio"], marker_color=PRI))
        fig.add_trace(go.Bar(name="Precio mercado",x=nm,y=dfo["mercado"],marker_color=ACC))
        fig.update_layout(**TH(title_text="Top 10 Mayor Margen vs Mercado",barmode="group",height=400,
            margin=dict(l=10,r=10,t=50,b=90),xaxis_tickangle=-35,
            legend=dict(orientation="h",y=1.05,bgcolor="rgba(0,0,0,0)")))
        st.plotly_chart(fig,use_container_width=True)

    st.markdown(f'<h4 style="color:{ACC};font-family:Syne,sans-serif;margin:20px 0 10px;">Radar de Competitividad por Categoria</h4>',unsafe_allow_html=True)
    rc=DF.groupby("cat").agg(rating=("rating","mean"),margen=("margen","mean"),
        unidades=("unidades",lambda x:x.mean()/1000),score=("score","mean"),
        precio=("precio",lambda x:max(0.0,10-(x.mean()/30)))).reset_index()
    cats6=rc["cat"].head(6).tolist()
    mlab=["Rating","Margen","Vol(K)","Score","Precio Comp."]; mcol=["rating","margen","unidades","score","precio"]; mmax=[5,15,120,120,10]
    cols6=[ACC,GOLD,GREEN,YEL,PALE,BRT]
    fig=go.Figure()
    for i,cat in enumerate(cats6):
        row=rc[rc["cat"]==cat].iloc[0]
        vals=[min(float(row[m])/(mx or 1)*10,10) for m,mx in zip(mcol,mmax)]; vals.append(vals[0])
        fig.add_trace(go.Scatterpolar(r=vals,theta=mlab+[mlab[0]],fill="toself",name=cat,
            fillcolor=cols6[i%len(cols6)]+"20",line_color=cols6[i%len(cols6)],line_width=2))
    fig.update_layout(**TH(title_text="Radar — Top 6 Categorias",height=450,
        polar_bgcolor=DARK+"80",
        legend=dict(orientation="h",y=-0.1,font_size=10,bgcolor="rgba(0,0,0,0)")))
    st.plotly_chart(fig,use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────
st.markdown("<br><hr>",unsafe_allow_html=True)
st.markdown(f'<div style="text-align:center;padding:16px 0;color:{PALE};font-size:.78rem;"><span style="font-family:Syne,sans-serif;font-size:1rem;color:{ACC};font-weight:700;">ESTUDIO DE MERCADO ROME</span> &nbsp;·&nbsp; {now.strftime("%B %Y")} &nbsp;·&nbsp; {len(DF)} productos &nbsp;·&nbsp; Base Local &amp; Makeup API<br><br><span style="opacity:.5;font-size:.7rem;">Estimaciones con fines de analisis competitivo. Actualizacion mensual.</span></div>',unsafe_allow_html=True)
