# payment_handlers.py

from telebot import TeleBot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton
from config import ADMINS, PLANS
from storage import load_users, save_users
from utils import generar_teclado_planes
from datetime import datetime, timedelta

# Almacena temporalmente los planes seleccionados por los usuarios
PENDING_PLANS = {}

def registrar_manejadores_pago(bot: TeleBot):

    @bot.message_handler(commands=['comprar', 'planes'])
    def mostrar_planes(msg: Message):
        teclado = generar_teclado_planes()
        bot.send_message(msg.chat.id, "💳 *Elige un plan de conexión:*", reply_markup=teclado, parse_mode="Markdown")

    @bot.message_handler(func=lambda m: m.text in PLANS.keys())
    def seleccionar_plan(msg: Message):
        user_id = msg.from_user.id
        PENDING_PLANS[user_id] = msg.text
        botones = ReplyKeyboardMarkup(resize_keyboard=True)
        botones.add(KeyboardButton("📸 Enviar comprobante"))
        botones.add(KeyboardButton("🔙 Cancelar"))
        texto = (
            f"📦 Has seleccionado el plan: *{msg.text}*\n\n"
            "💰 *Precio:* {} CUP\n\n"
            "👉 Ahora envía el comprobante de pago para validarlo."
        ).format(PLANS[msg.text]['price'])
        bot.send_message(user_id, texto, reply_markup=botones, parse_mode="Markdown")

    @bot.message_handler(func=lambda m: m.text == "📸 Enviar comprobante")
    def solicitar_comprobante(msg: Message):
        bot.send_message(msg.chat.id, "📥 Por favor, envía una *foto o captura de pantalla* del comprobante de pago.", parse_mode="Markdown")

    @bot.message_handler(content_types=['photo'])
    def recibir_comprobante(msg: Message):
        user_id = msg.from_user.id
        if user_id not in PENDING_PLANS:
            return bot.send_message(user_id, "⚠️ No has seleccionado ningún plan aún.")
        plan = PENDING_PLANS[user_id]
        caption = (
            f"📥 *Nuevo comprobante recibido*\n"
            f"👤 Usuario: @{msg.from_user.username or msg.from_user.first_name}\n"
            f"🆔 ID: `{user_id}`\n"
            f"📦 Plan: *{plan}*"
        )
        for admin_id in ADMINS:
            bot.send_photo(admin_id, msg.photo[-1].file_id, caption=caption, parse_mode="Markdown")
        bot.send_message(user_id, "✅ Comprobante enviado correctamente. Espera la aprobación del administrador.", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("/start")))

    @bot.message_handler(func=lambda m: m.text == "🔙 Cancelar")
    def cancelar(msg: Message):
        user_id = msg.from_user.id
        if user_id in PENDING_PLANS:
            del PENDING_PLANS[user_id]
        bot.send_message(user_id, "❌ Operación cancelada.", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("/start")))
