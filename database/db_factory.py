import os
from typing import Optional
from .db_interface import DatabaseInterface
from .sqlite_db import SQLiteDatabase

try:
    from .postgres_db import PostgresDatabase
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

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
        
        backend = os.environ.get("DB_BACKEND", "sqlite").lower()
        has_redis_url = "REDIS_URL" in os.environ
        database_url = os.environ.get("DATABASE_URL", "")

        if backend == "postgres":
            if not POSTGRES_AVAILABLE:
                raise RuntimeError("PostgreSQL backend requested but psycopg is not installed")
            cls._instance = PostgresDatabase(database_url)
            print("Using PostgreSQL database")
            cls._instance.initialize()
            return cls._instance

        # Optional Redis backend if explicitly enabled.
        if backend == 'redis' and has_redis_url and REDIS_AVAILABLE:
            try:
                cls._instance = KVDatabase()
                print("Using Redis database")
            except Exception as e:
                print(f"Failed to initialize Redis database: {e}")
                print("Falling back to SQLite database")
                cls._instance = SQLiteDatabase()
        else:
            # SQLite is the default for local and volume-backed deployments.
            db_path = os.environ.get('SQLITE_DB_PATH') or os.environ.get('DATABASE_PATH', 'dinner_planner.db')
            cls._instance = SQLiteDatabase(db_path)
            print(f"Using SQLite database at {db_path}")
        
        # Initialize the database
        cls._instance.initialize()
        
        return cls._instance 
