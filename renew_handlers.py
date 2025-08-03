# renew_handlers.py

from telebot import TeleBot
from telebot.types import Message
from config import PLANS
from storage import load_clients, save_clients
from utils import create_keyboard
from datetime import datetime, timedelta


def register_renew_handlers(bot: TeleBot):
    @bot.message_handler(func=lambda m: m.text == "🔁 Renovar configuración")
    def handle_renew(msg: Message):
        user_id = str(msg.from_user.id)
        clients = load_clients()

        if user_id not in clients:
            return bot.send_message(
                msg.chat.id,
                "❌ No tienes una configuración activa que se pueda renovar.",
            )

        client_data = clients[user_id]
        plan = client_data['plan']
        duration_hours = PLANS.get(plan, {}).get("duration_hours")

        if not duration_hours:
            return bot.send_message(
                msg.chat.id,
                "❌ No se encontró la duración del plan anterior. Contacta al administrador."
            )

        now = datetime.now()
        old_exp = datetime.strptime(client_data['expiration'], "%Y-%m-%d %H:%M:%S")

        # Si aún no ha vencido, extender desde fecha actual
        if now < old_exp:
            new_exp = old_exp + timedelta(hours=duration_hours)
        else:
            new_exp = now + timedelta(hours=duration_hours)

        # Actualizar datos del cliente
        client_data['expiration'] = new_exp.strftime("%Y-%m-%d %H:%M:%S")
        client_data['reminder_72'] = False
        client_data['reminder_24'] = False
        client_data['expired'] = False

        save_clients(clients)

        bot.send_message(
            msg.chat.id,
            f"✅ Tu plan *{plan}* ha sido renovado exitosamente.\n\n"
            f"📆 Nueva fecha de vencimiento: *{new_exp.strftime('%Y-%m-%d %H:%M:%S')}*",
            parse_mode="Markdown",
            reply_markup=create_keyboard(["🏠 Menú principal"])
        )
