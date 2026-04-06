#!/usr/bin/env python3
import anthropic
import requests
import os
from datetime import datetime, timedelta

ANTHROPIC_API_KEY  = os.environ["ANTHROPIC_API_KEY"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID   = os.environ["TELEGRAM_CHAT_ID"]
REGION             = os.environ.get("REGION", "")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def fechas():
    hoy = datetime.now()
    inicio = (hoy - timedelta(days=7)).strftime("%d de %B")
    fin = hoy.strftime("%d de %B de %Y")
    return inicio, fin

def enviar_telegram(mensaje: str):
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
        print(f"Telegram status: {r.status_code} - {r.text[:100]}")
        r.raise_for_status()

def generar_con_busqueda(prompt: str, tokens: int = 2000) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=tokens,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}],
    )
    texto = "\n".join(
        b.text for b in response.content if b.type == "text"
    )
    return texto.strip()

def generar_sin_busqueda(prompt: str, tokens: int = 2000) -> str:
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()

def briefing_semanal(inicio, fin):
    region_txt = f" especialmente en {REGION}" if REGION else " en toda Espana"
    return generar_con_busqueda(f"""Busca noticias reales de la ultima semana sobre la Espana rural{region_txt}.
Genera el resumen semanal del {inicio} al {fin}.
Usa solo texto plano y emojis. Sin tildes ni caracteres especiales.

RESUMEN SEMANAL {inicio} AL {fin}

LO MAS DESTACADO
[2-3 frases resumen de la semana]

NOTICIAS DE LA SEMANA
[6-8 noticias reales con titulo, 2 lineas de contexto y URL de la fuente debajo de cada una]

OPORTUNIDADES Y CONVOCATORIAS
[2-3 ayudas o subvenciones reales abiertas con URL de cada una]

EMPRENDIMIENTO RURAL
[2 iniciativas o casos de exito reales con URL]

DATO DE LA SEMANA
[Un dato real y verificable con fuente]

PROXIMA SEMANA
[Eventos o plazos reales proximos]

Espana Rural - Tu comunidad de pueblos vivos""", tokens=3000)

def instagram_posts(inicio, fin, briefing: str):
    region_txt = f" en {REGION}" if REGION else " en la Espana rural"
    return generar_sin_busqueda(f"""Eres community manager experto en ruralizacion.
Basandote en este briefing real de la semana:

{briefing[:2000]}

Crea 5 posts de Instagram para la semana del {inicio} al {fin}{region_txt}.
Usa solo texto plano y emojis. Sin tildes ni caracteres especiales.
Temas: emprendimiento, ayudas, turismo, tecnologia, cultura rural.

Para cada post:
- Primera linea: frase gancho que pare el scroll
- 4-6 lineas de texto cercano y emotivo
- 5-8 hashtags en castellano e ingles
- Separados con ---- entre cada uno

Tono esperanzador y cercano. Sin comillas ni markdown.""", tokens=2000)

def articulos_web(inicio, fin, briefing: str):
    region_txt = f" en {REGION}" if REGION else " en la Espana rural"
    return generar_sin_busqueda(f"""Eres redactor SEO especializado en mundo rural.
Basandote en este briefing real de la semana:

{briefing[:2000]}

Escribe 2 articulos completos para blog sobre las 2 noticias mas relevantes del {inicio} al {fin}{region_txt}.
Usa solo texto plano. Sin tildes ni caracteres especiales. Sin markdown.

Para cada articulo:
TITULO SEO: [titulo con palabra clave]
META DESCRIPCION: [maximo 160 caracteres]
INTRODUCCION: [2 parrafos que enganchen]
DESARROLLO: [3 secciones con subtitulo y 2 parrafos cada una]
CONCLUSION: [1 parrafo con llamada a la accion]
---""", tokens=2500)

if __name__ == "__main__":
    inicio, fin = fechas()
    print(f"Generando contenido: {inicio} al {fin}")

    print("--- Generando briefing con busqueda web ---")
    briefing = briefing_semanal(inicio, fin)
    enviar_telegram("MENSAJE 1 - RESUMEN SEMANAL\n\n" + briefing)

    print("--- Generando posts Instagram ---")
    enviar_telegram("MENSAJE 2 - POSTS INSTAGRAM\n\n" + instagram_posts(inicio, fin, briefing))

    print("--- Generando articulos web ---")
    enviar_telegram("MENSAJE 3 - ARTICULOS WEB\n\n" + articulos_web(inicio, fin, briefing))

    print("Todo enviado correctamente")