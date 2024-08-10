import os
from tinydb import TinyDB

# Path to the TinyDB database file
db_file = 'db.json'

# Option 1: Clear All Documents from Each Table
def clear_all_tables():
    db = TinyDB(db_file)
    tables = db.tables()
    for table_name in tables:
        table = db.table(table_name)
        table.truncate()  # Remove all documents
    print("All data has been flushed from all tables.")

# Option 2: Delete the Database File
def delete_database_file():
    if os.path.exists(db_file):
        os.remove(db_file)
        print("Database file has been deleted.")
    else:
        print("Database file does not exist.")

# Choose which option to execute
if __name__ == "__main__":
    # Uncomment the method you want to use
    clear_all_tables()  # Clear all data from all tables
    # delete_database_file()  # Delete the database file
