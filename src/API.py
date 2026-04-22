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
        return True
    except Exception as e:
        print(f"Internal Trace: {e}")
        raise ValueError("Error Creating DB or Cursor.")

def CREATE(Name, Sub_Value: tuple, Sub_Value_Types: tuple= (), Type="TABLE"):

    if isinstance(Sub_Value_Types, str):
        Sub_Value_Types = [Sub_Value_Types]
        
    # Same for Columns just in case
    if isinstance(Sub_Value, str):
        Sub_Value = [Sub_Value]

    final_definitions = []

    # check for unlisted characters
    if not whitelist_char(Name):
        raise ValueError(f"Invalid Table Name: {Name}")
    for col_def in Sub_Value:
        parts = col_def.split()
        for part in parts:
            if not whitelist_char(part):
                raise ValueError(f"Invalid Sub Value part: {part}")


    for i in range(len(Sub_Value)):
        col_name = Sub_Value[i]
        

        if not whitelist_char(col_name):
            raise ValueError(f"Invalid Column Name: {col_name}")
            

        if i < len(Sub_Value_Types):
            col_type = Sub_Value_Types[i]
        else:
            col_type = "TEXT"

        for part in col_type.split():
            if not whitelist_char(part):
                raise ValueError(f"Invalid Type part: {part}")


        final_definitions.append(f"{col_name} {col_type}")

    col_string = ", ".join(final_definitions)
    Type_upper = str.upper(Type)
    Typ = {"TABLE": "TABLE"}

    query = f"CREATE {Typ[Type_upper]} IF NOT EXISTS {Name} ({col_string})"

    try:
        CUR.execute(query)
        DB.commit()
        return True
    except KeyError:
        raise(ValueError(f"Unsupported Type: {Type}"))
    except Exception as e:
        raise e
    
def INSERT(table_name, Values: tuple, Column: tuple= ()):

    # check for unlisted characters
    if isinstance(Values, (str, int, float)): Values = (Values,)
    if isinstance(Column, str): Column = (Column,)

    if not whitelist_char(table_name):
        raise ValueError(f"Invalid Table Name: {table_name}")
    
    Qholder = ", ".join(["?" for _ in Values])

    if len(Column) == 0:

        cols_part = ""
    else:
        for col in Column:
            if not whitelist_char(col):
                raise ValueError(f"Invalid Column Name: {col}")
        cols_part = f"({', '.join(Column)})"

    try:
        query = f"INSERT INTO {table_name} {cols_part} VALUES ({Qholder})"
        CUR.execute(query, Values)
        DB.commit()
    except Exception as e:
        print(f"Internal Trace: {e}")
        raise ValueError("Error Inserting Data.")

    return True

def GET(table_name: str, column="*", Search_Column=None, Search_Value=None):

    select_arg = ["*"]

    if column in select_arg:
        pass
    elif not whitelist_char(column):
        raise(ValueError(f"Invalid Type: {column}"))
    
    if not whitelist_char(table_name):
        raise(ValueError(f"Invalid Table Name: {table_name}"))
    
    query = f"SELECT {column} FROM {table_name}"
    params = ()

    if Search_Column and Search_Value is not None:
        if not whitelist_char(Search_Column): raise ValueError("Invalid Search Column")
        
        query += f" WHERE {Search_Column} = ?"
        params = (Search_Value,)
    try:
        DB.row_factory = sqlite3.Row
        CUR.execute(query, params)
        return CUR.fetchall()
    except Exception as e:
        raise(ValueError(f"Could not GET Data. {e}"))
    
def UPDATE(table_name, Values: tuple, Column: tuple, Condition:str=None):

    # check for unlisted characters
    if isinstance(Values, (str, int, float)): Values = (Values,)
    if isinstance(Column, str): Column = (Column,)

    if len(Values) != len(Column):
        raise ValueError(f"Counts don't match: {len(Values)} values vs {len(Column)} columns.")

    for i in range(len(Column)):
        if not whitelist_char(Column[i]):
            raise ValueError(f"Invalid Column Name: {Column[i]}")

    if not whitelist_char(table_name):
        raise ValueError(f"Invalid Table Name: {table_name}")
    
    
    set_parts = [f"{col} = ?" for col in Column]
    set_string = ", ".join(set_parts)
    

    if Condition:
        query = f"UPDATE {table_name} SET {set_string} WHERE {Condition}"
    else:
        query = f"UPDATE {table_name} SET {set_string}"

    try:
        print(query, parse_tuple(Values))
        CUR.execute(query, Values)
        DB.commit()
        return True
    except Exception as e:
        print(f"Internal Trace: {e}")
        raise ValueError("Error Updating Data.")
    