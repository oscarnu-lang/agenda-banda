import streamlit as st
import pandas as pd
from datetime import datetime
import calendar

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Agenda Banda", page_icon="🎸", layout="centered")

# ¡¡¡ TU ENLACE CSV AQUÍ !!!
SHEET_ID = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSIK5nAcesnNerJZXhriHGeVXzZ9rcWnMl4pZkQlaJ6Y_F_BLUB14VtveXaqHff3wFPnkgvf1L7qx_o/pub?output=csv"

# --- ESTILOS CSS ---
st.markdown("""
<style>
    .stApp { background-color: #121212; color: #E0E0E0; }
    
    /* Estilos Generales */
    h1, h2, h3 { color: #FFFFFF !important; }
    
    /* TARJETAS (LISTA) */
    .gig-card {
        background-color: #1E1E1E;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 25px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.5);
        border-left: 8px solid #555;
    }
    .status-confirmado { border-left-color: #00C853 !important; }
    .status-pendiente { border-left-color: #FFAB00 !important; }
    .status-cancelado { border-left-color: #D50000 !important; }
    
    .gig-venue { font-size: 1.5em; font-weight: bold; color: #FFFFFF; }
    .date-box { background-color: #2C2C2C; border-radius: 10px; text-align: center; padding: 8px; }
    .date-day { font-size: 2em; font-weight: 900; color: #FFF; line-height: 1; }
    .date-month { color: #FFAB00; font-weight: bold; text-transform: uppercase; font-size: 0.8em; }
    
    .highlight-time { color: #4FC3F7; font-weight: bold; }

    /* ESTILOS DEL CALENDARIO VISUAL */
    .calendar-container {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
    }
    table.calendar-table {
        width: 100%;
        border-collapse: collapse;
        color: #FFF;
        font-family: sans-serif;
    }
    th { color: #FFAB00; padding: 10px; text-transform: uppercase; font-size: 0.8em; }
    td { 
        padding: 15px; 
        text-align: center; 
        border: 1px solid #333; 
        width: 14%; /* 7 días = 14% c/u */
        height: 60px;
        vertical-align: middle;
    }
    
    /* EL DÍA DEL CONCIERTO (ROJO) */
    .gig-day {
        background-color: #D50000; /* Rojo fuerte */
        color: white;
        font-weight: bold;
        border-radius: 50%;
        box-shadow: 0 0 10px rgba(213, 0, 0, 0.6);
        display: inline-block;
        width: 35px;
        height: 35px;
        line-height: 35px; /* Centrar verticalmente */
    }
    
    .today-day {
        border: 2px solid #FFAB00;
        border-radius: 50%;
        display: inline-block;
        width: 35px;
        height: 35px;
        line-height: 31px;
    }
    
    .empty-day { background-color: transparent; }

    /* Estilo de Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #2C2C2C; border-radius: 5px; color: white;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFAB00 !important; color: black !important;
    }

</style>
""", unsafe_allow_html=True)

# --- FUNCIONES ---
def traducir_mes(fecha_obj):
    meses = {"Jan": "ENE", "Feb": "FEB", "Mar": "MAR", "Apr": "ABR", "May": "MAY", "Jun": "JUN",
             "Jul": "JUL", "Aug": "AGO", "Sep": "SEP", "Oct": "OCT", "Nov": "NOV", "Dec": "DIC"}
    return meses.get(fecha_obj.strftime('%b'), fecha_obj.strftime('%b'))

def nombre_mes_espanol(numero_mes):
    meses = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    return meses[numero_mes]

# Generador de HTML del Calendario
def crear_html_calendario(year, month, dias_conciertos):
    # --- AQUÍ ESTABA EL ERROR, CORREGIDO AHORA ---
    cal = calendar.Calendar() # Usamos la clase genérica Calendar
    # ---------------------------------------------
    semanas = cal.monthdayscalendar(year, month)
    
    html = '<div class="calendar-container">'
    html += '<table class="calendar-table">'
    html += '<thead><tr><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th><th>D</th></tr></thead>'
    html += '<tbody>'
    
    hoy = datetime.now()
    
    for semana in semanas:
        html += '<tr>'
        for dia in semana:
            if dia == 0:
                html += '<td class="empty-day"></td>'
            else:
                # Clase base
                contenido = str(dia)
                clase = ""
                
                # Chequear si es día de concierto
                fecha_actual_str = f"{year}-{month:02d}-{dia:02d}"
                if fecha_actual_str in dias_conciertos:
                    clase = "gig-day" # CLASE ROJA
                
                # Chequear si es HOY (para referencia)
                elif dia == hoy.day and month == hoy.month and year == hoy.year:
                     clase = "today-day"

                if clase:
                    html += f'<td><span class="{clase}">{dia}</span></td>'
                else:
                    html += f'<td>{dia}</td>'
        html += '</tr>'
    
    html += '</tbody></table></div>'
    return html

