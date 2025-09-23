import asyncio
import os
import sqlite3
from dotenv import load_dotenv
from kwork import Kwork
from kwork.exceptions import KworkException
from kwork.types import Project

class Parser:
    def __init__(self):
        load_dotenv()
        self.login: str = os.getenv('LOGIN')
        self.password: str = os.getenv('PASSWORD')
        self.phone_num: str = os.getenv('PHONE_NUMB')
        self.time_delay: int = 180

        self.conn = sqlite3.connect("projects.db")
        self.cursor = self.conn.cursor()
        self._create_database()

    def _create_database(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects(
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            price INTEGER NOT NULL,
            possible_price_limit INTEGER,
            description TEXT
        )
        ''')
        self.conn.commit()

    def _add_to_database(self, project: Project):
        self.cursor.execute("SELECT 1 FROM projects WHERE id = ?", (project.id,))
        if self.cursor.fetchone() is None:
            self.cursor.execute(
                "INSERT INTO projects (id, title, price, possible_price_limit, description) "
                "VALUES (?, ?, ?, ?, ?)",
                (project.id, project.title, project.price, project.possible_price_limit, project.description)
            )
            self.conn.commit()
            print(f"Добавлен проект: {project.title}")
        else:
            print(f"Проект уже существует: {project.title}")

    def _close_database(self):
        self.cursor.close()
        self.conn.close()

    async def parse(self):
        api: Kwork = Kwork(login=self.login, password=self.password, phone_last=self.phone_num)

        try:
            while True:
                projects: list[Project] = await api.get_projects([41, 80, 40])

                for project in projects:
                    self._add_to_database(project)

                await asyncio.sleep(self.time_delay)

        except KworkException as e:
            print(e)
        finally:
            self._close_database()

asyncio.run(Parser().parse())