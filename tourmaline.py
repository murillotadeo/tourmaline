import sqlite3


class TourmalineTableConnector:
    def __init__(self, sql_connection, sql_cursor, table_name):
        self.cursor = sql_cursor
        self.connection = sql_connection
        self.table = table_name
        self.table_info = [info for info in self.cursor.execute(f"PRAGMA TABLE_INFO ({self.table})")]
        self.value_info = [(info[1], info[2], info[0]) for info in self.table_info]

    def get(self, key):
        self.cursor.execute(
            f"""
                SELECT * FROM {self.table} WHERE _p={key}
            """
        )
        sql_result = self.cursor.fetchone()
        dict_result = {"_p": key}

        for value_tuple in self.value_info:
            if value_tuple[1] == 'integer':
                converted_value = int(sql_result[value_tuple[2]])
            elif value_tuple[1] == 'text':
                converted_value = str(sql_result[value_tuple[2]])
            elif value_tuple[1] == 'real':
                converted_value = float(sql_result[value_tuple[2]])

            dict_result[value_tuple[0]] = converted_value

        return dict_result

    def update(self, structure):
        data_params = []
        data_values = []
        for key in structure.keys():
            data_params.append(f"{key}=?")
            data_values.append(structure[key])

        self.cursor.execute(f"UPDATE {self.table} SET {','.join(data_params)} WHERE _p={structure['_p']}", tuple(data_values))
        self.connection.commit()

    def insert(self, structure):
        total_keys = [key for key in structure.keys()]
        placeholders = ''
        values = []
        keys_iterated = []
        for key in total_keys:
            if type(structure[key]) == dict:
                total_keys.remove(key)
            keys_iterated.append(key)
            values.append(structure[key])
            placeholders += '?' + (',' if keys_iterated != total_keys else '')

        self.cursor.execute(f"INSERT INTO {self.table} VALUES ({placeholders})", tuple(values))
        self.connection.commit()

class Tourmaline:
    def __init__(self, database_name=None):
        if database_name is None:
            self.connection = sqlite3.connect('tourmaline.db')
        else:
            if not database_name.endswith('.db'):
                self.connection = sqlite3.connect(database_name + '.db')
            self.connection = sqlite3.connect(database_name)
        self.cursor = self.connection.cursor()

        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        for table in self.cursor.fetchall():
            setattr(self, table[0], TourmalineTableConnector(self.connection, self.cursor, table[0]))
