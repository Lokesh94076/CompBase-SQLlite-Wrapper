import sqlite3
import os

# Get current path
CURRENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def parse_tuple(data_tuple):
    return ", ".join(map(str, data_tuple))

def whitelist_char(value):
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
    value_list = list(value)
    if not value or value[0] in "0123456789":
        return True
    for char in value:
        if char not in allowed:
            return False
    return True

def INIT(folder_name, db_name="Database"):
    global DB, CUR, DB_PATH

    if not whitelist_char(folder_name):
        raise ValueError(f"Invalid Folder Name: {folder_name}")
    if not whitelist_char(db_name):
        raise ValueError(f"Invalid DB Name: {db_name}")
    
    TARGET_DIR = os.path.join(CURRENT_DIR, folder_name)
    DB_PATH = os.path.join(TARGET_DIR, f"{db_name}.db")

    try:
        os.makedirs(TARGET_DIR, exist_ok=True)
        DB = sqlite3.connect(DB_PATH)
        CUR = DB.cursor()
        DB.row_factory = sqlite3.Row
        return True
    except Exception as e:
        print(f"Internal Trace: {e}")
        raise ValueError("Error Creating DB or Cursor.")

def CREATE(Table_Name, Column_Names: tuple, Column_Data_Types: tuple= (), Type="TABLE"):

    if isinstance(Column_Data_Types, str):
        Column_Data_Types = [Column_Data_Types]
        
    # Same for Columns just in case
    if isinstance(Column_Names, str):
        Column_Names = [Column_Names]

    final_definitions = []

    # check for unlisted characters
    if not whitelist_char(Table_Name):
        raise ValueError(f"Invalid Table Name: {Table_Name}")
    for col_def in Column_Names:
        parts = col_def.split()
        for part in parts:
            if not whitelist_char(part):
                raise ValueError(f"Invalid Sub Value part: {part}")


    for i in range(len(Column_Names)):
        col_name = Column_Names[i]
        

        if not whitelist_char(col_name):
            raise ValueError(f"Invalid Column Name: {col_name}")
            

        if i < len(Column_Data_Types):
            col_type = Column_Data_Types[i]
        else:
            col_type = "TEXT"

        for part in col_type.split():
            if not whitelist_char(part):
                raise ValueError(f"Invalid Type part: {part}")


        final_definitions.append(f"{col_name} {col_type}")

    col_string = ", ".join(final_definitions)
    Type_upper = str.upper(Type)
    Typ = {"TABLE": "TABLE"}

    query = f"CREATE {Typ[Type_upper]} IF NOT EXISTS {Table_Name} ({col_string})"

    try:
        CUR.execute(query)
        DB.commit()
        return True
    except KeyError:
        raise(ValueError(f"Unsupported Type: {Type}"))
    except Exception as e:
        raise e
    
def INSERT(table_name, Row_Data: tuple, Targeted_Columns: tuple= ()):

    # check for unlisted characters
    if isinstance(Row_Data, (str, int, float)): Row_Data = (Row_Data,)
    if isinstance(Targeted_Columns, str): Targeted_Columns = (Targeted_Columns,)

    if not whitelist_char(table_name):
        raise ValueError(f"Invalid Table Name: {table_name}")
    
    Qholder = ", ".join(["?" for _ in Row_Data])

    if len(Targeted_Columns) == 0:

        cols_part = ""
    else:
        for col in Targeted_Columns:
            if not whitelist_char(col):
                raise ValueError(f"Invalid Column Name: {col}")
        cols_part = f"({', '.join(Targeted_Columns)})"

    try:
        query = f"INSERT INTO {table_name} {cols_part} VALUES ({Qholder})"
        CUR.execute(query, Row_Data)
        DB.commit()
        return True
    except Exception as e:
        print(f"Internal Trace: {e}")
        raise ValueError("Error Inserting Data.")
        
