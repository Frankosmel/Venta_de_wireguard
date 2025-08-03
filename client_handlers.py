# client_handlers.py

from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from config import PLANS, WG_CONFIG_DIR
from utils import generar_config_cliente, calcular_expiracion, enviar_configuracion, notificar_admin
from storage import save_config, get_configs_by_user
from datetime import datetime
import os

def registrar_client_handlers(bot: TeleBot):

    @bot.message_handler(commands=['start'])
    def handle_start(message):
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        for plan in PLANS.keys():
            kb.add(KeyboardButton(f"🛒 Contratar {plan}"))
        bot.send_message(message.chat.id, "👋 ¡Bienvenido al bot de configuraciones WireGuard!\n\nSelecciona un plan para comenzar:", reply_markup=kb)

    @bot.message_handler(func=lambda m: m.text and m.text.startswith("🛒 Contratar"))
    def contratar_plan(message):
        user_id = message.from_user.id
        plan_nombre = message.text.replace("🛒 Contratar ", "")
        plan = PLANS.get(plan_nombre)

        if not plan:
            return bot.send_message(message.chat.id, "⚠️ Plan no válido. Intenta de nuevo.")

        configuraciones = get_configs_by_user(user_id)
        if any(cfg["plan"] == "💡 Prueba 5H" for cfg in configuraciones) and plan_nombre == "💡 Prueba 5H":
            return bot.send_message(message.chat.id, "⚠️ Solo puedes usar la prueba gratuita una vez.")

        # Generar configuración
        ip_cliente, conf_text, qr_path, private_key = generar_config_cliente(user_id)

        # Calcular vencimiento
        fecha_expira = calcular_expiracion(plan["duration_hours"])

        # Guardar la configuración
        save_config(user_id, {
            "ip": ip_cliente,
            "plan": plan_nombre,
            "expira": fecha_expira.strftime("%Y-%m-%d %H:%M:%S"),
            "config": conf_text,
            "clave_privada": private_key
        })

        # Notificar administrador
        notificar_admin(bot, message.from_user, plan_nombre, ip_cliente, fecha_expira)

        # Enviar al cliente
        enviar_configuracion(bot, message.chat.id, conf_text, qr_path, fecha_expira, plan_nombre)
