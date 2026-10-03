import os
import asyncio
from aiohttp import web
from main import main

# Веб-страница, чтобы Render видел, что сервис жив
async def handle_health(request):
    return web.Response(text="Bot is alive!")

async def start():
    app = web.Application()
    app.router.add_get('/', handle_health)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

    # Запуск самого Telegram-бота
    await main()

if __name__ == '__main__':
    asyncio.run(start())