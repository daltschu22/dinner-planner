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
        
        # Check if we need to add sample data
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
