import streamlit as st
import plotly.graph_objects as go

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Whoop Clone - Health & Strain",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. MOTOR DE ESTILOS 3D, SOMBRAS Y ANIMACIONES (CSS Avanzado)
st.markdown("""
<style>
    /* Fondo OLED Ultra Oscuro */
    .stApp {
        background-color: #060709;
        color: #f3f4f6;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Contenedor tipo móvil */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 480px;
    }

    /* Animaciones */
    @keyframes pulseGlow {
        0% { transform: scale(1); box-shadow: 0 0 25px rgba(50, 215, 75, 0.2); }
        50% { transform: scale(1.02); box-shadow: 0 0 45px rgba(50, 215, 75, 0.45); }
        100% { transform: scale(1); box-shadow: 0 0 25px rgba(50, 215, 75, 0.2); }
    }

    @keyframes floatOrb {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-6px) rotate(180deg); }
    }

    /* Tarjetas con profundidad 3D y bordes biselados */
    .card-3d {
        background: linear-gradient(145deg, #16181d, #0d0e12);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 20px;
        padding: 16px;
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.7), inset 0 1px 1px rgba(255, 255, 255, 0.1);
        margin-bottom: 14px;
        transition: transform 0.2s ease;
    }

    /* Orbe 3D Healthspan animado */
    .bio-orb-container {
        background: radial-gradient(circle at center, #072517 0%, #0d1210 65%, #07090a 100%);
        border: 1px solid rgba(50, 215, 75, 0.3);
        border-radius: 24px;
        padding: 24px 16px;
        text-align: center;
        margin-bottom: 18px;
        animation: pulseGlow 4s infinite ease-in-out;
        position: relative;
        overflow: hidden;
    }

    .bio-orb-sphere {
        width: 140px;
        height: 140px;
        margin: 0 auto 12px auto;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, #34d399, #059669, #022c22);
        box-shadow: 0 0 40px rgba(52, 211, 153, 0.5), inset -10px -10px 20px rgba(0,0,0,0.8), inset 10px 10px 15px rgba(255,255,255,0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
    }

    .bio-orb-val {
        font-size: 38px;
        font-weight: 800;
        color: #ffffff;
        text-shadow: 0 2px 8px rgba(0,0,0,0.6);
        line-height: 1;
    }

    .bio-orb-sub {
        font-size: 10px;
        letter-spacing: 1.5px;
        font-weight: 700;
        color: rgba(255,255,255,0.8);
        margin-top: 4px;
    }

    /* Mini métricas duales (Pasos / Calorías) */
    .metric-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        margin-bottom: 14px;
    }

    .mini-metric-card {
        background: linear-gradient(145deg, #13151a, #0b0c0f);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 14px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.5);
    }

    .mini-title {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1px;
        color: #8e95a5;
        text-transform: uppercase;
    }

    .mini-val {
        font-size: 24px;
        font-weight: 800;
        color: #ffffff;
        margin-top: 4px;
    }

    /* Estado vacío para actividades */
    .empty-state {
        border: 1px dashed rgba(255, 255, 255, 0.15);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        color: #636b7a;
        font-size: 13px;
    }

    .activity-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #111317;
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 8px;
        border-left: 4px solid #3b82f6;
    }
</style>
""", unsafe_allow_html=True)

# 3. REPOSITORIO DE DATOS (EN CEROS POR DEFECTO HASTA CONECTAR LA API)
def fetch_wearable_data():
    """
    Retorna el estado inicial en ceros absolutos.
    Una vez conectada la API de Google Fit / SQLite, sustituye estas variables
    con la lectura directa de tu Mi Band.
    """
    return {
        "is_connected": False, # Bandera de estado
        "sleep_score": 0,      # Rango 0 - 100
        "recovery_score": 0,   # Rango 0 - 100%
        "strain_score": 0.0,   # Rango 0.0 - 21.0
        "bio_age": 0.0,        # 0.0 indica pendiente de cálculo
        "steps": 0,            # Pasos del día
        "calories": 0,         # Calorías quemadas activas + basales
        "rhr": 0,              # Resting Heart Rate
        "activities": []       # Lista vacía hasta registrar entrenamientos
    }

# 4. GENERADOR DE ANILLOS ESTILO WHOOP 3D
def render_metric_ring(value, max_val, color_hex, ring_title, suffix=""):
    # Si el valor es cero, se muestra un arco neutro tenue
    bar_color = color_hex if value > 0 else "rgba(255,255,255,0.08)"
    display_val = f"{value}{suffix}" if value > 0 else "--"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={
            'valueformat': ".1f" if isinstance(value, float) else "d",
            'font': {'size': 26, 'color': '#ffffff', 'family': 'sans-serif'},
            'suffix': suffix
        },
        gauge={
            'axis': {'range': [0, max_val], 'visible': False},
            'bar': {'color': bar_color, 'thickness': 0.18},
            'bgcolor': 'rgba(255, 255, 255, 0.03)',
            'borderwidth': 0,
        }
    ))

    fig.update_layout(
        height=130,
        margin=dict(l=5, r=5, t=10, b=5),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "#ffffff"}
    )
    return fig

