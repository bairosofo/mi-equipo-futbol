# config.py

# Estilos CSS de Los Troncos FC para un diseño oscuro y profesional
CSS_ESTILOS = """
<style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; background-color: #2e7d32; color: white; border-radius: 5px; }
    .stButton>button:hover { background-color: #1b5e20; }
    .stat-card {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.1);
        text-align: center;
        margin-bottom: 15px;
    }
</style>
"""

# Configuración matemática para el algoritmo del IRJ (Índice de Rendimiento del Jugador)
PESO_FISICO = 0.4
PESO_TECNICO = 0.4
PESO_MENTAL = 0.2

# Nombres exactos de las columnas en tus hojas de Google Sheets
HEADERS_JUGADORES = ["id", "nombre_completo", "edad", "fecha_nacimiento", "altura", "peso", "posicion", "pierna_dominante", "fecha_registro"]
HEADERS_USUARIOS = ["usuario", "contrasena", "rol", "id_jugador"]
HEADERS_EVALUACIONES = [
    "id_eval", "id_jugador", "nombre_jugador", "fecha_evaluacion", "posicion",
    "vel_10m", "vel_30m", "agilidad", "resistencia", "salto_vertical", "potencia",
    "precision_pase", "control_orientado", "conduccion", "definicion",
    "peso_eval", "altura_eval", "masa_muscular", "imc",
    "score_fisico", "score_tecnico", "score_mental", "irj", "proyeccion", "potencial_estrellas"
]
HEADERS_WELLNESS = ["fecha", "id_jugador", "sueno", "dolor_muscular", "energia"]
