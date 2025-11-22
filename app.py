import streamlit as st
import pandas as pd
from datetime import datetime
import calendar
import base64
import os

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Agenda Banda Departamental", page_icon="🎸", layout="centered")

# ¡¡¡ TU ENLACE CSV AQUÍ !!!
SHEET_ID = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSIK5nAcesnNerJZXhriHGeVXzZ9rcWnMl4pZkQlaJ6Y_F_BLUB14VtveXaqHff3wFPnkgvf1L7qx_o/pub?output=csv"

# --- FUNCIÓN MAGICA PARA EL FONDO (BASE64) ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(current_dir, png_file)
        bin_str = get_base64_of_bin_file(full_path) 
        
        page_bg_img = f'''
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.8)), url("data:image/jpg;base64,{bin_str}");
            background-size: cover;
            background-position: center center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        '''
        st.markdown(page_bg_img, unsafe_allow_html=True)
    except FileNotFoundError:
        st.markdown('<style>.stApp { background-color: #121212; }</style>', unsafe_allow_html=True)

# Ejecutamos fondo
set_png_as_page_bg("fondo.jpg")

# --- ESTILOS GENERALES (CSS MEJORADO PARA BOTONES) ---
st.markdown("""
<style>
    /* Estilos generales */
    .stApp, h1, h2, h3, p, div { color: #E0E0E0; }
    h1, h2, h3 { color: #FFFFFF !important; text-shadow: 2px 2px 4px #000000; }
    
    /* TARJETAS */
    .gig-card {
        background-color: rgba(20, 20, 20, 0.90); /* Un poco más oscuro para contraste */
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.8);
        border-left: 8px solid #555;
        backdrop-filter: blur(8px);
    }
    .status-confirmado { border-left-color: #00C853 !important; }
    .status-pendiente { border-left-color: #FFAB00 !important; }
    .status-cancelado { border-left-color: #D50000 !important; }
    
    .gig-venue { font-size: 1.5em; font-weight: bold; color: #FFFFFF; }
    
    /* CAJA DE FECHA */
    .date-box { 
        background-color: #2C2C2C; border-radius: 10px; text-align: center; 
        padding: 8px 12px; min-width: 80px; border: 1px solid #444;
    }
    .date-week { font-size: 0.85em; color: #B0B0B0; font-weight: bold; text-transform: uppercase; margin-bottom: -5px; }
    .date-day { font-size: 2.2em; font-weight: 900; color: #FFF; line-height: 1.1; }
    .date-month { color: #FFAB00; font-weight: bold; text-transform: uppercase; font-size: 0.8em; }
    
    .highlight-time { color: #4FC3F7; font-weight: bold; }

    /* CALENDARIO */
    .calendar-container { 
        background-color: rgba(30, 30, 30, 0.9);
        padding: 20px; border-radius: 15px; text-align: center; 
        backdrop-filter: blur(5px);
    }
    table.calendar-table { width: 100%; border-collapse: collapse; color: #FFF; font-family: sans-serif; }
    th { color: #FFAB00; padding: 10px; text-transform: uppercase; font-size: 0.8em; }
    td { padding: 15px; text-align: center; border: 1px solid #333; width: 14%; height: 60px; vertical-align: middle; }
    
    /* CÍRCULO ROJO */
    a.gig-link { text-decoration: none; display: inline-block; width: 100%; height: 100%; }
    .gig-day { 
        background-color: #D50000; color: white; font-weight: bold; border-radius: 50%; 
        display: inline-block; width: 35px; height: 35px; line-height: 35px; 
        transition: transform 0.2s; cursor: pointer;
    }
    .gig-day:hover { transform: scale(1.2); box-shadow: 0 0 15px rgba(255, 0, 0, 0.8); }
    .today-day { border: 2px solid #FFAB00; border-radius: 50%; display: inline-block; width: 35px; height: 35px; line-height: 31px; }
    .empty-day { background-color: transparent; }

    /* --- BOTONES DE ALTO CONTRASTE (NUEVO) --- */
    /* Apuntamos directamente a los enlaces generados por st.link_button */
    div[data-testid="stLinkButton"] > a {
        background-color: #FFAB00 !important; /* Fondo Naranja Intenso */
        color: #000000 !important; /* Texto Negro */
        border: none !important;
        font-weight: 800 !important; /* Letra gruesa */
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border-radius: 8px !important;
        transition: all 0.3s ease;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.4); /* Sombrita para que resalte */
    }
    
    div[data-testid="stLinkButton"] > a:hover {
        background-color: #FFD740 !important; /* Un poco más claro al pasar el mouse */
        color: #000 !important;
        transform: translateY(-2px); /* Se levanta un poquito */
        box-shadow: 0 6px 10px rgba(0,0,0,0.6);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: rgba(44, 44, 44, 0.9); border-radius: 5px; color: white; }
    .stTabs [aria-selected="true"] { background-color: #FFAB00 !important; color: black !important; font-weight: bold; }

</style>
""", unsafe_allow_html=True)

# --- FUNCIONES ---
def traducir_mes(fecha_obj):
    meses = {"Jan": "ENE", "Feb": "FEB", "Mar": "MAR", "Apr": "ABR", "May": "MAY", "Jun": "JUN",
             "Jul": "JUL", "Aug": "AGO", "Sep": "SEP", "Oct": "OCT", "Nov": "NOV", "Dec": "DIC"}
    return meses.get(fecha_obj.strftime('%b'), fecha_obj.strftime('%b'))

def traducir_dia_semana(fecha_obj):
    dias = {0: "LUN", 1: "MAR", 2: "MIÉ", 3: "JUE", 4: "VIE", 5: "SÁB", 6: "DOM"}
    return dias[fecha_obj.weekday()]

