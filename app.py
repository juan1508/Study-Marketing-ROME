"""
ESTUDIO DE MERCADO ROME
Inteligencia Comercial Global · Belleza & Cuidado Personal
Carga instantánea con datos locales + APIs opcionales en background
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import requests

# ══════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE PÁGINA
# ══════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Estudio de Mercado ROME",
    page_icon="🔵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════════
# PALETA AZUL
# ══════════════════════════════════════════════════════════════════

C = {
    "navy":    "#0A1628",
    "dark":    "#0D2137",
    "mid":     "#1A3A5C",
    "primary": "#1E5FAD",
    "bright":  "#2E86DE",
    "accent":  "#54A0FF",
    "light":   "#74B9FF",
    "pale":    "#A8D8F0",
    "white":   "#EEF6FF",
    "gold":    "#FFC300",
    "green":   "#00B894",
    "yellow":  "#FDCB6E",
    "red":     "#E17055",
    "text":    "#DDE8F5",
}

# ══════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');
.stApp { background: linear-gradient(135deg, #0A1628 0%, #0D2137 60%, #0B1E35 100%); }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: #DDE8F5; }
h1,h2,h3 { font-family: 'Syne', sans-serif; font-weight: 800; }
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D2137 0%, #1A3A5C 100%);
    border-right: 1px solid #1E5FAD40;
}
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #1A3A5CCC, #1E5FAD33) !important;
    border: 1px solid #54A0FF40 !important;
    border-radius: 16px !important;
    padding: 20px !important;
}
div[data-testid="metric-container"] label {
    color: #A8D8F0 !important;
    font-size: 0.82rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
[data-testid="stMetricValue"] {
    color: #EEF6FF !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1.6rem !important;
}
.stTabs [data-baseweb="tab-list"] { background: #1A3A5C80 !important; border-radius: 12px !important; padding: 4px !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #A8D8F0 !important; border-radius: 10px !important; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #1E5FAD, #2E86DE) !important; color: white !important; font-weight: 600 !important; }
.stButton > button { background: linear-gradient(135deg, #1E5FAD, #2E86DE) !important; color: white !important; border: none !important; border-radius: 10px !important; font-weight: 600 !important; }
.stSelectbox div[data-baseweb="select"] > div { background: #1A3A5C !important; border-color: #1E5FAD60 !important; color: #DDE8F5 !important; border-radius: 10px !important; }
.stTextInput input { background: #1A3A5C !important; border-color: #1E5FAD60 !important; color: #DDE8F5 !important; border-radius: 10px !important; }
.stRadio label, .stMultiSelect label, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label { color: #DDE8F5 !important; }
.streamlit-expanderHeader { background: #1A3A5C80 !important; border: 1px solid #1E5FAD30 !important; border-radius: 10px !important; color: #DDE8F5 !important; }
hr { border-color: #1E5FAD30 !important; }
#MainMenu, footer, header { visibility: hidden; }
.card { background: linear-gradient(135deg, #1A3A5C, #0D2137); border: 1px solid #54A0FF40; border-radius: 12px; padding: 16px; margin-bottom: 12px; }
.badge-alta  { background:#00B89425; color:#00B894; border:1px solid #00B89450; border-radius:20px; padding:2px 10px; font-size:0.75rem; font-weight:600; }
.badge-media { background:#FDCB6E25; color:#FDCB6E; border:1px solid #FDCB6E50; border-radius:20px; padding:2px 10px; font-size:0.75rem; font-weight:600; }
.badge-baja  { background:#E1705525; color:#E17055; border:1px solid #E1705550; border-radius:20px; padding:2px 10px; font-size:0.75rem; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# BASE DE DATOS LOCAL
# ══════════════════════════════════════════════════════════════════

LOCAL_PRODUCTS = [
    {"id":"SK01","cat":"Piel","sub":"Sueros","nombre":"The Ordinary Niacinamide 10% + Zinc","marca":"The Ordinary","origen":"Canada","precio":6.90,"mercado":8.50,"unidades":85000,"rating":4.6,"reviews":125000,"tend":"estable","rot":"muy_alta","desc":"Suero Niacinamida 10% para poros y manchas","target":"Mixto","problema":"Poros, manchas, acne","plat":["Amazon","ASOS","Sephora"]},
    {"id":"SK02","cat":"Piel","sub":"Sueros","nombre":"Paula Choice BHA 2pct Liquid Exfoliant","marca":"Paulas Choice","origen":"USA","precio":34.00,"mercado":36.00,"unidades":42000,"rating":4.8,"reviews":98000,"tend":"creciente","rot":"alta","desc":"Exfoliante quimico BHA para poros y acne","target":"Mixto","problema":"Poros, acne, opacidad","plat":["Paulas Choice","Amazon","Dermstore"]},
    {"id":"SK03","cat":"Piel","sub":"Vitamina C","nombre":"SkinCeuticals C E Ferulic","marca":"SkinCeuticals","origen":"USA","precio":182.00,"mercado":185.00,"unidades":18000,"rating":4.7,"reviews":45000,"tend":"estable","rot":"media","desc":"Vitamina C profesional antioxidante premium","target":"Femenino","problema":"Manchas, envejecimiento","plat":["Dermstore","Sephora","Amazon"]},
    {"id":"SK04","cat":"Piel","sub":"Retinol","nombre":"Differin Adapalene Gel 0.1pct","marca":"Differin","origen":"USA","precio":15.50,"mercado":18.00,"unidades":95000,"rating":4.5,"reviews":187000,"tend":"muy_creciente","rot":"muy_alta","desc":"Retinoide OTC mas potente del mercado","target":"Mixto","problema":"Acne, cicatrices, arrugas","plat":["Amazon","Walmart","Target"]},
    {"id":"SK05","cat":"Piel","sub":"Hidratacion","nombre":"CeraVe Moisturizing Cream","marca":"CeraVe","origen":"USA","precio":19.00,"mercado":21.00,"unidades":210000,"rating":4.8,"reviews":320000,"tend":"estable","rot":"muy_alta","desc":"Crema hidratante con ceramidas","target":"Mixto","problema":"Sequedad, barrera cutanea","plat":["Amazon","Walmart","CVS"]},
    {"id":"SK06","cat":"Piel","sub":"Manchas","nombre":"Good Molecules Discoloration Serum","marca":"Good Molecules","origen":"USA","precio":12.00,"mercado":14.00,"unidades":31000,"rating":4.4,"reviews":22000,"tend":"creciente","rot":"media_alta","desc":"Suero despigmentante con acido tranexamico","target":"Femenino","problema":"Hiperpigmentacion, manchas","plat":["Ulta","Amazon"]},
    {"id":"SK07","cat":"Piel","sub":"Celulitis","nombre":"Sol de Janeiro Brazilian Bum Bum Cream","marca":"Sol de Janeiro","origen":"Brasil","precio":48.00,"mercado":50.00,"unidades":55000,"rating":4.6,"reviews":78000,"tend":"muy_creciente","rot":"alta","desc":"Crema reafirmante con cafeina y cupuacu","target":"Femenino","problema":"Celulitis, flacidez","plat":["Sephora","Amazon","Ulta"]},
    {"id":"SK08","cat":"Piel","sub":"Estrias","nombre":"Bio-Oil Skincare Oil","marca":"Bio-Oil","origen":"Sudafrica","precio":14.00,"mercado":16.00,"unidades":120000,"rating":4.5,"reviews":145000,"tend":"estable","rot":"muy_alta","desc":"Aceite para estrias y cicatrices","target":"Femenino","problema":"Estrias, cicatrices","plat":["Amazon","Walmart","Target"]},
    {"id":"SK09","cat":"Piel","sub":"Acne","nombre":"La Roche-Posay Effaclar Duo Plus","marca":"La Roche-Posay","origen":"Francia","precio":30.00,"mercado":33.00,"unidades":68000,"rating":4.6,"reviews":89000,"tend":"creciente","rot":"alta","desc":"Tratamiento anti-imperfecciones clinico","target":"Mixto","problema":"Acne, poros, grasa","plat":["Amazon","Dermstore","Ulta"]},
    {"id":"SK10","cat":"Piel","sub":"Protector Solar","nombre":"EltaMD UV Clear SPF 46","marca":"EltaMD","origen":"USA","precio":39.00,"mercado":42.00,"unidades":88000,"rating":4.7,"reviews":112000,"tend":"muy_creciente","rot":"muy_alta","desc":"Protector solar con niacinamida","target":"Mixto","problema":"Dano solar, manchas","plat":["Amazon","Dermstore","Ulta"]},
    {"id":"CA01","cat":"Cabello","sub":"Caida","nombre":"Viviscal Extra Strength Hair Growth","marca":"Viviscal","origen":"USA","precio":49.99,"mercado":54.00,"unidades":38000,"rating":4.3,"reviews":62000,"tend":"creciente","rot":"alta","desc":"Suplemento clinico para crecimiento capilar","target":"Mixto","problema":"Caida, alopecia","plat":["Amazon","Ulta","CVS"]},
    {"id":"CA02","cat":"Cabello","sub":"Caida","nombre":"Minoxidil 5pct Kirkland Foam","marca":"Kirkland","origen":"USA","precio":29.00,"mercado":35.00,"unidades":95000,"rating":4.4,"reviews":134000,"tend":"muy_creciente","rot":"muy_alta","desc":"Minoxidil espuma 5pct para calvicie","target":"Masculino","problema":"Calvicie, entradas","plat":["Amazon","Costco","Walmart"]},
    {"id":"CA03","cat":"Cabello","sub":"Reparacion","nombre":"Olaplex No.3 Hair Perfector","marca":"Olaplex","origen":"USA","precio":30.00,"mercado":32.00,"unidades":72000,"rating":4.6,"reviews":115000,"tend":"estable","rot":"muy_alta","desc":"Reparador de enlaces moleculares","target":"Femenino","problema":"Cabello quebradizo, danado","plat":["Sephora","Amazon","Ulta"]},
    {"id":"CA04","cat":"Cabello","sub":"Caspa","nombre":"Nizoral Anti-Dandruff Shampoo","marca":"Nizoral","origen":"USA","precio":15.00,"mercado":17.00,"unidades":88000,"rating":4.6,"reviews":98000,"tend":"estable","rot":"muy_alta","desc":"Champu medicado con ketoconazol 1pct","target":"Mixto","problema":"Caspa, dermatitis","plat":["Amazon","CVS","Walgreens"]},
    {"id":"CA05","cat":"Cabello","sub":"Canas","nombre":"Madison Reed Root Touch Up","marca":"Madison Reed","origen":"USA","precio":26.00,"mercado":28.00,"unidades":51000,"rating":4.5,"reviews":67000,"tend":"creciente","rot":"alta","desc":"Retoque de raices sin amoniaco","target":"Mixto","problema":"Canas prematuras","plat":["Amazon","Ulta","Target"]},
    {"id":"EN01","cat":"Envejecimiento","sub":"Arrugas","nombre":"RoC Retinol Correxion Line Smoothing","marca":"RoC","origen":"Francia","precio":25.99,"mercado":28.00,"unidades":89000,"rating":4.4,"reviews":118000,"tend":"estable","rot":"muy_alta","desc":"Crema retinol puro para arrugas","target":"Femenino","problema":"Arrugas, lineas expresion","plat":["Amazon","Walmart","CVS"]},
    {"id":"EN02","cat":"Envejecimiento","sub":"Colageno","nombre":"Vital Proteins Collagen Peptides","marca":"Vital Proteins","origen":"USA","precio":43.00,"mercado":48.00,"unidades":165000,"rating":4.5,"reviews":210000,"tend":"muy_creciente","rot":"muy_alta","desc":"Colageno hidrolizado bovino en polvo","target":"Femenino","problema":"Arrugas, cabello, unas","plat":["Amazon","Target","Whole Foods"]},
    {"id":"EN03","cat":"Envejecimiento","sub":"Firmeza","nombre":"StriVectin-TL Tightening Neck Cream","marca":"StriVectin","origen":"USA","precio":89.00,"mercado":95.00,"unidades":21000,"rating":4.4,"reviews":28000,"tend":"creciente","rot":"media_alta","desc":"Crema reafirmante para cuello y escote","target":"Femenino","problema":"Flacidez cuello","plat":["Sephora","Amazon","Ulta"]},
    {"id":"EN04","cat":"Envejecimiento","sub":"Manchas Edad","nombre":"Murad Rapid Age Spot Correcting Serum","marca":"Murad","origen":"USA","precio":86.00,"mercado":90.00,"unidades":19000,"rating":4.5,"reviews":24000,"tend":"creciente","rot":"media_alta","desc":"Suero corrector manchas de la edad","target":"Femenino","problema":"Manchas edad, hiperpigmentacion","plat":["Sephora","Amazon","Murad"]},
    {"id":"MQ01","cat":"Maquillaje","sub":"Base","nombre":"Fenty Beauty Pro Filtr Foundation","marca":"Fenty Beauty","origen":"USA","precio":40.00,"mercado":42.00,"unidades":92000,"rating":4.6,"reviews":138000,"tend":"muy_creciente","rot":"muy_alta","desc":"Base 50 tonos inclusivos","target":"Femenino","problema":"Tono desigual, manchas","plat":["Sephora","Harvey Nichols","Fentybeauty.com"]},
    {"id":"MQ02","cat":"Maquillaje","sub":"Labios","nombre":"Charlotte Tilbury Pillow Talk Lip Liner","marca":"Charlotte Tilbury","origen":"UK","precio":28.00,"mercado":30.00,"unidades":68000,"rating":4.7,"reviews":89000,"tend":"muy_creciente","rot":"muy_alta","desc":"Delineador labial nude mas vendido","target":"Femenino","problema":"Labios finos, sin definicion","plat":["Sephora","Nordstrom"]},
    {"id":"MQ03","cat":"Maquillaje","sub":"Ojos","nombre":"Benefit Gimme Brow+ Volumizing Gel","marca":"Benefit","origen":"USA","precio":24.00,"mercado":26.00,"unidades":55000,"rating":4.5,"reviews":72000,"tend":"creciente","rot":"alta","desc":"Gel de cejas volumizador","target":"Femenino","problema":"Cejas escasas","plat":["Sephora","Ulta","Amazon"]},
    {"id":"MQ04","cat":"Maquillaje","sub":"Rimel","nombre":"LOreal Voluminous Original Mascara","marca":"LOreal","origen":"Francia","precio":10.99,"mercado":13.00,"unidades":198000,"rating":4.5,"reviews":245000,"tend":"estable","rot":"muy_alta","desc":"Mascara de pestanas voluminizadora","target":"Femenino","problema":"Pestanas cortas","plat":["Amazon","Walmart","CVS"]},
    {"id":"MQ05","cat":"Maquillaje","sub":"Contorno","nombre":"NYX Professional Makeup Wonder Stick","marca":"NYX","origen":"USA","precio":14.00,"mercado":15.00,"unidades":78000,"rating":4.4,"reviews":91000,"tend":"creciente","rot":"muy_alta","desc":"Stick contorno e iluminador 2 en 1","target":"Femenino","problema":"Definicion facial","plat":["Amazon","Ulta","Target"]},
    {"id":"MQ06","cat":"Maquillaje","sub":"Primer","nombre":"elf Poreless Putty Primer","marca":"elf","origen":"USA","precio":10.00,"mercado":12.00,"unidades":145000,"rating":4.5,"reviews":189000,"tend":"muy_creciente","rot":"muy_alta","desc":"Primer suavizante de poros ultra popular","target":"Femenino","problema":"Poros visibles, maquillaje duradero","plat":["Amazon","Target","Ulta"]},
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
    {"id":"BI01","cat":"Bienestar","sub":"Suplementos Piel","nombre":"HUM Nutrition Daily Cleanse","marca":"HUM Nutrition","origen":"USA","precio":40.00,"mercado":44.00,"unidades":22000,"rating":4.2,"reviews":15000,"tend":"muy_creciente","rot":"media_alta","desc":"Suplemento belleza interior piel clara","target":"Femenino","problema":"Acne interno, piel opaca","plat":["Sephora","Amazon","hum.com"]},
    {"id":"BI02","cat":"Bienestar","sub":"Perdida Peso","nombre":"Leanbean Fat Burner for Women","marca":"Leanbean","origen":"UK","precio":59.99,"mercado":65.00,"unidades":28000,"rating":4.1,"reviews":19000,"tend":"creciente","rot":"media_alta","desc":"Quemador grasa femenino natural","target":"Femenino","problema":"Exceso peso, metabolismo","plat":["leanbean.com","Amazon"]},
]

# ══════════════════════════════════════════════════════════════════
# MAKEUP API — fetch en vivo
# ══════════════════════════════════════════════════════════════════

MAKEUP_SEARCHES = [
    ("foundation","Maquillaje","Base","Femenino","Tono desigual"),
    ("lip_liner","Maquillaje","Labios","Femenino","Labios finos"),
    ("mascara","Maquillaje","Ojos","Femenino","Pestanas cortas"),
    ("bronzer","Maquillaje","Contorno","Femenino","Definicion facial"),
    ("primer","Maquillaje","Primer","Femenino","Poros visibles"),
    ("blush","Maquillaje","Colorete","Femenino","Falta de color"),
    ("eyeshadow","Maquillaje","Sombras","Femenino","Ojos sin profundidad"),
    ("moisturizer","Piel","Hidratacion","Mixto","Sequedad"),
    ("face_wash","Piel","Limpieza","Mixto","Poros, grasa"),
    ("serum","Skincare Premium","Serum","Femenino","Manchas, opacidad"),
    ("nail_polish","Manos y Unas","Esmalte","Femenino","Unas sin color"),
]

PLATFORMS_MAP = {
    "Maquillaje":["Sephora","Ulta","Amazon"],
    "Piel":["Amazon","Dermstore","Ulta"],
    "Skincare Premium":["Sephora","Dermstore","Amazon"],
    "Cabello":["Amazon","Ulta","Sally Beauty"],
    "Envejecimiento":["Sephora","Amazon","CVS"],
    "Cuerpo":["Amazon","GNC","Bodybuilding.com"],
    "Bienestar":["Amazon","Whole Foods","iHerb"],
    "Vello":["Amazon","Ulta"],
    "Sudoracion":["Amazon","Target","Walmart"],
    "Manos y Unas":["Amazon","Ulta","CVS"],
    "Pies":["Amazon","Ulta","Target"],
    "Cuidado Masculino":["Amazon","Sephora","Nordstrom"],
    "Mirada":["Sephora","Ulta","Amazon"],
}

ORIGINS_MAP = {
    "loreal":"Francia","lancome":"Francia","nuxe":"Francia","la roche":"Francia","vichy":"Francia",
    "charlotte tilbury":"UK","the ordinary":"Canada","deciem":"Canada",
    "fenty":"USA","rare beauty":"USA","nyx":"USA","maybelline":"USA","revlon":"USA",
    "neutrogena":"USA","cerave":"USA","olay":"USA","benefit":"USA","urban decay":"USA",
    "too faced":"USA","tarte":"USA","wet n wild":"USA","elf":"USA",
    "nivea":"Alemania","eucerin":"Alemania",
    "some by mi":"Korea","innisfree":"Korea","missha":"Korea",
    "shiseido":"Japon","tatcha":"Japon",
}

def _origin(brand):
    b = (brand or "").lower()
    for k, v in ORIGINS_MAP.items():
        if k in b:
            return v
    return "USA"

def _tend(rating, reviews):
    if reviews > 80000 and rating >= 4.5: return "muy_creciente"
    if reviews > 40000 and rating >= 4.2: return "creciente"
    if reviews > 10000: return "estable"
    return "creciente"

def _rot(reviews):
    if reviews > 100000: return "muy_alta"
    if reviews > 50000:  return "alta"
    if reviews > 20000:  return "media_alta"
    if reviews > 8000:   return "media"
    return "alta"

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_makeup():
    results = []
    try:
        for (ptype, cat, sub, target, problema) in MAKEUP_SEARCHES:
            try:
                r = requests.get(
                    "https://makeup-api.herokuapp.com/api/v1/products.json",
                    params={"product_type": ptype},
                    timeout=8
                )
                if r.status_code != 200:
                    continue
                items = [p for p in r.json()
                         if p.get("name") and p.get("price")
                         and float(p.get("price") or 0) > 0][:5]
                for p in items:
                    price  = round(float(p["price"]), 2)
                    revs   = len(p.get("product_colors", [])) * 1800 + 4000
                    rating = min(float(p.get("rating") or 4.1), 5.0)
                    brand  = (p.get("brand") or "Unknown").strip().title()
                    results.append({
                        "id":       f"API{len(results)+1:04d}",
                        "cat":      cat, "sub": sub,
                        "nombre":   (p.get("name") or "")[:80],
                        "marca":    brand,
                        "origen":   _origin(brand),
                        "precio":   price,
                        "mercado":  round(price * 1.12, 2),
                        "unidades": revs,
                        "rating":   round(rating, 1),
                        "reviews":  revs,
                        "tend":     _tend(rating, revs),
                        "rot":      _rot(revs),
                        "desc":     (p.get("description") or p.get("name") or "")[:100],
                        "target":   target,
                        "problema": problema,
                        "plat":     PLATFORMS_MAP.get(cat, ["Amazon","Sephora"]),
                        "fuente":   "Makeup API Live",
                        "img":      p.get("image_link") or "",
                        "url":      p.get("product_link") or "",
                    })
            except Exception:
                continue
    except Exception:
        pass
    return results

# ══════════════════════════════════════════════════════════════════
# CONSTRUIR DATAFRAME
# ══════════════════════════════════════════════════════════════════

def build_df(api_rows=None):
    rows = []
    for p in LOCAL_PRODUCTS:
        rows.append({**p, "fuente": "Base Local", "img": "", "url": ""})
    if api_rows:
        rows.extend(api_rows)
    df = pd.DataFrame(rows)
    df["precio"]   = pd.to_numeric(df["precio"],   errors="coerce").fillna(0)
    df["mercado"]  = pd.to_numeric(df["mercado"],  errors="coerce").fillna(0)
    df["unidades"] = pd.to_numeric(df["unidades"], errors="coerce").fillna(0).astype(int)
    df["rating"]   = pd.to_numeric(df["rating"],   errors="coerce").clip(1,5).fillna(4.0)
    df["reviews"]  = pd.to_numeric(df["reviews"],  errors="coerce").fillna(0).astype(int)
    df = df[(df["precio"] > 0) & (df["nombre"].str.strip() != "")]
    df = df.drop_duplicates(subset=["nombre","marca"], keep="first")
    df["margen"]  = ((df["mercado"] - df["precio"]) / df["mercado"].replace(0,1) * 100).round(1)
    df["vol_usd"] = (df["precio"] * df["unidades"]).round(0)
    df["score"]   = (df["rating"]*10 + df["margen"] + df["unidades"]/10000).round(1)
    return df.reset_index(drop=True)

# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════

def fmt(val):
    if val >= 1_000_000: return f"${val/1_000_000:.1f}M"
    if val >= 1_000:     return f"${val/1_000:.0f}K"
    return f"${val:.2f}"

def rot_badge(r):
    m = {
        "muy_alta": ("Muy Alta","alta"),
        "alta":     ("Alta","alta"),
        "media_alta":("Media-Alta","media"),
        "media":    ("Media","media"),
        "baja":     ("Baja","baja"),
    }
    label, cls = m.get(r, ("N/A","media"))
    return f'<span class="badge-{cls}">{label}</span>'

def tend_icon(t):
    return {"muy_creciente":"Muy Creciente","creciente":"Creciente",
            "estable":"Estable","decreciente":"Decreciente"}.get(t, t)

def theme():
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(13,33,55,0.6)",
        font=dict(family="DM Sans", color="#DDE8F5", size=12),
        title_font=dict(family="Syne", size=15, color="#EEF6FF"),
    )

def ax(title="", tickangle=0, extra=None):
    """Returns safe axis style dict for Plotly update_layout."""
    d = {
        "gridcolor": "#1E5FAD25",
        "linecolor": "#1A3A5C",
        "tickcolor": "#A8D8F0",
        "tickfont":  {"color": "#A8D8F0", "size": 11},
    }
    if title:     d["title"] = {"text": title, "font": {"color": "#A8D8F0"}}
    if tickangle: d["tickangle"] = tickangle
    if extra:     d.update(extra)
    return d

def gen_prices(base, months=12):
    np.random.seed(int(base*100) % 9999)
    h, p = [], float(base)
    for i in range(months):
        d = datetime.now() - timedelta(days=30*(months-i-1))
        p = max(p*(1+np.random.normal(0,0.025)), base*0.72)
        h.append({"mes": d.strftime("%b %Y"), "precio": round(p,2)})
    return h

def gen_units(base, tend, months=12):
    tf = {"muy_creciente":0.07,"creciente":0.035,"estable":0.005,"decreciente":-0.025}.get(tend,0.005)
    np.random.seed(int(base) % 9999)
    h, u = [], float(base)
    for i in range(months):
        d = datetime.now() - timedelta(days=30*(months-i-1))
        u = u*(1+tf)*(1+0.08*np.sin(i*np.pi/6))*np.random.normal(1,0.04)
        h.append({"mes": d.strftime("%b %Y"), "unidades": max(int(u),0)})
    return h

# ══════════════════════════════════════════════════════════════════
# CARGAR DATOS
# ══════════════════════════════════════════════════════════════════

with st.spinner("Cargando datos..."):
    api_rows  = fetch_makeup()
    df_full   = build_df(api_rows)
    api_count = len(api_rows)

now   = datetime.now()
nxt   = datetime(now.year, now.month+1 if now.month < 12 else 1, 1)
dleft = (nxt - now).days

# ══════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════

c1, c2, c3 = st.columns([1, 5, 2])
with c1:
    st.markdown(f'<div style="text-align:center;padding:10px 0;"><div style="width:64px;height:64px;background:linear-gradient(135deg,#1E5FAD,#2E86DE);border-radius:50%;display:inline-flex;align-items:center;justify-content:center;box-shadow:0 8px 32px #54A0FF60;font-size:28px;">🔬</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div style="padding:8px 0;"><h1 style="margin:0;font-size:2.1rem;background:linear-gradient(90deg,#EEF6FF,#54A0FF);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">ESTUDIO DE MERCADO ROME</h1><p style="margin:0;color:#A8D8F0;font-size:.9rem;letter-spacing:.05em;">Inteligencia Comercial Global &middot; Belleza &amp; Cuidado Personal &middot; Mercados Internacionales</p></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div style="text-align:right;padding:10px 0;"><div style="background:#1A3A5C80;border:1px solid #54A0FF40;border-radius:10px;padding:10px 14px;display:inline-block;"><div style="color:#A8D8F0;font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;">Ultima actualizacion</div><div style="color:#EEF6FF;font-weight:700;font-size:1rem;font-family:Syne,sans-serif;">{now.strftime("%B %Y")}</div><div style="color:#54A0FF;font-size:.72rem;">Proxima en {dleft} dias</div></div></div>', unsafe_allow_html=True)

st.markdown("<hr style='margin:8px 0 20px 0;'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown('<div style="text-align:center;font-family:Syne,sans-serif;font-size:1.2rem;font-weight:800;color:#EEF6FF;padding:16px 0 8px;">FILTROS</div>', unsafe_allow_html=True)
    st.markdown("---")

    cats      = ["Todas"] + sorted(df_full["cat"].dropna().unique().tolist())
    cat_sel   = st.selectbox("Categoria", cats)
    tgt_sel   = st.selectbox("Target", ["Todos","Femenino","Masculino","Mixto"])
    precio_r  = st.slider("Precio USD", 0, 250, (0, 250))
    tend_sel  = st.multiselect("Tendencia",
        ["muy_creciente","creciente","estable","decreciente"],
        default=["muy_creciente","creciente","estable","decreciente"])
    rot_sel   = st.multiselect("Rotacion",
        ["muy_alta","alta","media_alta","media","baja"],
        default=["muy_alta","alta","media_alta","media","baja"])
    rating_min = st.slider("Rating minimo", 1.0, 5.0, 4.0, 0.1)
    st.markdown("---")
    sort_by   = st.radio("Ordenar por",
        ["unidades","vol_usd","score","rating"],
        format_func=lambda x: {"unidades":"Unidades/mes","vol_usd":"Volumen USD","score":"Score","rating":"Rating"}[x])
    st.markdown("---")

    clr = "#00B894" if api_count > 0 else "#FDCB6E"
    ico = "En vivo" if api_count > 0 else "Datos locales"
    st.markdown(f'<div style="background:{clr}18;border:1px solid {clr}60;border-radius:10px;padding:10px;text-align:center;"><div style="color:{clr};font-weight:700;font-size:.75rem;">{ico}</div><div style="color:#DDE8F5;font-size:.8rem;margin-top:4px;">Local: {len(LOCAL_PRODUCTS)} | API: {api_count}</div><div style="color:#A8D8F0;font-size:.72rem;margin-top:2px;">{len(df_full)} productos totales</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Recargar datos", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ══════════════════════════════════════════════════════════════════
# FILTRAR
# ══════════════════════════════════════════════════════════════════

df = df_full.copy()
if cat_sel  != "Todas": df = df[df["cat"]    == cat_sel]
if tgt_sel  != "Todos": df = df[df["target"] == tgt_sel]
df = df[
    (df["precio"]  >= precio_r[0]) & (df["precio"]  <= precio_r[1]) &
    (df["tend"].isin(tend_sel)) & (df["rot"].isin(rot_sel)) &
    (df["rating"]  >= rating_min)
]
df_s = df.sort_values(sort_by, ascending=False)

# ══════════════════════════════════════════════════════════════════
# KPIs
# ══════════════════════════════════════════════════════════════════

st.markdown('<h3 style="color:#54A0FF;font-family:Syne,sans-serif;font-size:1rem;text-transform:uppercase;letter-spacing:.08em;margin-bottom:12px;">Indicadores Clave del Mercado</h3>', unsafe_allow_html=True)
k1,k2,k3,k4,k5,k6 = st.columns(6)
with k1: st.metric("Productos",    str(len(df)),                    delta=f"de {len(df_full)}")
with k2: st.metric("Vol Mensual",  fmt(df["vol_usd"].sum()),         delta="USD global")
with k3: st.metric("Unidades/mes", f"{df['unidades'].sum():,.0f}",   delta="total")
with k4: st.metric("Precio Prom.", f"${df['precio'].mean():.0f}",    delta="USD")
with k5: st.metric("Rating Prom.", f"{df['rating'].mean():.1f}/5",   delta="avg")
with k6: st.metric("Margen Prom.", f"{df['margen'].mean():.1f}%",    delta="vs mercado")
st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Top 10", "Tendencias", "Precios y Rotacion", "Explorador", "Comparativo"
])

# ────────── TAB 1: TOP 10 ──────────
with tab1:
    top10 = df_s.head(10).reset_index(drop=True)
    if len(top10) == 0:
        st.warning("Sin productos con los filtros actuales.")
    else:
        fig = go.Figure(go.Bar(
            y=top10["nombre"].apply(lambda x: x[:45]+"..." if len(x)>45 else x),
            x=top10[sort_by],
            orientation="h",
            marker=dict(
                color=top10[sort_by].tolist(),
                colorscale=[[0,"#1A3A5C"],[0.5,"#1E5FAD"],[1,"#54A0FF"]],
                showscale=False,
            ),
            text=top10[sort_by].apply(lambda x: fmt(x) if sort_by=="vol_usd" else f"{x:,.0f}"),
            textposition="outside",
            textfont=dict(color="#EEF6FF", size=11),
        ))
        fig.update_layout(
            **theme(), height=400,
            margin=dict(l=10,r=100,t=20,b=10),
            showlegend=False,
            xaxis=ax(title=sort_by.replace("_"," ").title()),
            yaxis=ax(extra={"categoryorder":"total ascending"}),
        )
        st.plotly_chart(fig, use_container_width=True)

        for i, row in top10.iterrows():
            rank  = i + 1
            medal = "Gold #1" if rank==1 else "Silver #2" if rank==2 else "Bronze #3" if rank==3 else f"#{rank}"
            with st.expander(f"{medal} | {row['nombre']} — {row['marca']} | ${row['precio']:.2f}", expanded=(rank<=2)):
                ca,cb,cc,cd = st.columns(4)
                with ca:
                    st.metric("Precio",    f"${row['precio']:.2f}")
                    st.metric("Mercado",   f"${row['mercado']:.2f}")
                with cb:
                    st.metric("Unid/mes",  f"{row['unidades']:,}")
                    st.metric("Vol USD",   fmt(row['vol_usd']))
                with cc:
                    st.metric("Rating",    f"{row['rating']}/5")
                    st.metric("Reviews",   f"{row['reviews']:,}")
                with cd:
                    st.metric("Margen",    f"{row['margen']}%")
                    st.metric("Score",     f"{row['score']:.0f}")
                plat_str = ", ".join(row["plat"]) if isinstance(row["plat"], list) else str(row["plat"])
                st.markdown(f"""
                <div class="card">
                  <table style="width:100%;border-collapse:collapse;">
                    <tr>
                      <td style="padding:4px 10px;color:#A8D8F0;font-size:.82rem;">Origen</td>
                      <td style="padding:4px 10px;color:#EEF6FF;">{row['origen']}</td>
                      <td style="padding:4px 10px;color:#A8D8F0;font-size:.82rem;">Categoria</td>
                      <td style="padding:4px 10px;color:#EEF6FF;">{row['cat']} &rsaquo; {row['sub']}</td>
                    </tr>
                    <tr>
                      <td style="padding:4px 10px;color:#A8D8F0;font-size:.82rem;">Target</td>
                      <td style="padding:4px 10px;color:#EEF6FF;">{row['target']}</td>
                      <td style="padding:4px 10px;color:#A8D8F0;font-size:.82rem;">Plataformas</td>
                      <td style="padding:4px 10px;color:#EEF6FF;">{plat_str}</td>
                    </tr>
                    <tr>
                      <td style="padding:4px 10px;color:#A8D8F0;font-size:.82rem;">Tendencia</td>
                      <td style="padding:4px 10px;color:#EEF6FF;">{tend_icon(row['tend'])}</td>
                      <td style="padding:4px 10px;color:#A8D8F0;font-size:.82rem;">Rotacion</td>
                      <td style="padding:4px 10px;">{rot_badge(row['rot'])}</td>
                    </tr>
                  </table>
                  <div style="margin-top:8px;padding-top:8px;border-top:1px solid #1E5FAD30;font-size:.82rem;">
                    <span style="color:#A8D8F0;">Problema: </span>
                    <span style="color:#54A0FF;">{row['problema']}</span>
                  </div>
                  <div style="margin-top:4px;font-size:.8rem;color:#DDE8F5;">{row['desc']}</div>
                  <div style="margin-top:4px;font-size:.72rem;color:#A8D8F090;">Fuente: {row['fuente']}</div>
                </div>""", unsafe_allow_html=True)

# ────────── TAB 2: TENDENCIAS ──────────
with tab2:
    col1, col2 = st.columns(2)
    with col1:
        tc = df_full["tend"].value_counts().reset_index()
        tc.columns = ["tend","n"]
        lmap = {"muy_creciente":"Muy Creciente","creciente":"Creciente","estable":"Estable","decreciente":"Decreciente"}
        tc["label"] = tc["tend"].map(lmap)
        fig = go.Figure(go.Pie(
            labels=tc["label"], values=tc["n"], hole=0.6,
            marker=dict(colors=["#54A0FF","#2E86DE","#1E5FAD","#E17055"],
                        line=dict(color="#0A1628",width=2)),
            textinfo="label+percent",
            textfont=dict(size=11, color="#EEF6FF"),
        ))
        fig.update_layout(**theme(), title="Distribucion por Tendencia",
                          height=300, margin=dict(l=20,r=20,t=50,b=20), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        vc = df_full.groupby("cat")["vol_usd"].sum().sort_values()
        fig = go.Figure(go.Bar(
            y=vc.index, x=vc.values, orientation="h",
            marker=dict(color=list(vc.values),
                        colorscale=[[0,"#1A3A5C"],[1,"#54A0FF"]], showscale=False),
            text=[fmt(v) for v in vc.values],
            textposition="outside",
            textfont=dict(color="#EEF6FF",size=10),
        ))
        fig.update_layout(**theme(), title="Volumen Mensual por Categoria (USD)",
                          height=300, margin=dict(l=10,r=90,t=50,b=10), showlegend=False,
                          xaxis=ax(), yaxis=ax())
        st.plotly_chart(fig, use_container_width=True)

    # Simulador
    st.markdown('<h4 style="color:#54A0FF;font-family:Syne,sans-serif;margin:20px 0 10px;">Simulador Precio-Rotacion (12 meses)</h4>', unsafe_allow_html=True)
    sel = st.selectbox("Producto:", df_full["nombre"].tolist(), key="sim")
    row = df_full[df_full["nombre"]==sel].iloc[0]
    ph  = gen_prices(row["precio"])
    rh  = gen_units(row["unidades"], row["tend"])
    ml  = [x["mes"]      for x in ph]
    pl  = [x["precio"]   for x in ph]
    ul  = [x["unidades"] for x in rh]

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=ml, y=pl, name="Precio USD",
        line=dict(color="#FFC300",width=3), mode="lines+markers",
        marker=dict(size=7)), secondary_y=False)
    fig.add_trace(go.Bar(x=ml, y=ul, name="Unidades",
        marker=dict(color="#54A0FF",opacity=0.7)), secondary_y=True)
    fig.update_layout(**theme(), title=f"Precio vs Rotacion — {sel[:45]}",
                      height=350, margin=dict(l=20,r=20,t=50,b=40),
                      legend=dict(orientation="h",y=1.05,bgcolor="rgba(0,0,0,0)"),
                      hovermode="x unified", xaxis=ax())
    fig.update_yaxes(title_text="Precio USD",    secondary_y=False, gridcolor="#1E5FAD25", linecolor="#1A3A5C", tickfont={"color":"#A8D8F0"})
    fig.update_yaxes(title_text="Unidades/mes",  secondary_y=True,  gridcolor="#1E5FAD25", linecolor="#1A3A5C", tickfont={"color":"#A8D8F0"})
    st.plotly_chart(fig, use_container_width=True)

    pchg = (pl[-1]-pl[0])/pl[0]*100
    uchg = (ul[-1]-ul[0])/ul[0]*100 if ul[0]>0 else 0
    corr = float(np.corrcoef(pl, ul)[0,1])
    if   pchg < -3 and uchg < 5: insight = "Alerta: Precio baja sin que la rotacion suba — revisar competitividad."
    elif uchg > 0:                insight = "Saludable: Rotacion creciente independiente del precio."
    else:                         insight = "Comportamiento normal de mercado."
    st.markdown(f"""
    <div class="card">
      <div style="font-family:Syne,sans-serif;font-weight:700;color:#EEF6FF;margin-bottom:10px;">Insight Automatico</div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;">
        <div><span style="color:#A8D8F0;font-size:.78rem;">Variacion precio 12m</span><br>
          <span style="color:#FFC300;font-size:1.2rem;font-weight:700;">{"+" if pchg>0 else ""}{pchg:.1f}%</span></div>
        <div><span style="color:#A8D8F0;font-size:.78rem;">Variacion rotacion 12m</span><br>
          <span style="color:#54A0FF;font-size:1.2rem;font-weight:700;">{"+" if uchg>0 else ""}{uchg:.1f}%</span></div>
        <div><span style="color:#A8D8F0;font-size:.78rem;">Correlacion P-R</span><br>
          <span style="color:#00B894;font-size:1.2rem;font-weight:700;">{corr:.2f}</span></div>
      </div>
      <div style="margin-top:10px;padding-top:8px;border-top:1px solid #1E5FAD30;color:#DDE8F5;font-size:.84rem;">{insight}</div>
    </div>""", unsafe_allow_html=True)

# ────────── TAB 3: PRECIOS & ROTACIÓN ──────────
with tab3:
    col1, col2 = st.columns(2)
    with col1:
        fig = px.scatter(df_full, x="precio", y="rating", size="unidades",
            color="cat", hover_name="nombre",
            color_discrete_sequence=px.colors.sequential.Blues_r,
            labels={"precio":"Precio USD","rating":"Rating","cat":"Categoria"})
        fig.update_layout(**theme(), title="Precio vs Rating (tamano = volumen)",
                          height=360, margin=dict(l=20,r=20,t=50,b=30),
                          xaxis=ax(), yaxis=ax(),
                          legend=dict(orientation="h",y=-0.28,font=dict(size=9),bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        dfc = df_full.copy()
        dfc["rango"] = pd.cut(dfc["precio"], bins=[0,20,50,100,250],
                               labels=["$0-20","$20-50","$50-100","$100+"])
        fig = px.box(dfc.dropna(subset=["rango"]), x="rango", y="unidades",
            color="rango",
            color_discrete_sequence=["#1A3A5C","#1E5FAD","#2E86DE","#54A0FF"],
            labels={"rango":"Rango precio","unidades":"Unidades/mes"})
        fig.update_layout(**theme(), title="Volumen por Rango de Precio",
                          height=360, showlegend=False, margin=dict(l=20,r=20,t=50,b=30),
                          xaxis=ax(), yaxis=ax())
        st.plotly_chart(fig, use_container_width=True)

    # Heatmap
    st.markdown('<h4 style="color:#54A0FF;font-family:Syne,sans-serif;margin:20px 0 10px;">Heatmap Rotacion — Categoria x Tendencia</h4>', unsafe_allow_html=True)
    piv = df_full.groupby(["cat","tend"])["unidades"].sum().reset_index()
    piv = piv.pivot(index="cat", columns="tend", values="unidades").fillna(0)
    fig = go.Figure(go.Heatmap(
        z=piv.values, x=piv.columns.tolist(), y=piv.index.tolist(),
        colorscale=[[0,"#0A1628"],[0.3,"#1A3A5C"],[0.6,"#1E5FAD"],[1,"#54A0FF"]],
        text=[[fmt(v) for v in r] for r in piv.values],
        texttemplate="%{text}",
        textfont=dict(size=10, color="#EEF6FF"),
        colorbar=dict(tickfont=dict(color="#A8D8F0")),
    ))
    fig.update_layout(**theme(), title="Unidades/mes — Categoria x Tendencia",
                      height=380, margin=dict(l=20,r=80,t=50,b=30),
                      xaxis=ax(), yaxis=ax())
    st.plotly_chart(fig, use_container_width=True)

# ────────── TAB 4: EXPLORADOR ──────────
with tab4:
    search = st.text_input("Buscar por nombre, marca o problema...",
                           placeholder="Ej: acne, retinol, Sephora, caida cabello...")
    dfe = df_full.copy()
    if search:
        q = search.lower()
        mask = (dfe["nombre"].str.lower().str.contains(q,na=False) |
                dfe["marca"].str.lower().str.contains(q,na=False)  |
                dfe["problema"].str.lower().str.contains(q,na=False)|
                dfe["cat"].str.lower().str.contains(q,na=False)    |
                dfe["desc"].str.lower().str.contains(q,na=False))
        dfe = dfe[mask]
    st.markdown(f'<p style="color:#A8D8F0;font-size:.84rem;">Mostrando {len(dfe)} productos</p>', unsafe_allow_html=True)
    if len(dfe) == 0:
        st.warning("Sin resultados.")
    else:
        disp = dfe[["id","nombre","marca","cat","precio","mercado","margen","unidades","rating","tend","rot","target","fuente"]].copy()
        disp.columns = ["ID","Producto","Marca","Categoria","Precio","Mercado","Margen%","Unid/mes","Rating","Tendencia","Rotacion","Target","Fuente"]
        disp["Tendencia"] = disp["Tendencia"].map({"muy_creciente":"Muy Creciente","creciente":"Creciente","estable":"Estable","decreciente":"Decreciente"})
        disp["Rotacion"]  = disp["Rotacion"].map({"muy_alta":"Muy Alta","alta":"Alta","media_alta":"Media-Alta","media":"Media","baja":"Baja"})
        disp["Precio"]    = disp["Precio"].apply(lambda x: f"${x:.2f}")
        disp["Mercado"]   = disp["Mercado"].apply(lambda x: f"${x:.2f}")
        disp["Margen%"]   = disp["Margen%"].apply(lambda x: f"{x:.1f}%")
        disp["Unid/mes"]  = disp["Unid/mes"].apply(lambda x: f"{x:,}")
        disp["Rating"]    = disp["Rating"].apply(lambda x: f"{x:.1f}")
        st.dataframe(disp, use_container_width=True, hide_index=True, height=460)
        csv = dfe.drop(columns=["plat","img","url"], errors="ignore").to_csv(index=False).encode("utf-8")
        st.download_button("Descargar CSV", csv,
            f"rome_market_{now.strftime('%Y%m')}.csv", "text/csv")

# ────────── TAB 5: COMPARATIVO ──────────
with tab5:
    col1, col2 = st.columns(2)
    with col1:
        fig = px.treemap(df_full, path=["cat","sub"], values="vol_usd",
            color="score",
            color_continuous_scale=[[0,"#1A3A5C"],[0.5,"#1E5FAD"],[1,"#54A0FF"]])
        fig.update_layout(**theme(), title="Mapa de Oportunidades por Volumen USD",
                          height=400, margin=dict(l=10,r=10,t=50,b=10),
                          coloraxis_colorbar=dict(title="Score",tickfont=dict(color="#A8D8F0")))
        fig.update_traces(textfont=dict(size=11,color="white"),
                          marker=dict(line=dict(width=2,color="#0A1628")))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        dfo   = df_full.nlargest(10,"margen")
        names = dfo["nombre"].apply(lambda x: x[:26]+"..." if len(x)>26 else x)
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Precio propio",  x=names, y=dfo["precio"],  marker_color="#1E5FAD"))
        fig.add_trace(go.Bar(name="Precio mercado", x=names, y=dfo["mercado"], marker_color="#54A0FF"))
        fig.update_layout(**theme(), title="Top 10 Mayor Margen vs Mercado",
                          barmode="group", height=400,
                          margin=dict(l=10,r=10,t=50,b=90),
                          legend=dict(orientation="h",y=1.05,bgcolor="rgba(0,0,0,0)"),
                          xaxis=ax(tickangle=-35, extra={"tickfont":{"color":"#A8D8F0","size":9}}),
                          yaxis=ax())
        st.plotly_chart(fig, use_container_width=True)

    # Radar
    st.markdown('<h4 style="color:#54A0FF;font-family:Syne,sans-serif;margin:20px 0 10px;">Radar de Competitividad por Categoria</h4>', unsafe_allow_html=True)
    rc = df_full.groupby("cat").agg(
        rating=("rating","mean"),
        margen=("margen","mean"),
        unidades=("unidades", lambda x: x.mean()/1000),
        score=("score","mean"),
        precio=("precio", lambda x: max(0.0, 10-(x.mean()/30)))
    ).reset_index()

    cats6   = rc["cat"].head(6).tolist()
    mlabels = ["Rating","Margen","Vol(K)","Score","Precio Comp."]
    mcols   = ["rating","margen","unidades","score","precio"]
    max_v   = [5,15,120,120,10]
    colors6 = ["#54A0FF","#FFC300","#00B894","#FDCB6E","#A8D8F0","#2E86DE"]

    fig = go.Figure()
    for i, cat in enumerate(cats6):
        row  = rc[rc["cat"]==cat].iloc[0]
        vals = [min(float(row[m])/(mx or 1)*10, 10) for m,mx in zip(mcols,max_v)]
        vals.append(vals[0])
        fig.add_trace(go.Scatterpolar(
            r=vals, theta=mlabels+[mlabels[0]],
            fill="toself", name=cat,
            fillcolor=colors6[i%len(colors6)]+"20",
            line=dict(color=colors6[i%len(colors6)], width=2),
        ))
    fig.update_layout(
        **theme(),
        polar=dict(
            bgcolor="#0D213780",
            radialaxis=dict(visible=True, range=[0,10],
                            tickfont=dict(color="#A8D8F0",size=9),
                            gridcolor="#1E5FAD30"),
            angularaxis=dict(tickfont=dict(color="#DDE8F5",size=11),
                             gridcolor="#1E5FAD30"),
        ),
        title="Radar — Top 6 Categorias",
        height=450,
        legend=dict(orientation="h",y=-0.1,font=dict(size=10),bgcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown(f'<div style="text-align:center;padding:16px 0;color:#A8D8F0;font-size:.78rem;"><span style="font-family:Syne,sans-serif;font-size:1rem;color:#54A0FF;font-weight:700;">ESTUDIO DE MERCADO ROME</span> &nbsp;·&nbsp; {now.strftime("%B %Y")} &nbsp;·&nbsp; {len(df_full)} productos &nbsp;·&nbsp; Fuentes: Base Local · Makeup API<br><br><span style="opacity:.5;font-size:.7rem;">Estimaciones con fines de analisis competitivo. Actualizacion mensual.</span></div>', unsafe_allow_html=True)
