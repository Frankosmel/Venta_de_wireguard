from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from config import TOKEN, ADMINS, PLANS
from storage import load_users, save_users, init_files
from utils import generate_config, notify_expiration, schedule_reminders
import threading
import time

bot = TeleBot(TOKEN)

# Inicializar archivos necesarios
init_files()

# Teclado principal del usuario
def get_main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("📝 Solicitar configuración"))
    markup.add(KeyboardButton("🕓 Ver vigencia"))
    markup.add(KeyboardButton("💸 Renovar o recargar"))
    return markup

# Teclado del administrador
def get_admin_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("📋 Ver usuarios activos"))
    markup.add(KeyboardButton("📢 Enviar mensaje"))
    return markup

# Comando /start
@bot.message_handler(commands=['start'])
def cmd_start(message):
    user_id = str(message.from_user.id)
    if int(user_id) in ADMINS:
        bot.send_message(message.chat.id, "👋 Bienvenido, administrador.", reply_markup=get_admin_menu())
    else:
        bot.send_message(message.chat.id, "👋 Bienvenido a *WireGuard Francho VPN*.\nSelecciona una opción:", 
                         reply_markup=get_main_menu(), parse_mode="Markdown")

# Solicitud de configuración
@bot.message_handler(func=lambda msg: msg.text == "📝 Solicitar configuración")
def solicitar_configuracion(message):
    user_id = str(message.from_user.id)
    plans_text = "💼 *Planes disponibles:*\n\n"
    for name, data in PLANS.items():
        price = "Gratis" if data['price'] == 0 else f"{data['price']} CUP"
        plans_text += f"• {name} — {data['duration_hours']}h — {price}\n"
    plans_text += "\n📩 Envíame el nombre del plan que deseas."
    bot.send_message(message.chat.id, plans_text, parse_mode="Markdown")
    bot.register_next_step_handler(message, procesar_plan)

def procesar_plan(message):
    plan_name = message.text.strip()
    if plan_name not in PLANS:
        bot.send_message(message.chat.id, "❌ Plan no válido. Intenta de nuevo.")
        return

    user_id = str(message.from_user.id)
    user_data = generate_config(user_id, plan_name)
    if not user_data:
        bot.send_message(message.chat.id, "⚠️ Error al generar configuración. Contacta a soporte.")
        return

    bot.send_message(message.chat.id, f"✅ Tu configuración fue creada exitosamente.\n"
                                      f"📥 Te envío el archivo .conf", reply_markup=get_main_menu())
    bot.send_document(message.chat.id, open(user_data['config_path'], 'rb'))

# Ver vigencia del plan
@bot.message_handler(func=lambda msg: msg.text == "🕓 Ver vigencia")
def ver_vigencia(message):
    user_id = str(message.from_user.id)
    users = load_users()
    if user_id not in users:
        return bot.send_message(message.chat.id, "❌ No tienes ninguna configuración activa.")
    
    data = users[user_id]
    bot.send_message(message.chat.id, f"⏳ Tu configuración expira el:\n*{data['expires']}*", parse_mode="Markdown")

# Renovar o recargar
@bot.message_handler(func=lambda msg: msg.text == "💸 Renovar o recargar")
def renovar_config(message):
    bot.send_message(message.chat.id, "🔁 Para renovar tu plan, selecciona uno nuevo y se sumará el tiempo restante.\n"
                                      "Escribe el nombre del plan que deseas.")
    bot.register_next_step_handler(message, procesar_renovacion)

def procesar_renovacion(message):
    plan_name = message.text.strip()
    if plan_name not in PLANS:
        bot.send_message(message.chat.id, "❌ Plan no válido. Intenta de nuevo.")
        return

    user_id = str(message.from_user.id)
    result = generate_config(user_id, plan_name, renovar=True)
    if not result:
        return bot.send_message(message.chat.id, "⚠️ No se pudo renovar. Asegúrate de tener una configuración activa.")
    
    bot.send_message(message.chat.id, f"✅ Tu plan ha sido renovado correctamente.\n"
                                      f"📥 Archivo actualizado:", reply_markup=get_main_menu())
    bot.send_document(message.chat.id, open(result['config_path'], 'rb'))

# ADMIN: Ver usuarios activos
@bot.message_handler(func=lambda msg: msg.text == "📋 Ver usuarios activos")
def ver_usuarios_activos(message):
    if message.from_user.id not in ADMINS:
        return
    users = load_users()
    if not users:
        return bot.send_message(message.chat.id, "No hay usuarios activos.")
    
    texto = "📄 Usuarios activos:\n\n"
    for uid, data in users.items():
        texto += f"👤 ID: `{uid}`\n📆 Vence: {data['expires']}\n\n"
    bot.send_message(message.chat.id, texto, parse_mode="Markdown")

# ADMIN: Enviar mensaje masivo
@bot.message_handler(func=lambda msg: msg.text == "📢 Enviar mensaje")
def admin_mensaje(message):
    bot.send_message(message.chat.id, "✏️ Escribe el mensaje que deseas enviar a todos los usuarios:")
    bot.register_next_step_handler(message, enviar_broadcast)

def enviar_broadcast(message):
    texto = message.text
    users = load_users()
    for uid in users:
        try:
            bot.send_message(uid, f"📢 *Mensaje de administración:*\n\n{texto}", parse_mode="Markdown")
        except Exception:
            continue
    bot.send_message(message.chat.id, "✅ Mensaje enviado a todos los usuarios.")

# Hilo de verificación de vencimientos
def monitor_expiraciones():
    while True:
        notify_expiration(bot)
        time.sleep(3600)  # cada hora

# Iniciar hilo secundario
threading.Thread(target=monitor_expiraciones, daemon=True).start()

# Iniciar bot
print("🤖 Bot iniciado correctamente.")
bot.infinity_polling()
