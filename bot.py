#!/usr/bin/env python3
"""
🌿 España Rural — Bot de Noticias Diarias para Telegram
Versión para despliegue en Render.com
"""

import anthropic
import requests
import schedule
import time
import os
from datetime import datetime

# ─────────────────────────────────────────
#  Configuración desde variables de entorno
#  (se configuran en el panel de Render)
# ─────────────────────────────────────────
ANTHROPIC_API_KEY  = os.environ.get("ANTHROPIC_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "")
HORA_ENVIO         = os.environ.get("HORA_ENVIO", "08:00")
REGION             = os.environ.get("REGION", "")

TEMAS = [
    "emprendimiento rural y nuevos negocios en pueblos pequeños España",
    "subvenciones y ayudas zonas rurales España despoblación",
    "turismo rural sostenible España noticias",
    "conectividad fibra óptica banda ancha rural España",
    "iniciativas cultura patrimonio pueblos España",
]


def construir_prompt() -> str:
    fecha = datetime.now().strftime("%A %d de %B de %Y")
    region_txt = f" especialmente en {REGION}" if REGION else " en toda España"
    temas_txt = "\n".join(f"  • {t}" for t in TEMAS)

    return f"""Eres un periodista especializado en la España rural y la lucha contra la despoblación.

Hoy es {fecha}.

Genera un briefing diario de noticias sobre la España rural{region_txt}.
Temáticas a cubrir:
{temas_txt}

Formato para Telegram (usa emojis y texto plano, sin markdown complejo):

🌿 PULSO RURAL — {fecha.upper()}

📌 TITULAR DEL DÍA
[Una frase impactante]

📰 NOTICIAS DESTACADAS
[4 noticias con título, fuente probable y 2 líneas de contexto cada una]

💶 OPORTUNIDAD DE LA SEMANA
[Una convocatoria, subvención o iniciativa concreta y accionable]

📊 DATO RURAL
[Un dato sorprendente o motivador sobre la España rural]

💬 PARA REFLEXIONAR
[Una frase inspiradora final]

──────────────────
🌐 España Rural · Tu comunidad de pueblos vivos

Sé concreto, útil y esperanzador. Orientado a emprendedores y personas que quieren vivir o invertir en la España rural."""


def generar_briefing() -> str:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Generando briefing con Claude...")
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": construir_prompt()}],
    )
    texto = "\n".join(
        bloque.text for bloque in response.content if bloque.type == "text"
    )
    return texto.strip()


def enviar_telegram(mensaje: str) -> bool:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    if len(mensaje) > 4000:
        mensaje = mensaje[:3997] + "..."
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensaje,
        "parse_mode": "HTML",
    }
    try:
        r = requests.post(url, json=payload, timeout=15)
        r.raise_for_status()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Mensaje enviado a Telegram")
        return True
    except requests.RequestException as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error Telegram: {e}")
        return False


def job_diario():
    print(f"\n🌿 Iniciando briefing diario — {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    try:
        briefing = generar_briefing()
        enviar_telegram(briefing)
    except Exception as e:
        print(f"❌ Error: {e}")
        enviar_telegram(f"⚠️ Error al generar el briefing de hoy:\n{str(e)[:200]}")


# ── Arranque ──
print(f"🌿 Bot España Rural arrancado en Render")
print(f"📅 Enviará el briefing todos los días a las {HORA_ENVIO} UTC")
print(f"📱 Chat ID destino: {TELEGRAM_CHAT_ID}")

# Enviar mensaje de prueba al arrancar
enviar_telegram("✅ Bot España Rural conectado y activo. Recibirás el briefing diario a las " + HORA_ENVIO + " UTC 🌿")

schedule.every().day.at(HORA_ENVIO).do(job_diario)

while True:
    schedule.run_pending()
    time.sleep(30)
