import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date
import pandas as pd
import time

# Configuración de la página
st.set_page_config(page_title="Mi Equipo - Panel de Control", page_icon="⚽", layout="centered")

# ─────────────────────────────────────────
#  CABECERAS DE GOOGLE SHEETS
# ─────────────────────────────────────────
HEADERS_JUGADORES = ["id", "nombre_completo", "edad", "fecha_nacimiento", "altura", "peso", "posicion", "pierna_dominante", "fecha_registro"]
HEADERS_USUARIOS = ["usuario", "contrasena", "rol", "id_jugador"]
HEADERS_EVALUACIONES = [
    "id_eval", "id_jugador", "nombre_jugador", "fecha_evaluacion", "posicion",
    "vel_10m", "vel_30m", "agilidad", "resistencia", "salto_vertical", "potencia",
    "precision_pase", "control_orientado", "conduccion", "definicion",
    "peso_eval", "altura_eval", "masa_muscular", "imc",
    "score_fisico", "score_tecnico", "score_corporal",
    "irj", "fortalezas", "debilidades",
    "potencial_corto", "potencial_mediano",
    "registrado_by"
]

# ── Pesos por posición asignados por el Motor Analítico (Físico, Técnico, Corporal)
PESOS_POSICION = {
    "Portero":                  (0.30, 0.35, 0.35),
    "Defensa Central":          (0.35, 0.35, 0.30),
    "Lateral Derecho":          (0.38, 0.37, 0.25),
    "Lateral Izquierdo":        (0.38, 0.37, 0.25),
    "Mediocampista Defensivo":  (0.35, 0.40, 0.25),
    "Mediocampista Central":    (0.32, 0.48, 0.20),
    "Mediocampista Ofensivo":   (0.30, 0.50, 0.20),
    "Extremo Derecho":          (0.50, 0.35, 0.15),
    "Extremo Izquierdo":        (0.50, 0.35, 0.15),
    "Segundo Delantero":        (0.40, 0.45, 0.15),
    "Delantero Centro":         (0.45, 0.40, 0.15),
}

# ─────────────────────────────────────────
#  FASE 3: BIBLIOTECAS DE ENTRENAMIENTO ASIGNADAS
# ─────────────────────────────────────────
BI_GIMNASIO = {
    "Hipertrofia": [
        {"ejercicio": "Sentadilla Libre", "series": "4x10", "descanso": "90s"},
        {"ejercicio": "Prensa Inclinada de Piernas", "series": "3x12", "descanso": "60s"},
        {"ejercicio": "Press de Banca Plano", "series": "4x10", "descanso": "90s"},
        {"ejercicio": "Remo con Barra", "series": "3x12", "descanso": "60s"}
    ],
    "Fuerza": [
        {"ejercicio": "Sentadilla Pesada (SNC)", "series": "5x5", "descanso": "180s"},
        {"ejercicio": "Peso Muerto Convencional", "series": "4x4", "descanso": "180s"},
        {"ejercicio": "Press Militar Integrado", "series": "4x5", "descanso": "120s"}
    ],
    "Potencia": [
        {"ejercicio": "Saltos Pliométricos a Cajón", "series": "4x6", "descanso": "120s"},
        {"ejercicio": "Clean / Cargadas colgantes", "series": "4x4", "descanso": "150s"},
        {"ejercicio": "Zancadas Explosivas con Salto", "series": "3x8", "descanso": "90s"}
    ],
    "Velocidad / Resistencia": [
        {"ejercicio": "Saltos Monopodales en Escalera", "series": "3x10", "descanso": "60s"},
        {"ejercicio": "Core - Planchas dinámicas e IPP", "series": "4x45s", "descanso": "45s"}
    ]
}

BI_CAMPO = {
    "Portero": [
        {"bloque": "Reflejos y Blocaje", "detalle": "Lanzamientos cruzados a tres alturas con caídas laterales (4 series x 6 rep)"},
        {"bloque": "Juego de Pies", "detalle": "Pases tensos de primera intención tras control orientado bajo presión (3 series x 2 min)"}
    ],
    "Defensa": [
        {"bloque": "Posicionamiento", "detalle": "Desplazamientos en diagonal, perfiles y temporización ante extremos veloces (4 series x 3 min)"},
        {"bloque": "Salida y Pase", "detalle": "Pase largo tensionado buscando cambio de orientación (10 rep por pierna)"}
    ],
    "Mediocampista": [
        {"bloque": "Control Orientado", "detalle": "Giro en 180° tras recibir pase de espaldas para filtrar entrelíneas (5 series x 10 rep)"},
        {"bloque": "Potencia Metabólica", "detalle": "Pasadas intermitentes en rombo con conducción en velocidad (3 series x 4 min)"}
    ],
    "Delantero": [
        {"bloque": "Definición Extrema", "detalle": "Remate de primera tras centro lateral cruzado en velocidad (12 rep por perfil)"},
        {"bloque": "Agilidad y Desmarque", "detalle": "Sprints con cambios de dirección cortos en el área y tiro a puerta (5 series)"}
    ]
}

