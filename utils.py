# utils.py

import subprocess
import os
import ipaddress
from config import WG_CONFIG_DIR, SERVER_PUBLIC_IP, LISTEN_PORT, VENCIMIENTO_AVISOS_HORAS
import qrcode
import base64
from io import BytesIO
from storage import load_users
from datetime import datetime, timedelta

def generate_keypair():
    """
    Genera una clave privada y pública única para un nuevo cliente.
    """
    private_key = subprocess.check_output("wg genkey", shell=True).decode().strip()
    public_key = subprocess.check_output(f"echo {private_key} | wg pubkey", shell=True).decode().strip()
    return private_key, public_key

def get_used_ips():
    """
    Devuelve una lista de IPs ya asignadas a clientes.
    """
    used_ips = set()
    for file in os.listdir(WG_CONFIG_DIR):
        if file.endswith(".conf") and file.startswith("client_"):
            with open(os.path.join(WG_CONFIG_DIR, file)) as f:
                for line in f:
                    if line.strip().startswith("Address"):
                        ip = line.strip().split("=")[1].strip().split("/")[0]
                        used_ips.add(ip)
    return used_ips

def get_next_available_ip():
    """
    Calcula la próxima IP disponible dentro del rango 10.9.0.2 a 10.9.0.254.
    """
    base = ipaddress.IPv4Address("10.9.0.1")
    used_ips = get_used_ips()
    for i in range(2, 255):
        candidate = str(base + i)
        if candidate not in used_ips:
            return candidate
    return None

def generate_conf(client_name, private_key, ip, server_pubkey):
    """
    Genera el archivo de configuración .conf del cliente.
    """
    config = f"""[Interface]
PrivateKey = {private_key}
Address = {ip}/32
DNS = 1.1.1.1

[Peer]
PublicKey = {server_pubkey}
Endpoint = {SERVER_PUBLIC_IP}:{LISTEN_PORT}
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
"""
    path = os.path.join(WG_CONFIG_DIR, f"client_{client_name}.conf")
    with open(path, "w") as f:
        f.write(config)
    return path

def generate_qr_code(config_path):
    """
    Genera un código QR desde el contenido del archivo de configuración.
    """
    with open(config_path, "r") as f:
        content = f.read()
    qr = qrcode.QRCode(border=1)
    qr.add_data(content)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    bio = BytesIO()
    img.save(bio, format='PNG')
    bio.seek(0)
    return bio

def delete_conf(client_name):
    """
    Elimina el archivo de configuración del cliente.
    """
    path = os.path.join(WG_CONFIG_DIR, f"client_{client_name}.conf")
    if os.path.exists(path):
        os.remove(path)
        return True
    return False

def notify_expiration(bot):
    """
    Notifica a los usuarios cuyo plan está por vencer según VENCIMIENTO_AVISOS_HORAS.
    """
    users = load_users()
    ahora = datetime.now()
    for uid, data in users.items():
        try:
            vencimiento = datetime.strptime(data['expires'], "%Y-%m-%d %H:%M:%S")
            horas_restantes = (vencimiento - ahora).total_seconds() / 3600
            for horas in VENCIMIENTO_AVISOS_HORAS:
                if abs(horas_restantes - horas) < 0.5:
                    bot.send_message(uid, f"⚠️ Tu configuración expira en {int(horas)} horas. ¡Renueva a tiempo para no quedarte sin conexión!")
        except Exception:
            continue

def schedule_reminders():
    """
    Placeholder por si deseas más adelante programar acciones desde utils.
    Actualmente no hace nada.
    """
    pass
