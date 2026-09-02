import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA (Optimizada para celular, tema oscuro)
st.set_page_config(page_title="My Health Dashboard", layout="centered", initial_sidebar_state="collapsed")

# CSS Personalizado para imitar la interfaz oscura y tarjetas redondeadas
st.markdown("""
    <style>
    .stApp { background-color: #0d0d0f; color: #ffffff; }
    .metric-card {
        background-color: #1c1c1e;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .activity-card {
        background-color: #1c1c1e;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .activity-title { font-size: 16px; font-weight: bold; }
    .activity-time { color: #8e8e93; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

# 2. CONEXIÓN A DATOS (Mi Band -> Google Fit API o SQLite Gadgetbridge)
def fetch_mi_band_data():
    # AQUÍ VA TU CONEXIÓN A LA API. 
    # Ejemplo: Usar google-api-python-client para leer 'com.google.heart_rate.bpm'
    # Por ahora, estructuramos un diccionario con el formato que entregarás:
    return {
        "rhr": 52, # Ritmo cardíaco en reposo
        "sleep_score": 85,
        "sleep_hours": 7.5,
        "age": 23,
        "vo2_max": 48.5,
        "activities": [
            {"name": "Fútbol (Dragones)", "type": "Cardio", "duration": 90, "avg_hr": 155},
            {"name": "Fuerza (Casa)", "type": "Pesas", "duration": 45, "avg_hr": 115}
        ]
    }

# 3. ALGORITMOS (Tu propio motor analítico)
def calculate_strain(activities):
    # Fórmula logarítmica simplificada (0-21) basada en tiempo y HR
    total_load = sum([act['duration'] * (act['avg_hr']/100) for act in activities])
    # Mapeo simple: 100 de carga = ~10 strain, 200 = ~15, 300 = ~18, 400 = 20
    strain = min(21.0, round((total_load ** 0.5) * 1.2, 1))
    return strain

def calculate_recovery(sleep_score, rhr):
    # Relación entre buen sueño y RHR bajo
    base_recovery = sleep_score
    rhr_penalty = max(0, (rhr - 50) * 1.5) # Penaliza si el RHR sube de 50
    return max(0, min(100, int(base_recovery - rhr_penalty)))

def calculate_bio_age(chronological_age, vo2_max, rhr):
    # Cálculo de edad biológica basado en fitness cardiovascular
    age_offset = (45 - vo2_max) * 0.2 + (rhr - 55) * 0.1
    return round(chronological_age + age_offset, 1)

# Generar gráfico circular (Anillos estilo Whoop)
def create_ring(value, max_value, color, title, suffix=""):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        number = {'suffix': suffix, 'font': {'size': 40, 'color': 'white'}},
        gauge = {
            'axis': {'range': [None, max_value], 'visible': False},
            'bar': {'color': color, 'thickness': 0.8},
            'bgcolor': "#2c2c2e",
            'borderwidth': 0
        }
    ))
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        height=180,
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "white"}
    )
    return fig

# 4. INTERFAZ DE USUARIO (Dashboard)
def main():
    st.markdown("<h3 style='text-align: center; color: white; margin-top: -30px;'>TODAY</h3>", unsafe_allow_html=True)
    
    # Cargar y procesar datos
    data = fetch_mi_band_data()
    strain = calculate_strain(data['activities'])
    recovery = calculate_recovery(data['sleep_score'], data['rhr'])
    bio_age = calculate_bio_age(data['age'], data['vo2_max'], data['rhr'])
    
    # Anillos principales (Layout en 3 columnas)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.plotly_chart(create_ring(data['sleep_score'], 100, "#4a90e2", ""), use_container_width=True)
        st.markdown("<div style='text-align:center; font-size:12px; font-weight:bold; letter-spacing:1px;'>SLEEP</div>", unsafe_allow_html=True)
        
    with col2:
        # Color verde si >66%, amarillo si >33%, rojo si <33%
        rec_color = "#32d74b" if recovery >= 66 else ("#ffd60a" if recovery >= 33 else "#ff453a")
        st.plotly_chart(create_ring(recovery, 100, rec_color, "", "%"), use_container_width=True)
        st.markdown("<div style='text-align:center; font-size:12px; font-weight:bold; letter-spacing:1px;'>RECOVERY</div>", unsafe_allow_html=True)
        
    with col3:
        st.plotly_chart(create_ring(strain, 21, "#0a84ff", ""), use_container_width=True)
        st.markdown("<div style='text-align:center; font-size:12px; font-weight:bold; letter-spacing:1px;'>STRAIN</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tarjeta de Edad Biológica (Healthspan)
    st.markdown("""
        <div class='metric-card' style='background: radial-gradient(circle, #002d18 0%, #1c1c1e 80%); border: 1px solid #32d74b;'>
            <h4 style='color: #8e8e93; margin-bottom: 5px; font-size: 14px;'>BIOLOGICAL AGE</h4>
            <h1 style='color: white; font-size: 48px; margin: 0;'>{0}</h1>
            <p style='color: #32d74b; font-size: 14px; font-weight: bold;'>{1} years younger</p>
        </div>
    """.format(bio_age, round(data['age'] - bio_age, 1)), unsafe_allow_html=True)
    
    st.markdown("### Today's Activities")
    
    # Listado de actividades dinámico
    for act in data['activities']:
        color_tag = "#ff9f0a" if act['type'] == "Cardio" else "#32d74b"
        st.markdown(f"""
            <div class='activity-card'>
                <div>
                    <div class='activity-title'>{act['name']}</div>
                    <div class='activity-time'>{act['duration']} min • Avg HR: {act['avg_hr']} bpm</div>
                </div>
                <div style='background-color: {color_tag}; padding: 5px 12px; border-radius: 8px; color: black; font-weight: bold;'>
                    ✓
                </div>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
