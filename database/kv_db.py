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
        self.DISH_PREFIX = "dish:"
        self.DISH_IDS_KEY = "dish_ids"
        self.DISH_EVENT_PREFIX = "dish_event:"
        self.CATEGORY_PREFIX = "category:"
        self.CATEGORY_IDS_KEY = "category_ids"
    
    def initialize(self) -> None:
        """Initialize the database, creating necessary keys if they don't exist."""
        # Check if we need to initialize the counter
        if not self.redis.exists(self.COUNTER_KEY):
            self.redis.set(self.COUNTER_KEY, "0")
        
        # Check if we need to initialize the event IDs set
        if not self.redis.exists(self.EVENT_IDS_KEY):
            # Redis sets can't be empty, so we don't need to initialize it
            pass
        
        # Check if we need to initialize dish categories
        if not self.redis.exists(self.CATEGORY_IDS_KEY):
            categories = [
                "Appetizer",
                "Main Dish",
                "Side Dish",
                "Salad",
                "Dessert",
                "Bread",
                "Beverage"
            ]
            
            for i, category in enumerate(categories, 1):
                category_key = f"{self.CATEGORY_PREFIX}{i}"
                self.redis.set(category_key, json.dumps({"id": i, "name": category}))
                self.redis.sadd(self.CATEGORY_IDS_KEY, str(i))
        
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
        
        # Get all dishes for this event
        dish_event_key = f"{self.DISH_EVENT_PREFIX}{event_id}"
        dish_ids = self.redis.smembers(dish_event_key)
        
        # Delete all dishes for this event
        for dish_id in dish_ids:
            dish_id = int(dish_id.decode('utf-8'))
            dish_key = f"{self.DISH_PREFIX}{dish_id}"
            self.redis.delete(dish_key)
            self.redis.srem(self.DISH_IDS_KEY, str(dish_id))
        
        # Delete the dish-event mapping
        self.redis.delete(dish_event_key)
        
        # Delete the event
        self.redis.delete(event_key)
        
        # Remove the event ID from the set of all event IDs
        self.redis.srem(self.EVENT_IDS_KEY, str(event_id))
        
        return True
    
    # Methods for dish sign-ups - Phase 5
    
    def get_dish_categories(self) -> List[Dict[str, Any]]:
        """Get all dish categories."""
        category_ids = self.redis.smembers(self.CATEGORY_IDS_KEY)
        if not category_ids:
            return []
        
        # Convert bytes IDs to integers
        category_ids = [int(id.decode('utf-8')) for id in category_ids]
        
        # Get all categories
        categories = []
        for category_id in category_ids:
            category_key = f"{self.CATEGORY_PREFIX}{category_id}"
            category_json = self.redis.get(category_key)
            if category_json:
                category = json.loads(category_json)
                categories.append(category)
        
        # Sort categories by name
        categories.sort(key=lambda x: x['name'])
        return categories
    
    def get_dishes_for_event(self, event_id: int) -> List[Dict[str, Any]]:
        """Get all dishes signed up for a specific event."""
        dish_event_key = f"{self.DISH_EVENT_PREFIX}{event_id}"
        dish_ids = self.redis.smembers(dish_event_key)
        if not dish_ids:
            return []
        
        # Convert bytes IDs to integers
        dish_ids = [int(id.decode('utf-8')) for id in dish_ids]
        
        # Get all dishes
        dishes = []
        for dish_id in dish_ids:
            dish_key = f"{self.DISH_PREFIX}{dish_id}"
            dish_json = self.redis.get(dish_key)
            if dish_json:
                dish = json.loads(dish_json)
                
                # Get category name
                category_id = dish['category_id']
                category_key = f"{self.CATEGORY_PREFIX}{category_id}"
                category_json = self.redis.get(category_key)
                if category_json:
                    category = json.loads(category_json)
                    dish['category_name'] = category['name']
                else:
                    dish['category_name'] = "Unknown"
                
                dishes.append(dish)
        
        # Sort dishes by category name, then dish name
        dishes.sort(key=lambda x: (x['category_name'], x['name']))
        return dishes
    
    def get_dish_by_id(self, dish_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific dish by ID."""
        dish_key = f"{self.DISH_PREFIX}{dish_id}"
        dish_json = self.redis.get(dish_key)
        
        if not dish_json:
            return None
        
        dish = json.loads(dish_json)
        
        # Get category name
        category_id = dish['category_id']
        category_key = f"{self.CATEGORY_PREFIX}{category_id}"
        category_json = self.redis.get(category_key)
        if category_json:
            category = json.loads(category_json)
            dish['category_name'] = category['name']
        else:
            dish['category_name'] = "Unknown"
        
        return dish
    
    def add_dish(self, event_id: int, name: str, category_id: int, 
                person_name: str, description: str = "", 
                serves: int = 0) -> Dict[str, Any]:
        """Add a new dish to an event."""
        # Check if the event exists
        event_key = f"{self.EVENT_PREFIX}{event_id}"
        if not self.redis.exists(event_key):
            raise ValueError(f"Event with ID {event_id} does not exist")
        
        # Check if the category exists
        category_key = f"{self.CATEGORY_PREFIX}{category_id}"
        if not self.redis.exists(category_key):
            raise ValueError(f"Category with ID {category_id} does not exist")
        
        # Get a new ID
        dish_id = self._get_next_id()
        
        # Get current timestamp
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create the dish
        dish = {
            'id': dish_id,
            'event_id': event_id,
            'name': name,
            'category_id': category_id,
            'person_name': person_name,
            'description': description,
            'serves': serves,
            'created_at': created_at
        }
        
        # Store the dish
        dish_key = f"{self.DISH_PREFIX}{dish_id}"
        self.redis.set(dish_key, json.dumps(dish))
        
        # Add the dish ID to the set of all dish IDs
        self.redis.sadd(self.DISH_IDS_KEY, str(dish_id))
        
        # Add the dish ID to the set of dishes for this event
        dish_event_key = f"{self.DISH_EVENT_PREFIX}{event_id}"
        self.redis.sadd(dish_event_key, str(dish_id))
        
        # Get category name for the response
        category_json = self.redis.get(category_key)
        if category_json:
            category = json.loads(category_json)
            dish['category_name'] = category['name']
        else:
            dish['category_name'] = "Unknown"
        
        return dish
    
    def update_dish(self, dish_id: int, name: str, category_id: int, 
                   person_name: str, description: str = "", 
                   serves: int = 0) -> Optional[Dict[str, Any]]:
        """Update an existing dish."""
        dish_key = f"{self.DISH_PREFIX}{dish_id}"
        
        # Check if the dish exists
        if not self.redis.exists(dish_key):
            return None
        
        # Check if the category exists
        category_key = f"{self.CATEGORY_PREFIX}{category_id}"
        if not self.redis.exists(category_key):
            raise ValueError(f"Category with ID {category_id} does not exist")
        
        # Get the existing dish to preserve event_id and created_at
        existing_dish_json = self.redis.get(dish_key)
        existing_dish = json.loads(existing_dish_json)
        
        # Update the dish
        dish = {
            'id': dish_id,
            'event_id': existing_dish['event_id'],
            'name': name,
            'category_id': category_id,
            'person_name': person_name,
            'description': description,
            'serves': serves,
            'created_at': existing_dish['created_at']
        }
        
        self.redis.set(dish_key, json.dumps(dish))
        
        # Get category name for the response
        category_json = self.redis.get(category_key)
        if category_json:
            category = json.loads(category_json)
            dish['category_name'] = category['name']
        else:
            dish['category_name'] = "Unknown"
        
        return dish
    
    def delete_dish(self, dish_id: int) -> bool:
        """Delete a dish from the database."""
        dish_key = f"{self.DISH_PREFIX}{dish_id}"
        
        # Check if the dish exists
        if not self.redis.exists(dish_key):
            return False
        
        # Get the dish to find its event_id
        dish_json = self.redis.get(dish_key)
        dish = json.loads(dish_json)
        event_id = dish['event_id']
        
        # Remove the dish ID from the set of dishes for this event
        dish_event_key = f"{self.DISH_EVENT_PREFIX}{event_id}"
        self.redis.srem(dish_event_key, str(dish_id))
        
        # Delete the dish
        self.redis.delete(dish_key)
        
        # Remove the dish ID from the set of all dish IDs
        self.redis.srem(self.DISH_IDS_KEY, str(dish_id))
        
        return True 
