# aplicacion.py
import streamlit as st
from streamlit_option_menu import option_menu
import config
import utils
from datetime import datetime

st.markdown(config.CSS_ESTILOS, unsafe_allow_html=True)

# Inicializar estados de la sesión
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
    st.session_state['usuario'] = None
    st.session_state['rol'] = None
    st.session_state['id_jugador'] = None

# --- PANTALLA DE ACCESO (LOGIN DE LA RESTRICCIÓN ABIERTA) ---
if not st.session_state['autenticado']:
    st.title("⚽ Los Troncos FC - Sistema Cerrado")
    st.subheader("Acceso Restringido - Mayores de 18 años")
    
    usuario_input = st.text_input("Usuario / Jugador")
    clave_input = st.text_input("Contraseña", type="password")
    
    if st.button("Ingresar al Vestuario"):
        # Cuenta maestra del Entrenador
        if usuario_input.strip().lower() == "entrenador" and clave_input == "admin1234":
            st.session_state['autenticado'] = True
            st.session_state['usuario'] = "Entrenador Principal"
            st.session_state['rol'] = "Entrenador"
            st.success("¡Bienvenido Profe! Iniciando Centro de Mando...")
            st.rerun()
        # Cuenta por defecto de emergencia solicitada
        elif usuario_input.strip().lower() == "admin" and clave_input == "1234":
            st.session_state['autenticado'] = True
            st.session_state['usuario'] = "Administrador"
            st.session_state['rol'] = "Entrenador"
            st.rerun()
        else:
            # Validación e inicio de sesión desde Google Sheets para Jugadores
            try:
                df_usuarios = utils.get_data_from_sheet("usuarios")
                usuario_row = df_usuarios[df_usuarios['usuario'].astype(str).str.strip().str.lower() == usuario_input.strip().lower()]
                
                if not usuario_row.empty:
                    hash_guardado = usuario_row.iloc[0]['contrasena']
                    if utils.check_password(clave_input, str(hash_guardado)):
                        st.session_state['autenticado'] = True
                        st.session_state['usuario'] = usuario_row.iloc[0]['usuario']
                        st.session_state['rol'] = usuario_row.iloc[0]['rol']
                        st.session_state['id_jugador'] = usuario_row.iloc[0]['id_jugador']
                        st.rerun()
                    else:
                        st.error("Contraseña incorrecta.")
                else:
                    st.error("El usuario no está registrado en el plantel.")
            except Exception:
                st.error("Error de sincronización con la base de datos.")

