import asyncio
import os
import aiosqlite
from dotenv import load_dotenv
from kwork import Kwork
from kwork.exceptions import KworkException
from kwork.types import Project


class Parser:
    def __init__(self) -> None:
        load_dotenv()
        self.login: str = os.getenv('LOGIN')
        self.password: str = os.getenv('PASSWORD')
        self.phone_num: str = os.getenv('PHONE_NUMB')
        self.time_delay: int = 30
        self.db: aiosqlite.Connection | None = None

    async def init(self) -> None:
        self.db = await aiosqlite.connect("projects.db")
        await self._create_database()

    async def _create_database(self) -> None:
        await self.db.execute('''
        CREATE TABLE IF NOT EXISTS projects(
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            price INTEGER NOT NULL,
            possible_price_limit INTEGER,
            description TEXT,
            already_sent BOOLEAN NOT NULL DEFAULT 0
        )
        ''')
        await self.db.commit()

    async def _add_to_database(self, project: Project) -> None:
        async with self.db.execute("SELECT 1 FROM projects WHERE id = ?", (project.id,)) as cursor:
            row = await cursor.fetchone()

        if row is None:
            await self.db.execute(
                "INSERT INTO projects (id, title, price, possible_price_limit, description, already_sent) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (project.id, project.title, project.price, project.possible_price_limit, project.description, 0)
            )
            await self.db.commit()
            print(f"Добавлен проект: {project.title}")

    async def parse(self) -> None:
        api: Kwork = Kwork(login=self.login, password=self.password, phone_last=self.phone_num)
        print("Парсер запущен...")
        try:
            while True:
                try:
                    projects: list[Project] = await api.get_projects([41, 80, 40])
                    for project in projects:
                        await self._add_to_database(project)
                    await asyncio.sleep(self.time_delay)
                except KworkException as e:
                    print(f"Ошибка парсинга: {e}")
                    await asyncio.sleep(30)
        finally:
            await api.close()