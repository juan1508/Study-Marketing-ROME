# 🔵 Estudio de Mercado ROME

> Plataforma de Inteligencia Comercial Global · Belleza & Cuidado Personal

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red?style=flat-square&logo=streamlit)
![Plotly](https://img.shields.io/badge/Plotly-5.18+-purple?style=flat-square&logo=plotly)
![Mercados](https://img.shields.io/badge/Mercados-USA·UK·FR·JP·KR-blue?style=flat-square)
![Actualización](https://img.shields.io/badge/Actualización-Mensual-green?style=flat-square)

---

## 🎯 ¿Qué es?

**Estudio de Mercado ROME** es una aplicación de análisis competitivo de mercado para el sector de belleza y cuidado personal a nivel internacional.

Diseñada para identificar oportunidades en mercados fuera de Colombia, con productos **no tradicionales, competitivos y de alta rotación** que se venden en plataformas como Amazon, Sephora, Ulta, ASOS y más.

---

## 🔬 Categorías Cubiertas

| Categoría | Productos | Problema Atacado |
|-----------|-----------|-----------------|
| 🧴 Piel | 10 | Acné, poros, manchas, estrías, celulitis |
| 💇 Cabello | 6 | Caída, calvicie, caspa, volumen, canas |
| 🏋️ Cuerpo | 4 | Grasa localizada, flacidez, masa muscular |
| 😁 Sonrisa | 3 | Blanqueamiento, mal aliento, labios |
| 👁️ Mirada | 3 | Bolsas, cejas escasas, pestañas |
| 🦵 Vello | 2 | Depilación, vello encarnado |
| 💦 Sudoración | 2 | Hiperhidrosis, mal olor |
| 💅 Manos & Pies | 4 | Hongos, uñas frágiles, callos |
| ⏳ Envejecimiento | 4 | Arrugas, firmeza, manchas edad |
| 💄 Maquillaje | 5 | Base, labios, cejas, contorno |
| ✨ Skincare Premium | 4 | Vitamina C, protección solar, K-Beauty |
| 🧔 Cuidado Masculino | 2 | Barba, piel masculina |
| 💊 Bienestar | 2 | Suplementos piel, control peso |

**Total: 51 productos indexados** con historial de 12 meses

---

## 📊 Funcionalidades

### 🏆 Top 10 por Categoría
- Ranking dinámico filtrable por categoría, target, precio y tendencia
- Fichas detalladas de cada producto con métricas clave
- Información de plataformas de venta internacionales

### 📈 Análisis de Tendencias
- Distribución de tendencias del mercado (muy creciente → decreciente)
- Simulación interactiva precio–rotación mensual (12 meses)
- Correlación precio vs volumen con insight automático
- **Alerta automática**: si el precio baja pero la rotación no sube

### 💰 Precios & Rotación
- Scatter plot: precio vs rating por volumen
- Análisis de volumen por rango de precio
- Heatmap de rotación por categoría y tendencia

### 🔍 Explorador de Productos
- Búsqueda libre por nombre, marca, problema o categoría
- Exportación a CSV con todos los datos
- Vista tabular optimizada

### 📊 Análisis Comparativo
- Treemap de oportunidades por volumen USD
- Comparativa precio propio vs precio de mercado (top 10 márgenes)
- Radar de competitividad por las 6 principales categorías

---

## 🚀 Instalación y Uso

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/estudio-mercado-rome.git
cd estudio-mercado-rome
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación
```bash
streamlit run app.py
```

La app abrirá automáticamente en `http://localhost:8501`

---

## 🌐 Deploy en Streamlit Cloud

1. Fork este repositorio en GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu cuenta de GitHub
4. Selecciona el repositorio y el archivo `app.py`
5. ¡Deploy en 1 clic!

---

## 📅 Sistema de Actualización Mensual

La app incluye un indicador de última actualización y cuenta regresiva para la próxima.

Para actualizar los datos mensualmente:
1. Edita `data/products_db.py`
2. Actualiza precios en el campo `precio_usd`
3. Ajusta `unidades_mes` según datos de mercado
4. Commit y push → Streamlit Cloud se actualiza automáticamente

---

## 📁 Estructura del Proyecto

```
estudio-mercado-rome/
├── app.py                    # App principal Streamlit
├── requirements.txt          # Dependencias Python
├── README.md                 # Documentación
├── data/
│   └── products_db.py        # Base de datos de productos
└── assets/                   # Recursos gráficos (opcional)
```

---

## 🎨 Diseño

- **Paleta**: Azules profundos (`#0A1628` → `#54A0FF`)
- **Tipografía**: Syne (títulos) + DM Sans (cuerpo)
- **Gráficos**: Plotly con tema dark personalizado
- **UI**: Glassmorphism + gradientes azules

---

## 📊 Métricas del Dashboard

| KPI | Descripción |
|-----|-------------|
| Volumen mensual USD | Precio × unidades/mes por producto |
| Margen de oportunidad | (Precio mercado - precio propio) / mercado |
| Score de oportunidad | Rating×10 + margen + vol/10000 |
| Correlación precio-rotación | Pearson entre historial precio y unidades |

---

## 🌍 Plataformas Cubiertas

Amazon · Sephora · Ulta Beauty · ASOS · Dermstore · Target · Walmart · Costco · CVS · Walgreens · Nordstrom · YesStyle · GNC · Bodybuilding.com

---

## ⚠️ Aviso Legal

Los precios y volúmenes son estimaciones de mercado con fines de análisis competitivo e investigación de mercado. No constituyen datos financieros oficiales.

---

<div align="center">
  <strong>ESTUDIO DE MERCADO ROME</strong><br>
  Inteligencia Comercial Global · Belleza & Cuidado Personal<br>
  Actualización Mensual Automática
</div>
