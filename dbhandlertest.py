import dbhandler

dbh = dbhandler.dbhandler()

#dbh.addToDb(124)
dbh.dropTable()
#dbh.deleteOldTimestamps(1480730400)
dbh.printAll()