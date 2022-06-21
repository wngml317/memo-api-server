import mysql.connector

def get_connection() :
    connection = mysql.connector.connect(
        host = 'database-1.c8z17ubvxzpp.ap-northeast-2.rds.amazonaws.com',
        database = 'memo_db',
        user = 'memo_user',
        password = '1234'
    )

    return connection