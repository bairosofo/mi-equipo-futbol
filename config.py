# config.py

# Estilos visuales para que las tarjetas de los jugadores se vean profesionales
CSS_ESTILOS = """
<style>
    .stat-card { 
        background-color: #1e293b; 
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid rgba(255,255,255,0.1); 
        text-align: center; 
        margin-bottom: 10px;
    }
</style>
"""

# Los nombres exactos de las columnas de tus pestañas en Google Sheets
HEADERS_JUGADORES = ["id", "nombre_completo", "edad", "fecha_nacimiento", "altura", "peso", "posicion", "pierna_dominante", "fecha_registro"]
HEADERS_USUARIOS = ["usuario", "contrasena", "rol", "id_jugador"]

