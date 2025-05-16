"""Chainlit front‑end for NL→SQL Cloudflare Worker bot.
Set BOT_ENDPOINT env var to your Worker URL before launch, e.g.
    BOT_ENDPOINT="https://<worker>.workers.dev" chainlit run chainlit_app.py --host 0.0.0.0 --port 8000
"""
import os
import httpx
import chainlit as cl

BOT_ENDPOINT = os.getenv("BOT_ENDPOINT", "https://<worker>.workers.dev")
TIMEOUT_SEC = 20

@cl.on_chat_start
async def welcome():
    await cl.Message(content="Привет! Задайте вопрос о базе данных, и я верну Markdown‑таблицу.").send()

@cl.on_message
async def handle(message: cl.Message):
    """Handles every user message, proxies it to the Cloudflare Worker and returns the result."""
    question = (message.content or "").strip()
    if not question:
        await cl.Message(content="❓ Вопрос пустой. Попробуйте ещё раз.").send()
        return

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SEC) as client:
            resp = await client.post(BOT_ENDPOINT, json={"question": question})
    except httpx.RequestError as exc:
        await cl.Message(content=f"🚨 Ошибка соединения с бот‑сервером: {exc}").send()
        return

    if resp.status_code != 200:
        await cl.Message(content=f"⚠️ {resp.status_code}: {resp.text}").send()
        return

    # Worker returns plain‑text Markdown
    await cl.Message(content=resp.text).send()
