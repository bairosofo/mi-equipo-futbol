# aplicacion.py
import streamlit as st
import config  # Importamos la despensa
import utils   # Importamos las funciones de lógica y datos

# Configuración básica de la página
st.set_page_config(page_title="Gestión de Equipo", layout="wide")

# Aplicamos los estilos visuales que guardamos en config.py
st.markdown(config.CSS_ESTILOS, unsafe_allow_html=True)

st.title("⚽ Panel de Control - Mi Equipo")

# Creamos dos pestañas en la aplicación
tab1, tab2 = st.tabs(["📋 Plantilla", "🔐 Prueba de Seguridad"])

with tab1:
    st.header("Lista de Jugadores Registrados")
    
    if st.button("🔄 Cargar / Actualizar Datos"):
        try:
            # Llamamos a la función de utils.py para traer la pestaña 'jugadores' de tu Google Sheet
            df_jugadores = utils.get_data_from_sheet("jugadores")
            st.dataframe(df_jugadores, use_container_width=True)
        except Exception as e:
            st.error("Falta configurar las credenciales de Google Sheets en Streamlit Cloud.")

with tab2:
    st.header("Demostración de Encriptación de Contraseñas")
    
    clave_usuario = st.text_input("Escribe una contraseña de prueba:", type="password")
    
    if clave_usuario:
        # Usamos las funciones de seguridad de utils.py
        clave_encriptada = utils.hash_password(clave_usuario)
        
        st.info(f"**Así se enviará a Google Sheets (Encriptada):** {clave_encriptada}")
        st.write("Aunque alguien robe tu cuenta de Google Sheets, jamás sabrá cuál era la clave original.")
