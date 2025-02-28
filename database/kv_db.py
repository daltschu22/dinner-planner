import os
import json
import redis
from typing import List, Dict, Any, Optional
from datetime import datetime
from .db_interface import DatabaseInterface

class KVDatabase(DatabaseInterface):
    """Redis implementation of the database interface for Vercel deployment."""
    
    def __init__(self):
        """Initialize the Redis database connection."""
        # Get Redis connection URL from environment variable
        redis_url = os.environ.get('REDIS_URL')
        
        if not redis_url:
            raise EnvironmentError("REDIS_URL environment variable is not set")
        
        # Initialize Redis client
        self.redis = redis.Redis.from_url(redis_url)
        
        # Key prefixes for different data types
        self.EVENT_PREFIX = "event:"
        self.EVENT_IDS_KEY = "event_ids"
        self.COUNTER_KEY = "counter"
    
    def initialize(self) -> None:
        """Initialize the database, creating necessary keys if they don't exist."""
        # Check if we need to initialize the counter
        if not self.redis.exists(self.COUNTER_KEY):
            self.redis.set(self.COUNTER_KEY, "0")
        
        # Check if we need to initialize the event IDs set
        if not self.redis.exists(self.EVENT_IDS_KEY):
            # Redis sets can't be empty, so we don't need to initialize it
            pass
        
        # Check if we need to add sample data
        event_ids = self.redis.smembers(self.EVENT_IDS_KEY)
        if not event_ids:
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
                self.add_event(
                    event['title'],
                    event['date'],
                    event['location'],
                    event['description']
                )
    
    def _get_next_id(self) -> int:
        """Get the next available ID and increment the counter."""
        # Increment the counter and return the new value
        return int(self.redis.incr(self.COUNTER_KEY))
    
    def get_events(self) -> List[Dict[str, Any]]:
        """Get all events from the database."""
        event_ids = self.redis.smembers(self.EVENT_IDS_KEY)
        if not event_ids:
            return []
        
        # Convert bytes IDs to integers
        event_ids = [int(id.decode('utf-8')) for id in event_ids]
        
        # Get all events
        events = []
        for event_id in event_ids:
            event_key = f"{self.EVENT_PREFIX}{event_id}"
            event_json = self.redis.get(event_key)
            if event_json:
                event = json.loads(event_json)
                events.append(event)
        
        # Sort events by date
        events.sort(key=lambda x: x['date'])
        return events
    
    def get_upcoming_events(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get upcoming events (events with dates in the future)."""
        now = datetime.now()
        all_events = self.get_events()
        
        # Filter for upcoming events
        upcoming_events = []
        for event in all_events:
            event_date = datetime.strptime(event['date'], '%Y-%m-%d %H:%M')
            if event_date >= now:
                upcoming_events.append(event)
        
        # Sort by date
        upcoming_events.sort(key=lambda x: x['date'])
        
        # Apply limit if specified
        if limit and limit > 0:
            upcoming_events = upcoming_events[:limit]
            
        return upcoming_events
    
    def get_event_by_id(self, event_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific event by ID."""
        event_key = f"{self.EVENT_PREFIX}{event_id}"
        event_json = self.redis.get(event_key)
        
        if event_json:
            return json.loads(event_json)
        return None
    
    def add_event(self, title: str, date: str, location: str, description: str) -> Dict[str, Any]:
        """Add a new event to the database."""
        # Get a new ID
        event_id = self._get_next_id()
        
        # Create the event
        event = {
            'id': event_id,
            'title': title,
            'date': date,
            'location': location,
            'description': description
        }
        
        # Store the event
        event_key = f"{self.EVENT_PREFIX}{event_id}"
        self.redis.set(event_key, json.dumps(event))
        
        # Add the event ID to the set of all event IDs
        self.redis.sadd(self.EVENT_IDS_KEY, str(event_id))
        
        return event
    
    def update_event(self, event_id: int, title: str, date: str, location: str, description: str) -> Optional[Dict[str, Any]]:
        """Update an existing event."""
        event_key = f"{self.EVENT_PREFIX}{event_id}"
        
        # Check if the event exists
        if not self.redis.exists(event_key):
            return None
        
        # Update the event
        event = {
            'id': event_id,
            'title': title,
            'date': date,
            'location': location,
            'description': description
        }
        
        self.redis.set(event_key, json.dumps(event))
        return event
    
    def delete_event(self, event_id: int) -> bool:
        """Delete an event from the database."""
        event_key = f"{self.EVENT_PREFIX}{event_id}"
        
        # Check if the event exists
        if not self.redis.exists(event_key):
            return False
        
        # Delete the event
        self.redis.delete(event_key)
        
        # Remove the event ID from the set of all event IDs
        self.redis.srem(self.EVENT_IDS_KEY, str(event_id))
        
        return True 
