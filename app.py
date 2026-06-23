# aplicacion.py
import streamlit as st
from streamlit_option_menu import option_menu
import config
import utils

st.set_page_config(page_title="Los Troncos FC - Gestión", layout="wide")
st.markdown(config.CSS_ESTILOS, unsafe_allow_html=True)

# --- SISTEMA DE SESIÓN (LOGIN) ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
    st.session_state['usuario'] = None
    st.session_state['rol'] = None

if not st.session_state['autenticado']:
    st.title("⚽ Los Troncos FC - Iniciar Sesión")
    usuario_input = st.text_input("Usuario")
    clave_input = st.text_input("Contraseña", type="password")
    
    if st.button("Ingresar"):
        # --- ATAJO DIRECTO DE EMERGENCIA ---
        if usuario_input == "admin" and clave_input == "1234":
            st.session_state['autenticado'] = True
            st.session_state['usuario'] = "admin"
            st.session_state['rol'] = "Admin"
            st.success("¡Entrando como Administrador de emergencia!")
            st.rerun()
        else:
            # Si no usas el atajo, intenta buscar en el Excel por si acaso
            try:
                df_usuarios = utils.get_data_from_sheet("usuarios")
                usuario_row = df_usuarios[df_usuarios['usuario'] == usuario_input]
                
                if not usuario_row.empty:
                    hash_guardado = usuario_row.iloc[0]['contrasena']
                    if utils.check_password(clave_input, str(hash_guardado)):
                        st.session_state['autenticado'] = True
                        st.session_state['usuario'] = usuario_input
                        st.session_state['rol'] = usuario_row.iloc[0]['rol']
                        st.success(f"Bienvenido {usuario_input}")
                        st.rerun()
                    else:
                        st.error("Contraseña incorrecta")
                else:
                    st.error("El usuario no existe")
            except Exception as e:
                st.error("Error de conexión o credenciales no válidas.")

else:
    # --- MENÚ PRINCIPAL SEGÚN EL ROL (Tu diseño original) ---
    st.sidebar.title(f"Menu ({st.session_state['rol']})")
    
    opciones_menu = ["Inicio", "Plantilla", "Asistencia", "Rendimiento", "Planes IA"]
    if st.session_state['rol'] == 'Admin':
        opciones_menu.append("Configuración")
        
    seleccion = option_menu(
        menu_title="Los Troncos FC",
        options=opciones_menu,
        icons=["house", "people", "calendar-check", "activity", "robot", "gear"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal"
    )
    
    # --- RENDER DE PÁGINAS ---
    if seleccion == "Inicio":
        st.subheader(f"Bienvenido al panel de control de Los Troncos, {st.session_state['usuario']}.")
        
    elif seleccion == "Plantilla":
        st.header("📋 Gestión de Plantilla")
        df_jugadores = utils.get_data_from_sheet("jugadores")
        st.dataframe(df_jugadores, use_container_width=True)
        
    elif seleccion == "Asistencia":
        st.header("📅 Control de Asistencia")
        df_asistencia = utils.get_data_from_sheet("asistencia")
        st.dataframe(df_asistencia, use_container_width=True)
        
    elif seleccion == "Rendimiento":
        st.header("📊 Estadísticas e IRJ")
        df_rendimiento = utils.get_data_from_sheet("rendimiento")
        st.dataframe(df_rendimiento, use_container_width=True)

    elif seleccion == "Planes IA":
        st.header("🤖 Inteligencia Artificial")
        # Aquí puedes llamar a tu generador usando: utils.generar_plan_entrenamiento_ia(...)
        st.info("Espacio para la generación de entrenamientos inteligentes.")

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False
        st.rerun()
