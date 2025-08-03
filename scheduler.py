# scheduler.py

from datetime import datetime, timedelta
import threading
import time
from telebot import TeleBot
from config import ADMINS, PLANS, REMINDER_HOURS
from storage import load_clients, save_clients
from utils import create_keyboard

def check_expirations(bot: TeleBot):
    while True:
        clients = load_clients()
        now = datetime.now()

        for user_id, data in list(clients.items()):
            expiration = datetime.strptime(data['expiration'], "%Y-%m-%d %H:%M:%S")
            remaining = expiration - now

            # Notificar 3 días y 1 día antes
            for hrs in REMINDER_HOURS:
                delta = timedelta(hours=hrs)
                if remaining <= delta and not data.get(f"reminder_{hrs}", False):
                    try:
                        kb = create_keyboard(["🔁 Renovar configuración"])
                        msg = f"📢 *Aviso importante*\n\nTu configuración *{data['plan']}* expirará en *{int(remaining.total_seconds() // 3600)} horas*.\n\nPuedes renovarla ahora para evitar interrupciones."
                        bot.send_message(user_id, msg, parse_mode="Markdown", reply_markup=kb)
                        data[f"reminder_{hrs}"] = True
                    except Exception as e:
                        print(f"❌ Error al enviar recordatorio a {user_id}: {e}")

            # Verificar si ya expiró
            if now >= expiration and not data.get("expired", False):
                try:
                    msg = (
                        f"⚠️ *Configuración expirada*\n\n"
                        f"Tu configuración *{data['plan']}* ha expirado.\n"
                        f"Debes renovarla para seguir utilizando el servicio.\n\n"
                        f"Puedes adquirir un nuevo plan desde el menú principal."
                    )
                    kb = create_keyboard(["🔁 Renovar configuración"])
                    bot.send_message(user_id, msg, parse_mode="Markdown", reply_markup=kb)
                except Exception as e:
                    print(f"❌ Error al notificar expiración a {user_id}: {e}")
                data["expired"] = True  # Marcar como vencido

        save_clients(clients)
        time.sleep(3600)  # Ejecutar cada 1 hora


def start_scheduler(bot: TeleBot):
    t = threading.Thread(target=check_expirations, args=(bot,), daemon=True)
    t.start()
    print("✅ Scheduler de expiraciones iniciado correctamente.")
