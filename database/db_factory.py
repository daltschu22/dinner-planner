import os
from typing import Optional
from .db_interface import DatabaseInterface
from .sqlite_db import SQLiteDatabase

# Try to import the KV database, but don't fail if it's not available
try:
    from .kv_db import KVDatabase
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

class DatabaseFactory:
    """Factory class to create the appropriate database implementation."""
    
    _instance: Optional[DatabaseInterface] = None
    
    @classmethod
    def get_database(cls) -> DatabaseInterface:
        """
        Get the appropriate database implementation based on the environment.
        
        Returns:
            An instance of a class implementing DatabaseInterface
        """
        # If we already have an instance, return it (singleton pattern)
        if cls._instance is not None:
            return cls._instance
        
        # Check if we're running on Vercel or if REDIS_URL is set
        is_vercel = os.environ.get('VERCEL', '0') == '1'
        has_redis_url = 'REDIS_URL' in os.environ
        
        # If we're on Vercel or have a Redis URL, and Redis is available, use it
        if (is_vercel or has_redis_url) and REDIS_AVAILABLE:
            try:
                cls._instance = KVDatabase()
                print("Using Redis database")
            except Exception as e:
                print(f"Failed to initialize Redis database: {e}")
                print("Falling back to SQLite database")
                cls._instance = SQLiteDatabase()
        else:
            # Use SQLite for local development
            db_path = os.environ.get('SQLITE_DB_PATH', 'dinner_planner.db')
            cls._instance = SQLiteDatabase(db_path)
            print(f"Using SQLite database at {db_path}")
        
        # Initialize the database
        cls._instance.initialize()
        
        return cls._instance 
