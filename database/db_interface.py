from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

class DatabaseInterface(ABC):
    """
    Abstract base class defining the interface for database operations.
    All database implementations must implement these methods.
    """
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the database, creating tables or structures as needed."""
        pass
    
    @abstractmethod
    def get_events(self) -> List[Dict[str, Any]]:
        """
        Get all events from the database.
        
        Returns:
            List of event dictionaries
        """
        pass
    
    @abstractmethod
    def get_upcoming_events(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get upcoming events (events with dates in the future).
        
        Args:
            limit: Optional maximum number of events to return
            
        Returns:
            List of event dictionaries
        """
        pass
    
    @abstractmethod
    def get_event_by_id(self, event_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific event by ID.
        
        Args:
            event_id: The ID of the event to retrieve
            
        Returns:
            Event dictionary or None if not found
        """
        pass
    
    @abstractmethod
    def add_event(self, title: str, date: str, location: str, description: str) -> Dict[str, Any]:
        """
        Add a new event to the database.
        
        Args:
            title: Event title
            date: Event date and time (format: 'YYYY-MM-DD HH:MM')
            location: Event location
            description: Event description
            
        Returns:
            The newly created event dictionary
        """
        pass
    
    @abstractmethod
    def update_event(self, event_id: int, title: str, date: str, location: str, description: str) -> Optional[Dict[str, Any]]:
        """
        Update an existing event.
        
        Args:
            event_id: The ID of the event to update
            title: New event title
            date: New event date and time
            location: New event location
            description: New event description
            
        Returns:
            Updated event dictionary or None if event not found
        """
        pass
    
    @abstractmethod
    def delete_event(self, event_id: int) -> bool:
        """
        Delete an event from the database.
        
        Args:
            event_id: The ID of the event to delete
            
        Returns:
            True if the event was deleted, False otherwise
        """
        pass
    
    # Methods for dish sign-ups - Phase 5
    
    @abstractmethod
    def get_dish_categories(self) -> List[Dict[str, Any]]:
        """
        Get all dish categories.
        
        Returns:
            List of category dictionaries with 'id' and 'name' keys
        """
        pass
    
    @abstractmethod
    def get_dishes_for_event(self, event_id: int) -> List[Dict[str, Any]]:
        """
        Get all dishes signed up for a specific event.
        
        Args:
            event_id: The ID of the event
            
        Returns:
            List of dish dictionaries
        """
        pass
    
    @abstractmethod
    def get_dish_by_id(self, dish_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific dish by ID.
        
        Args:
            dish_id: The ID of the dish to retrieve
            
        Returns:
            Dish dictionary or None if not found
        """
        pass
    
    @abstractmethod
    def add_dish(self, event_id: int, name: str, category_id: int, 
                person_name: str, description: str = "", 
                serves: int = 0) -> Dict[str, Any]:
        """
        Add a new dish to an event.
        
        Args:
            event_id: The ID of the event
            name: Name of the dish
            category_id: Category ID of the dish
            person_name: Name of the person bringing the dish
            description: Optional description of the dish
            serves: Optional number of people the dish serves
            
        Returns:
            The newly created dish dictionary
        """
        pass
    
    @abstractmethod
    def update_dish(self, dish_id: int, name: str, category_id: int, 
                   person_name: str, description: str = "", 
                   serves: int = 0) -> Optional[Dict[str, Any]]:
        """
        Update an existing dish.
        
        Args:
            dish_id: The ID of the dish to update
            name: New name of the dish
            category_id: New category ID
            person_name: New name of the person bringing the dish
            description: New description
            serves: New number of people the dish serves
            
        Returns:
            Updated dish dictionary or None if dish not found
        """
        pass
    
    @abstractmethod
    def delete_dish(self, dish_id: int) -> bool:
        """
        Delete a dish from the database.
        
        Args:
            dish_id: The ID of the dish to delete
            
        Returns:
            True if the dish was deleted, False otherwise
        """
        pass
