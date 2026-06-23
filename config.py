# config.py

# Estilos CSS que ya tenías configurados para tus tarjetas y diseño
CSS_ESTILOS = """
<style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; background-color: #4CAF50; color: white; }
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

# Configuración de pesos para tus fórmulas matemáticas
PESO_ASISTENCIA = 0.4
PESO_IRJ = 0.6

# Encabezados exactos de tus pestañas de Google Sheets
HEADERS_JUGADORES = ["id", "nombre_completo", "edad", "fecha_nacimiento", "altura", "peso", "posicion", "pierna_dominante", "fecha_registro"]
HEADERS_USUARIOS = ["usuario", "contrasena", "rol", "id_jugador"]
HEADERS_ASISTENCIA = ["id_asistencia", "fecha", "tipo_evento", "id_jugador", "estado", "observaciones"]
HEADERS_PARTIDOS = ["id_partido", "fecha", "rival", "resultado_nosotros", "resultado_rival", "tipo_partido", "observaciones"]
HEADERS_RENDIMIENTO = ["id_rendimiento", "id_partido", "id_jugador", "minutos_jugados", "goles", "asistencias", "tarjeta_amarilla", "tarjeta_roja", "calificacion_dt"]
