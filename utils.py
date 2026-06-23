# utils.py
import streamlit as st
import gspread
import bcrypt
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# --- 1. SEGURIDAD (BCRYPT) ---
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return password == hashed  # Compatibilidad si hay claves viejas en texto plano

# --- 2. CONEXIONES A GOOGLE SHEETS ---
@st.cache_data(ttl=300)
def get_data_from_sheet(sheet_name: str):
    """Lectura optimizada con caché de 5 minutos."""
    creds_dict = st.secrets["gcp_service_account"]
    credentials = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    client = gspread.authorize(credentials)
    ss = client.open_by_key(st.secrets["spreadsheet_id"])
    ws = ss.worksheet(sheet_name)
    return pd.DataFrame(ws.get_all_records())

def get_sheet_connection(sheet_name: str):
    """Conexión directa sin caché para escrituras inmediatas (Append)."""
    creds_dict = st.secrets["gcp_service_account"]
    credentials = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    client = gspread.authorize(credentials)
    ss = client.open_by_key(st.secrets["spreadsheet_id"])
    return ss.worksheet(sheet_name)

# --- 3. MOTOR ANALÍTICO: CÁLCULOS DE RENDIMIENTO (IRJ / IMC) ---
def calcular_irj_e_imc(datos_eval: dict):
    # Cálculo de IMC
    altura_m = datos_eval["altura_eval"] / 100
    imc = datos_eval["peso_eval"] / (altura_m ** 2) if altura_m > 0 else 0
    
    # Puntuación Promedio Física (Escala 1 a 100 sugerida en tests)
    score_fisico = (datos_eval["vel_10m"] + datos_eval["vel_30m"] + datos_eval["agilidad"] + datos_eval["resistencia"] + datos_eval["salto_vertical"]) / 5
    # Puntuación Promedio Técnica
    score_tecnico = (datos_eval["precision_pase"] + datos_eval["control_orientado"] + datos_eval["conduccion"] + datos_eval["definicion"]) / 4
    # Puntuación Mental/Actitud asignada por el DT
    score_mental = datos_eval["score_mental_dt"]
    
    # Aplicación de los Pesos de la Arquitectura Maestra (config.py)
    import config
    irj = (score_fisico * config.PESO_FISICO) + (score_tecnico * config.PESO_TECNICO) + (score_mental * config.PESO_MENTAL)
    
    return round(imc, 2), round(score_fisico, 1), round(score_tecnico, 1), round(irj, 1)

# --- 4. MOTOR INTELIGENTE DE PLANIFICACIÓN (INTEGRACIÓN IA / DUCKDUCKGO) ---
def generar_plan_ia_duckduckgo(posicion, edad, objetivos, dias):
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            query = f"football training drill plan for {posicion} age {edad} focus on {objetivos}"
            resultados = [r for r in ddgs.text(query, max_results=2)]
            if resultados:
                return f"### 🤖 Plan Inteligente Sugerido por IA:\nBasado en tendencias competitivas de fútbol para un {posicion} ({edad} años) con enfoque en {objetivos}:\n\n- **Estructura Semanal ({dias} días):** Entrenamiento de fuerza explosiva integrada combinando los siguientes circuitos analizados:\n\n1. {resultados[0]['title']}: {resultados[0]['body']}"
    except Exception:
        pass
    return f"### 🤖 Plan Inteligente Base (Modo Local):\nPlan diseñado para **{posicion}** enfocado en **{objetivos}**:\n- **Microciclo (Fuerza/Velocidad):** 4 series de transferencia pliométrica seguidas de remates técnicos.\n- **Gimnasio:** Enfoque en core y cadena posterior."
