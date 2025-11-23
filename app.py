import streamlit as st
import pandas as pd
from datetime import datetime
import calendar
import base64
import os
from PIL import Image # Importamos esto para manejar el logo como profesionales

# --- 1. BLINDAJE DE RUTAS Y CARGA DE LOGO ---
# Esto asegura que encuentre los archivos aunque Python esté mirando a otro lado
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
except:
    current_dir = os.getcwd()

# Definimos las rutas exactas
logo_path_png = os.path.join(current_dir, "logo.png")
logo_path_jpg = os.path.join(current_dir, "logo.jpg")
fondo_path = os.path.join(current_dir, "fondo.jpg")

# Lógica: Busca el logo y cárgalo en memoria
icono_app = "🎸" # Por defecto
try:
    if os.path.exists(logo_path_png):
        icono_app = Image.open(logo_path_png)
    elif os.path.exists(logo_path_jpg):
        icono_app = Image.open(logo_path_jpg)
except Exception as e:
    print(f"No se pudo cargar el logo: {e}")

# --- CONFIGURACIÓN DE PÁGINA (Debe ser la primera orden de Streamlit) ---
st.set_page_config(page_title="Agenda Banda Departamental", page_icon=icono_app, layout="centered")

# ¡¡¡ TU ENLACE CSV AQUÍ !!!
SHEET_ID = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSIK5nAcesnNerJZXhriHGeVXzZ9rcWnMl4pZkQlaJ6Y_F_BLUB14VtveXaqHff3wFPnkgvf1L7qx_o/pub?output=csv"

# --- 2. FUNCIONES ---

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f: data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(full_path_to_img):
    try:
        bin_str = get_base64_of_bin_file(full_path_to_img) 
        st.markdown(f'''
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.8)), url("data:image/jpg;base64,{bin_str}");
            background-size: cover; background-position: center; background-repeat: no-repeat; background-attachment: fixed;
        }}
        </style>''', unsafe_allow_html=True)
    except: st.markdown('<style>.stApp { background-color: #121212; }</style>', unsafe_allow_html=True)

@st.cache_data(ttl=60)
def load_data():
    try:
        d = pd.read_csv(SHEET_ID)
        d.columns = d.columns.str.strip()
        return d
    except: return pd.DataFrame()

def traducir_mes(f): return {"Jan":"ENE","Feb":"FEB","Mar":"MAR","Apr":"ABR","May":"MAY","Jun":"JUN","Jul":"JUL","Aug":"AGO","Sep":"SEP","Oct":"OCT","Nov":"NOV","Dec":"DIC"}.get(f.strftime('%b'), f.strftime('%b'))
def traducir_dia(f): return {0:"LUN",1:"MAR",2:"MIÉ",3:"JUE",4:"VIE",5:"SÁB",6:"DOM"}[f.weekday()]
def mes_esp(n): return ["","Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"][n]

def crear_calendario(y, m, dias):
    cal = calendar.Calendar()
    html = '<div class="calendar-container"><table class="calendar-table"><thead><tr><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th><th>D</th></tr></thead><tbody>'
    hoy = datetime.now()
    for sem in cal.monthdayscalendar(y, m):
        html += '<tr>'
        for d in sem:
            if d == 0: html += '<td class="empty-day"></td>'
            else:
                f_str = f"{y}-{m:02d}-{d:02d}"
                if f_str in dias:
                    clase = "gig-day"
                    html += f'<td><a class="gig-link" href="?fecha={f_str}" target="_self"><span class="{clase}">{d}</span></a></td>'
                elif (d==hoy.day and m==hoy.month and y==hoy.year):
                    clase = "today-day"
                    html += f'<td><span class="{clase}">{d}</span></td>'
                else:
                    html += f'<td>{d}</td>'
        html += '</tr>'
    return html + '</tbody></table></div>'

