import os
import psycopg2
import urlparse

class dbhandler:
    'Handle database connection and updates'

    def __init__(self):
        urlparse.uses_netloc.append("postgres")

        url = urlparse.urlparse(os.environ["DATABASE_URL"])

        self.conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )

        self.cur = self.conn.cursor()

        self.cur.execute("CREATE TABLE IF NOT EXISTS timestamps (starttime INTEGER PRIMARY KEY);")

        self.conn.commit()

    def __del__(self):
        self.cur.close()
        self.conn.close()

    def exists(self, timestamp):
        self.cur.execute("SELECT starttime FROM timestamps WHERE starttime = (%s);", (timestamp,))
        res = self.cur.fetchone()
        print res
        if not res:
            return False
        else:
            return True

    def addToDb(self, timestamp):
        print "Adding {} to DB".format(timestamp)
        try:
            self.cur.execute("INSERT INTO timestamps(starttime) VALUES (%s);", (timestamp,))
            self.conn.commit()
        except psycopg2.IntegrityError:
            self.conn.rollback()
            print "DB Insert failure for {}".format(timestamp)

    def deleteOldTimestamps(self, timestamp):
        print "Deleting all timestamps before {}".format(timestamp)
        try:
            self.cur.execute("DELETE FROM timestamps WHERE starttime < (%s);", (timestamp,))
            self.conn.commit()
        except psycopg2.IntegrityError:
            self.conn.rollback()
            print "DB delete failure for {}".format(timestamp)


    def printAll(self):
        self.cur.execute("SELECT starttime FROM timestamps;")
        res = self.cur.fetchall()
        print res

    def dropTable(self):
        self.cur.execute("DROP TABLE timestamps;")
        self.conn.commit()
