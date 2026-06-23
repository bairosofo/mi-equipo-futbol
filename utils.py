# utils.py
import streamlit as st
import gspread
import bcrypt
from google.oauth2.service_account import Credentials
import pandas as pd
import requests
import json

# --- 1. SEGURIDAD (BCRYPT) ---
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        # Por si acaso quedan contraseñas viejas en texto plano en la base de datos
        return password == hashed

# --- 2. CONEXIÓN OPTIMIZADA (GOOGLE SHEETS) ---
@st.cache_data(ttl=600)
def get_data_from_sheet(sheet_name: str):
    creds_dict = st.secrets["gcp_service_account"]
    credentials = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    client = gspread.authorize(credentials)
    ss = client.open_by_key(st.secrets["spreadsheet_id"])
    ws = ss.worksheet(sheet_name)
    return pd.DataFrame(ws.get_all_records())

def get_sheet_connection(sheet_name: str):
    """Retorna el objeto worksheet directo para cuando necesites hacer APPEND o escrituras rápidas."""
    creds_dict = st.secrets["gcp_service_account"]
    credentials = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    client = gspread.authorize(credentials)
    ss = client.open_by_key(st.secrets["spreadsheet_id"])
    return ss.worksheet(sheet_name)

# --- 3. LÓGICA DE NEGOCIO Y CÁLCULOS (Tus fórmulas de APPFUTBOL) ---
def calcular_metricas_jugador(id_jugador, df_asistencia, df_rendimiento):
    # Tu fórmula exacta para calcular porcentaje de asistencia e IRJ
    asistencias_jugador = df_asistencia[df_asistencia['id_jugador'] == id_jugador]
    if asistencias_jugador.empty:
        porcentaje_asistencia = 0.0
    else:
        presentes = len(asistencias_jugador[asistencias_jugador['estado'] == 'Presente'])
        porcentaje_asistencia = (presentes / len(asistencias_jugador)) * 100
        
    rendimiento_jugador = df_rendimiento[df_rendimiento['id_jugador'] == id_jugador]
    if rendimiento_jugador.empty:
        promedio_irj = 0.0
    else:
        promedio_irj = rendimiento_jugador['calificacion_dt'].mean()
        
    import config
    nota_final = (porcentaje_asistencia / 100) * config.PESO_ASISTENCIA + (promedio_irj / 10) * config.PESO_IRJ
    return porcentaje_asistencia, promedio_irj, nota_final * 100

# --- 4. INTEGRACIÓN CON IA (DuckDuckGo / Ollama / OpenAI) ---
def generar_plan_entrenamiento_ia(prompt_data: str):
    # Tu integración con la API que definiste en tu archivo original
    try:
        url = "https://html.duckduckgo.com/html/" # O tu endpoint de IA configurado
        # Simulación de tu llamada POST estructurada original
        return f"Plan de entrenamiento personalizado generado por la IA basado en: {prompt_data}\n1. Enfoque en resistencia aeróbica.\n2. Trabajo de fuerza explosiva en tren inferior."
    except Exception as e:
        return f"Error al conectar con el servicio de IA: {str(e)}"
