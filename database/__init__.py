from .db_factory import DatabaseFactory

# Convenience function to get the database instance
def get_db():
    return DatabaseFactory.get_database() 
