import sqlite3
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from .db_interface import DatabaseInterface

class SQLiteDatabase(DatabaseInterface):
    """SQLite implementation of the database interface."""
    
    def __init__(self, db_path: str = 'dinner_planner.db'):
        """
        Initialize the SQLite database.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def _connect(self):
        """Establish a connection to the database."""
        self.conn = sqlite3.connect(self.db_path)
        # Configure SQLite to return dictionaries for rows
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    def _disconnect(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
    
    def initialize(self) -> None:
        """Initialize the database, creating tables if they don't exist."""
        self._connect()
        
        # Create events table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT
        )
        ''')
        
        # Create dish categories table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS dish_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
        ''')
        
        # Create dishes table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS dishes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            category_id INTEGER NOT NULL,
            person_name TEXT NOT NULL,
            description TEXT,
            serves INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (event_id) REFERENCES events (id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES dish_categories (id)
        )
        ''')
        
        # Check if we need to add sample dish categories
        self.cursor.execute("SELECT COUNT(*) FROM dish_categories")
        count = self.cursor.fetchone()[0]
        
        # Add sample dish categories if the table is empty
        if count == 0:
            categories = [
                "Appetizer",
                "Main Dish",
                "Side Dish",
                "Salad",
                "Dessert",
                "Bread",
                "Beverage"
            ]
            
            for category in categories:
                self.cursor.execute(
                    "INSERT INTO dish_categories (name) VALUES (?)",
                    (category,)
                )
        
        # Check if we need to add sample data for events
        self.cursor.execute("SELECT COUNT(*) FROM events")
        count = self.cursor.fetchone()[0]
        
        # Add sample data if the table is empty
        if count == 0:
            sample_events = [
                {
                    'title': 'Easter Dinner',
                    'date': '2024-03-31 17:00',
                    'location': 'Mom\'s House',
                    'description': 'Annual family Easter dinner. Everyone is welcome to bring a dish!'
                },
                {
                    'title': 'Summer BBQ',
                    'date': '2024-07-04 16:00',
                    'location': 'Backyard',
                    'description': 'Independence Day celebration with grilling and fireworks.'
                },
                {
                    'title': 'Thanksgiving Dinner',
                    'date': '2024-11-28 16:00',
                    'location': 'Grandma\'s House',
                    'description': 'Traditional Thanksgiving dinner with the whole family.'
                }
            ]
            
            for event in sample_events:
                self.cursor.execute(
                    "INSERT INTO events (title, date, location, description) VALUES (?, ?, ?, ?)",
                    (event['title'], event['date'], event['location'], event['description'])
                )
        
        self.conn.commit()
        self._disconnect()
    
    def get_events(self) -> List[Dict[str, Any]]:
        """Get all events from the database."""
        self._connect()
        self.cursor.execute("SELECT * FROM events ORDER BY date")
        events = [dict(row) for row in self.cursor.fetchall()]
        self._disconnect()
        return events
    
    def get_upcoming_events(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get upcoming events (events with dates in the future)."""
        self._connect()
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        query = "SELECT * FROM events WHERE date >= ? ORDER BY date"
        if limit:
            query += f" LIMIT {limit}"
        
        self.cursor.execute(query, (now,))
        events = [dict(row) for row in self.cursor.fetchall()]
        self._disconnect()
        return events
    
    def get_event_by_id(self, event_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific event by ID."""
        self._connect()
        self.cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        event = self.cursor.fetchone()
        self._disconnect()
        
        if event:
            return dict(event)
        return None
    
    def add_event(self, title: str, date: str, location: str, description: str) -> Dict[str, Any]:
        """Add a new event to the database."""
        self._connect()
        self.cursor.execute(
            "INSERT INTO events (title, date, location, description) VALUES (?, ?, ?, ?)",
            (title, date, location, description)
        )
        event_id = self.cursor.lastrowid
        self.conn.commit()
        
        # Fetch the newly created event
        self.cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        event = dict(self.cursor.fetchone())
        
        self._disconnect()
        return event
    
    def update_event(self, event_id: int, title: str, date: str, location: str, description: str) -> Optional[Dict[str, Any]]:
        """Update an existing event."""
        self._connect()
        
        # Check if the event exists
        self.cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        if not self.cursor.fetchone():
            self._disconnect()
            return None
        
        # Update the event
        self.cursor.execute(
            "UPDATE events SET title = ?, date = ?, location = ?, description = ? WHERE id = ?",
            (title, date, location, description, event_id)
        )
        self.conn.commit()
        
        # Fetch the updated event
        self.cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        event = dict(self.cursor.fetchone())
        
        self._disconnect()
        return event
    
    def delete_event(self, event_id: int) -> bool:
        """Delete an event from the database."""
        self._connect()
        
        # Check if the event exists
        self.cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        if not self.cursor.fetchone():
            self._disconnect()
            return False
        
        # Delete the event
        self.cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
        self.conn.commit()
        self._disconnect()
        return True
    
    # Methods for dish sign-ups - Phase 5
    
    def get_dish_categories(self) -> List[Dict[str, Any]]:
        """Get all dish categories."""
        self._connect()
        self.cursor.execute("SELECT * FROM dish_categories ORDER BY name")
        categories = [dict(row) for row in self.cursor.fetchall()]
        self._disconnect()
        return categories
    
    def get_dishes_for_event(self, event_id: int) -> List[Dict[str, Any]]:
        """Get all dishes signed up for a specific event."""
        self._connect()
        self.cursor.execute("""
            SELECT d.*, c.name as category_name 
            FROM dishes d
            JOIN dish_categories c ON d.category_id = c.id
            WHERE d.event_id = ?
            ORDER BY c.name, d.name
        """, (event_id,))
        dishes = [dict(row) for row in self.cursor.fetchall()]
        self._disconnect()
        return dishes
    
    def get_dish_by_id(self, dish_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific dish by ID."""
        self._connect()
        self.cursor.execute("""
            SELECT d.*, c.name as category_name 
            FROM dishes d
            JOIN dish_categories c ON d.category_id = c.id
            WHERE d.id = ?
        """, (dish_id,))
        dish = self.cursor.fetchone()
        self._disconnect()
        
        if dish:
            return dict(dish)
        return None
    
    def add_dish(self, event_id: int, name: str, category_id: int, 
                person_name: str, description: str = "", 
                serves: int = 0) -> Dict[str, Any]:
        """Add a new dish to an event."""
        self._connect()
        
        # Check if the event exists
        self.cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        if not self.cursor.fetchone():
            self._disconnect()
            raise ValueError(f"Event with ID {event_id} does not exist")
        
        # Check if the category exists
        self.cursor.execute("SELECT * FROM dish_categories WHERE id = ?", (category_id,))
        if not self.cursor.fetchone():
            self._disconnect()
            raise ValueError(f"Category with ID {category_id} does not exist")
        
        # Get current timestamp
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Insert the dish
        self.cursor.execute(
            """
            INSERT INTO dishes 
            (event_id, name, category_id, person_name, description, serves, created_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (event_id, name, category_id, person_name, description, serves, created_at)
        )
        dish_id = self.cursor.lastrowid
        self.conn.commit()
        
        # Fetch the newly created dish with category name
        self.cursor.execute("""
            SELECT d.*, c.name as category_name 
            FROM dishes d
            JOIN dish_categories c ON d.category_id = c.id
            WHERE d.id = ?
        """, (dish_id,))
        dish = dict(self.cursor.fetchone())
        
        self._disconnect()
        return dish
    
    def update_dish(self, dish_id: int, name: str, category_id: int, 
                   person_name: str, description: str = "", 
                   serves: int = 0) -> Optional[Dict[str, Any]]:
        """Update an existing dish."""
        self._connect()
        
        # Check if the dish exists
        self.cursor.execute("SELECT * FROM dishes WHERE id = ?", (dish_id,))
        if not self.cursor.fetchone():
            self._disconnect()
            return None
        
        # Check if the category exists
        self.cursor.execute("SELECT * FROM dish_categories WHERE id = ?", (category_id,))
        if not self.cursor.fetchone():
            self._disconnect()
            raise ValueError(f"Category with ID {category_id} does not exist")
        
        # Update the dish
        self.cursor.execute(
            """
            UPDATE dishes 
            SET name = ?, category_id = ?, person_name = ?, description = ?, serves = ?
            WHERE id = ?
            """,
            (name, category_id, person_name, description, serves, dish_id)
        )
        self.conn.commit()
        
        # Fetch the updated dish with category name
        self.cursor.execute("""
            SELECT d.*, c.name as category_name 
            FROM dishes d
            JOIN dish_categories c ON d.category_id = c.id
            WHERE d.id = ?
        """, (dish_id,))
        dish = dict(self.cursor.fetchone())
        
        self._disconnect()
        return dish
    
    def delete_dish(self, dish_id: int) -> bool:
        """Delete a dish from the database."""
        self._connect()
        
        # Check if the dish exists
        self.cursor.execute("SELECT * FROM dishes WHERE id = ?", (dish_id,))
        if not self.cursor.fetchone():
            self._disconnect()
            return False
        
        # Delete the dish
        self.cursor.execute("DELETE FROM dishes WHERE id = ?", (dish_id,))
        self.conn.commit()
        self._disconnect()
        return True 
