import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from psycopg import connect
from psycopg.rows import dict_row

from .db_interface import DatabaseInterface


class PostgresDatabase(DatabaseInterface):
    """PostgreSQL implementation of the database interface."""

    def __init__(self, database_url: str):
        if not database_url:
            raise ValueError("DATABASE_URL is required for Postgres backend")
        self.database_url = database_url

    def _connect(self):
        return connect(self.database_url, row_factory=dict_row)

    def initialize(self) -> None:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id BIGSERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    date TEXT NOT NULL,
                    location TEXT NOT NULL,
                    description TEXT
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS dish_categories (
                    id BIGSERIAL PRIMARY KEY,
                    name TEXT NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS dishes (
                    id BIGSERIAL PRIMARY KEY,
                    event_id BIGINT NOT NULL REFERENCES events(id) ON DELETE CASCADE,
                    name TEXT NOT NULL,
                    category_id BIGINT NOT NULL REFERENCES dish_categories(id),
                    person_name TEXT NOT NULL,
                    description TEXT,
                    serves INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL
                )
                """
            )

            cur.execute("SELECT COUNT(*) AS count FROM dish_categories")
            if cur.fetchone()["count"] == 0:
                categories = [
                    ("Appetizer",),
                    ("Main Dish",),
                    ("Side Dish",),
                    ("Salad",),
                    ("Dessert",),
                    ("Bread",),
                    ("Beverage",),
                ]
                cur.executemany("INSERT INTO dish_categories (name) VALUES (%s)", categories)

            cur.execute("SELECT COUNT(*) AS count FROM events")
            if cur.fetchone()["count"] == 0 and os.environ.get("SEED_SAMPLE_DATA", "true").lower() == "true":
                sample_events = [
                    (
                        "Easter Dinner",
                        "2024-03-31 17:00",
                        "Mom's House",
                        "Annual family Easter dinner. Everyone is welcome to bring a dish!",
                    ),
                    (
                        "Summer BBQ",
                        "2024-07-04 16:00",
                        "Backyard",
                        "Independence Day celebration with grilling and fireworks.",
                    ),
                    (
                        "Thanksgiving Dinner",
                        "2024-11-28 16:00",
                        "Grandma's House",
                        "Traditional Thanksgiving dinner with the whole family.",
                    ),
                ]
                cur.executemany(
                    "INSERT INTO events (title, date, location, description) VALUES (%s, %s, %s, %s)",
                    sample_events,
                )
            conn.commit()

    def get_events(self) -> List[Dict[str, Any]]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM events ORDER BY date")
            return list(cur.fetchall())

    def get_upcoming_events(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        query = "SELECT * FROM events WHERE date >= %s ORDER BY date"
        params: List[Any] = [now]
        if limit is not None:
            query += " LIMIT %s"
            params.append(limit)
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(query, params)
            return list(cur.fetchall())

    def get_event_by_id(self, event_id: int) -> Optional[Dict[str, Any]]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM events WHERE id = %s", (event_id,))
            return cur.fetchone()

    def add_event(self, title: str, date: str, location: str, description: str) -> Dict[str, Any]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO events (title, date, location, description) VALUES (%s, %s, %s, %s) RETURNING *",
                (title, date, location, description),
            )
            event = cur.fetchone()
            conn.commit()
            return event

    def update_event(
        self, event_id: int, title: str, date: str, location: str, description: str
    ) -> Optional[Dict[str, Any]]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                UPDATE events
                SET title = %s, date = %s, location = %s, description = %s
                WHERE id = %s
                RETURNING *
                """,
                (title, date, location, description, event_id),
            )
            event = cur.fetchone()
            conn.commit()
            return event

    def delete_event(self, event_id: int) -> bool:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM events WHERE id = %s", (event_id,))
            deleted = cur.rowcount > 0
            conn.commit()
            return deleted

    def get_dish_categories(self) -> List[Dict[str, Any]]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM dish_categories ORDER BY name")
            return list(cur.fetchall())

    def get_dishes_for_event(self, event_id: int) -> List[Dict[str, Any]]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT d.*, c.name AS category_name
                FROM dishes d
                JOIN dish_categories c ON d.category_id = c.id
                WHERE d.event_id = %s
                ORDER BY c.name, d.name
                """,
                (event_id,),
            )
            return list(cur.fetchall())

    def get_dish_by_id(self, dish_id: int) -> Optional[Dict[str, Any]]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT d.*, c.name AS category_name
                FROM dishes d
                JOIN dish_categories c ON d.category_id = c.id
                WHERE d.id = %s
                """,
                (dish_id,),
            )
            return cur.fetchone()

    def add_dish(
        self,
        event_id: int,
        name: str,
        category_id: int,
        person_name: str,
        description: str = "",
        serves: int = 0,
    ) -> Dict[str, Any]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1 FROM events WHERE id = %s", (event_id,))
            if not cur.fetchone():
                raise ValueError(f"Event with ID {event_id} does not exist")

            cur.execute("SELECT 1 FROM dish_categories WHERE id = %s", (category_id,))
            if not cur.fetchone():
                raise ValueError(f"Category with ID {category_id} does not exist")

            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute(
                """
                INSERT INTO dishes (event_id, name, category_id, person_name, description, serves, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (event_id, name, category_id, person_name, description, serves, created_at),
            )
            dish_id = cur.fetchone()["id"]
            cur.execute(
                """
                SELECT d.*, c.name AS category_name
                FROM dishes d
                JOIN dish_categories c ON d.category_id = c.id
                WHERE d.id = %s
                """,
                (dish_id,),
            )
            dish = cur.fetchone()
            conn.commit()
            return dish

    def update_dish(
        self,
        dish_id: int,
        name: str,
        category_id: int,
        person_name: str,
        description: str = "",
        serves: int = 0,
    ) -> Optional[Dict[str, Any]]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1 FROM dishes WHERE id = %s", (dish_id,))
            if not cur.fetchone():
                return None

            cur.execute("SELECT 1 FROM dish_categories WHERE id = %s", (category_id,))
            if not cur.fetchone():
                raise ValueError(f"Category with ID {category_id} does not exist")

            cur.execute(
                """
                UPDATE dishes
                SET name = %s, category_id = %s, person_name = %s, description = %s, serves = %s
                WHERE id = %s
                RETURNING id
                """,
                (name, category_id, person_name, description, serves, dish_id),
            )
            updated = cur.fetchone()
            if not updated:
                return None
            cur.execute(
                """
                SELECT d.*, c.name AS category_name
                FROM dishes d
                JOIN dish_categories c ON d.category_id = c.id
                WHERE d.id = %s
                """,
                (dish_id,),
            )
            dish = cur.fetchone()
            conn.commit()
            return dish

    def delete_dish(self, dish_id: int) -> bool:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM dishes WHERE id = %s", (dish_id,))
            deleted = cur.rowcount > 0
            conn.commit()
            return deleted
