#!/usr/bin/env python3
import anthropic
import requests
import os
from datetime import datetime, timedelta

ANTHROPIC_API_KEY  = os.environ["ANTHROPIC_API_KEY"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID   = os.environ["TELEGRAM_CHAT_ID"]
REGION             = os.environ.get("REGION", "")

TEMAS = [
    "emprendimiento rural y nuevos negocios en pueblos pequenos Espana",
    "subvenciones y ayudas zonas rurales Espana despoblacion",
    "turismo rural sostenible Espana noticias",
    "conectividad fibra optica banda ancha rural Espana",
    "iniciativas cultura patrimonio pueblos Espana",
]

def construir_prompt() -> str:
    hoy = datetime.now()
    semana_inicio = (hoy - timedelta(days=7)).strftime("%d de %B")
    semana_fin = hoy.strftime("%d de %B de %Y")
    region_txt = f" especialmente en {REGION}" if REGION else " en toda Espana"
    temas_txt = "\n".join(f"  - {t}" for t in TEMAS)
    return f"""Eres un periodista especializado en la Espana rural.

Genera el resumen semanal del {semana_inicio} al {semana_fin}{region_txt}.
Temas: {temas_txt}

Formato Telegram (sin caracteres especiales, solo texto plano y emojis):

RESUMEN SEMANAL {semana_inicio} AL {semana_fin}

LO MAS DESTACADO
[2-3 frases resumen]

NOTICIAS DE LA SEMANA
[6-8 noticias con titulo y 2 lineas cada una]

OPORTUNIDADES Y CONVOCATORIAS
[2-3 ayudas o subvenciones abiertas]

EMPRENDIMIENTO RURAL
[2 iniciativas o casos de exito]

DATO DE LA SEMANA
[Un dato relevante]

PROXIMA SEMANA
[Eventos o plazos importantes]

REFLEXION FINAL
[Frase inspiradora]

Espana Rural - Tu comunidad de pueblos vivos"""

def generar_briefing() -> str:
    print("Generando resumen semanal...")
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        messages=[{"role": "user", "content": construir_prompt()}],
    )
    print("Briefing generado OK")
    return response.content[0].text.strip()

def enviar_telegram(mensaje: str):
    print("Enviando a Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    if len(mensaje) > 4000:
        partes = [mensaje[:3997] + "...", "..." + mensaje[3997:]]
    else:
        partes = [mensaje]
    for parte in partes:
        r = requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": parte
        }, timeout=15)
        print(f"Respuesta Telegram: {r.status_code} - {r.text[:200]}")
        r.raise_for_status()
    print("Enviado correctamente")

if __name__ == "__main__":
    briefing = generar_briefing()
    enviar_telegram(briefing)