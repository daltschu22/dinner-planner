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
    
    # Methods for dish sign-ups will be added in Phase 5 
