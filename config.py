# config.py

# TOKEN del bot de Telegram
TOKEN = 'TU_TOKEN_AQUÍ'

# ID del administrador (puedes poner más si es necesario)
ADMINS = [1383931339]

# Ruta de la carpeta donde se guardarán los archivos WireGuard
WG_CONFIG_DIR = '/etc/wireguard/'

# Dirección IP del servidor WireGuard
SERVER_PUBLIC_IP = '3.145.41.118'  # reemplaza por la IP de tu VPS

# Puerto por el cual escuchará WireGuard
LISTEN_PORT = 51820

# Rango de IP para los clientes (la IP del servidor debe estar fuera de este rango)
IP_RANGE = '10.9.0.0/24'

# Planes disponibles (nombre, duración en horas, precio en CUP)
PLANS = {
    "💡 Prueba 5H": {
        "duration_hours": 5,
        "price": 0
    },
    "🟢 Básico 3 días": {
        "duration_hours": 72,
        "price": 100
    },
    "🔵 Medio 7 días": {
        "duration_hours": 168,
        "price": 200
    },
    "🔴 Premium 30 días": {
        "duration_hours": 720,
        "price": 500
    }
}

# Tiempo de aviso antes de expirar (en horas)
REMINDER_HOURS = [72, 24]  # 3 días y 1 día antes