def render_card(row):
    est = row.get('Estado', 'Pendiente')
    col_est, emo = ("status-confirmado", "✅") if est == "Confirmado" else ("status-cancelado", "❌") if est == "Cancelado" else ("status-pendiente", "⚠️")
    
    st.markdown(f"""
    <div class="gig-card {col_est}">
        <div style="display: flex; align-items: center;">
            <div class="date-box" style="margin-right: 15px;">
                <div class="date-week">{traducir_dia(row['Fecha'])}</div>
                <div class="date-day">{row['Fecha'].day}</div>
                <div class="date-month">{traducir_mes(row['Fecha'])}</div>
            </div>
            <div style="flex-grow: 1;">
                <div class="gig-venue">{row['Lugar']}</div>
                <div style="color: #aaa; font-style: italic;">{row.get('Ciudad','')}</div>
                <div style="margin-top: 5px; color: #fff;">⏰ {row['Hora']} hs | {emo} {est}</div>
            </div>
        </div>
        {'<div style="margin-top:10px; border-top:1px solid #444; padding-top:5px; font-size:0.9em; color:#ccc;">' + (f'🚐 Salida: <span class="highlight-time">{row["Salida"]}</span> &nbsp; ' if pd.notna(row.get("Salida")) else "") + (f'🎤 Prueba: <span class="highlight-time">{row["Prueba"]}</span>' if pd.notna(row.get("Prueba")) else "") + '</div>' if (pd.notna(row.get("Salida")) or pd.notna(row.get("Prueba"))) else ""}
    </div>""", unsafe_allow_html=True)
    
    # Botones
    lk_map = row.get('Mapa')
    if pd.isna(lk_map) or not str(lk_map).startswith('http'): lk_map = None

    lk_rep = row.get('Repertorio')
    if pd.isna(lk_rep) or not str(lk_rep).startswith('http'): lk_rep = None

    if lk_map and lk_rep:
        c1, c2 = st.columns(2)
        with c1: st.link_button("🗺️ Ver Ubicación", lk_map)
        with c2: st.link_button("📄 Ver Repertorio", lk_rep)
    elif lk_map: st.link_button("🗺️ Ver Ubicación", lk_map)
    elif lk_rep: st.link_button("📄 Ver Repertorio", lk_rep)


# --- 3. ESTILOS Y EJECUCIÓN ---

# Aplicar Fondo (Usando la ruta segura)
set_png_as_page_bg(fondo_path)

# Aplicar CSS
st.markdown("""
<style>
    .stApp, h1, h2, h3, p, div { color: #E0E0E0; }
    h1, h2, h3 { color: #FFFFFF !important; text-shadow: 2px 2px 4px #000; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .gig-card {
        background-color: rgba(20, 20, 20, 0.90); border-radius: 15px; padding: 20px;
        margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.8);
        border-left: 8px solid #555; backdrop-filter: blur(8px);
    }
    .status-confirmado { border-left-color: #00C853 !important; }
    .status-pendiente { border-left-color: #FFAB00 !important; }
    .status-cancelado { border-left-color: #D50000 !important; }
    
    .gig-venue { font-size: 1.5em; font-weight: bold; color: #FFFFFF; }
    
    .date-box { background-color: #2C2C2C; border-radius: 10px; text-align: center; padding: 8px 12px; min-width: 80px; border: 1px solid #444; }
    .date-week { font-size: 0.85em; color: #B0B0B0; font-weight: bold; text-transform: uppercase; margin-bottom: -5px; }
    .date-day { font-size: 2.2em; font-weight: 900; color: #FFF; line-height: 1.1; }
    .date-month { color: #FFAB00; font-weight: bold; text-transform: uppercase; font-size: 0.8em; }
    .highlight-time { color: #4FC3F7; font-weight: bold; }

    .calendar-container { background-color: rgba(30, 30, 30, 0.9); padding: 20px; border-radius: 15px; text-align: center; backdrop-filter: blur(5px); }
    table.calendar-table { width: 100%; border-collapse: collapse; color: #FFF; font-family: sans-serif; }
    th { color: #FFAB00; padding: 10px; text-transform: uppercase; font-size: 0.8em; }
    td { padding: 15px; text-align: center; border: 1px solid #333; width: 14%; height: 60px; vertical-align: middle; }
    
    a.gig-link { text-decoration: none; display: inline-block; width: 100%; height: 100%; }
    .gig-day { background-color: #D50000; color: white; font-weight: bold; border-radius: 50%; display: inline-block; width: 35px; height: 35px; line-height: 35px; transition: transform 0.2s; cursor: pointer; }
    .gig-day:hover { transform: scale(1.2); box-shadow: 0 0 15px rgba(255, 0, 0, 0.8); }
    .today-day { border: 2px solid #FFAB00; border-radius: 50%; display: inline-block; width: 35px; height: 35px; line-height: 31px; }
    .empty-day { background-color: transparent; }

    div[data-testid="stLinkButton"] > a {
        background-color: #FFAB00 !important; color: #000000 !important; border: none !important;
        font-weight: 800 !important; text-transform: uppercase; letter-spacing: 0.5px;
        border-radius: 8px !important; transition: all 0.3s ease; text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.4);
    }
    div[data-testid="stLinkButton"] > a:hover {
        background-color: #FFD740 !important; color: #000 !important; transform: translateY(-2px); box-shadow: 0 6px 10px rgba(0,0,0,0.6);
    }

    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: rgba(44, 44, 44, 0.9); border-radius: 5px; color: white; }
    .stTabs [aria-selected="true"] { background-color: #FFAB00 !important; color: black !important; font-weight: bold; }

</style>
""", unsafe_allow_html=True)

