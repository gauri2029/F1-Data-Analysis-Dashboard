import sqlite3
import os

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
    
    # Check if database already exists
    db_exists = os.path.exists(db_path)
    
    # Create a connection to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Read and execute the schema.sql file
    schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
        
    cursor.executescript(schema_sql)
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    return not db_exists  # Return True if a new database was created

def get_db_connection():
    """Get a connection to the SQLite database"""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

if __name__ == "__main__":
    # When run directly, initialize the database
    created = init_db()
    if created:
        print("Database initialized with new schema!")
    else:
        print("Database schema refreshed!")