import os
import sqlite3


class INIT:
    def __init__(self, folder_name, db_name="Database", check_same_thread: bool = True):
        # Base pathing setup relative to file location
        self.current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        if not self._whitelist_char(folder_name) or not self._whitelist_char(db_name):
            raise ValueError(f"Invalid Names: {folder_name} or {db_name}.")

        self.target_dir = os.path.join(self.current_dir, folder_name)
        self.db_path = os.path.join(self.target_dir, f"{db_name}.db")

        try:
            os.makedirs(self.target_dir, exist_ok=True)
            self.db = sqlite3.connect(
                self.db_path, timeout=10, check_same_thread=check_same_thread
            )
            self.cur = self.db.cursor()
            self.db.row_factory = sqlite3.Row
        except Exception as e:
            print(f"Internal Trace: {e}")
            raise RuntimeError(f"Failed to initialize database: {e}")

    def _parse_tuple(self, data_tuple):
        return ", ".join(map(str, data_tuple))

    def _whitelist_char(self, value):
        allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
        if not value or value[0] in "0123456789":
            return False
        return all(char in allowed for char in value)

    def CREATE(
        self,
        Table_Name,
        Column_Names,
        Column_Data_Types=(),
        Type="TABLE",
    ):
        # Normalized inputs safely into local scope variable arrays
        norm_data_types = (
            [Column_Data_Types]
            if isinstance(Column_Data_Types, str)
            else list(Column_Data_Types)
        )
        norm_col_names = (
            [Column_Names] if isinstance(Column_Names, str) else list(Column_Names)
        )

        if not self._whitelist_char(Table_Name):
            raise ValueError(f"Invalid Table Name: {Table_Name}")

        final_definitions = []
        for i in range(len(norm_col_names)):
            col_name = norm_col_names[i]

            if not self._whitelist_char(col_name):
                raise ValueError(f"Invalid Column Name: {col_name}")

            col_type = norm_data_types[i] if i < len(norm_data_types) else "TEXT"

            for part in col_type.split():
                if not self._whitelist_char(part):
                    raise ValueError(f"Invalid Type part: {part}")

            final_definitions.append(f"{col_name} {col_type}")

        col_string = ", ".join(final_definitions)
        Type_upper = str.upper(Type)
        Typ = {"TABLE": "TABLE"}

        query = f"CREATE {Typ[Type_upper]} IF NOT EXISTS {Table_Name} ({col_string})"

        try:
            self.cur.execute(query)
            self.db.commit()
            return True
        except KeyError:
            raise ValueError(f"Unsupported Type: {Type}")
        except Exception as e:
            raise e

    def INSERT(self, table_name, Row_Data, Targeted_Columns=()):
        norm_row_data = (
            (Row_Data,) if isinstance(Row_Data, (str, int, float)) else Row_Data
        )
        norm_targeted_cols = (
            (Targeted_Columns,)
            if isinstance(Targeted_Columns, str)
            else Targeted_Columns
        )

        if not self._whitelist_char(table_name):
            raise ValueError(f"Invalid Table Name: {table_name}")

        Qholder = ", ".join(["?" for _ in norm_row_data])
        cols_part = ""

        if len(norm_targeted_cols) > 0:
            for col in norm_targeted_cols:
                if not self._whitelist_char(col):
                    raise ValueError(f"Invalid Column Name: {col}")
            cols_part = f"({', '.join(norm_targeted_cols)})"

        try:
            query = f"INSERT INTO {table_name} {cols_part} VALUES ({Qholder})"
            self.cur.execute(query, norm_row_data)
            self.db.commit()
            return True
        except Exception as e:
            print(f"Internal Trace: {e}")
            raise ValueError("Error Inserting Data.")

    def GET(
        self,
        table_name: str,
        Targeted_Columns=None,
        Look_for_Data=None,
        Fetch_Columns="*",
    ):
        if Fetch_Columns != "*" and not self._whitelist_char(Fetch_Columns):
            raise ValueError(f"Invalid Type: {Fetch_Columns}")

        if not self._whitelist_char(table_name):
            raise ValueError(f"Invalid Table Name: {table_name}")

        query = f"SELECT {Fetch_Columns} FROM {table_name}"
        params = ()

        if Targeted_Columns and Look_for_Data is not None:
            if not self._whitelist_char(Targeted_Columns):
                raise ValueError("Invalid Search Column")

            query += f" WHERE {Targeted_Columns} = ?"
            params = (Look_for_Data,)

        try:
            self.cur.execute(query, params)
            return self.cur.fetchall()
        except Exception as e:
            raise ValueError(f"Could not GET Data. {e}")

    def GET_ONE(
        self, table_name, Look_in_Column=None, Look_for_Data=None, Fetch_Columns="*"
    ):
        results = self.GET(table_name, Look_in_Column, Look_for_Data, Fetch_Columns)

        if not results:
            return None

        first_row = results[0]
        return first_row if Fetch_Columns == "*" else first_row[0]

    def UPDATE(
        self, table_name, New_Row_Data=None, Targeted_Column=None, Condition: str = None
    ):
        norm_row_data = (
            (New_Row_Data,)
            if isinstance(New_Row_Data, (str, int, float))
            else New_Row_Data
        )
        norm_targeted_col = (
            (Targeted_Column,) if isinstance(Targeted_Column, str) else Targeted_Column
        )

        if len(norm_row_data) != len(norm_targeted_col):
            raise ValueError(
                f"Counts don't match: {len(norm_row_data)} values vs {len(norm_targeted_col)} columns."
            )

        for col in norm_targeted_col:
            if not self._whitelist_char(col):
                raise ValueError(f"Invalid Column Name: {col}")

        if not self._whitelist_char(table_name):
            raise ValueError(f"Invalid Table Name: {table_name}")

        set_parts = [f"{col} = ?" for col in norm_targeted_col]
        set_string = ", ".join(set_parts)

        if Condition:
            query = f"UPDATE {table_name} SET {set_string} WHERE {Condition}"
        else:
            query = f"UPDATE {table_name} SET {set_string}"

        try:
            self.cur.execute(query, norm_row_data)
            self.db.commit()
            return True
        except Exception as e:
            print(f"Internal Trace: {e}")
            raise ValueError("Error Updating Data.")

    def DELETE(
        self, table_name: str, Targeted_Column=None, Row_Data=None, Condition: str = ""
    ):
        if not self._whitelist_char(table_name):
            raise ValueError(f"Invalid Table: {table_name}")

        query = f"DELETE FROM {table_name}"
        params = ()

        if Targeted_Column and Row_Data is not None:
            if not self._whitelist_char(Targeted_Column):
                raise ValueError(f"Invalid Column: {Targeted_Column}")

            # If the user passed a tuple/list of multiple items
            if isinstance(Row_Data, (tuple, list)) and len(Row_Data) > 1:
                # Create placeholders like (?, ?) based on how many items are in the tuple
                placeholders = ", ".join(["?" for _ in Row_Data])
                query += f" WHERE {Targeted_Column} IN ({placeholders})"
                params = tuple(Row_Data)  # Pass the whole tuple straight to execute
            else:
                # If it's just a single item (unwrap tuple if necessary)
                actual_data = (
                    Row_Data[0] if isinstance(Row_Data, (tuple, list)) else Row_Data
                )
                query += f" WHERE {Targeted_Column} = ?"
                params = (actual_data,)

        elif Condition:
            query += f" WHERE {Condition}"

        try:
            self.cur.execute(query, params)
            self.db.commit()
            return True
        except Exception as e:
            print(f"Delete Error: {e}")
            return False

    def DROP(self, table_name: str):
        if not self._whitelist_char(table_name):
            raise ValueError(f"Invalid Table: {table_name}")

        query = f"DROP TABLE IF EXISTS {table_name}"

        try:
            self.cur.execute(query)
            self.db.commit()
            return True
        except Exception as e:
            print(f"Drop Failed: {e}")
            return False

    def EXECUTE(self, command: str):
        try:
            self.cur.execute(command)
            self.db.commit()
            return True
        except Exception as e:
            raise ValueError(f"Could not execute custom command: {command}. Trace: {e}")

    def STOP(self):
        if self.db:
            self.db.commit()
            self.db.close()
            self.db = None
            self.cur = None
            return True
        return False
