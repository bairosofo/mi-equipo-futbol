# utils.py
import streamlit as st
import gspread
import bcrypt
from google.oauth2.service_account import Credentials
import pandas as pd

# --- 1. SISTEMA DE SEGURIDAD (BCRYPT) ---
def hash_password(password: str) -> str:
    """Encripta la contraseña antes de guardarla en Google Sheets."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    """Compara la contraseña que ingresa el usuario con la encriptada."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


# --- 2. CONEXIÓN OPTIMIZADA A GOOGLE SHEETS ---
@st.cache_data(ttl=600)  # Guarda los datos en memoria por 10 minutos para que sea ultra rápido
def get_data_from_sheet(sheet_name: str):
    """Se conecta a Google Sheets y devuelve los datos como una tabla (DataFrame)."""
    # Carga las credenciales guardadas en los Secrets de Streamlit
    creds_dict = st.secrets["gcp_service_account"]
    credentials = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    client = gspread.authorize(credentials)
    
    # Abre tu hoja de cálculo usando el ID guardado en Secrets
    ss = client.open_by_key(st.secrets["spreadsheet_id"])
    ws = ss.worksheet(sheet_name)
    
    return pd.DataFrame(ws.get_all_records())