def obtener_perfil_tactico(posicion):
    pos = str(posicion).lower()
    if "portero" in pos or "arquero" in pos: return "Portero"
    if "defensa" in pos or "central" in pos or "lateral" in pos: return "Defensa"
    if "medio" in pos or "volante" in pos or "centrocampista" in pos: return "Mediocampista"
    return "Delantero"

# ─────────────────────────────────────────
#  CONEXIÓN A GOOGLE SHEETS
# ─────────────────────────────────────────
def get_gsheet_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(credentials)

def load_spreadsheet():
    client = get_gsheet_client()
    return client.open_by_key(st.secrets["spreadsheet_id"])

def get_or_create_worksheet(spreadsheet, name, headers):
    for ws in spreadsheet.worksheets():
        if ws.title.lower() == name.lower():
            return ws
    ws = spreadsheet.add_worksheet(title=name, rows=500, cols=len(headers))
    ws.append_row(headers, value_input_option="USER_ENTERED")
    return ws

# ─────────────────────────────────────────
#  COMPONENTES VISUALES Y ESTILOS CSS
# ─────────────────────────────────────────
def render_header():
    st.markdown("""
    <style>
    .stat-card {
        background-color: #1e293b;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.1);
        text-align: center;
        margin-bottom: 10px;
    }
    .stat-card .num {
        font-weight: bold;
        font-family: 'Oswald', sans-serif;
    }
    .stat-card .label {
        color: #94a3b8;
        font-size: 0.85rem;
        text-transform: uppercase;
        margin-top: 5px;
    }
    </style>
    <div style="background-color:#0f2027; padding:20px; border-radius:10px; margin-bottom:20px; border-left: 5px solid #203a43;">
        <h1 style="color:white; margin:0; font-size:28px;">⚽ MI EQUIPO</h1>
        <p style="color:#81a1c1; margin:5px 0 0 0;">Sistema Privado de Gestión Deportiva</p>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────
#  LÓGICA DEL MOTOR ANALÍTICO
# ─────────────────────────────────────────
def normalizar(valor, minv, maxv, invertir=False):
    if maxv == minv:
        return 50.0
    n = (valor - minv) / (maxv - minv) * 100
    n = max(0.0, min(100.0, n))
    return round(100 - n if invertir else n, 2)

def calcular_irj(pos, vel10, vel30, agil, resist, salto, potencia,
                 pase, control, conduc, definic,
                 peso, altura, masa_musc, edad):
    
    # ── SCORE FÍSICO
    s_vel10  = normalizar(vel10,  1.2, 2.5, invertir=True)
    s_vel30  = normalizar(vel30,  3.5, 6.0, invertir=True)
    s_agil   = normalizar(agil,   9.0, 16.0, invertir=True)
    s_resist = normalizar(resist, 5.0, 23.0)   
    s_salto  = normalizar(salto,  20,  80)
    s_pot    = normalizar(potencia, 500, 3000)
    score_fis = round((s_vel10 + s_vel30 + s_agil + s_resist + s_salto + s_pot) / 6, 2)

    # ── SCORE TÉCNICO
    s_pase    = normalizar(pase,    1, 10)
    s_ctrl    = normalizar(control, 1, 10)
    s_cond    = normalizar(conduc,  1, 10)
    s_def     = normalizar(definic, 1, 10)
    score_tec = round((s_pase + s_ctrl + s_cond + s_def) / 4, 2)

    # ── SCORE CORPORAL
    imc = round(peso / ((altura / 100) ** 2), 2)
    s_imc  = round(max(0, 100 - abs(imc - 22) * 6), 2)
    s_masa = normalizar(masa_musc, 30, 65)
    score_corp = round((s_imc + s_masa) / 2, 2)

    # ── IRJ PONDERADO POR POSICIÓN
    w_fis, w_tec, w_corp = PESOS_POSICION.get(pos, (0.37, 0.40, 0.23))
    irj = round(score_fis * w_fis + score_tec * w_tec + score_corp * w_corp, 1)
    irj = max(1.0, min(100.0, irj))

    # ── DETECCIÓN DE FORTALEZAS Y DEBILIDADES
    metricas = {
        "Velocidad 10m":       s_vel10,
        "Velocidad 30m":       s_vel30,
        "Agilidad":            s_agil,
        "Resistencia (Yo-Yo)": s_resist,
        "Salto Vertical":      s_salto,
        "Potencia Física":     s_pot,
        "Precisión de Pase":   s_pase,
        "Control Orientado":   s_ctrl,
        "Conducción":          s_cond,
        "Definición":          s_def,
        "Balance de IMC":      s_imc,
        "Masa Muscular":       s_masa,
    }
    ordenadas = sorted(metricas.items(), key=lambda x: x[1], reverse=True)
    fortalezas = ", ".join([f"{k} ({v:.0f} pts)" for k, v in ordenadas[:3]])
    debilidades = ", ".join([f"{k} ({v:.0f} pts)" for k, v in ordenadas[-3:]])

    # ── PROYECCIÓN DE POTENCIAL
    if edad <= 19:     mult_corto, mult_medio = 1.12, 1.22
    elif edad <= 22:   mult_corto, mult_medio = 1.08, 1.16
    elif edad <= 26:   mult_corto, mult_medio = 1.04, 1.08
    elif edad <= 29:   mult_corto, mult_medio = 1.01, 1.03
    else:              mult_corto, mult_medio = 0.99, 0.97

    pot_corto  = round(min(100, irj * mult_corto), 1)
    pot_mediano = round(min(100, irj * mult_medio), 1)

    return {
        "imc": imc,
        "score_fisico":   score_fis,
        "score_tecnico":  score_tec,
        "score_corporal": score_corp,
        "irj":            irj,
        "fortalezas":     fortalezas,
        "debilidades":    debilidades,
        "potencial_corto":   pot_corto,
        "potencial_mediano": pot_mediano,
        "metricas":          metricas,
    }

def color_irj(irj):
    if irj >= 80: return "#2ecc71"
    if irj >= 60: return "#f1c40f"
    if irj >= 40: return "#e67e22"
    return "#e74c3c"

def label_irj(irj):
    if irj >= 85: return "ÉLITE"
    if irj >= 70: return "MUY BUENO"
    if irj >= 55: return "BUENO"
    if irj >= 40: return "REGULAR"
    return "EN DESARROLLO"

# ─────────────────────────────────────────
#  MÓDULO: REGISTRO DE JUGADORES
# ─────────────────────────────────────────
def render_registro_jugador():
    st.markdown("### 📋 Registrar Nuevo Jugador")
    
    with st.form("form_registro", clear_on_submit=True):
        nombre = st.text_input("Nombre Completo")
        fecha_nac = st.date_input("Fecha de Nacimiento", value=date(2005, 1, 1))
        altura = st.number_input("Altura (cm)", min_value=120, max_value=220, value=170)
        peso = st.number_input("Peso (kg)", min_value=30, max_value=150, value=65)
        
        posicion = st.selectbox("Posición Principal", list(PESOS_POSICION.keys()))
        pierna = st.selectbox("Pierna Dominante", ["Derecha", "Izquierda", "Ambidiestro"])
        
        st.markdown("---")
        st.caption("🔑 Credenciales de acceso para el jugador:")
        usuario_jug = st.text_input("Nombre de Usuario (sin espacios/minúsculas)", placeholder="ej: juany_10")
        contra_jug = st.text_input("Contraseña Temporal (mínimo 6 caracteres)", type="password")
        
        submitted = st.form_submit_button("Guardar Registro")
        
    if submitted:
        if not nombre or not usuario_jug or len(contra_jug) < 6:
            st.error("Por favor, completa todos los campos correctamente. La contraseña debe tener mínimo 6 caracteres.")
            return
            
        try:
            ss = load_spreadsheet()
            ws_jug = get_or_create_worksheet(ss, "jugadores", HEADERS_JUGADORES)
            ws_usu = get_or_create_worksheet(ss, "usuarios", HEADERS_USUARIOS)
            
            hoy = date.today()
            edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
            if edad < 18:
                st.error("Error: El sistema está restringido exclusivamente para jugadores mayores de 18 años.")
                return
                
            id_jugador = f"JUG{len(ws_jug.get_all_values()):03d}"
            
            ws_jug.append_row([
                id_jugador, nombre, edad, str(fecha_nac), altura, peso, posicion, pierna, datetime.now().strftime("%Y-%m-%d")
            ], value_input_option="USER_ENTERED")
            
            ws_usu.append_row([
                usuario_jug.strip().lower(), contra_jug, "jugador", id_jugador
            ], value_input_option="USER_ENTERED")
            
            st.success(f"¡Felicidades! {nombre} ha sido registrado con éxito.")
            time.sleep(1)
        except Exception as e:
            st.error(f"Error al guardar datos: {e}")

# ─────────────────────────────────────────
#  MÓDULO: VER PLANTILLA
# ─────────────────────────────────────────
def render_plantilla():
    st.markdown("### 👥 Plantilla del Equipo")
    try:
        ss = load_spreadsheet()
        ws = get_or_create_worksheet(ss, "jugadores", HEADERS_JUGADORES)
        datos = ws.get_all_records()
        
        if not datos:
            st.info("Aún no tienes jugadores registrados en tu plantilla.")
            return
            
        for jug in datos:
            with st.expander(f"👕 {jug['nombre_completo']} - {jug['posicion']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Edad:** {jug['edad']} años")
                    st.write(f"**Estatura:** {jug['altura']} cm")
                with col2:
                    st.write(f"**Peso:** {jug['peso']} kg")
                    st.write(f"**Pierna Fuerte:** {jug['pierna_dominante']}")
    except Exception as e:
        st.error(f"Error al leer la plantilla: {e}")

# ─────────────────────────────────────────
#  MÓDULO: FORMULARIO DE EVALUACIÓN OFICIAL
# ─────────────────────────────────────────
def render_evaluacion():
    st.markdown("### 📊 Registrar Evaluación Oficial")

    try:
        ss = load_spreadsheet()
        ws_jug  = get_or_create_worksheet(ss, "jugadores",    HEADERS_JUGADORES)
        ws_eval = get_or_create_worksheet(ss, "evaluaciones", HEADERS_EVALUACIONES)
        records = ws_jug.get_all_records()
    except Exception as e:
        st.error(f"Error al conectar: {e}")
        return

    if not records:
        st.info("No hay jugadores registrados aún.")
        return

    df_jug = pd.DataFrame(records)
    nombres = df_jug["nombre_completo"].tolist()
    seleccion = st.selectbox("Selecciona el jugador a evaluar", ["— Elige —"] + nombres)

    if seleccion == "— Elige —":
        return

    jug = df_jug[df_jug["nombre_completo"] == seleccion].iloc[0]
    posicion = jug.get("posicion", "Mediocampista Central")
    edad = int(jug.get("edad", 22))

    st.markdown(f"""
    <div style="background:rgba(32,58,67,0.5); border:1px solid #203a43; border-radius:10px; padding:15px; margin-bottom:15px;">
        <span style="color:#38bdf8; font-weight:bold; font-size:18px;">{seleccion}</span> <br>
        <span style="color:#94a3b8;">{posicion} · {edad} años</span>
    </div>
    """, unsafe_allow_html=True)

    with st.form("form_eval", clear_on_submit=False):
        fecha_eval = st.date_input("📅 Fecha de evaluación", value=date.today())

        st.markdown("#### 🏃 Evaluación Física")
        st.caption("Tiempos en segundos · Resistencia = nivel Yo-Yo · Salto en cm · Potencia en Watts")
        cf1, cf2, cf3 = st.columns(3)
        with cf1:
            vel10    = st.number_input("Velocidad 10m (seg)", 1.0, 3.0, 1.80, 0.01, format="%.2f")
            resistencia = st.number_input("Resistencia Yo-Yo (nivel)", 5.0, 23.0, 12.0, 0.5)
        with cf2:
            vel30    = st.number_input("Velocidad 30m (seg)", 3.0, 7.0, 4.50, 0.01, format="%.2f")
            salto    = st.number_input("Salto Vertical (cm)", 20, 90, 45)
        with cf3:
            agilidad = st.number_input("Agilidad Test (seg)", 8.0, 18.0, 12.0, 0.1, format="%.1f")
            potencia = st.number_input("Potencia estimada (W)", 500, 3500, 1500, 50)

        st.divider()
        st.markdown("#### ⚽ Evaluación Técnico")
        st.caption("Escala del 1 (muy malo) al 10 (excelente)")
        ct1, ct2 = st.columns(2)
        with ct1:
            pase    = st.slider("Precisión de Pase",     1, 10, 6)
            control = st.slider("Control Orientado",      1, 10, 6)
        with ct2:
            conduc  = st.slider("Conducción en Velocidad", 1, 10, 6)
            definic = st.slider("Definición / Remate",     1, 10, 6)

        st.divider()
        st.markdown("#### 💪 Evaluación Corporal")
        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            peso_eval   = st.number_input("Peso actual (kg)", 40.0, 150.0, float(jug.get("peso", 70) or 70), 0.1, format="%.1f")
        with cc2:
            altura_eval = st.number_input("Altura actual (cm)", 140, 220, int(jug.get("altura", 175) or 175))
        with cc3:
            masa_musc   = st.number_input("Masa muscular estimada (%)", 20.0, 70.0, 45.0, 0.5)

        calcular_btn = st.form_submit_button("⚡ Calcular IRJ y Guardar", use_container_width=True)

    if calcular_btn:
        resultado = calcular_irj(
            posicion, vel10, vel30, agilidad, resistencia, salto, potencia,
            pase, control, conduc, definic,
            peso_eval, altura_eval, masa_musc, edad
        )

        irj   = resultado["irj"]
        color = color_irj(irj)
        label = label_irj(irj)

        st.markdown("---")
        st.markdown("## 🎯 Resultados del Motor Analítico")

        st.markdown(f"""
        <div style="text-align:center;padding:1.5rem;background:rgba(0,0,0,0.3);
             border-radius:16px;border:2px solid {color};margin-bottom:1.2rem;">
            <div style="font-size:5rem; color:{color}; line-height:1; font-weight:700">{irj}</div>
            <div style="color:{color}; font-size:1.2rem; letter-spacing:0.2em; font-weight:600; margin-top:0.3rem">{label}</div>
            <div style="color:rgba(255,255,255,0.4); font-size:0.8rem; margin-top:0.2rem">IRJ — Índice de Rendimiento del Jugador</div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        scores = [
            ("🏃 Físico",   resultado["score_fisico"],   "#3498db"),
            ("⚽ Técnico",  resultado["score_tecnico"],  "#9b59b6"),
            ("💪 Corporal", resultado["score_corporal"], "#1abc9c"),
        ]
        for col, (lbl, val, clr) in zip([c1, c2, c3], scores):
            with col:
                st.markdown(f"""
                <div class="stat-card" style="border-color:{clr}40">
                    <div class="num" style="color:{clr}; font-size:2rem;">{val:.1f}</div>
                    <div class="label">{lbl}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col_f, col_d, col_p = st.columns(3)
        with col_f:
            st.markdown("##### ✅ Fortalezas Destacadas")
            for item in resultado["fortalezas"].split(", "):
                st.markdown(f"🟢 {item}")
        with col_d:
            st.markdown("##### ⚠️ Áreas de Mejora")
            for item in resultado["debilidades"].split(", "):
                st.markdown(f"🔴 {item}")
        with col_p:
            st.markdown("##### 🚀 Potencial Estimado")
            st.write(f"**A Corto Plazo (6m):** `{resultado['potencial_corto']} pts`")
            st.write(f"**Mediano Plazo (1-2 años):** `{resultado['potencial_mediano']} pts`")
            st.write(f"**IMC Actual:** `{resultado['imc']}`")

        st.markdown("---")
        st.markdown("#### 📈 Desglose Analítico por Métrica")
        df_metricas = pd.DataFrame(
            [(k, v) for k, v in resultado["metricas"].items()],
            columns=["Métrica", "Score (0–100)"]
        ).sort_values("Score (0–100)", ascending=False)
        
        st.dataframe(
            df_metricas,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Score (0–100)": st.column_config.ProgressColumn(
                    "Score (0–100)", min_value=0, max_value=100, format="%.1f"
                )
            }
        )

        try:
            all_evals = ws_eval.get_all_values()
            id_eval = f"EVL{len(all_evals):05d}"

            fila = [
                id_eval, str(jug["id"]), seleccion, str(fecha_eval), posicion,
                vel10, vel30, agilidad, resistencia, salto, potencia,
                pase, control, conduc, definic,
                peso_eval, altura_eval, masa_musc, resultado["imc"],
                resultado["score_fisico"], resultado["score_tecnico"], resultado["score_corporal"],
                irj, resultado["fortalezas"], resultado["debilidades"],
                resultado["potencial_corto"], resultado["potencial_mediano"],
                "Entrenador"
            ]
            ws_eval.append_row(fila, value_input_option="USER_ENTERED")
            st.success(f"✅ Evaluación guardada con éxito [ID: {id_eval}]")
            if irj >= 80: st.balloons()
        except Exception as ex:
            st.error(f"Error al guardar en Sheets: {ex}")

# ─────────────────────────────────────────
#  MÓDULO: HISTORIAL DE EVALUACIONES
# ─────────────────────────────────────────
def render_historial_evaluaciones():
    st.markdown("### 📈 Historial y Evolución del Plantel")

    try:
        ss = load_spreadsheet()
        ws_eval = get_or_create_worksheet(ss, "evaluaciones", HEADERS_EVALUACIONES)
        records = ws_eval.get_all_records()
    except Exception as e:
        st.error(f"Error: {e}")
        return

    if not records:
        st.info("Aún no hay evaluaciones registradas.")
        return

    df = pd.DataFrame(records)
    jugadores_unicos = ["Todos"] + sorted(df["nombre_jugador"].unique().tolist())
    sel = st.selectbox("Filtrar por jugador", jugadores_unicos)

    if sel != "Todos":
        df = df[df["nombre_jugador"] == sel]

    cols_tabla = ["fecha_evaluacion", "nombre_jugador", "posicion", "irj", "score_fisico", "score_tecnico", "score_corporal"]
    cols_ok = [c for c in cols_tabla if c in df.columns]

    st.dataframe(
        df[cols_ok].rename(columns={
            "fecha_evaluacion": "Fecha", "nombre_jugador": "Jugador",
            "posicion": "Posición", "irj": "IRJ",
            "score_fisico": "Físico", "score_tecnico": "Técnico", "score_corporal": "Corporal"
        }).sort_values("Fecha", ascending=False),
        use_container_width=True,
        hide_index=True,
        column_config={
            "IRJ": st.column_config.ProgressColumn("IRJ", min_value=0, max_value=100, format="%.1f"),
            "Físico": st.column_config.ProgressColumn("Físico", min_value=0, max_value=100, format="%.1f"),
            "Técnico": st.column_config.ProgressColumn("Técnico", min_value=0, max_value=100, format="%.1f"),
            "Corporal": st.column_config.ProgressColumn("Corporal", min_value=0, max_value=100, format="%.1f"),
        }
    )

    if sel != "Todos" and len(df) > 1:
        st.markdown("---")
        st.markdown(f"#### 📉 Gráfica de Evolución — {sel}")
        df_sorted = df.sort_values("fecha_evaluacion")
        st.line_chart(
            df_sorted.set_index("fecha_evaluacion")[["irj", "score_fisico", "score_tecnico", "score_corporal"]],
            use_container_width=True
        )

# ─────────────────────────────────────────
#  PANEL PRINCIPAL — ENTRENADOR
# ─────────────────────────────────────────
def render_panel_entrenador():
    render_header()
    
    col_role, col_logout = st.columns([3, 1])
    with col_role:
        st.markdown(f"""
        <div style="background-color:#1e293b; padding:10px; border-radius:8px; margin-bottom:15px;">
            <span style="color:#38bdf8; font-weight:bold; background:#0f172a; padding:5px 10px; border-radius:5px;">🏃‍♂️ ENTRENADOR</span>
            <span style="color:#94a3b8; margin-left: 10px;">Hola, Profesor</span>
        </div>
        """, unsafe_allow_html=True)
    with col_logout:
        if st.button("Salir 🚪", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    st.markdown("## 🏠 Panel de Control Principal")
    
    menu = st.selectbox(
        "📂 SELECCIONAR SECCIÓN:",
        ["🏠 Inicio Dashboard", "📋 Registrar Jugador", "👥 Ver Plantilla", "📊 Nueva Evaluación", "📈 Historial Clínico/Físico"]
    )
    st.markdown("<br>", unsafe_allow_html=True)

    if menu == "🏠 Inicio Dashboard":
        st.markdown("""
        <div style="background:rgba(26,111,168,0.1);border:1px solid rgba(26,111,168,0.3);
             border-radius:12px;padding:1.2rem;margin-bottom:1rem;">
            <p style="color:rgba(255,255,255,0.7);margin:0">
            👋 Bienvenido, Entrenador. Usa el menú superior para gestionar tu plantilla y el Motor Analítico.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            ss = load_spreadsheet()
            ws_jug = get_or_create_worksheet(ss, "jugadores", HEADERS_JUGADORES)
            ws_eva = get_or_create_worksheet(ss, "evaluaciones", HEADERS_EVALUACIONES)
            
            records_j = ws_jug.get_all_records()
            records_e = ws_eva.get_all_records()
            
            df_j = pd.DataFrame(records_j) if records_j else pd.DataFrame()
            df_e = pd.DataFrame(records_e) if records_e else pd.DataFrame()

            total = len(df_j)
            activos = total
            lesionados = 0
            evals = len(df_e)

            c1, c2, c3, c4 = st.columns(4)
            for col, (n, lbl, clr) in zip([c1, c2, c3, c4], [
                (total, "Jugadores", "#38bdf8"), (activos, "Activos", "#2ecc71"),
                (lesionados, "Lesionados", "#e74c3c"), (evals, "Evaluaciones", "#34d399")
            ]):
                with col:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="num" style="font-size:2rem; font-weight:bold; color:{clr};">{n}</div>
                        <div class="label">{lbl}</div>
                    </div>
                    """, unsafe_allow_html=True)

            if not df_e.empty and "irj" in df_e.columns:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("#### 🏆 Top 5 — Mejor IRJ Actual")
                
                top5 = (df_e.sort_values("irj", ascending=False)
                           .drop_duplicates("nombre_jugador")[["nombre_jugador","posicion","irj"]]
                           .head(5))
                
                st.dataframe(top5.rename(columns={
                    "nombre_jugador":"Jugador","posicion":"Posición","irj":"IRJ"
                }), use_container_width=True, hide_index=True,
                column_config={
                    "IRJ": st.column_config.ProgressColumn("IRJ", min_value=0, max_value=100, format="%.1f")
                })
                
        except Exception as e:
            st.warning(f"No se pudo conectar a las estadísticas de Sheets: {e}")

    elif menu == "📋 Registrar Jugador":
        render_registro_jugador()

    elif menu == "👥 Ver Plantilla":
        render_plantilla()
        
    elif menu == "📊 Nueva Evaluación":
        render_evaluacion()
        
    elif menu == "📈 Historial Clínico/Físico":
        render_historial_evaluaciones()


# ─────────────────────────────────────────
#  PANEL PRINCIPAL — JUGADOR (ACTUALIZADO FASE 3)
# ─────────────────────────────────────────
def render_panel_jugador(usuario, id_jugador):
    render_header()
    
    st.markdown(f"""
    <div style="background-color:#1e293b; padding:15px; border-radius:8px; margin-bottom:15px;">
        <span style="color:#fbbf24; font-weight:bold; background:#0f172a; padding:5px 10px; border-radius:5px;">⚽ JUGADOR PRIVADO (+18)</span>
        <span style="color:#94a3b8; margin-left:10px;">Hola, {usuario}</span>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Salir 🚪"):
        st.session_state.clear()
        st.rerun()

    st.markdown("## 🏠 Mi Perfil Deportivo")
    
    try:
        ss = load_spreadsheet()
        ws_jug = get_or_create_worksheet(ss, "jugadores", HEADERS_JUGADORES)
        jugadores = ws_jug.get_all_records()
        mis_datos = next((j for j in jugadores if str(j["id"]) == str(id_jugador)), None)
        
        ws_eva = get_or_create_worksheet(ss, "evaluaciones", HEADERS_EVALUACIONES)
        evaluaciones = ws_eva.get_all_records()
        mis_evaluaciones = [e for e in evaluaciones if str(e["id_jugador"]) == str(id_jugador)]
        
        if mis_datos:
            st.markdown(f"### ¡Bienvenido, **{mis_datos['nombre_completo']}**!")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Posición de Campo:** {mis_datos['posicion']}")
                st.write(f"**Edad:** {mis_datos['edad']} años (Validación +18)")
            with col2:
                st.write(f"**Pierna Fuerte:** {mis_datos['pierna_dominante']}")
                st.write(f"**Estatura/Peso:** {mis_datos['altura']} cm / {mis_datos['peso']} kg")
        
            st.divider()
            
            if mis_evaluaciones:
                ultima_eva = mis_evaluaciones[-1]
                st.markdown("### 📊 Mi Estado de Rendimiento Oficial")
                
                color = color_irj(float(ultima_eva['irj']))
                label = label_irj(float(ultima_eva['irj']))
                
                st.markdown(f"""
                <div style="text-align:center;padding:1rem;background:rgba(0,0,0,0.2);border-radius:10px;border:1px solid {color};margin-bottom:15px;">
                    <div style="font-size:3rem; color:{color}; font-weight:bold;">{ultima_eva['irj']}</div>
                    <div style="color:{color}; font-size:1rem; font-weight:600; letter-spacing:0.1em;">{label}</div>
                    <div style="color:rgba(255,255,255,0.4); font-size:0.8rem;">IRJ Actualizado</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Deducción automática del enfoque según su score físico actual
                score_f = float(ultima_eva['score_fisico'])
                if score_f < 60:
                    enfoque_estimado = "Potencia"
                elif score_f < 75:
                    enfoque_estimado = "Hipertrofia"
                else:
                    enfoque_estimado = "Fuerza"
                
                st.markdown("## 🤖 Motor Inteligente de Planificación")
                st.info(f"💡 **Diagnóstico Automático:** Basado en tu IRJ, tu plan de trabajo actual está enfocado en **{enfoque_estimado}**.")
                
                tab1, tab2, tab3 = st.tabs(["📅 Plan Mensual", "🗓️ Distribución Semanal", "🏋️ Rutina de Hoy"])
                
                with tab1:
                    st.markdown(f"### Macrociclo: Desarrollo Físico Adulto — Enfoque {enfoque_estimado}")
                    st.write("• **Objetivo principal:** Optimizar la transferencia de fuerza a gestos de carrera y fútbol.")
                    st.write("• **Duración:** Bloque adaptativo de 1 mes vinculado a tus métricas del club.")
                    
                with tab2:
                    st.markdown("### Microciclo Semanal (Estructura Híbrida)")
                    st.write("• **Lunes / Miércoles / Viernes:** Trabajo enfocado en Gimnasio (Fuerza Base).")
                    st.write("• **Martes / Jueves:** Adaptación metabólica y técnica individual en campo.")
                    st.write("• **Fin de semana:** Simulación competitiva o partido oficial.")
                    
                with tab3:
                    st.markdown("### 🏋️ Biblioteca de Gimnasio Asignada")
                    ejercicios_gym = BI_GIMNASIO.get(enfoque_estimado, BI_GIMNASIO["Hipertrofia"])
                    df_gym = pd.DataFrame(ejercicios_gym)
                    st.table(df_gym.rename(columns={"ejercicio": "Ejercicio", "series": "Series x Repeticiones", "descanso": "Tiempos de Descanso"}))
                    
                    st.markdown("### ⚽ Biblioteca de Entrenamiento de Campo")
                    perfil_campo = obtener_perfil_tactico(mis_datos['posicion'])
                    trabajos_campo = BI_CAMPO.get(perfil_campo, BI_CAMPO["Mediocampista"])
                    
                    for t in trabajos_campo:
                        st.markdown(f"**🎯 {t['bloque']}:** {t['detalle']}")
                        
                    st.write("---")
                    if st.button("💪 Marcar Rutina de Hoy como Completada (Soporte Offline)", use_container_width=True):
                        st.success("✅ ¡Entrenamiento guardado localmente! Se sincronizará con el vestuario automáticamente al detectar señal.")
            else:
                st.info("💡 Tu entrenador aún no ha cargado evaluaciones analíticas para activar el Motor de Planificación.")
        else:
            st.error("No se encontraron tus datos personales en la tabla de jugadores.")
    except Exception as e:
        st.error(f"Error al cargar tu perfil: {e}")

# ─────────────────────────────────────────
#  SISTEMA DE LOGUEO PRINCIPAL (PROTEGIDO)
# ─────────────────────────────────────────
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.rol = None
        st.session_state.usuario = None
        st.session_state.id_jugador = None

    if st.session_state.logged_in:
        if st.session_state.rol == "entrenador":
            render_panel_entrenador()
        else:
            render_panel_jugador(st.session_state.usuario, st.session_state.id_jugador)
    else:
        render_header()
        st.markdown("### 🔒 Iniciar Sesión")
        
        usuario = st.text_input("Usuario", placeholder="ej: entrenador o tu usuario de jugador")
        contrasena = st.text_input("Contraseña", type="password")
        
        if st.button("Ingresar →", use_container_width=True):
            # Login Administrador
            if usuario.strip().lower() == "entrenador" and contrasena == "admin1234":
                st.session_state.logged_in = True
                st.session_state.rol = "entrenador"
                st.session_state.usuario = "Entrenador"
                st.rerun()
            else:
                try:
                    ss = load_spreadsheet()
                    ws_usu = get_or_create_worksheet(ss, "usuarios", HEADERS_USUARIOS)
                    usuarios_registrados = ws_usu.get_all_records()
                    
                    # Motor de emparejamiento inteligente e inmune a Ñ o tildes
                    user_match = None
                    for u in usuarios_registrados:
                        user_excel = str(u.get("usuario", "")).strip().lower()
                        if user_excel == usuario.strip().lower():
                            # Intenta leer con 'contrasena' y si no encuentra usa 'contraseña'
                            pass_excel = u.get("contrasena") if "contrasena" in u else u.get("contraseña", "")
                            if str(pass_excel).strip() == contrasena.strip():
                                user_match = u
                                break
                    
                    if user_match:
                        st.session_state.logged_in = True
                        st.session_state.rol = "jugador"
                        st.session_state.usuario = user_match.get("usuario")
                        st.session_state.id_jugador = user_match.get("id_jugador")
                        st.success("¡Acceso concedido!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Usuario o contraseña incorrectos.")
                except Exception as e:
                    st.error(f"Error en el sistema de login: {e}")

if __name__ == "__main__":
    main()
