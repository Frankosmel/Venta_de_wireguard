# notifications.py

from telebot import TeleBot
from datetime import datetime, timedelta
from config import REMINDER_HOURS, PLANS
from storage import load, save
from utils import format_timedelta
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def check_expirations(bot: TeleBot):
    """
    Revisa todas las configuraciones activas y notifica a los usuarios si están a punto de vencer.
    Envía aviso 3 días y 1 día antes del vencimiento.
    """
    clients = load("clients")
    now = datetime.utcnow()

    for user_id, data in clients.items():
        expires_at_str = data.get("expires_at")
        plan_name = data.get("plan_name")
        if not expires_at_str or not plan_name:
            continue

        try:
            expires_at = datetime.fromisoformat(expires_at_str)
        except ValueError:
            continue

        # Calcular el tiempo restante
        time_remaining = expires_at - now
        hours_remaining = int(time_remaining.total_seconds() / 3600)

        if hours_remaining in REMINDER_HOURS:
            try:
                markup = ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(KeyboardButton("🔄 Reactivar Plan"))
                markup.add(KeyboardButton("❌ Cancelar"))

                msg = (
                    f"⏰ *Aviso importante sobre tu configuración WireGuard*\n\n"
                    f"Tu plan actual *({plan_name})* expira en *{format_timedelta(time_remaining)}*.\n\n"
                    f"🔁 Puedes reactivarlo ahora mismo con el botón de abajo.\n\n"
                    f"⚠️ Si no lo haces antes del vencimiento, *no podrás seguir utilizando la conexión.*"
                )
                bot.send_message(
                    int(user_id),
                    msg,
                    parse_mode="Markdown",
                    reply_markup=markup
                )
            except Exception as e:
                print(f"[!] Error al notificar al usuario {user_id}: {e}")
