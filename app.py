import streamlit as st
import pandas as pd
from datetime import datetime
import calendar
import base64
import os

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Agenda Banda Lavalleja", page_icon="🎸", layout="centered")

# ¡¡¡ TU ENLACE CSV AQUÍ !!!
SHEET_ID = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSIK5nAcesnNerJZXhriHGeVXzZ9rcWnMl4pZkQlaJ6Y_F_BLUB14VtveXaqHff3wFPnkgvf1L7qx_o/pub?output=csv"

# --- 2. FUNCIONES DE SISTEMA ---

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f: data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_filename):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
    except:
        current_dir = os.getcwd()
    
    for nombre in [png_filename, "Fondo.jpg", "fondo.png", "Fondo.png"]:
        path = os.path.join(current_dir, nombre)
        if os.path.exists(path):
            try:
                bin_str = get_base64_of_bin_file(path) 
                st.markdown(f'''
                <style>
                .stApp {{
                    background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.95)), url("data:image/jpg;base64,{bin_str}");
                    background-size: cover; background-position: center; background-repeat: no-repeat; background-attachment: fixed;
                }}
                </style>''', unsafe_allow_html=True)
                return
            except: pass

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

def generar_html_para_imprimir(dataframe):
    html = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; padding: 40px; color: black; background-color: white; }
            h1 { text-align: center; color: #333; border-bottom: 2px solid #FF8C00; padding-bottom: 10px; }
            .fecha-impresion { text-align: center; font-size: 0.9em; color: #666; margin-bottom: 30px; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th { background-color: #f2f2f2; color: #333; padding: 12px; text-align: left; border-bottom: 2px solid #ddd; }
            td { padding: 12px; border-bottom: 1px solid #eee; color: #000; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            .status-ok { color: green; font-weight: bold; }
            .status-warn { color: orange; font-weight: bold; }
            .status-bad { color: red; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>🎸 Banda Departamental de Lavalleja</h1>
        <div class="fecha-impresion">Reporte generado: """ + datetime.now().strftime("%d/%m/%Y") + """</div>
        <table>
            <thead>
                <tr><th>FECHA</th><th>HORA</th><th>LUGAR</th><th>CIUDAD</th><th>LOGÍSTICA</th><th>ESTADO</th></tr>
            </thead>
            <tbody>
    """
    for index, row in dataframe.iterrows():
        fecha_str = f"{row['Fecha'].day}/{row['Fecha'].month}/{row['Fecha'].year} ({traducir_dia(row['Fecha'])})"
        logistica = ""
        if pd.notna(row.get('Salida')): logistica += f"Salida: {row['Salida']} <br>"
        if pd.notna(row.get('Prueba')): logistica += f"Prueba: {row['Prueba']}"
        est = row.get('Estado', 'Pendiente')
        clase_estado = "status-ok" if est == "Confirmado" else "status-bad" if est == "Cancelado" else "status-warn"
        html += f"""<tr><td>{fecha_str}</td><td>{row['Hora']} hs</td><td><strong>{row['Lugar']}</strong></td><td>{row.get('Ciudad', '')}</td><td><small>{logistica}</small></td><td><span class="{clase_estado}">{est}</span></td></tr>"""
    html += """</tbody></table><script>window.onload = function() { window.print(); }</script></body></html>"""
    return html

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
    
    lk_map = row.get('Mapa')
    if pd.isna(lk_map) or not str(lk_map).startswith('http'): lk_map = None
    lk_rep = row.get('Repertorio')
    if pd.isna(lk_rep) or not str(lk_rep).startswith('http'): lk_rep = None

    if lk_map and lk_rep:
        c1, c2 = st.columns(2)
        with c1: st.link_button("📍 Ubicación", lk_map)
        with c2: st.link_button("🎼 Repertorio", lk_rep)
    elif lk_map: st.link_button("📍 Ubicación", lk_map)
    elif lk_rep: st.link_button("🎼 Repertorio", lk_rep)


# --- 3. ESTILOS Y SCRIPTS "ANTIMARCAS" ---

set_png_as_page_bg("fondo.jpg")

# ESTO COMBINA CSS Y JAVASCRIPT PARA BORRAR TODO
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lobster&family=Montserrat:wght@400;800&display=swap');

    /* Ocultar elementos por CSS */
    header, footer, [data-testid="stHeader"], [data-testid="stFooter"], [data-testid="stToolbar"], [data-testid="stDecoration"] {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }
    
    #MainMenu {display: none !important;}
    
    /* Ajustar contenedores para que no quede espacio vacío arriba */
    .block-container { padding-top: 0rem !important; padding-bottom: 3rem !important; }
    .stApp { margin-top: -50px !important; } /* Forzar subida */

    /* ESTILOS DE LA APP */
    .stApp, h1, h2, h3, p, div { color: #E0E0E0; font-family: 'Montserrat', sans-serif; }
    
    /* ... (Resto de tus estilos de siempre) ... */
    .titulo-contenedor { text-align: center; margin-bottom: 20px; margin-top: 60px; } /* Margen top para compensar subida */
    .linea-superior { display: flex; justify-content: center; align-items: center; gap: 15px; margin-bottom: 5px; }
    .iconos-header { font-size: 3.5rem; text-shadow: 0 0 15px rgba(255, 215, 0, 0.6); }
    .highlight-agenda {
        font-family: 'Lobster', cursive; font-size: 6rem !important; font-weight: 400;
        background: -webkit-linear-gradient(#FFF700, #FF4500); -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        -webkit-text-stroke: 1.5px #FFD700; line-height: 1.0;
        text-shadow: 0 0 15px rgba(255, 215, 0, 0.9), 0 0 30px rgba(255, 69, 0, 0.7), 5px 5px 8px #000000;
        margin: 0; padding-top: 10px; transform: rotate(-2deg) scale(1.05); z-index: 10;
    }
    .subtitulo-banda {
        font-family: 'Montserrat', sans-serif; font-size: 1.6rem !important; font-weight: 800;
        text-transform: uppercase; letter-spacing: 1px; color: #FFFFFF; text-shadow: 3px 3px 6px #000000;
        border-top: 3px solid #FF8C00; border-bottom: 3px solid #FF8C00; padding: 12px 0;
        margin-top: 10px; display: inline-block; line-height: 1.3;
    }
    
    /* Estilos Expander */
    .streamlit-expanderHeader { background-color: rgba(30, 30, 30, 0.6) !important; border: 1px solid #444 !important; border-radius: 8px !important; color: #bbb !important; font-size: 0.9rem !important; }
    .streamlit-expanderContent { background-color: rgba(20, 20, 20, 0.8) !important; border-radius: 0 0 8px 8px !important; border: 1px solid #444 !important; border-top: none !important; }

    @media only screen and (max-width: 600px) {
        .highlight-agenda { font-size: 3.8rem !important; }
        .iconos-header { font-size: 2.2rem !important; }
        .subtitulo-banda { font-size: 1rem !important; padding: 8px 0; }
        .date-box { min-width: 60px !important; padding: 5px !important; margin-right: 10px !important; }
        .date-day { font-size: 1.8rem !important; }
        .gig-venue { font-size: 1.2rem !important; }
    }

    .gig-card { background-color: rgba(20, 20, 20, 0.90); border-radius: 15px; padding: 20px; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.8); border-left: 8px solid #555; backdrop-filter: blur(8px); }
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
    div[data-testid="stLinkButton"] > a { background-color: transparent !important; border: 1px solid #FFAB00 !important; color: #FFAB00 !important; font-weight: 600 !important; font-size: 0.8rem !important; text-transform: uppercase; padding: 0.3rem 0rem !important; min-height: 0px !important; border-radius: 20px !important; transition: all 0.3s ease; text-align: center; margin-top: -5px !important; }
    div[data-testid="stLinkButton"] > a:hover { background-color: #FFAB00 !important; color: #000 !important; border: 1px solid #FFAB00 !important; box-shadow: 0 0 10px rgba(255, 171, 0, 0.5); }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; margin-bottom: 20px; }
    .stTabs [data-baseweb="tab"] { background-color: rgba(60, 60, 60, 0.8); border-radius: 8px; color: #E0E0E0; font-size: 1.1rem !important; font-weight: 600 !important; padding: 10px 20px !important; border: 1px solid #444; }
    .stTabs [aria-selected="true"] { background-color: #FFAB00 !important; color: black !important; font-weight: 900 !important; box-shadow: 0 0 10px rgba(255, 171, 0, 0.5); border: 1px solid #FFAB00; }
</style>

<script>
    // Función que busca y destruye los elementos de Streamlit
    function eliminarMarcas() {
        // 1. Header Superior
        var header = window.parent.document.querySelector('header');
        if (header) { header.style.display = 'none'; header.remove(); }
        
        // 2. Footer (Made with Streamlit)
        var footer = window.parent.document.querySelector('footer');
        if (footer) { footer.style.display = 'none'; footer.remove(); }
        
        // 3. Barra de colores (Decoration)
        var decoration = window.parent.document.querySelector('[data-testid="stDecoration"]');
        if (decoration) { decoration.style.display = 'none'; decoration.remove(); }
        
        // 4. Toolbar (Menú Hamburguesa y Deploy)
        var toolbar = window.parent.document.querySelector('[data-testid="stToolbar"]');
        if (toolbar) { toolbar.style.display = 'none'; toolbar.remove(); }
        
        // 5. Status Widget (Running...)
        var status = window.parent.document.querySelector('[data-testid="stStatusWidget"]');
        if (status) { status.style.display = 'none'; status.remove(); }
    }
    
    // Ejecutar al cargar y repetir cada 500ms por si Streamlit los vuelve a poner
    eliminarMarcas();
    setInterval(eliminarMarcas, 500);
</script>
""", unsafe_allow_html=True)

# --- 4. LÓGICA DE EJECUCIÓN ---

df = load_data()
fecha_url = st.query_params.get("fecha", None)

# --- MODO DETALLE ---
if not df.empty and fecha_url:
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors='coerce', dayfirst=True)
    df = df.dropna(subset=['Fecha']).sort_values(by="Fecha")
    
    st.markdown("""
    <div class="titulo-contenedor">
    <div class="linea-superior"><span class="iconos-header">🎸</span><span class="highlight-agenda">Agenda</span><span class="iconos-header">🎷</span></div>
    <div class="subtitulo-banda">Banda Departamental de Lavalleja</div>
    </div>
    """, unsafe_allow_html=True)

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

# --- MODO PRINCIPAL ---
elif not df.empty:
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors='coerce', dayfirst=True)
    df = df.dropna(subset=['Fecha']).sort_values(by="Fecha")
    dias_shows = df["Fecha"].dt.strftime('%Y-%m-%d').unique().tolist()
    hoy = pd.Timestamp.now().normalize()

    # 1. TÍTULO
    st.markdown("""
    <div class="titulo-contenedor">
    <div class="linea-superior"><span class="iconos-header">🎸</span><span class="highlight-agenda">Agenda</span><span class="iconos-header">🎷</span></div>
    <div class="subtitulo-banda">Banda Departamental de Lavalleja</div>
    </div>
    """, unsafe_allow_html=True)

    # 2. MENÚ DE GESTIÓN (EXPANDER OCULTO)
    with st.expander("⚙️ Gestión / Herramientas"):
        c1, c2, c3 = st.columns(3)
        with c1:
            hist = st.toggle("Ver Historial", value=False)
        with c2:
            if st.button("🔄 Actualizar Datos", help="Recargar Excel"): st.cache_data.clear()
        with c3:
            vis_print = df if hist else df[df["Fecha"] >= hoy]
            html_print = generar_html_para_imprimir(vis_print)
            st.download_button("🖨️ Imprimir Lista", html_print, file_name="agenda.html", mime="text/html")

    # Filtro visual
    vis = df if hist else df[df["Fecha"] >= hoy]
    st.caption(f"Próximos eventos: {len(vis)}")
    
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