@st.cache_data(ttl=60)
def load_data():
    try:
        data = pd.read_csv(SHEET_ID)
        data.columns = data.columns.str.strip()
        return data
    except: return pd.DataFrame()

# --- APP PRINCIPAL ---
st.title("🎸 AGENDA OFICIAL")

df = load_data()
col_spacer, col_btn = st.columns([3,1])
with col_btn:
    if st.button("🔄 Actualizar"): st.cache_data.clear()

if not df.empty:
    # Convertir fechas asegurando formato latino (dayfirst=True)
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors='coerce', dayfirst=True)
    df = df.dropna(subset=['Fecha']).sort_values(by="Fecha")
    
    # Crear lista de fechas de conciertos (en formato texto YYYY-MM-DD)
    fechas_conciertos = df["Fecha"].dt.strftime('%Y-%m-%d').unique().tolist()

    # --- SISTEMA DE PESTAÑAS ---
    tab_lista, tab_cal = st.tabs(["📋 Lista de Shows", "📅 Ver Calendario"])
    
    # PESTAÑA 1: LA LISTA (Lo que ya teníamos)
    with tab_lista:
        for index, row in df.iterrows():
            estado = row.get('Estado', 'Pendiente')
            clase_estado = "status-pendiente"
            emoji = "⚠️"
            if estado == "Confirmado": clase_estado, emoji = "status-confirmado", "✅"
            elif estado == "Cancelado": clase_estado, emoji = "status-cancelado", "❌"
            
            dia, mes = row['Fecha'].day, traducir_mes(row['Fecha'])
            
            # HTML de la Tarjeta
            st.markdown(f"""
            <div class="gig-card {clase_estado}">
                <div style="display: flex; align-items: center;">
                    <div class="date-box" style="margin-right: 15px;">
                        <div class="date-day">{dia}</div>
                        <div class="date-month">{mes}</div>
                    </div>
                    <div style="flex-grow: 1;">
                        <div class="gig-venue">{row['Lugar']}</div>
                        <div style="color: #aaa; font-style: italic;">{row.get('Ciudad','')}</div>
                        <div style="margin-top: 5px; color: #fff;">⏰ {row['Hora']} hs | {emoji} {estado}</div>
                    </div>
                </div>
                {'<div style="margin-top:10px; border-top:1px solid #444; padding-top:5px; font-size:0.9em; color:#ccc;">' + 
                 (f'🚐 Salida: <span class="highlight-time">{row["Salida"]}</span> &nbsp; ' if pd.notna(row.get("Salida")) else "") +
                 (f'🎤 Prueba: <span class="highlight-time">{row["Prueba"]}</span>' if pd.notna(row.get("Prueba")) else "") +
                 '</div>' if (pd.notna(row.get("Salida")) or pd.notna(row.get("Prueba"))) else ""}
            </div>
            """, unsafe_allow_html=True)
            
            # Botón de mapa fuera del HTML puro para usar funcionalidad nativa
            if pd.notna(row.get('Mapa')) and str(row.get('Mapa')).startswith('http'):
                st.link_button("🗺️ Ver Ubicación", row['Mapa'])

    # PESTAÑA 2: EL CALENDARIO
    with tab_cal:
        st.write("Visualización mensual de fechas.")
        
        # Selectores de Año y Mes
        col_year, col_month = st.columns(2)
        with col_year:
            year_sel = st.number_input("Año", value=datetime.now().year, step=1)
        with col_month:
            mes_actual = datetime.now().month
            month_sel = st.selectbox("Mes", range(1, 13), index=mes_actual-1, format_func=lambda x: nombre_mes_espanol(x))

        # Generar HTML del Calendario
        html_cal = crear_html_calendario(year_sel, month_sel, fechas_conciertos)
        
        # Título del mes
        st.markdown(f"<h3 style='text-align: center; color: #FFAB00;'>{nombre_mes_espanol(month_sel)} {year_sel}</h3>", unsafe_allow_html=True)
        
        # Pintar el calendario
        st.markdown(html_cal, unsafe_allow_html=True)
        
        # Leyenda
        st.caption("🔴 Rojo: Día de Concierto | 🟡 Círculo: Hoy")

else:
    st.error("No hay datos. Verifica el enlace CSV o que las fechas tengan formato correcto (AAAA-MM-DD).")