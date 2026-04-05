#!/usr/bin/env python3
"""
🌿 España Rural — Briefing diario para GitHub Actions
Se ejecuta una vez y termina (GitHub Actions lo programa)
"""

import anthropic
import requests
import os
from datetime import datetime

ANTHROPIC_API_KEY  = os.environ["ANTHROPIC_API_KEY"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID   = os.environ["TELEGRAM_CHAT_ID"]
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

Formato para Telegram (usa emojis y texto plano):

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

Sé concreto, útil y esperanzador."""


def generar_briefing() -> str:
    print("🤖 Generando briefing con Claude...")
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


def enviar_telegram(mensaje: str):
    print("📱 Enviando a Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    if len(mensaje) > 4000:
        mensaje = mensaje[:3997] + "..."
    r = requests.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensaje,
        "parse_mode": "HTML",
    }, timeout=15)
    r.raise_for_status()
    print("✅ Briefing enviado correctamente")


if __name__ == "__main__":
    briefing = generar_briefing()
    enviar_telegram(briefing)
