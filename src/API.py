import sqlite3
import os

# Get current path and join with database path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def parse_tuple(tuple):
    i = 1
    out = tuple[0]
    while i < len(tuple):
        out = out + ", " + tuple[i]
        i+=1
    return out

def whitelist_char(value):
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
    value_list = list(value)
    if not value or value[0] in "0123456789":
        return False
    for char in value:
        if char not in allowed:
            return False
    return True

def INIT(folder_name, db_name="Database"):
    global DB
    global CUR
    global DB_PATH


    if not whitelist_char(folder_name):
        raise ValueError(f"Invalid Folder Name: {folder_name}")
    if not whitelist_char(db_name):
        raise ValueError(f"Invalid DB Name: {db_name}")
    

    for i in range(3):
        if os.path.isdir(folder_name):
            try:
                DB_PATH = os.path.join(folder_name, (".".join([db_name, "db"])))
                break
            except OSError:
                raise(ValueError("Error Creating folder."))
        else:
            try: 
                os.mkdir(folder_name)
            except OSError:
                raise(ValueError("Error Creating folder."))
    
    try:
        DB = sqlite3.connect(DB_PATH)
        CUR = DB.cursor()
    except sqlite3.Error:
        raise(ValueError("Error Creating DB or Cursor."))


def CREATE(Name, Sub_Value: tuple, Type="TABLE"):

    # check for unlisted characters
    if not whitelist_char(Name):
        raise ValueError(f"Invalid Table Name: {Name}")
    

    for col_def in Sub_Value:
        parts = col_def.split()
        for part in parts:
            if not whitelist_char(part):
                raise ValueError(f"Invalid Sub Value part: {part}")

    Type_upper = str.upper(Type)
    Typ = {"TABLE": "TABLE"}
    
    try:
        CUR.execute(f"CREATE {Typ[Type_upper]} {Name}({parse_tuple(Sub_Value)})")
    except KeyError:
        raise(ValueError(f"Unsupported Type: {Type}"))
    except Exception as e:
        raise e
    

def INSERT(table_name, Column: tuple, Values: tuple):
    print(table_name, parse_tuple(Column), parse_tuple(Values))