"""
Base de datos de productos de belleza y cuidado personal
Mercado internacional - No tradicionales - Competitivos globalmente
Actualización mensual con historial de precios y rotación
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# ─────────────────────────────────────────────
# SEED para reproducibilidad
random.seed(42)
np.random.seed(42)

# ─────────────────────────────────────────────
# BASE DE DATOS DE PRODUCTOS
# ─────────────────────────────────────────────

PRODUCTS = [

    # ════════════════════════════════════════
    # CATEGORÍA 1: PIEL - TRATAMIENTOS AVANZADOS
    # ════════════════════════════════════════
    {
        "id": "SK001", "categoria": "Piel", "subcategoria": "Sueros y Activos",
        "nombre": "The Ordinary Niacinamide 10% + Zinc 1%",
        "marca": "The Ordinary", "origen": "Canadá",
        "precio_usd": 6.90, "precio_promedio_mercado": 8.50,
        "plataformas": ["Amazon", "ASOS", "Sephora"],
        "unidades_mes": 85000, "rating": 4.6, "reviews": 125000,
        "tendencia": "estable", "rotacion": "muy_alta",
        "descripcion": "Suero con Niacinamida 10% para poros y manchas",
        "target": "Mixto", "tipo_piel": "Grasa/Mixta",
        "problema_ataca": "Poros dilatados, manchas, acné"
    },
    {
        "id": "SK002", "categoria": "Piel", "subcategoria": "Sueros y Activos",
        "nombre": "Paula's Choice BHA 2% Liquid Exfoliant",
        "marca": "Paula's Choice", "origen": "USA",
        "precio_usd": 34.00, "precio_promedio_mercado": 36.00,
        "plataformas": ["Paula's Choice", "Amazon", "Dermstore"],
        "unidades_mes": 42000, "rating": 4.8, "reviews": 98000,
        "tendencia": "creciente", "rotacion": "alta",
        "descripcion": "Exfoliante químico BHA para poros y acné",
        "target": "Mixto", "tipo_piel": "Grasa",
        "problema_ataca": "Poros, acné, piel opaca"
    },
    {
        "id": "SK003", "categoria": "Piel", "subcategoria": "Vitamina C",
        "nombre": "Skinceuticals C E Ferulic",
        "marca": "SkinCeuticals", "origen": "USA",
        "precio_usd": 182.00, "precio_promedio_mercado": 185.00,
        "plataformas": ["Dermstore", "Sephora", "Amazon"],
        "unidades_mes": 18000, "rating": 4.7, "reviews": 45000,
        "tendencia": "estable", "rotacion": "media",
        "descripcion": "Vitamina C profesional antioxidante premium",
        "target": "Femenino", "tipo_piel": "Todos",
        "problema_ataca": "Manchas, envejecimiento, opacidad"
    },
    {
        "id": "SK004", "categoria": "Piel", "subcategoria": "Retinol",
        "nombre": "Differin Adapalene Gel 0.1%",
        "marca": "Differin", "origen": "USA",
        "precio_usd": 15.50, "precio_promedio_mercado": 18.00,
        "plataformas": ["Amazon", "Walmart", "Target"],
        "unidades_mes": 95000, "rating": 4.5, "reviews": 187000,
        "tendencia": "muy_creciente", "rotacion": "muy_alta",
        "descripcion": "Retinoide OTC más potente del mercado",
        "target": "Mixto", "tipo_piel": "Grasa/Mixta",
        "problema_ataca": "Acné severo, cicatrices, envejecimiento"
    },
    {
        "id": "SK005", "categoria": "Piel", "subcategoria": "Hidratación",
        "nombre": "CeraVe Moisturizing Cream",
        "marca": "CeraVe", "origen": "USA",
        "precio_usd": 19.00, "precio_promedio_mercado": 21.00,
        "plataformas": ["Amazon", "Walmart", "CVS"],
        "unidades_mes": 210000, "rating": 4.8, "reviews": 320000,
        "tendencia": "estable", "rotacion": "muy_alta",
        "descripcion": "Crema hidratante con ceramidas para barrera cutánea",
        "target": "Mixto", "tipo_piel": "Seca/Normal",
        "problema_ataca": "Sequedad, barrera cutánea dañada"
    },
    {
        "id": "SK006", "categoria": "Piel", "subcategoria": "Manchas",
        "nombre": "Good Molecules Discoloration Correcting Serum",
        "marca": "Good Molecules", "origen": "USA",
        "precio_usd": 12.00, "precio_promedio_mercado": 14.00,
        "plataformas": ["Ulta", "Amazon"],
        "unidades_mes": 31000, "rating": 4.4, "reviews": 22000,
        "tendencia": "creciente", "rotacion": "media_alta",
        "descripcion": "Suero despigmentante con tranexámico",
        "target": "Femenino", "tipo_piel": "Todos",
        "problema_ataca": "Hiperpigmentación, manchas oscuras"
    },
    {
        "id": "SK007", "categoria": "Piel", "subcategoria": "Celulitis",
        "nombre": "Sol de Janeiro Brazilian Bum Bum Cream",
        "marca": "Sol de Janeiro", "origen": "Brasil/USA",
        "precio_usd": 48.00, "precio_promedio_mercado": 50.00,
        "plataformas": ["Sephora", "Amazon", "Ulta"],
        "unidades_mes": 55000, "rating": 4.6, "reviews": 78000,
        "tendencia": "muy_creciente", "rotacion": "alta",
        "descripcion": "Crema reafirmante con cafeína y aceite de cupuaçu",
        "target": "Femenino", "tipo_piel": "Todos",
        "problema_ataca": "Celulitis, flacidez, piel seca"
    },
    {
        "id": "SK008", "categoria": "Piel", "subcategoria": "Estrías",
        "nombre": "Bio-Oil Skincare Oil",
        "marca": "Bio-Oil", "origen": "Sudáfrica",
        "precio_usd": 14.00, "precio_promedio_mercado": 16.00,
        "plataformas": ["Amazon", "Walmart", "Target"],
        "unidades_mes": 120000, "rating": 4.5, "reviews": 145000,
        "tendencia": "estable", "rotacion": "muy_alta",
        "descripcion": "Aceite especializado para estrías y cicatrices",
        "target": "Femenino", "tipo_piel": "Todos",
        "problema_ataca": "Estrías, cicatrices, manchas"
    },
    {
        "id": "SK009", "categoria": "Piel", "subcategoria": "Ojeras",
        "nombre": "Kiehl's Creamy Eye Treatment Avocado",
        "marca": "Kiehl's", "origen": "USA",
        "precio_usd": 32.00, "precio_promedio_mercado": 35.00,
        "plataformas": ["Kiehl's", "Sephora", "Amazon"],
        "unidades_mes": 28000, "rating": 4.5, "reviews": 41000,
        "tendencia": "estable", "rotacion": "media_alta",
        "descripcion": "Tratamiento contorno de ojos con aguacate",
        "target": "Mixto", "tipo_piel": "Seca/Normal",
        "problema_ataca": "Ojeras, bolsas, arrugas contorno"
    },
    {
        "id": "SK010", "categoria": "Piel", "subcategoria": "Acné",
        "nombre": "La Roche-Posay Effaclar Duo+",
        "marca": "La Roche-Posay", "origen": "Francia",
        "precio_usd": 30.00, "precio_promedio_mercado": 33.00,
        "plataformas": ["Amazon", "Dermstore", "Ulta"],
        "unidades_mes": 68000, "rating": 4.6, "reviews": 89000,
        "tendencia": "creciente", "rotacion": "alta",
        "descripcion": "Tratamiento anti-imperfecciones para acné",
        "target": "Mixto", "tipo_piel": "Grasa",
        "problema_ataca": "Acné, poros, exceso de grasa"
    },

    # ════════════════════════════════════════
    # CATEGORÍA 2: CABELLO
    # ════════════════════════════════════════
    {
        "id": "CA001", "categoria": "Cabello", "subcategoria": "Caída",
        "nombre": "Viviscal Extra Strength Hair Growth",
        "marca": "Viviscal", "origen": "USA",
        "precio_usd": 49.99, "precio_promedio_mercado": 54.00,
        "plataformas": ["Amazon", "Ulta", "CVS"],
        "unidades_mes": 38000, "rating": 4.3, "reviews": 62000,
        "tendencia": "creciente", "rotacion": "alta",
        "descripcion": "Suplemento clínico para crecimiento capilar",
        "target": "Mixto", "tipo_piel": "N/A",
        "problema_ataca": "Caída del cabello, alopecia"
    },
    {
        "id": "CA002", "categoria": "Cabello", "subcategoria": "Caída",
        "nombre": "Minoxidil 5% Kirkland Foam",
        "marca": "Kirkland", "origen": "USA",
        "precio_usd": 29.00, "precio_promedio_mercado": 35.00,
        "plataformas": ["Amazon", "Costco", "Walmart"],
        "unidades_mes": 95000, "rating": 4.4, "reviews": 134000,
        "tendencia": "muy_creciente", "rotacion": "muy_alta",
        "descripcion": "Minoxidil espuma 5% para calvicie masculina",
        "target": "Masculino", "tipo_piel": "N/A",
        "problema_ataca": "Calvicie, entradas, alopecia androgenética"
    },
    {
        "id": "CA003", "categoria": "Cabello", "subcategoria": "Brillo y Fuerza",
        "nombre": "Olaplex No.3 Hair Perfector",
        "marca": "Olaplex", "origen": "USA",
        "precio_usd": 30.00, "precio_promedio_mercado": 32.00,
        "plataformas": ["Sephora", "Amazon", "Ulta"],
        "unidades_mes": 72000, "rating": 4.6, "reviews": 115000,
        "tendencia": "estable", "rotacion": "muy_alta",
        "descripcion": "Tratamiento reparador de enlaces moleculares",
        "target": "Femenino", "tipo_piel": "N/A",
        "problema_ataca": "Cabello quebradizo, sin brillo, dañado"
    },
    {
        "id": "CA004", "categoria": "Cabello", "subcategoria": "Caspa",
        "nombre": "Nizoral Anti-Dandruff Shampoo",
        "marca": "Nizoral", "origen": "USA",
        "precio_usd": 15.00, "precio_promedio_mercado": 17.00,
        "plataformas": ["Amazon", "CVS", "Walgreens"],
        "unidades_mes": 88000, "rating": 4.6, "reviews": 98000,
        "tendencia": "estable", "rotacion": "muy_alta",
        "descripcion": "Champú medicado con ketoconazol 1%",
        "target": "Mixto", "tipo_piel": "N/A",
        "problema_ataca": "Caspa, dermatitis seborreica"
    },
    {
        "id": "CA005", "categoria": "Cabello", "subcategoria": "Volumen",
        "nombre": "Bumble and bumble Thickening Spray",
        "marca": "Bumble and bumble", "origen": "USA",
        "precio_usd": 33.00, "precio_promedio_mercado": 35.00,
        "plataformas": ["Sephora", "Ulta", "Amazon"],
        "unidades_mes": 29000, "rating": 4.4, "reviews": 32000,
        "tendencia": "creciente", "rotacion": "media_alta",
        "descripcion": "Spray texturizador para cabello fino sin volumen",
        "target": "Femenino", "tipo_piel": "N/A",
        "problema_ataca": "Cabello fino, sin volumen"
    },
    {
        "id": "CA006", "categoria": "Cabello", "subcategoria": "Canas",
        "nombre": "Madison Reed Root Touch Up",
        "marca": "Madison Reed", "origen": "USA",
        "precio_usd": 26.00, "precio_promedio_mercado": 28.00,
        "plataformas": ["Amazon", "Ulta", "Target"],
        "unidades_mes": 51000, "rating": 4.5, "reviews": 67000,
        "tendencia": "creciente", "rotacion": "alta",
        "descripcion": "Kit retoque de raíces sin amoníaco",
        "target": "Mixto", "tipo_piel": "N/A",
        "problema_ataca": "Canas prematuras, raíces visibles"
    },

    # ════════════════════════════════════════
    # CATEGORÍA 3: CUERPO Y PESO
    # ════════════════════════════════════════
    {
        "id": "CO001", "categoria": "Cuerpo", "subcategoria": "Grasa Localizada",
        "nombre": "Isavera Fat Freezing System",
        "marca": "Isavera", "origen": "USA",
        "precio_usd": 59.00, "precio_promedio_mercado": 65.00,
        "plataformas": ["Amazon"],
        "unidades_mes": 22000, "rating": 3.9, "reviews": 18000,
        "tendencia": "creciente", "rotacion": "media",
        "descripcion": "Sistema casero de criolipólisis",
        "target": "Mixto", "tipo_piel": "N/A",
        "problema_ataca": "Grasa localizada, papada, llantas"
    },
    {
        "id": "CO002", "categoria": "Cuerpo", "subcategoria": "Masa Muscular",
        "nombre": "Optimum Nutrition Gold Standard Whey",
        "marca": "Optimum Nutrition", "origen": "USA",
        "precio_usd": 58.00, "precio_promedio_mercado": 65.00,
        "plataformas": ["Amazon", "GNC", "Bodybuilding.com"],
        "unidades_mes": 185000, "rating": 4.7, "reviews": 290000,
        "tendencia": "estable", "rotacion": "muy_alta",
        "descripcion": "Proteína de suero de leche premium",
        "target": "Masculino", "tipo_piel": "N/A",
        "problema_ataca": "Falta de masa muscular, delgadez"
    },
    {
        "id": "CO003", "categoria": "Cuerpo", "subcategoria": "Flacidez",
        "nombre": "Bliss Spa Fat Girl Slim Arm Candy",
        "marca": "Bliss", "origen": "USA",
        "precio_usd": 38.00, "precio_promedio_mercado": 42.00,
        "plataformas": ["Amazon", "Ulta"],
        "unidades_mes": 18000, "rating": 4.1, "reviews": 12000,
        "tendencia": "creciente", "rotacion": "media",
        "descripcion": "Crema reafirmante para brazos con cafeína",
        "target": "Femenino", "tipo_piel": "N/A",
        "problema_ataca": "Flacidez brazos, celulitis"
    },
    {
        "id": "CO004", "categoria": "Cuerpo", "subcategoria": "Glúteos",
        "nombre": "Gluteboost Enhancement Cream",
        "marca": "Gluteboost", "origen": "USA",
        "precio_usd": 44.95, "precio_promedio_mercado": 50.00,
        "plataformas": ["Amazon", "gluteboost.com"],
        "unidades_mes": 15000, "rating": 4.0, "reviews": 8500,
        "tendencia": "muy_creciente", "rotacion": "media_alta",
        "descripcion": "Crema potenciadora de glúteos con fitohormonas",
        "target": "Femenino", "tipo_piel": "N/A",
        "problema_ataca": "Falta de volumen en glúteos"
    },

    # ════════════════════════════════════════
    # CATEGORÍA 4: SONRISA Y ROSTRO
    # ════════════════════════════════════════
    {
        "id": "SO001", "categoria": "Sonrisa", "subcategoria": "Blanqueamiento",
        "nombre": "Crest 3D Whitestrips Professional",
        "marca": "Crest", "origen": "USA",
        "precio_usd": 49.99, "precio_promedio_mercado": 55.00,
        "plataformas": ["Amazon", "Walmart", "CVS"],
        "unidades_mes": 145000, "rating": 4.4, "reviews": 198000,
        "tendencia": "estable", "rotacion": "muy_alta",
        "descripcion": "Tiras blanqueadoras profesionales en casa",
        "target": "Mixto", "tipo_piel": "N/A",
        "problema_ataca": "Dientes amarillos, manchados"
    },
    {
        "id": "SO002", "categoria": "Sonrisa", "subcategoria": "Cuidado Dental",
        "nombre": "Moon Teeth Whitening Activated Charcoal",
        "marca": "Moon", "origen": "USA",
        "precio_usd": 12.99, "precio_promedio_mercado": 15.00,
        "plataformas": ["Amazon", "Target", "Ulta"],
        "unidades_mes": 48000, "rating": 4.2, "reviews": 31000,
        "tendencia": "creciente", "rotacion": "alta",
        "descripcion": "Pasta blanqueadora con carbón activado",
        "target": "Mixto", "tipo_piel": "N/A",
        "problema_ataca": "Dientes amarillos, mal aliento"
    },
    {
        "id": "SO003", "categoria": "Rostro", "subcategoria": "Labios",
        "nombre": "NUXE Rêve de Miel Ultra Nourishing Lip Balm",
        "marca": "NUXE", "origen": "Francia",
        "precio_usd": 20.00, "precio_promedio_mercado": 22.00,
        "plataformas": ["Amazon", "Sephora", "Dermstore"],
        "unidades_mes": 35000, "rating": 4.7, "reviews": 42000,
        "tendencia": "estable", "rotacion": "alta",
        "descripcion": "Bálsamo labial ultra nutritivo con miel",
        "target": "Femenino", "tipo_piel": "N/A",
        "problema_ataca": "Labios secos, labios finos, agrietados"
    },

    # ════════════════════════════════════════
    # CATEGORÍA 5: MIRADA Y EXPRESIÓN
    # ════════════════════════════════════════
    {
        "id": "MI001", "categoria": "Mirada", "subcategoria": "Bolsas",
        "nombre": "Neutrogena Rapid Wrinkle Repair Eye Cream",
        "marca": "Neutrogena", "origen": "USA",
        "precio_usd": 22.00, "precio_promedio_mercado": 25.00,
        "plataformas": ["Amazon", "Walmart", "CVS"],
        "unidades_mes": 62000, "rating": 4.4, "reviews": 82000,
        "tendencia": "estable", "rotacion": "muy_alta",
        "descripcion": "Contorno de ojos con retinol acelerado",
        "target": "Femenino", "tipo_piel": "N/A",
        "problema_ataca": "Bolsas, ojeras, arrugas contorno"
    },
    {
        "id": "MI002", "categoria": "Mirada", "subcategoria": "Cejas",
        "nombre": "Revive Science Castor Oil Eyebrow Serum",
        "marca": "Revive Science", "origen": "USA",
        "precio_usd": 19.95, "precio_promedio_mercado": 22.00,
        "plataformas": ["Amazon"],
        "unidades_mes": 28000, "rating": 4.3, "reviews": 19000,
        "tendencia": "muy_creciente", "rotacion": "alta",
        "descripcion": "Suero aceite de ricino para cejas y pestañas",
        "target": "Femenino", "tipo_piel": "N/A",
        "problema_ataca": "Cejas escasas, pestañas cortas"
    },
    {
        "id": "MI003", "categoria": "Mirada", "subcategoria": "Pestañas",
        "nombre": "RapidLash Eyelash Enhancing Serum",
        "marca": "RapidLash", "origen": "USA",
        "precio_usd": 49.99, "precio_promedio_mercado": 55.00,
        "plataformas": ["Amazon", "Ulta", "CVS"],
        "unidades_mes": 32000, "rating": 4.4, "reviews": 28000,
        "tendencia": "creciente", "rotacion": "alta",
        "descripcion": "Suero clínico para crecimiento de pestañas",
        "target": "Femenino", "tipo_piel": "N/A",
        "problema_ataca": "Pestañas cortas, ralas, cejas escasas"
    },

    # ════════════════════════════════════════
    # CATEGORÍA 6: VELLO CORPORAL
    # ════════════════════════════════════════
    {
        "id": "VE001", "categoria": "Vello", "subcategoria": "Depilación",
        "nombre": "Ulike Air 3 IPL Hair Removal Device",
        "marca": "Ulike", "origen": "China/Global",
        "precio_usd": 219.00, "precio_promedio_mercado": 250.00,
        "plataformas": ["Amazon", "ulike.com"],
        "unidades_mes": 41000, "rating": 4.4, "reviews": 52000,
        "tendencia": "muy_creciente", "rotacion": "alta",
        "descripcion": "Dispositivo IPL depilación láser en casa",
        "target": "Femenino", "tipo_piel": "N/A",
        "problema_ataca": "Vello facial, vello corporal excesivo"
    },
    {
        "id": "VE002", "categoria": "Vello", "subcategoria": "Vello Encarnado",
        "nombre": "Tend Skin Solution",
        "marca": "Tend Skin", "origen": "USA",
        "precio_usd": 24.00, "precio_promedio_mercado": 26.00,
        "plataformas": ["Amazon", "Ulta", "Sephora"],
        "unidades_mes": 38000, "rating": 4.5, "reviews": 45000,
        "tendencia": "estable", "rotacion": "alta",
        "descripcion": "Solución para pelos encarnados post-depilación",
        "target": "Mixto", "tipo_piel": "N/A",
        "problema_ataca": "Vello encarnado, irritación post-depilación"
    },

    # ════════════════════════════════════════
    # CATEGORÍA 7: SUDORACIÓN Y OLOR
    # ════════════════════════════════════════
    {
        "id": "SU001", "categoria": "Sudoración", "subcategoria": "Hiperhidrosis",
        "nombre": "Carpe Antiperspirant Hand Lotion",
        "marca": "Carpe", "origen": "USA",
        "precio_usd": 14.95, "precio_promedio_mercado": 16.00,
        "plataformas": ["Amazon", "Target"],
        "unidades_mes": 45000, "rating": 4.3, "reviews": 38000,
        "tendencia": "muy_creciente", "rotacion": "alta",
        "descripcion": "Loción antitranspirante clínica para manos",
        "target": "Mixto", "tipo_piel": "N/A",
        "problema_ataca": "Sudoración excesiva, hiperhidrosis"
    },
    {
        "id": "SU002", "categoria": "Sudoración", "subcategoria": "Desodorante",
        "nombre": "Native Natural Deodorant",
        "marca": "Native", "origen": "USA",
        "precio_usd": 13.00, "precio_promedio_mercado": 15.00,
        "plataformas": ["Amazon", "Target", "Walmart"],
        "unidades_mes": 132000, "rating": 4.4, "reviews": 178000,
        "tendencia": "muy_creciente", "rotacion": "muy_alta",
        "descripcion": "Desodorante natural sin aluminio ni parabenos",
        "target": "Mixto", "tipo_piel": "N/A",
        "problema_ataca": "Mal olor corporal, transpiración"
    },

    # ════════════════════════════════════════
    # CATEGORÍA 8: MANOS, UÑAS Y PIES
    # ════════════════════════════════════════
    {
        "id": "MA001", "categoria": "Manos y Uñas", "subcategoria": "Hongos",
        "nombre": "Fungi-Nail Anti-Fungal Solution",
        "marca": "Fungi-Nail", "origen": "USA",
        "precio_usd": 18.99, "precio_promedio_mercado": 20.00,
        "plataformas": ["Amazon", "CVS", "Walmart"],
        "unidades_mes": 55000, "rating": 4.1, "reviews": 42000,
        "tendencia": "estable", "rotacion": "alta",
        "descripcion": "Solución antifúngica para uñas de manos y pies",
        "target": "Mixto", "tipo_piel": "N/A",
        "problema_ataca": "Hongos en uñas, uñas quebradizas"
    },
    {
        "id": "MA002", "categoria": "Manos y Uñas", "subcategoria": "Uñas Frágiles",
        "nombre": "OPI Nail Envy Original",
        "marca": "OPI", "origen": "USA",
        "precio_usd": 19.99, "precio_promedio_mercado": 22.00,
        "plataformas": ["Amazon", "Ulta", "Sally Beauty"],
        "unidades_mes": 78000, "rating": 4.5, "reviews": 95000,
        "tendencia": "estable", "rotacion": "muy_alta",
        "descripcion": "Endurecedor de uñas fórmula profesional",
        "target": "Femenino", "tipo_piel": "N/A",
        "problema_ataca": "Uñas frágiles, quebradizas, laminadas"
    },
    {
        "id": "MA003", "categoria": "Pies", "subcategoria": "Pies Agrietados",
        "nombre": "Baby Foot Exfoliant Foot Peel",
        "marca": "Baby Foot", "origen": "Japón",
        "precio_usd": 25.00, "precio_promedio_mercado": 28.00,
        "plataformas": ["Amazon", "Ulta", "Target"],
        "unidades_mes": 62000, "rating": 4.4, "reviews": 88000,
        "tendencia": "creciente", "rotacion": "alta",
        "descripcion": "Peeling químico exfoliante para pies",
        "target": "Mixto", "tipo_piel": "N/A",
        "problema_ataca": "Pies agrietados, callos, durezas"
    },
    {
        "id": "MA004", "categoria": "Manos y Uñas", "subcategoria": "Manos Envejecidas",
        "nombre": "L'Occitane Shea Butter Hand Cream",
        "marca": "L'Occitane", "origen": "Francia",
        "precio_usd": 32.00, "precio_promedio_mercado": 34.00,
        "plataformas": ["Sephora", "Amazon", "L'Occitane"],
        "unidades_mes": 48000, "rating": 4.8, "reviews": 72000,
        "tendencia": "estable", "rotacion": "alta",
        "descripcion": "Crema de manos ultra nutritiva con manteca de karité",
        "target": "Femenino", "tipo_piel": "N/A",
        "problema_ataca": "Manos resecas, envejecidas, agrietadas"
    },

    # ════════════════════════════════════════
    # CATEGORÍA 9: ENVEJECIMIENTO
    # ════════════════════════════════════════
    {
        "id": "EN001", "categoria": "Envejecimiento", "subcategoria": "Arrugas",
        "nombre": "RoC Retinol Correxion Line Smoothing Cream",
        "marca": "RoC", "origen": "Francia",
        "precio_usd": 25.99, "precio_promedio_mercado": 28.00,
        "plataformas": ["Amazon", "Walmart", "CVS"],
        "unidades_mes": 89000, "rating": 4.4, "reviews": 118000,
        "tendencia": "estable", "rotacion": "muy_alta",
        "descripcion": "Crema con retinol puro para arrugas",
        "target": "Femenino", "tipo_piel": "Normal/Mixta",
        "problema_ataca": "Arrugas, líneas de expresión"
    },
    {
        "id": "EN002", "categoria": "Envejecimiento", "subcategoria": "Firmeza",
        "nombre": "StriVectin-TL Tightening Neck Cream",
        "marca": "StriVectin", "origen": "USA",
        "precio_usd": 89.00, "precio_promedio_mercado": 95.00,
        "plataformas": ["Sephora", "Amazon", "Ulta"],
        "unidades_mes": 21000, "rating": 4.4, "reviews": 28000,
        "tendencia": "creciente", "rotacion": "media_alta",
        "descripcion": "Crema reafirmante para cuello y escote",
        "target": "Femenino", "tipo_piel": "N/A",
        "problema_ataca": "Flacidez cuello, pérdida firmeza"
    },
    {
        "id": "EN003", "categoria": "Envejecimiento", "subcategoria": "Manchas Edad",
        "nombre": "Murad Rapid Age Spot Correcting Serum",
        "marca": "Murad", "origen": "USA",
        "precio_usd": 86.00, "precio_promedio_mercado": 90.00,
        "plataformas": ["Sephora", "Amazon", "Murad"],
        "unidades_mes": 19000, "rating": 4.5, "reviews": 24000,
        "tendencia": "creciente", "rotacion": "media_alta",
        "descripcion": "Suero corrector manchas de la edad",
        "target": "Femenino", "tipo_piel": "Todos",
        "problema_ataca": "Manchas de la edad, hiperpigmentación"
    },
    {
        "id": "EN004", "categoria": "Envejecimiento", "subcategoria": "Colágeno",
        "nombre": "Vital Proteins Collagen Peptides",
        "marca": "Vital Proteins", "origen": "USA",
        "precio_usd": 43.00, "precio_promedio_mercado": 48.00,
        "plataformas": ["Amazon", "Target", "Whole Foods"],
        "unidades_mes": 165000, "rating": 4.5, "reviews": 210000,
        "tendencia": "muy_creciente", "rotacion": "muy_alta",
        "descripcion": "Colágeno hidrolizado bovino en polvo",
        "target": "Femenino", "tipo_piel": "N/A",
        "problema_ataca": "Arrugas, cabello, uñas, articulaciones"
    },

    # ════════════════════════════════════════
    # CATEGORÍA 10: MAQUILLAJE MUJER (NO TRADICIONAL)
    # ════════════════════════════════════════
    {
        "id": "MQ001", "categoria": "Maquillaje", "subcategoria": "Base",
        "nombre": "Fenty Beauty Pro Filt'r Soft Matte Foundation",
        "marca": "Fenty Beauty", "origen": "USA",
        "precio_usd": 40.00, "precio_promedio_mercado": 42.00,
        "plataformas": ["Sephora", "Harvey Nichols", "Fentybeauty.com"],
        "unidades_mes": 92000, "rating": 4.6, "reviews": 138000,
        "tendencia": "muy_creciente", "rotacion": "muy_alta",
        "descripcion": "Base de maquillaje 50 tonos inclusivos",
        "target": "Femenino", "tipo_piel": "Grasa",
        "problema_ataca": "Tono desigual, manchas, imperfecciones"
    },
    {
        "id": "MQ002", "categoria": "Maquillaje", "subcategoria": "Labios",
        "nombre": "Charlotte Tilbury Pillow Talk Lip Liner",
        "marca": "Charlotte Tilbury", "origen": "UK",
        "precio_usd": 28.00, "precio_promedio_mercado": 30.00,
        "plataformas": ["Sephora", "Nordstrom", "CT website"],
        "unidades_mes": 68000, "rating": 4.7, "reviews": 89000,
        "tendencia": "muy_creciente", "rotacion": "muy_alta",
        "descripcion": "Delineador labial más vendido del mundo tono nude",
        "target": "Femenino", "tipo_piel": "N/A",
        "problema_ataca": "Labios finos, falta de definición"
    },
    {
        "id": "MQ003", "categoria": "Maquillaje", "subcategoria": "Ojos",
        "nombre": "Benefit Gimme Brow+ Volumizing Eyebrow Gel",
        "marca": "Benefit", "origen": "USA",
        "precio_usd": 24.00, "precio_promedio_mercado": 26.00,
        "plataformas": ["Sephora", "Ulta", "Amazon"],
        "unidades_mes": 55000, "rating": 4.5, "reviews": 72000,
        "tendencia": "creciente", "rotacion": "alta",
        "descripcion": "Gel de cejas volumizador con microfilamentos",
        "target": "Femenino", "tipo_piel": "N/A",
        "problema_ataca": "Cejas escasas, finas, asimétricas"
    },
    {
        "id": "MQ004", "categoria": "Maquillaje", "subcategoria": "Contorno",
        "nombre": "NYX Professional Makeup Wonder Stick",
        "marca": "NYX", "origen": "USA",
        "precio_usd": 14.00, "precio_promedio_mercado": 15.00,
        "plataformas": ["Amazon", "Ulta", "Target"],
        "unidades_mes": 78000, "rating": 4.4, "reviews": 91000,
        "tendencia": "creciente", "rotacion": "muy_alta",
        "descripcion": "Stick de contorno e iluminador 2-en-1",
        "target": "Femenino", "tipo_piel": "N/A",
        "problema_ataca": "Falta de definición facial, nariz"
    },
    {
        "id": "MQ005", "categoria": "Maquillaje", "subcategoria": "Rímel",
        "nombre": "L'Oreal Paris Voluminous Original Mascara",
        "marca": "L'Oreal", "origen": "Francia",
        "precio_usd": 10.99, "precio_promedio_mercado": 13.00,
        "plataformas": ["Amazon", "Walmart", "CVS"],
        "unidades_mes": 198000, "rating": 4.5, "reviews": 245000,
        "tendencia": "estable", "rotacion": "muy_alta",
        "descripcion": "Máscara de pestañas voluminizadora clásica",
        "target": "Femenino", "tipo_piel": "N/A",
        "problema_ataca": "Pestañas cortas, ralas"
    },

    # ════════════════════════════════════════
    # CATEGORÍA 11: SKINCARE MUJER PREMIUM
    # ════════════════════════════════════════
    {
        "id": "SP001", "categoria": "Skincare Premium", "subcategoria": "Sérum Facial",
        "nombre": "Drunk Elephant C-Firma Fresh Day Serum",
        "marca": "Drunk Elephant", "origen": "USA",
        "precio_usd": 90.00, "precio_promedio_mercado": 95.00,
        "plataformas": ["Sephora", "Amazon", "Dermstore"],
        "unidades_mes": 38000, "rating": 4.6, "reviews": 52000,
        "tendencia": "muy_creciente", "rotacion": "alta",
        "descripcion": "Vitamina C 15% + vitamina E + ácido ferúlico",
        "target": "Femenino", "tipo_piel": "Todos",
        "problema_ataca": "Opacidad, manchas, envejecimiento"
    },
    {
        "id": "SP002", "categoria": "Skincare Premium", "subcategoria": "Mascarilla",
        "nombre": "GlamGlow Supermud Clearing Treatment",
        "marca": "GlamGlow", "origen": "USA",
        "precio_usd": 69.00, "precio_promedio_mercado": 72.00,
        "plataformas": ["Sephora", "Amazon", "Ulta"],
        "unidades_mes": 28000, "rating": 4.4, "reviews": 38000,
        "tendencia": "estable", "rotacion": "media_alta",
        "descripcion": "Mascarilla de barro activado para acné y poros",
        "target": "Mixto", "tipo_piel": "Grasa",
        "problema_ataca": "Acné, poros, impurezas profundas"
    },
    {
        "id": "SP003", "categoria": "Skincare Premium", "subcategoria": "Protector Solar",
        "nombre": "EltaMD UV Clear Broad-Spectrum SPF 46",
        "marca": "EltaMD", "origen": "USA",
        "precio_usd": 39.00, "precio_promedio_mercado": 42.00,
        "plataformas": ["Amazon", "Dermstore", "Ulta"],
        "unidades_mes": 88000, "rating": 4.7, "reviews": 112000,
        "tendencia": "muy_creciente", "rotacion": "muy_alta",
        "descripcion": "Protector solar con niacinamida para acné",
        "target": "Mixto", "tipo_piel": "Sensible/Grasa",
        "problema_ataca": "Daño solar, manchas, envejecimiento"
    },
    {
        "id": "SP004", "categoria": "Skincare Premium", "subcategoria": "Tónico",
        "nombre": "Some By Mi AHA BHA PHA Toner",
        "marca": "Some By Mi", "origen": "Korea",
        "precio_usd": 22.00, "precio_promedio_mercado": 25.00,
        "plataformas": ["Amazon", "YesStyle", "Ulta"],
        "unidades_mes": 62000, "rating": 4.5, "reviews": 78000,
        "tendencia": "muy_creciente", "rotacion": "alta",
        "descripcion": "Tónico K-Beauty triple ácido exfoliante",
        "target": "Femenino", "tipo_piel": "Grasa/Mixta",
        "problema_ataca": "Poros, textura, manchas, acné"
    },

    # ════════════════════════════════════════
    # CATEGORÍA 12: FRAGANCIAS Y CUIDADO MASCULINO
    # ════════════════════════════════════════
    {
        "id": "FM001", "categoria": "Cuidado Masculino", "subcategoria": "Barba",
        "nombre": "Beardbrand Gold Beard Oil",
        "marca": "Beardbrand", "origen": "USA",
        "precio_usd": 25.00, "precio_promedio_mercado": 28.00,
        "plataformas": ["beardbrand.com", "Amazon"],
        "unidades_mes": 32000, "rating": 4.6, "reviews": 28000,
        "tendencia": "creciente", "rotacion": "alta",
        "descripcion": "Aceite de barba premium con mezcla de aceites naturales",
        "target": "Masculino", "tipo_piel": "N/A",
        "problema_ataca": "Barba áspera, piel bajo barba irritada"
    },
    {
        "id": "FM002", "categoria": "Cuidado Masculino", "subcategoria": "Piel",
        "nombre": "Jack Black Pure Clean Daily Facial Cleanser",
        "marca": "Jack Black", "origen": "USA",
        "precio_usd": 24.00, "precio_promedio_mercado": 26.00,
        "plataformas": ["Amazon", "Sephora", "Nordstrom"],
        "unidades_mes": 38000, "rating": 4.5, "reviews": 42000,
        "tendencia": "creciente", "rotacion": "alta",
        "descripcion": "Limpiador facial masculino con extractos botánicos",
        "target": "Masculino", "tipo_piel": "Todos",
        "problema_ataca": "Piel grasa, poros, acné masculino"
    },

    # ════════════════════════════════════════
    # CATEGORÍA 13: BIENESTAR INTERNO
    # ════════════════════════════════════════
    {
        "id": "BI001", "categoria": "Bienestar", "subcategoria": "Suplementos Piel",
        "nombre": "HUM Nutrition Daily Cleanse Supplement",
        "marca": "HUM Nutrition", "origen": "USA",
        "precio_usd": 40.00, "precio_promedio_mercado": 44.00,
        "plataformas": ["Sephora", "Amazon", "hum.com"],
        "unidades_mes": 22000, "rating": 4.2, "reviews": 15000,
        "tendencia": "muy_creciente", "rotacion": "media_alta",
        "descripcion": "Suplemento de belleza interior para piel clara",
        "target": "Femenino", "tipo_piel": "N/A",
        "problema_ataca": "Acné interno, toxinas, piel opaca"
    },
    {
        "id": "BI002", "categoria": "Bienestar", "subcategoria": "Pérdida Peso",
        "nombre": "Leanbean Fat Burner for Women",
        "marca": "Leanbean", "origen": "UK",
        "precio_usd": 59.99, "precio_promedio_mercado": 65.00,
        "plataformas": ["leanbean.com", "Amazon"],
        "unidades_mes": 28000, "rating": 4.1, "reviews": 19000,
        "tendencia": "creciente", "rotacion": "media_alta",
        "descripcion": "Quemador de grasa femenino con ingredientes naturales",
        "target": "Femenino", "tipo_piel": "N/A",
        "problema_ataca": "Exceso de peso, metabolismo lento"
    },
]


# ─────────────────────────────────────────────
# GENERADOR DE HISTORIAL MENSUAL
# ─────────────────────────────────────────────

def generate_price_history(base_price, months=12):
    """Genera historial de precios con variaciones realistas"""
    history = []
    price = base_price
    for i in range(months):
        date = datetime.now() - timedelta(days=30 * (months - i - 1))
        variation = np.random.normal(0, 0.03)  # 3% SD
        price = max(price * (1 + variation), base_price * 0.7)
        history.append({
            "mes": date.strftime("%Y-%m"),
            "precio": round(price, 2)
        })
    return history


def generate_rotation_history(base_units, tendencia, months=12):
    """Genera historial de rotación mensual"""
    trends = {
        "muy_creciente": 0.08,
        "creciente": 0.04,
        "estable": 0.01,
        "decreciente": -0.03
    }
    trend_factor = trends.get(tendencia, 0.01)
    history = []
    units = base_units
    for i in range(months):
        date = datetime.now() - timedelta(days=30 * (months - i - 1))
        seasonal = 1 + 0.1 * np.sin(i * np.pi / 6)  # Estacionalidad
        noise = np.random.normal(1, 0.05)
        units = units * (1 + trend_factor) * seasonal * noise
        history.append({
            "mes": date.strftime("%Y-%m"),
            "unidades": int(units)
        })
    return history


def get_dataframe():
    """Retorna DataFrame completo con todos los productos"""
    df = pd.DataFrame(PRODUCTS)
    df["margen_oportunidad"] = ((df["precio_promedio_mercado"] - df["precio_usd"]) / df["precio_promedio_mercado"] * 100).round(1)
    df["volumen_mensual_usd"] = (df["precio_usd"] * df["unidades_mes"]).round(0)
    df["score_oportunidad"] = (
        df["rating"] * 10 +
        df["margen_oportunidad"] +
        df["unidades_mes"] / 10000
    ).round(1)
    return df


def get_top10_by_category(categoria=None, metric="unidades_mes"):
    """Retorna top 10 productos por categoría y métrica"""
    df = get_dataframe()
    if categoria and categoria != "Todas":
        df = df[df["categoria"] == categoria]
    return df.nlargest(10, metric)


def get_categories():
    """Lista de categorías únicas"""
    df = get_dataframe()
    return ["Todas"] + sorted(df["categoria"].unique().tolist())