def GET(table_name: str, Targeted_Columns=None, Look_for_Data=None, Fetch_Columns="*"):

    select_arg = ["*"]

    if Fetch_Columns in select_arg:
        pass
    elif not whitelist_char(Fetch_Columns):
        raise(ValueError(f"Invalid Type: {Fetch_Columns}"))
    
    if not whitelist_char(table_name):
        raise(ValueError(f"Invalid Table Name: {table_name}"))
    
    query = f"SELECT {Fetch_Columns} FROM {table_name}"
    params = ()

    if Targeted_Columns and Look_for_Data is not None:
        if not whitelist_char(Targeted_Columns): raise ValueError("Invalid Search Column")
        
        query += f" WHERE {Targeted_Columns} = ?"
        params = (Look_for_Data,)
    try:
        CUR.execute(query, params)
        return CUR.fetchall()
    except Exception as e:
        raise(ValueError(f"Could not GET Data. {e}"))
    
def GET_ONE(table_name, Look_in_Column=None, Look_for_Data=None, Fetch_Columns="*"):
    # 1. Reuse your existing GET logic
    results = GET(table_name, Look_in_Column, Look_for_Data, Fetch_Columns)
    
    if not results:
        return None

    first_row = results[0]
    
    if Fetch_Columns == "*":
        return first_row
    else:
        return first_row[0]

def UPDATE(table_name, New_Row_Data=None, Targeted_Column=None, Condition:str=None):

    # check for unlisted characters
    if isinstance(New_Row_Data, (str, int, float)): New_Row_Data = (New_Row_Data,)
    if isinstance(Targeted_Column, str): Targeted_Column = (Targeted_Column,)

    if len(New_Row_Data) != len(Targeted_Column):
        raise ValueError(f"Counts don't match: {len(New_Row_Data)} values vs {len(Targeted_Column)} columns.")

    for i in range(len(Targeted_Column)):
        if not whitelist_char(Targeted_Column[i]):
            raise ValueError(f"Invalid Column Name: {Targeted_Column[i]}")

    if not whitelist_char(table_name):
        raise ValueError(f"Invalid Table Name: {table_name}")
    
    
    set_parts = [f"{col} = ?" for col in Targeted_Column]
    set_string = ", ".join(set_parts)
    

    if Condition:
        query = f"UPDATE {table_name} SET {set_string} WHERE {Condition}"
    else:
        query = f"UPDATE {table_name} SET {set_string}"

    try:
        CUR.execute(query, New_Row_Data)
        DB.commit()
        return True
    except Exception as e:
        print(f"Internal Trace: {e}")
        raise ValueError("Error Updating Data.")
    
def DELETE(table_name: str, Targeted_Column=None, Row_Data=None, Condition:str=None):

    if not whitelist_char(table_name): 
        raise ValueError(f"Invalid Table: {table_name}")
    

    query = f"DELETE FROM {table_name}"
    params = ()

    # 2. Reuse the same "Targeting" logic
    if Targeted_Column and Row_Data is not None:
        if not whitelist_char(Targeted_Column): 
            raise ValueError(f"Invalid Column: {Targeted_Column}")
        
        query += f" WHERE {Targeted_Column} = ?"
        params = (Row_Data,)
    
    # 3. Execute and Commit
    try:
        CUR.execute(query, params)
        DB.commit()
        return True
    except Exception as e:
        print(f"Delete Error: {e}")
        return False
    
def DROP(table_name: str):
    if not whitelist_char(table_name): 
        raise ValueError(f"Invalid Table: {table_name}")
    
    query = f"DROP TABLE IF EXISTS {table_name}"
    
    try:
        CUR.execute(query)
        DB.commit()
        return True
    except Exception as e:
        print(f"Drop Failed: {e}")
        return False
    
def EXECUTE(command:str):

    try:
        CUR.execute(command)
        DB.commit()
        return True
    except Exception as e:
        raise(ValueError(f"Could not execute custom command: {command}"))
    
def STOP():

    global DB, CUR
    if DB:
        DB.commit()
        DB.close()
        DB = None
        CUR = None
        return True
    