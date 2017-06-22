# Import builtin module
import mysql.connector
# Import custom module
import config

DBHOST = config.DBHOST
DBNAME = config.DBNAME
DBUSER = config.DBUSER
DBPASS = config.DBPASS

def sql_query(query=None, host=DBHOST, database=DBNAME, user=DBUSER, password=DBPASS, connection_timeout=5):
    conn = mysql.connector.connect(host=host, database=database, user=user, password=password)
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

def sql_insert(query=None, host=DBHOST, database=DBNAME, user=DBUSER, password=DBPASS, connection_timeout=30):
    import mysql.connector
    conn = mysql.connector.connect(host=host, database=database, user=user, password=password)
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()