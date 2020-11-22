import sqlite3

 class SQLiteConnection():
    def __init__(self, instance):
        self.instance = instance

    def connection(self):
        try:
            connection = sqlite3.connect(f"file://{self.instance}", uri=True)
            return connection
        except Error:
            print(Error)
        
    def ticketReport(self, ticketNumber):
        connection = self.connection()
        cursor = connection.cursor()
        cursor.execute(f'SELECT * FROM ticket WHERE ticket="{ticketNumber}" ORDER BY id DESC LIMIT 1;')
        result = cursor.fetchone()
        connection.close()
        return result