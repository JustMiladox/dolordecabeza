import re
import os
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters
from telegram.error import Unauthorized

TOKEN = os.getenv("TOKEN")
ARCHIVO_IDS = "ids.txt"

mensajes_borrados = 0

# ===== CREAR ARCHIVO SI NO EXISTE =====
if not os.path.exists(ARCHIVO_IDS):
    open(ARCHIVO_IDS, "w").close()

# ===== CARGAR IDS =====
with open(ARCHIVO_IDS, "r") as f:
    ids_guardadas = set(line.strip() for line in f if line.strip())

regex_id = re.compile(r'\b\d{7,}\b')

# ===== DETECTAR IDS =====
def detectar_ids(update, context):
    global mensajes_borrados

    if not update.message or not update.message.text:
        return

    texto = update.message.text
    encontrados = regex_id.findall(texto)

    if not encontrados:
        return

    borrar = False
    nuevas = []

    for num in encontrados:
        if num in ids_guardadas:
            borrar = True
        else:
            ids_guardadas.add(num)
            nuevas.append(num)

    if nuevas:
        with open(ARCHIVO_IDS, "a") as f:
            for n in nuevas:
                f.write(n + "\n")

    if borrar:
        try:
            update.message.delete()
            mensajes_borrados += 1
        except Forbidden:
            pass
        except:
            pass

# ===== PANEL =====
def panel(update, context):
    total_ids = len(ids_guardadas)

    texto = (
        "╔═PANEL══╗\n"
        f"📦 IDs guardadas: {total_ids}\n"
        f"🗑️ Mensajes borrados: {mensajes_borrados}\n"
        "🤖 Estado: Activo\n"
        "╚═══════════════════╝"
    )

    update.message.reply_text(texto)

# ===== LIMPIAR ARCHIVO =====
def limpiar_archivo(update, context):
    with open(ARCHIVO_IDS, "r") as f:
        lineas = [line.strip() for line in f if line.strip()]

    antes = len(lineas)
    unicas = sorted(set(lineas), key=lineas.index)
    despues = len(unicas)

    with open(ARCHIVO_IDS, "w") as f:
        for i in unicas:
            f.write(i + "\n")

    update.message.reply_text(
        f"🧹 Archivo limpiado\n"
        f"📦 IDs antes: {antes}\n"
        f"✅ IDs únicas: {despues}\n"
        f"❌ Duplicadas eliminadas: {antes - despues}"
    )

# ===== TEST =====
def prueba(update, context):
    update.message.reply_text("✅ El bot funciona")

# ===== INICIAR =====
updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("panel", panel))
dp.add_handler(CommandHandler("limpiar", limpiar_archivo))
dp.add_handler(CommandHandler("test", prueba))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, detectar_ids))

print("🤖 Bot anti-IDs repetidas iniciado")

updater.start_polling()
updater.idle()
