# admin_handlers.py

from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, timedelta
from config import ADMINS, REMINDER_HOURS, PLANS
from storage import load_users, save_users
from utils import notify_user, generate_config_file, remove_expired_config

def register_admin_handlers(bot: TeleBot):
    @bot.message_handler(func=lambda m: m.chat.id in ADMINS and m.text == "🛠 Panel de Administración")
    def show_admin_menu(message):
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(KeyboardButton("👥 Ver usuarios activos"))
        kb.add(KeyboardButton("📢 Notificar vencimientos"))
        kb.add(KeyboardButton("🔙 Volver"))
        bot.send_message(message.chat.id, "🔧 *Panel de administración de WireGuard activado.*\nSelecciona una opción:", reply_markup=kb, parse_mode="Markdown")

    @bot.message_handler(func=lambda m: m.chat.id in ADMINS and m.text == "👥 Ver usuarios activos")
    def list_active_users(message):
        users = load_users()
        if not users:
            bot.send_message(message.chat.id, "⚠️ No hay usuarios activos actualmente.")
            return

        info = "📋 *Usuarios activos:*\n\n"
        for uid, data in users.items():
            expira = datetime.fromisoformat(data['expira']).strftime('%Y-%m-%d %H:%M')
            info += f"🧑 Usuario ID: `{uid}`\n📦 Plan: {data['plan']}\n⏳ Expira: {expira}\n\n"
        bot.send_message(message.chat.id, info, parse_mode="Markdown")

    @bot.message_handler(func=lambda m: m.chat.id in ADMINS and m.text == "📢 Notificar vencimientos")
    def notify_expiring(message):
        users = load_users()
        if not users:
            bot.send_message(message.chat.id, "⚠️ No hay usuarios registrados.")
            return

        now = datetime.utcnow()
        count = 0
        for uid, data in users.items():
            expira = datetime.fromisoformat(data['expira'])
            horas_faltan = (expira - now).total_seconds() / 3600

            for h in REMINDER_HOURS:
                if abs(horas_faltan - h) <= 1:  # tolerancia de 1 hora
                    notify_user(bot, uid, data['plan'], expira)
                    count += 1
                    break

        bot.send_message(message.chat.id, f"📨 Notificaciones enviadas a {count} usuarios.")