# 5. ESTRUCTURA PRINCIPAL
def main():
    data = fetch_wearable_data()

    # Barra superior con estado del hardware
    status_color = "#32d74b" if data["is_connected"] else "#ff453a"
    status_text = "SYNCED" if data["is_connected"] else "OFFLINE • ESPERANDO DATOS"
    
    st.markdown(f"""
        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;'>
            <div style='font-size: 11px; letter-spacing: 2px; color: #8e95a5; font-weight: 800;'>DISPOSITIVO</div>
            <div style='display: flex; align-items: center; gap: 6px;'>
                <div style='width: 8px; height: 8px; border-radius: 50%; background: {status_color}; box-shadow: 0 0 8px {status_color};'></div>
                <span style='font-size: 10px; font-weight: 700; color: #8e95a5; letter-spacing: 1px;'>{status_text}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 3 ANILLOS PRINCIPALES (SUEÑO, RECUPERACIÓN, ESFUERZO)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.plotly_chart(render_metric_ring(data["sleep_score"], 100, "#60a5fa", "SLEEP", "%"), use_container_width=True)
        st.markdown("<div style='text-align: center; font-size: 11px; font-weight: 700; color: #60a5fa; letter-spacing: 1px; margin-top: -15px;'>SUEÑO</div>", unsafe_allow_html=True)

    with col2:
        # Dinámica de color: Verde > 66%, Amarillo > 33%, Rojo <= 33%
        rec_color = "#34d399" if data["recovery_score"] >= 66 else ("#fbbf24" if data["recovery_score"] >= 33 else "#f87171")
        st.plotly_chart(render_metric_ring(data["recovery_score"], 100, rec_color, "RECOVERY", "%"), use_container_width=True)
        st.markdown(f"<div style='text-align: center; font-size: 11px; font-weight: 700; color: {rec_color}; letter-spacing: 1px; margin-top: -15px;'>RECUPERACIÓN</div>", unsafe_allow_html=True)

    with col3:
        st.plotly_chart(render_metric_ring(data["strain_score"], 21, "#38bdf8", "STRAIN", ""), use_container_width=True)
        st.markdown("<div style='text-align: center; font-size: 11px; font-weight: 700; color: #38bdf8; letter-spacing: 1px; margin-top: -15px;'>ESFUERZO</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

    # ORBE 3D DE EDAD BIOLÓGICA (HEALTHSPAN)
    bio_age_str = f"{data['bio_age']:.1f}" if data["bio_age"] > 0 else "--"
    sub_text = "Esperando sincronización de VO2 Max y RHR" if data["bio_age"] == 0 else "Optimización Cardiovascular Activa"

    st.markdown(f"""
        <div class='bio-orb-container'>
            <div style='font-size: 11px; font-weight: 700; letter-spacing: 2px; color: #34d399; margin-bottom: 16px;'>HEALTHSPAN & BIOLOGICAL AGE</div>
            <div class='bio-orb-sphere'>
                <div class='bio-orb-val'>{bio_age_str}</div>
                <div class='bio-orb-sub'>AÑOS</div>
            </div>
            <div style='font-size: 12px; color: #a1a1aa; font-weight: 500; margin-top: 10px;'>{sub_text}</div>
        </div>
    """, unsafe_allow_html=True)

    # TARJETAS DUALES: PASOS Y CALORÍAS
    st.markdown(f"""
        <div class='metric-grid'>
            <div class='mini-metric-card'>
                <div class='mini-title'>👟 Pasos</div>
                <div class='mini-val'>{data['steps']:,}</div>
                <div style='height: 4px; background: rgba(255,255,255,0.06); border-radius: 2px; margin-top: 8px; overflow: hidden;'>
                    <div style='height: 100%; width: {min(100, (data["steps"]/10000)*100)}%; background: #3b82f6;'></div>
                </div>
            </div>
            <div class='mini-metric-card'>
                <div class='mini-title'>🔥 Calorías</div>
                <div class='mini-val'>{data['calories']:,} <span style='font-size: 14px; font-weight: 400; color: #71717a;'>kcal</span></div>
                <div style='height: 4px; background: rgba(255,255,255,0.06); border-radius: 2px; margin-top: 8px; overflow: hidden;'>
                    <div style='height: 100%; width: {min(100, (data["calories"]/2500)*100)}%; background: #f97316;'></div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ÚLTIMAS ACTIVIDADES FÍSICAS
    st.markdown("<div style='font-size: 14px; font-weight: 700; letter-spacing: 1px; margin-bottom: 12px;'>ACTIVIDADES REGISTRADAS</div>", unsafe_allow_html=True)

    if not data["activities"]:
        st.markdown("""
            <div class='empty-state'>
                <div style='font-size: 20px; margin-bottom: 4px;'>⏱️</div>
                No hay actividades recientes registradas hoy.<br>Tus sesiones aparecerán aquí al sincronizar.
            </div>
        """, unsafe_allow_html=True)
    else:
        for act in data["activities"]:
            st.markdown(f"""
                <div class='activity-row'>
                    <div>
                        <div style='font-weight: 700; font-size: 14px;'>{act['name']}</div>
                        <div style='font-size: 12px; color: #8e95a5;'>{act['duration']} min • FC Media: {act['avg_hr']} ppm</div>
                    </div>
                    <div style='background: rgba(59, 130, 246, 0.15); color: #60a5fa; font-weight: 700; padding: 4px 10px; border-radius: 8px; font-size: 12px;'>
                        +{act.get('strain', '--')}
                    </div>
                </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
