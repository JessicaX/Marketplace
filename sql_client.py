import mysql.connector
from datetime import datetime

class MySqlClient():
    def __init__(self):
        self.mydb = mysql.connector.connect(
            host="104.197.80.146",
            user="cs6400",
            passwd="xx", # please check with me the password
            database="cs6400"
        )

    def get_latest_items(self):
        mycursor = self.mydb.cursor(buffered=True)
        mycursor.execute('''SELECT u.Name as Username, i.* FROM items i 
                            INNER JOIN users u ON i.UserId = u.Id
                            LIMIT 20;''')
        result = []
        columns = tuple( [d[0] for d in mycursor.description] )
        for row in mycursor:
            result.append(dict(zip(columns, row)))
            
        return result

    def check_username(self, username):
        result = self.get_user_by_name(username)
        return len(result)

    def register(self, username, password):
        try:
            cursor = self.mydb.cursor()
            cursor.execute('''Insert into users (Name, password, Email, JoinTime) values (%s, %s, %s, %s)''', (username, password, '', datetime.now()))
            self.mydb.commit()
        except Exception as e:
            print(e)
            return 0
        return cursor.rowcount

    def get_user_by_name(self, name):
        result = self._select("SELECT * from users where name = '%s';"%name)
        if len(result) > 0:
            return result[0]
        else:
            return None

    def get_user_by_username_password(self, name, password):
        result = self._select("SELECT * from users where name = '%s' and password = '%s';" % (name, password))
        if len(result) > 0:
            return result[0]
        else:
            return None

    def _select(self, sql):
        mycursor = self.mydb.cursor(buffered=True)
        mycursor.execute(sql)
        return self._parse_result(mycursor)

    def _parse_result(self, mycursor):
        result = []
        columns = tuple( [d[0] for d in mycursor.description] )
        for row in mycursor:
            result.append(dict(zip(columns, row)))
        return result