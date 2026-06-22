import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import date, datetime
import time

# ─────────────────────────────────────────
#  CONFIGURACIÓN GENERAL
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Club de Fútbol",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────
#  ESTILOS CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;600;700&family=Inter:wght@300;400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Fondo general */
    .stApp {
        background: linear-gradient(160deg, #0a0f1e 0%, #0d2137 50%, #071525 100%);
        min-height: 100vh;
    }

    /* Ocultar menú de Streamlit */
    #MainMenu, footer, header {visibility: hidden;}

    /* ── PANTALLA DE LOGIN ── */
    .login-container {
        max-width: 420px;
        margin: 4vh auto;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 2.5rem 2rem;
        backdrop-filter: blur(12px);
    }
    .logo-area {
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .logo-area .escudo {
        font-size: 4rem;
        display: block;
    }
    .logo-area h1 {
        font-family: 'Oswald', sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin: 0.3rem 0 0.1rem;
    }
    .logo-area p {
        color: #4fa3d1;
        font-size: 0.8rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
    }
    .login-divider {
        border: none;
        border-top: 1px solid rgba(255,255,255,0.08);
        margin: 1.2rem 0;
    }

    /* ── HEADER DE APP ── */
    .app-header {
        background: rgba(0,0,0,0.35);
        border-bottom: 2px solid #1a6fa8;
        padding: 0.8rem 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
        border-radius: 0 0 12px 12px;
    }
    .app-header h2 {
        font-family: 'Oswald', sans-serif;
        color: #ffffff;
        margin: 0;
        font-size: 1.4rem;
        letter-spacing: 0.08em;
    }
    .badge-rol {
        background: #1a6fa8;
        color: white;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 500;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    /* ── CARDS ── */
    .stat-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1.2rem 1rem;
        text-align: center;
        transition: border-color 0.2s;
    }
    .stat-card:hover { border-color: #1a6fa8; }
    .stat-card .num {
        font-family: 'Oswald', sans-serif;
        font-size: 2.4rem;
        color: #4fa3d1;
        line-height: 1;
    }
    .stat-card .label {
        color: rgba(255,255,255,0.55);
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 0.3rem;
    }

    /* Inputs más oscuros */
    .stTextInput>div>div>input,
    .stSelectbox>div>div>div,
    .stTextArea textarea,
    .stNumberInput input,
    .stDateInput input {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        color: #e8edf2 !important;
        border-radius: 8px !important;
    }
    .stTextInput>div>div>input:focus {
        border-color: #1a6fa8 !important;
        box-shadow: 0 0 0 2px rgba(26,111,168,0.25) !important;
    }

    /* Labels */
    .stTextInput label, .stSelectbox label, .stTextArea label,
    .stNumberInput label, .stDateInput label, .stRadio label {
        color: rgba(255,255,255,0.7) !important;
        font-size: 0.82rem !important;
    }

    /* Botón primario */
    .stButton>button {
        background: linear-gradient(135deg, #1a6fa8, #0d4f7a) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        letter-spacing: 0.04em !important;
        padding: 0.55rem 1.5rem !important;
        width: 100% !important;
        transition: opacity 0.2s !important;
    }
    .stButton>button:hover { opacity: 0.88 !important; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(0,0,0,0.3);
        border-radius: 10px;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: rgba(255,255,255,0.5);
        border-radius: 7px;
        font-size: 0.85rem;
    }
    .stTabs [aria-selected="true"] {
        background: #1a6fa8 !important;
        color: white !important;
    }

    /* Mensajes de éxito/error */
    .stSuccess { border-radius: 8px; }
    .stError { border-radius: 8px; }

    /* Dataframe */
    .stDataFrame { border-radius: 10px; overflow: hidden; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(5,15,35,0.95) !important;
    }
    section[data-testid="stSidebar"] .stRadio label { color: white !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  CONEXIÓN A GOOGLE SHEETS
# ─────────────────────────────────────────
SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

@st.cache_resource(ttl=300)
def get_gsheet_client():
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)

def get_or_create_worksheet(spreadsheet, name, headers):
    """Obtiene una hoja o la crea con cabeceras si no existe."""
    try:
        ws = spreadsheet.worksheet(name)
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=name, rows=500, cols=len(headers))
        ws.append_row(headers, value_input_option="USER_ENTERED")
    return ws

def load_spreadsheet():
    client = get_gsheet_client()
    return client.open_by_url(st.secrets["sheet"]["url"])

# ─────────────────────────────────────────
#  CABECERAS DE CADA HOJA
# ─────────────────────────────────────────
HEADERS_JUGADORES = [
    # Datos personales
    "id", "nombre_completo", "fecha_nacimiento", "edad", "ci",
    "telefono", "email", "direccion", "contacto_emergencia", "tel_emergencia",
    # Datos deportivos
    "dorsal", "posicion", "pie_dominante", "altura_cm", "peso_kg",
    "fecha_incorporacion", "estado",
    # Historial lesiones (campo libre / contador)
    "num_lesiones", "notas_lesiones",
    # Metadata
    "fecha_registro", "registrado_por"
]

HEADERS_LESIONES = [
    "id_lesion", "id_jugador", "nombre_jugador", "tipo_lesion",
    "fecha_inicio", "fecha_alta", "dias_baja", "descripcion",
    "fecha_registro"
]

HEADERS_USUARIOS = [
    "username", "password_hash", "rol", "id_jugador", "activo"
]

# ─────────────────────────────────────────
#  AUTENTICACIÓN
# ─────────────────────────────────────────
def check_login(username: str, password: str):
    """
    Verifica credenciales. Entrenador desde secrets.toml,
    jugadores desde la hoja 'usuarios'.
    """
    # Entrenador hardcodeado en secrets
    if (username.lower() == "entrenador" and
            password == st.secrets["passwords"]["entrenador"]):
        return {"rol": "entrenador", "nombre": "Entrenador", "id_jugador": None}

    # Jugadores: buscar en Google Sheets
    try:
        ss = load_spreadsheet()
        ws_users = get_or_create_worksheet(ss, "usuarios", HEADERS_USUARIOS)
        records = ws_users.get_all_records()
        for row in records:
            if (str(row["username"]).lower() == username.lower() and
                    str(row["password_hash"]) == password and
                    str(row["activo"]) == "1"):
                return {
                    "rol": row["rol"],
                    "nombre": username,
                    "id_jugador": row.get("id_jugador", "")
                }
    except Exception:
        pass
    return None

# ─────────────────────────────────────────
#  PANTALLA DE LOGIN
# ─────────────────────────────────────────
def render_login():
    st.markdown("""
    <div class="login-container">
        <div class="logo-area">
            <span class="escudo">⚽</span>
            <h1>Mi Equipo</h1>
            <p>Panel de Gestión Deportiva</p>
        </div>
        <hr class="login-divider">
    </div>
    """, unsafe_allow_html=True)

    # Centramos el formulario
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("#### 🔐 Iniciar sesión")
            username = st.text_input("Usuario", placeholder="entrenador / tu usuario")
            password = st.text_input("Contraseña", type="password", placeholder="••••••••")
            login_btn = st.button("Ingresar →", use_container_width=True)

        if login_btn:
            if not username or not password:
                st.error("Completa ambos campos.")
            else:
                with st.spinner("Verificando..."):
                    result = check_login(username, password)
                if result:
                    st.session_state["logged_in"] = True
                    st.session_state["rol"] = result["rol"]
                    st.session_state["nombre"] = result["nombre"]
                    st.session_state["id_jugador"] = result.get("id_jugador")
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")

        st.markdown(
            "<p style='text-align:center;color:rgba(255,255,255,0.3);font-size:0.7rem;margin-top:1.5rem;'>"
            "Acceso restringido • Solo personal autorizado</p>",
            unsafe_allow_html=True
        )

# ─────────────────────────────────────────
#  HEADER COMÚN
# ─────────────────────────────────────────
def render_header():
    rol = st.session_state.get("rol", "")
    nombre = st.session_state.get("nombre", "")
    badge = "🏋️ Entrenador" if rol == "entrenador" else "⚽ Jugador"
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown(f"""
        <div class="app-header">
            <span style="font-size:1.8rem">⚽</span>
            <h2>MI EQUIPO</h2>
            <span class="badge-rol">{badge}</span>
            <span style="color:rgba(255,255,255,0.4);font-size:0.82rem;margin-left:auto">
                Hola, {nombre}
            </span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("Salir 🚪"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# ─────────────────────────────────────────
#  MÓDULO: REGISTRO DE JUGADOR
# ─────────────────────────────────────────
def render_registro_jugador():
    st.markdown("### 📋 Registrar nuevo jugador")

    try:
        ss = load_spreadsheet()
        ws_jug = get_or_create_worksheet(ss, "jugadores", HEADERS_JUGADORES)
        ws_usr = get_or_create_worksheet(ss, "usuarios", HEADERS_USUARIOS)
    except Exception as e:
        st.error(f"Error conectando a Google Sheets: {e}")
        return

    with st.form("form_registro", clear_on_submit=True):
        # ── DATOS PERSONALES ──
        st.markdown("#### 👤 Datos Personales")
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre completo *", placeholder="Ej: Carlos Mamani Quispe")
            fecha_nac = st.date_input(
                "Fecha de nacimiento *",
                min_value=date(1980, 1, 1),
                max_value=date(date.today().year - 18, date.today().month, date.today().day),
                value=date(2000, 1, 1)
            )
            ci = st.text_input("C.I. (Cédula de Identidad)", placeholder="Ej: 12345678")
        with c2:
            telefono = st.text_input("Teléfono / WhatsApp", placeholder="Ej: 71234567")
            email = st.text_input("Email (opcional)", placeholder="jugador@email.com")
            direccion = st.text_input("Dirección", placeholder="Zona, ciudad")

        c3, c4 = st.columns(2)
        with c3:
            contacto_emerg = st.text_input("Contacto de emergencia", placeholder="Nombre del familiar")
        with c4:
            tel_emerg = st.text_input("Teléfono de emergencia", placeholder="Ej: 71234567")

        st.divider()

        # ── DATOS DEPORTIVOS ──
        st.markdown("#### ⚽ Datos Deportivos")
        c5, c6, c7 = st.columns(3)
        with c5:
            dorsal = st.number_input("Dorsal #", min_value=1, max_value=99, value=10)
            posicion = st.selectbox("Posición *", [
                "Portero", "Defensa Central", "Lateral Derecho", "Lateral Izquierdo",
                "Mediocampista Defensivo", "Mediocampista Central",
                "Mediocampista Ofensivo", "Extremo Derecho", "Extremo Izquierdo",
                "Segundo Delantero", "Delantero Centro"
            ])
        with c6:
            pie = st.selectbox("Pie dominante", ["Derecho", "Izquierdo", "Ambidiestro"])
            altura = st.number_input("Altura (cm)", min_value=140, max_value=220, value=175)
        with c7:
            peso = st.number_input("Peso (kg)", min_value=40, max_value=150, value=70)
            estado = st.selectbox("Estado", ["Activo", "Lesionado", "Suspendido", "Baja"])

        fecha_incorp = st.date_input("Fecha de incorporación al club", value=date.today())

        st.divider()

        # ── HISTORIAL DE LESIONES ──
        st.markdown("#### 🏥 Historial de Lesiones (inicial)")
        notas_lesiones = st.text_area(
            "Lesiones previas conocidas (opcional)",
            placeholder="Ej: Rotura de ligamentos rodilla derecha en 2022. Recuperado.",
            height=90
        )

        st.divider()

        # ── CREDENCIALES DE ACCESO ──
        st.markdown("#### 🔐 Credenciales de acceso para el jugador")
        c8, c9 = st.columns(2)
        with c8:
            usuario_login = st.text_input(
                "Nombre de usuario *",
                placeholder="Ej: cmamani (sin espacios)"
            )
        with c9:
            pass_jugador = st.text_input(
                "Contraseña temporal *",
                type="password",
                placeholder="Mínimo 6 caracteres"
            )

        submitted = st.form_submit_button("✅ Registrar jugador", use_container_width=True)

    if submitted:
        # Validaciones
        errores = []
        if not nombre.strip():
            errores.append("El nombre es obligatorio.")
        if not posicion:
            errores.append("La posición es obligatoria.")
        if not usuario_login.strip():
            errores.append("El nombre de usuario es obligatorio.")
        if len(pass_jugador) < 6:
            errores.append("La contraseña debe tener mínimo 6 caracteres.")
        if " " in usuario_login:
            errores.append("El usuario no puede tener espacios.")

        # Verificar usuario duplicado
        try:
            existing_users = ws_usr.col_values(1)  # columna 'username'
            if usuario_login.lower() in [u.lower() for u in existing_users]:
                errores.append(f"El usuario '{usuario_login}' ya existe.")
        except Exception:
            pass

        if errores:
            for e in errores:
                st.error(e)
        else:
            try:
                # Calcular edad
                hoy = date.today()
                edad = hoy.year - fecha_nac.year - (
                    (hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day)
                )

                # Generar ID único
                all_rows = ws_jug.get_all_values()
                next_id = len(all_rows)  # filas existentes (incl. cabecera)

                id_jugador = f"JUG{next_id:04d}"
                ahora = datetime.now().strftime("%Y-%m-%d %H:%M")

                # Fila del jugador
                fila_jugador = [
                    id_jugador, nombre.strip(), str(fecha_nac), str(edad), ci,
                    telefono, email, direccion, contacto_emerg, tel_emerg,
                    str(dorsal), posicion, pie, str(altura), str(peso),
                    str(fecha_incorp), estado,
                    "0", notas_lesiones.strip(),
                    ahora, "Entrenador"
                ]

                # Fila de usuario
                fila_usuario = [
                    usuario_login.lower(), pass_jugador, "jugador", id_jugador, "1"
                ]

                ws_jug.append_row(fila_jugador, value_input_option="USER_ENTERED")
                ws_usr.append_row(fila_usuario, value_input_option="USER_ENTERED")

                st.success(f"✅ Jugador **{nombre}** registrado con ID `{id_jugador}`")
                st.info(f"🔑 Credenciales: usuario `{usuario_login}` — contraseña `{pass_jugador}`")
                time.sleep(0.5)

            except Exception as ex:
                st.error(f"Error al guardar: {ex}")

# ─────────────────────────────────────────
#  MÓDULO: PLANTILLA (lista de jugadores)
# ─────────────────────────────────────────
def render_plantilla():
    st.markdown("### 👥 Plantilla del Equipo")

    try:
        ss = load_spreadsheet()
        ws_jug = get_or_create_worksheet(ss, "jugadores", HEADERS_JUGADORES)
        records = ws_jug.get_all_records()
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return

    if not records:
        st.info("Aún no hay jugadores registrados. Ve a **Registrar Jugador** para agregar el primero.")
        return

    df = pd.DataFrame(records)

    # Stats rápidas
    total = len(df)
    activos = len(df[df["estado"] == "Activo"]) if "estado" in df.columns else 0
    lesionados = len(df[df["estado"] == "Lesionado"]) if "estado" in df.columns else 0

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        (total, "Total jugadores"),
        (activos, "Activos"),
        (lesionados, "Lesionados"),
        (total - activos - lesionados, "Otros"),
    ]
    for col, (num, label) in zip([c1, c2, c3, c4], cards):
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <div class="num">{num}</div>
                <div class="label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Filtros
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        busqueda = st.text_input("🔍 Buscar por nombre", placeholder="Escribe un nombre...")
    with col_f2:
        filtro_estado = st.selectbox("Filtrar por estado", ["Todos", "Activo", "Lesionado", "Suspendido", "Baja"])

    df_filtrado = df.copy()
    if busqueda:
        df_filtrado = df_filtrado[
            df_filtrado["nombre_completo"].str.contains(busqueda, case=False, na=False)
        ]
    if filtro_estado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["estado"] == filtro_estado]

    # Columnas a mostrar
    cols_mostrar = ["id", "dorsal", "nombre_completo", "posicion", "edad",
                    "pie_dominante", "altura_cm", "peso_kg", "estado", "fecha_incorporacion"]
    cols_disponibles = [c for c in cols_mostrar if c in df_filtrado.columns]

    st.dataframe(
        df_filtrado[cols_disponibles].rename(columns={
            "id": "ID", "dorsal": "#", "nombre_completo": "Nombre",
            "posicion": "Posición", "edad": "Edad", "pie_dominante": "Pie",
            "altura_cm": "Alt (cm)", "peso_kg": "Peso (kg)",
            "estado": "Estado", "fecha_incorporacion": "Incorporación"
        }),
        use_container_width=True,
        hide_index=True,
    )

    # Ver detalle de un jugador
    if not df_filtrado.empty:
        st.markdown("---")
        st.markdown("#### 🔎 Ver perfil completo")
        opciones = ["— Selecciona —"] + df_filtrado["nombre_completo"].tolist()
        seleccionado = st.selectbox("Jugador", opciones, label_visibility="collapsed")

        if seleccionado != "— Selecciona —":
            jug = df_filtrado[df_filtrado["nombre_completo"] == seleccionado].iloc[0]
            c_a, c_b = st.columns(2)
            with c_a:
                st.markdown("**👤 Datos Personales**")
                st.write(f"🪪 CI: {jug.get('ci', '-')}")
                st.write(f"📅 Nacimiento: {jug.get('fecha_nacimiento', '-')} ({jug.get('edad', '-')} años)")
                st.write(f"📞 Tel: {jug.get('telefono', '-')}")
                st.write(f"📧 Email: {jug.get('email', '-')}")
                st.write(f"🏠 Dirección: {jug.get('direccion', '-')}")
                st.write(f"🆘 Emergencia: {jug.get('contacto_emergencia', '-')} — {jug.get('tel_emergencia', '-')}")
            with c_b:
                st.markdown("**⚽ Datos Deportivos**")
                st.write(f"# Dorsal: {jug.get('dorsal', '-')}")
                st.write(f"🧤 Posición: {jug.get('posicion', '-')}")
                st.write(f"👟 Pie: {jug.get('pie_dominante', '-')}")
                st.write(f"📏 Altura: {jug.get('altura_cm', '-')} cm")
                st.write(f"⚖️ Peso: {jug.get('peso_kg', '-')} kg")
                st.write(f"📌 Estado: {jug.get('estado', '-')}")
                st.write(f"📅 Incorporación: {jug.get('fecha_incorporacion', '-')}")

            if jug.get("notas_lesiones"):
                st.markdown("**🏥 Historial de lesiones**")
                st.info(jug["notas_lesiones"])

# ─────────────────────────────────────────
#  MÓDULO: PERFIL DEL JUGADOR
# ─────────────────────────────────────────
def render_perfil_jugador():
    id_jug = st.session_state.get("id_jugador")
    if not id_jug:
        st.warning("No se encontró tu perfil. Contacta al entrenador.")
        return

    st.markdown("### 👤 Mi Perfil")

    try:
        ss = load_spreadsheet()
        ws_jug = get_or_create_worksheet(ss, "jugadores", HEADERS_JUGADORES)
        records = ws_jug.get_all_records()
        df = pd.DataFrame(records)
        jug = df[df["id"] == id_jug]
        if jug.empty:
            st.warning("Perfil no encontrado.")
            return
        jug = jug.iloc[0]
    except Exception as e:
        st.error(f"Error: {e}")
        return

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**👤 Datos Personales**")
        st.write(f"📛 Nombre: **{jug.get('nombre_completo', '-')}**")
        st.write(f"📅 Nacimiento: {jug.get('fecha_nacimiento', '-')} ({jug.get('edad', '-')} años)")
        st.write(f"📞 Tel: {jug.get('telefono', '-')}")
        st.write(f"📧 Email: {jug.get('email', '-')}")
    with c2:
        st.markdown("**⚽ Datos Deportivos**")
        st.write(f"# Dorsal: **{jug.get('dorsal', '-')}**")
        st.write(f"🧤 Posición: {jug.get('posicion', '-')}")
        st.write(f"👟 Pie dominante: {jug.get('pie_dominante', '-')}")
        st.write(f"📏 Altura: {jug.get('altura_cm', '-')} cm | ⚖️ Peso: {jug.get('peso_kg', '-')} kg")
        st.write(f"📌 Estado actual: **{jug.get('estado', '-')}**")

    if jug.get("notas_lesiones"):
        st.markdown("---")
        st.markdown("**🏥 Historial de Lesiones**")
        st.info(jug["notas_lesiones"])

# ─────────────────────────────────────────
#  PANEL PRINCIPAL — ENTRENADOR
# ─────────────────────────────────────────
def render_panel_entrenador():
    render_header()
    menu = st.sidebar.radio(
        "Menú",
        ["🏠 Inicio", "📋 Registrar Jugador", "👥 Ver Plantilla"],
        label_visibility="collapsed"
    )

    if menu == "🏠 Inicio":
        st.markdown("### 🏠 Panel del Entrenador")
        st.markdown("""
        <div style="background:rgba(26,111,168,0.1);border:1px solid rgba(26,111,168,0.3);
             border-radius:12px;padding:1.2rem;margin-bottom:1rem;">
            <p style="color:rgba(255,255,255,0.7);margin:0">
            👋 Bienvenido, Entrenador. Desde el menú lateral puedes registrar jugadores
            y consultar la plantilla completa.
            </p>
        </div>
        """, unsafe_allow_html=True)
        try:
            ss = load_spreadsheet()
            ws_jug = get_or_create_worksheet(ss, "jugadores", HEADERS_JUGADORES)
            records = ws_jug.get_all_records()
            df = pd.DataFrame(records) if records else pd.DataFrame()

            total = len(df)
            activos = len(df[df["estado"] == "Activo"]) if not df.empty else 0
            lesionados = len(df[df["estado"] == "Lesionado"]) if not df.empty else 0

            c1, c2, c3 = st.columns(3)
            for col, (n, lbl) in zip([c1, c2, c3], [
                (total, "Jugadores"), (activos, "Activos"), (lesionados, "Lesionados")
            ]):
                with col:
                    st.markdown(f'<div class="stat-card"><div class="num">{n}</div>'
                                f'<div class="label">{lbl}</div></div>', unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"No se pudo conectar a Sheets: {e}")

    elif menu == "📋 Registrar Jugador":
        render_registro_jugador()

    elif menu == "👥 Ver Plantilla":
        render_plantilla()

# ─────────────────────────────────────────
#  PANEL PRINCIPAL — JUGADOR
# ─────────────────────────────────────────
def render_panel_jugador():
    render_header()
    st.markdown("### ⚽ Bienvenido al Panel del Jugador")
    st.markdown("""
    <div style="background:rgba(26,111,168,0.1);border:1px solid rgba(26,111,168,0.3);
         border-radius:12px;padding:1rem;margin-bottom:1rem;">
        <p style="color:rgba(255,255,255,0.7);margin:0">
        Aquí puedes consultar tu perfil. Más módulos (estadísticas, convocatorias, etc.)
        llegarán en próximas actualizaciones.
        </p>
    </div>
    """, unsafe_allow_html=True)
    render_perfil_jugador()

# ─────────────────────────────────────────
#  PUNTO DE ENTRADA
# ─────────────────────────────────────────
def main():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        render_login()
    else:
        rol = st.session_state.get("rol", "")
        if rol == "entrenador":
            render_panel_entrenador()
        elif rol == "jugador":
            render_panel_jugador()
        else:
            st.error("Rol no reconocido.")
            if st.button("Cerrar sesión"):
                for k in list(st.session_state.keys()):
                    del st.session_state[k]
                st.rerun()

if __name__ == "__main__":
    main()