else:
    # --- INTERFAZ DEL ENTRENADOR (CENTRO DE MANDO GLOBAL) ---
    if st.session_state['rol'] == "Entrenador":
        st.sidebar.title("👨‍🏫 Centro de Mando")
        st.sidebar.write(f"Usuario: {st.session_state['usuario']}")
        
        seleccion = option_menu(
            menu_title="Los Troncos FC - Panel Técnico",
            options=["Plantilla", "Evaluación Oficial", "Scouting Interno", "Planificación IA"],
            icons=["people", "calculator", "search", "robot"],
            menu_icon="cone-striped",
            orientation="horizontal"
        )
        
        if seleccion == "Plantilla":
            st.header("👤 Registro e Historial de Plantilla (+18)")
            
            # Formulario de alta de jugadores
            with st.form("alta_jugador"):
                st.subheader("Registrar Nuevo Futbolista")
                c1, c2 = st.columns(2)
                with c1:
                    id_j = st.text_input("ID Jugador (Ej: T01)")
                    nombre = st.text_input("Nombre Completo")
                    edad = st.number_input("Edad (Validación +18 obligatoria)", min_value=18, max_value=50, value=20)
                with c2:
                    posicion = st.selectbox("Posición Principal", ["Arquero", "Defensa", "Mediocampista", "Delantero"])
                    pierna = st.selectbox("Pierna Dominante", ["Derecha", "Izquierda", "Ambidiestro"])
                
                if st.form_submit_button("Dar de Alta en el Plantel"):
                    if id_j and nombre:
                        ws = utils.get_sheet_connection("jugadores")
                        ws.append_row([id_j, nombre, int(edad), "", "", "", posicion, pierna, str(datetime.now().date())])
                        st.cache_data.clear()
                        st.success(f"{nombre} ha sido integrado con éxito.")
                        st.rerun()
            
            st.markdown("---")
            try:
                st.subheader("Lista del Plantel Actual")
                st.dataframe(utils.get_data_from_sheet("jugadores"), use_container_width=True)
            except:
                st.info("Pestaña 'jugadores' vacía o no encontrada.")

        elif seleccion == "Evaluación Oficial":
            st.header("📊 Ingreso de Tests Oficiales y Motor Analítico")
            
            try:
                df_j = utils.get_data_from_sheet("jugadores")
                lista_jugadores = df_j['nombre_completo'].tolist()
                id_map = dict(zip(df_j['nombre_completo'], df_j['id']))
                
                if lista_jugadores:
                    j_seleccionado = st.selectbox("Seleccionar Jugador para Evaluar", lista_jugadores)
                    id_actual = id_map[j_seleccionado]
                    
                    with st.form("eval_form"):
                        st.subheader("Métricas Físicas y Corporales")
                        f1, f2 = st.columns(2)
                        with f1:
                            peso = st.number_input("Peso Actual (kg)", value=70.0)
                            vel10 = st.slider("Velocidad 10m (Puntaje 1-100)", 1, 100, 70)
                            agilidad = st.slider("Test de Agilidad (Puntaje 1-100)", 1, 100, 70)
                        with f2:
                            altura = st.number_input("Altura Actual (cm)", value=175.0)
                            vel30 = st.slider("Velocidad 30m (Puntaje 1-100)", 1, 100, 70)
                            resis = st.slider("Resistencia (Yo-Yo Test 1-100)", 1, 100, 70)
                        
                        st.subheader("Métricas Técnicas y Actitud")
                        t1, t2 = st.columns(2)
                        with t1:
                            pase = st.slider("Precisión de Pase", 1, 100, 70)
                            conduccion = st.slider("Conducción en Velocidad", 1, 100, 70)
                        with t2:
                            control = st.slider("Control Orientado", 1, 100, 70)
                            definicion = st.slider("Definición / Remate", 1, 100, 70)
                        
                        mental = st.slider("🧠 Mentalidad y Actitud (Evaluación DT)", 1, 100, 80)
                        
                        st.subheader("🔍 Proyección (Scouting Interno)")
                        proyeccion = st.selectbox("Rol Proyectado en Plantilla", ["Titular", "Rotación", "Jugador a desarrollar"])
                        estrellas = st.slider("Potencial Estimado", 1, 5, 3)
                        
                        if st.form_submit_button("Calcular e Inyectar Evaluación"):
                            # Empaquetar datos para el motor analítico de utils.py
                            datos = {
                                "peso_eval": peso, "altura_eval": altura, "vel_10m": vel10, "vel_30m": vel30,
                                "agilidad": agilidad, "resistencia": resis, "salto_vertical": 70,
                                "precision_pase": pase, "control_orientado": control, "conduccion": conduccion,
                                "definicion": definicion, "score_mental_dt": mental
                            }
                            imc, s_fis, s_tec, irj = utils.calcular_irj_e_imc(datos)
                            
                            # Guardar en Sheets
                            ws_eval = utils.get_sheet_connection("evaluaciones")
                            id_eval = f"E-{id_actual}-{int(datetime.now().timestamp())}"
                            ws_eval.append_row([
                                id_eval, id_actual, j_seleccionado, str(datetime.now().date()), "Fútbol",
                                vel10, vel30, agilidad, resis, 70, 70, pase, control, conduccion, definicion,
                                peso, altura, 0, imc, s_fis, s_tec, mental, irj, proyeccion, estrellas
                            ])
                            st.cache_data.clear()
                            st.success(f"¡Evaluación completada! El IRJ procesado para {j_seleccionado} es **{irj}**")
                else:
                    st.warning("Primero debes dar de alta jugadores en la pestaña Plantilla.")
            except Exception as e:
                st.error("Crea la pestaña 'evaluaciones' en tu Google Sheet con sus headers.")

        elif seleccion == "Scouting Interno":
            st.header("🔍 Matriz de Scouting Interno - Exclusivo DT")
            try:
                df_ev = utils.get_data_from_sheet("evaluaciones")
                if not df_ev.empty:
                    # Mostrar rankings por IRJ, Proyecciones y Estrellas
                    st.subheader("Ranking de Competencia Sana (Ordenado por IRJ de Élite)")
                    df_ranking = df_ev[["nombre_jugador", "irj", "proyeccion", "potencial_estrellas", "imc"]].sort_values(by="irj", ascending=False)
                    st.dataframe(df_ranking, use_container_width=True)
                else:
                    st.info("No hay evaluaciones registradas para generar la matriz de scouting.")
            except:
                st.error("Error al cargar la base de datos de scouting.")

        elif seleccion == "Planificación IA":
            st.header("🤖 Motor Inteligente de Planificación de Cargas")
            pos = st.selectbox("Posición a Planificar", ["Defensa", "Mediocampista", "Delantero"])
            obj = st.selectbox("Objetivo del Microciclo", ["Hipertrofia", "Fuerza Máxima", "Potencia / Pliometría", "Velocidad Punta"])
            dias = st.slider("Días disponibles a la semana", 1, 7, 4)
            
            if st.button("Generar Macro/Microciclo Automático"):
                with st.spinner("Conectando con el motor de IA..."):
                    plan = utils.generar_plan_ia_duckduckgo(pos, 22, obj, dias)
                    st.markdown(plan)

    # --- INTERFAZ DEL JUGADOR (ACCESO PRIVADO Y PRIVACIDAD ABSOLUTA) ---
    elif st.session_state['rol'] == "jugador":
        st.title(f"⚽ Vestuario Virtual - Los Troncos FC")
        st.subheader(f"Panel de Jugador: {st.session_state['usuario']}")
        
        j_sel = option_menu(
            menu_title=None,
            options=["Mi Perfil e IRJ", "Check-in Wellness", "Biblioteca de Entrenamiento"],
            icons=["person-badge", "heart-pulse", "book"],
            orientation="horizontal"
        )
        
        if j_sel == "Mi Perfil e IRJ":
            st.header("📊 Tu Rendimiento Comparado")
            try:
                df_ev = utils.get_data_from_sheet("evaluaciones")
                mis_datos = df_ev[df_ev['id_jugador'] == st.session_state['id_jugador']]
                
                if not mis_datos.empty:
                    ultimo_test = mis_datos.iloc[-1]
                    st.metric("Tu Índice de Rendimiento (IRJ)", f"{ultimo_test['irj']} / 100")
                    
                    # Comparativa Intra-Equipo explicada en la arquitectura
                    promedio_equipo = df_ev['irj'].mean()
                    st.write(f"**Promedio del Plantel:** {round(promedio_equipo, 1)}")
                    if ultimo_test['irj'] >= promedio_equipo:
                        st.success("⭐ ¡Estás por encima del promedio del vestuario! Sigue compitiendo así.")
                    else:
                        st.warning("⚠️ Estás por debajo de la media física del equipo. Enfócate en tus debilidades.")
                else:
                    st.info("El Entrenador aún no ha ingresado tu primera evaluación oficial.")
            except:
                st.error("No se pudo cargar tu historial evolutivo.")
                
        elif j_sel == "Check-in Wellness":
            st.header("📅 Check-in Diario Wellness (30 Segundos)")
            with st.form("well"):
                sueno = st.slider("Calidad del Sueño (1 = Fatal, 5 = Excelente)", 1, 5, 3)
                dolor = st.slider("Dolor Muscular / Fatiga (1 = Sin dolor, 5 = Sobrecargado)", 1, 5, 2)
                energia = st.slider("Nivel de Energía (1 = Agotado, 5 = A tope)", 1, 5, 4)
                
                if st.form_submit_button("Enviar Reporte Diario"):
                    try:
                        ws = utils.get_sheet_connection("wellness")
                        ws.append_row([str(datetime.now().date()), st.session_state['id_jugador'], sueno, dolor, energia])
                        st.success("Reporte enviado. Los datos de sobreentrenamiento se han actualizado en el panel del DT.")
                    except:
                        st.error("Pestaña 'wellness' no encontrada en Sheets.")

        elif j_sel == "Biblioteca de Entrenamiento":
            st.header("💪 Biblioteca del Futbolista")
            st.subheader("Rutinas de Campo e Invisible de Gimnasio")
            st.info("Rutina del Día: Enfoque en Core, Estabilidad de Tobillo y Circuitos de Potencia Metabólica.")

    if st.sidebar.button("Salir del Vestuario"):
        st.session_state['autenticado'] = False
        st.rerun()
