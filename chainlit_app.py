"""Chainlit front‑end for NL→SQL Cloudflare Worker bot.
Replace BOT_ENDPOINT with your Worker URL or set env var BOT_ENDPOINT.
Run with:  chainlit run chainlit_app.py -h 0.0.0.0 -p 8000
"""
import os
import httpx
import chainlit as cl

BOT_ENDPOINT = os.getenv("BOT_ENDPOINT", "https://<worker>.workers.dev")

@cl.on_chat_start
async def welcome():
    await cl.Message(content="Привет! Задайте вопрос о базе данных, и я верну таблицу.").send()

@cl.on_message
async def handle(message: str):
    question = message
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(BOT_ENDPOINT, json={"question": question})
    if r.status_code != 200:
        await cl.Message(content=f"⚠️ Error {r.status_code}: {r.text}").send()
        return

    # ответ Worker‑а — Markdown‑таблица в виде plain‑text
    await cl.Message(content=r.text, markdown=True).send()
