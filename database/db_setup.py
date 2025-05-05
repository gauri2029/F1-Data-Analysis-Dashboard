import sqlite3
import os
import traceback
import sys

def get_db_path():
    """Returns the path to the SQLite database file"""
    # Create the database directory if it doesn't exist
    db_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database')
    os.makedirs(db_dir, exist_ok=True)
    
    # Define the database file path
    return os.path.join(db_dir, 'f1_database.db')

def init_db():
    """Initialize the database by creating all tables"""
    db_path = get_db_path()
    
    try:
        db_exists = os.path.exists(db_path)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')
        
        print(f"Schema path: {schema_path}")
        print(f"Schema exists: {os.path.exists(schema_path)}")
        
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema file not found at {schema_path}")
        
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
            
        try:
            cursor.executescript(schema_sql)
            print("Schema executed successfully")
        except sqlite3.Error as e:
            print(f"SQLite error executing schema: {e}")
            traceback.print_exc()
            raise
        
        conn.commit()
        conn.close()
        
        print("Database initialization completed successfully")
        return not db_exists
    
    except Exception as e:
        print(f"Error initializing database: {e}")
        traceback.print_exc()
        return False

def get_db_connection():
    """Get a connection to the SQLite database"""
    try:
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # When run directly, initialize the database
    created = init_db()
    if created:
        print("Database initialized with new schema!")
    else:
        print("Database schema refreshed!")