def nombre_mes_espanol(numero_mes):
    meses = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    return meses[numero_mes]

def crear_html_calendario(year, month, dias_conciertos):
    cal = calendar.Calendar()
    semanas = cal.monthdayscalendar(year, month)
    html = '<div class="calendar-container"><table class="calendar-table"><thead><tr><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th><th>D</th></tr></thead><tbody>'
    hoy = datetime.now()
    for semana in semanas:
        html += '<tr>'
        for dia in semana:
            if dia == 0: html += '<td class="empty-day"></td>'
            else:
                fecha_str = f"{year}-{month:02d}-{dia:02d}"
                if fecha_str in dias_conciertos:
                    html += f'<td><a class="gig-link" href="?fecha={fecha_str}" target="_self"><span class="gig-day">{dia}</span></a></td>'
                elif dia == hoy.day and month == hoy.month and year == hoy.year: 
                     html += f'<td><span class="today-day">{dia}</span></td>'
                else: html += f'<td>{dia}</td>'
        html += '</tr>'
    return html + '</tbody></table></div>'

def renderizar_tarjeta(row):
    estado = row.get('Estado', 'Pendiente')
    clase_estado, emoji = ("status-confirmado", "✅") if estado == "Confirmado" else \
                          ("status-cancelado", "❌") if estado == "Cancelado" else \
                          ("status-pendiente", "⚠️")
    dia_num, mes_nom, dia_sem = row['Fecha'].day, traducir_mes(row['Fecha']), traducir_dia_semana(row['Fecha'])
    
    st.markdown(f"""
    <div class="gig-card {clase_estado}">
        <div style="display: flex; align-items: center;">
            <div class="date-box" style="margin-right: 15px;">
                <div class="date-week">{dia_sem}</div>
                <div class="date-day">{dia_num}</div>
                <div class="date-month">{mes_nom}</div>
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
    
    link_mapa = row.get('Mapa') if pd.notna(row.get('Mapa')) and str(row.get('Mapa')).startswith('http') else None
    link_rep = row.get('Repertorio') if pd.notna(row.get('Repertorio')) and str(row.get('Repertorio')).startswith('http') else None

    # Botones
    if link_mapa or link_rep:
        if link_mapa and link_rep:
            c1, c2 = st.columns(2)
            with c1: st.link_button("🗺️ Ver Ubicación", link_mapa)
            with c2: st.link_button("📄 Ver Repertorio", link_rep)
        elif link_mapa: st.link_button("🗺️ Ver Ubicación", link_mapa)
        elif link_rep: st.link_button("📄 Ver Repertorio", link_rep)

@st.cache_data(ttl=60)
def load_data():
    try:
        data = pd.read_csv(SHEET_ID)
        data.columns = data.columns.str.strip()
        return data
    except: return pd.DataFrame()

# --- APP PRINCIPAL ---
st.title("🎸 Agenda Banda Departamental")

df = load_data()
query_params = st.query_params
filtro_fecha = query_params.get("fecha", None)

if not df.empty:
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors='coerce', dayfirst=True)
    df = df.dropna(subset=['Fecha']).sort_values(by="Fecha")
    fechas_conciertos = df["Fecha"].dt.strftime('%Y-%m-%d').unique().tolist()
    hoy = pd.Timestamp.now().normalize()

    if filtro_fecha:
        if st.button("⬅️ VOLVER A LA AGENDA COMPLETA", type="primary"):
            st.query_params.clear()
            st.rerun()
        st.divider()
        try:
            fecha_dt = pd.to_datetime(filtro_fecha)
            df_filtrado = df[df["Fecha"] == fecha_dt]
            if not df_filtrado.empty:
                st.write(f"📅 Detalle del día: {fecha_dt.strftime('%d/%m/%Y')}")
                for index, row in df_filtrado.iterrows():
                    renderizar_tarjeta(row)
            else:
                st.warning("No se encontraron datos para esta fecha.")
        except: st.error("Error leyendo la fecha.")

    else:
        col_switch, col_btn = st.columns([3,1])
        with col_switch: mostrar_historial = st.toggle("Mostrar pasados", value=False)
        with col_btn: 
            if st.button("🔄"): st.cache_data.clear()

        df_visible = df if mostrar_historial else df[df["Fecha"] >= hoy]
        st.caption(f"Eventos visibles: {len(df_visible)}")

        tab_lista, tab_cal = st.tabs(["📋 Lista de Shows", "📅 Ver Calendario"])
        
        with tab_lista:
            if df_visible.empty: st.info("🎉 ¡No hay fechas pendientes!")
            else:
                for index, row in df_visible.iterrows(): renderizar_tarjeta(row)

        with tab_cal:
            st.write("Selecciona un día rojo para ver detalles.")
            col_year, col_month = st.columns(2)
            with col_year: year_sel = st.number_input("Año", value=datetime.now().year, step=1)
            with col_month:
                mes_actual = datetime.now().month
                month_sel = st.selectbox("Mes", range(1, 13), index=mes_actual-1, format_func=lambda x: nombre_mes_espanol(x))
            
            st.markdown(f"<h3 style='text-align: center; color: #FFAB00; text-shadow: 2px 2px 4px #000;'>{nombre_mes_espanol(month_sel)} {year_sel}</h3>", unsafe_allow_html=True)
            st.markdown(crear_html_calendario(year_sel, month_sel, fechas_conciertos), unsafe_allow_html=True)
            st.caption("🔴 Rojo: Concierto (Click para ver) | 🟡 Círculo: Hoy")

else:
    st.error("No hay datos. Verifica el enlace CSV.")