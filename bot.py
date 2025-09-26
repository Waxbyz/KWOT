import asyncio
import os
import aiosqlite

from dotenv import load_dotenv
from parser import Parser
from utils import text_redactor
from telegram.ext import ApplicationBuilder
load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
MY_CHAT_ID = int(os.getenv('MY_CHAT_ID'))

async def send_message(application) -> None:
    async with aiosqlite.connect("projects.db") as db:
        while True:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM projects WHERE already_sent = 0"
            ) as cursor:
                rows = await cursor.fetchall()

            for row in rows:
                await application.bot.send_message(
                    chat_id=MY_CHAT_ID,
                    text=(
                        f"📝Новый проект на Kwork\n\n"
                        f"📢Название: {row['title']}\n"
                        f"💵Цена: {row['price']}₽\n"
                        f"💸Допустимо до: {row['possible_price_limit']}₽\n\n"
                        f"📒Описание: {text_redactor(row['description'])}\n\n"
                        f"🔗Ссылка: https://kwork.ru/projects/{row['id']}/view\n"
                    )
                )
                await db.execute(
                    "UPDATE projects SET already_sent = 1 WHERE id = ?",
                    (row['id'],)
                )
            await db.commit()

            await asyncio.sleep(10)

async def post_init(application):
    parser = Parser()
    await parser.init()
    asyncio.create_task(parser.parse())
    print("Отсылаю сообщение пользователю...")
    asyncio.create_task(send_message(application))

def main() -> None:
    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()

    print("Бот запущен...")
    app.run_polling()

if __name__ == '__main__':
    main()