# --- APP ---
st.title("🎸 Agenda Banda Departamental")

df = load_data()
fecha_url = st.query_params.get("fecha", None)

if not df.empty:
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors='coerce', dayfirst=True)
    df = df.dropna(subset=['Fecha']).sort_values(by="Fecha")
    dias_shows = df["Fecha"].dt.strftime('%Y-%m-%d').unique().tolist()
    hoy = pd.Timestamp.now().normalize()

    if fecha_url:
        if st.button("⬅️ VOLVER A LA AGENDA", type="primary"): 
            st.query_params.clear()
            st.rerun()
        st.divider()
        try:
            f_dt = pd.to_datetime(fecha_url)
            sub = df[df["Fecha"] == f_dt]
            if not sub.empty:
                st.write(f"📅 Detalle del día: {f_dt.strftime('%d/%m/%Y')}")
                for i, r in sub.iterrows(): render_card(r)
            else: st.warning("Sin datos para esta fecha.")
        except: st.error("Error en la fecha seleccionada.")
    else:
        c_sw, c_bt = st.columns([3,1])
        with c_sw: hist = st.toggle("Ver historial", value=False)
        with c_bt: 
            if st.button("🔄"): st.cache_data.clear()
        
        vis = df if hist else df[df["Fecha"] >= hoy]
        st.caption(f"Eventos visibles: {len(vis)}")
        
        t1, t2 = st.tabs(["📋 Lista de Shows", "📅 Ver Calendario"])
        
        with t1:
            if vis.empty: st.info("🎉 ¡No hay fechas pendientes!")
            else: 
                for i, r in vis.iterrows(): render_card(r)
        with t2:
            st.write("Selecciona un día rojo para ver detalles.")
            cy, cm = st.columns(2)
            with cy: ys = st.number_input("Año", value=datetime.now().year, step=1)
            with cm: ms = st.selectbox("Mes", range(1, 13), index=datetime.now().month-1, format_func=mes_esp)
            st.markdown(f"<h3 style='text-align: center; color: #FFAB00; text-shadow: 2px 2px 4px #000;'>{mes_esp(ms)} {ys}</h3>", unsafe_allow_html=True)
            st.markdown(crear_calendario(ys, ms, dias_shows), unsafe_allow_html=True)
            st.caption("🔴 Rojo: Concierto | 🟡 Círculo: Hoy")

else: st.error("No hay datos. Verifica el enlace CSV.")