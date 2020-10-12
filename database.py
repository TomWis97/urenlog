import sqlite3

class DatabaseLogic:
    def __init__(self, path):
        self.connection = sqlite3.connect(path)
        self.initializeDatabase()

    def initializeDatabase(self):
        # Idk how to properly indent this.
        # But also I'm not using enough docstrings.
        #self.connection.execute('''DROP TABLE codes''')
        #self.connection.execute('''DROP TABLE hours''')
        self.connection.execute('''CREATE TABLE IF NOT EXISTS codes
            (displayname TEXT,
            sapcode TEXT,
            sapname TEXT,
            displayed BOOLEAN,
            internalid INTEGER PRIMARY KEY)''')
        self.connection.execute('''CREATE TABLE IF NOT EXISTS hours
            (date INTEGER,
            code INTEGER REFERENCES codes(internalid),
            amount REAL,
            comment TEXT,
            entryid INTEGER PRIMARY KEY)''')
        self.connection.commit()

    def _formatCodes(self, fetchall):
        """Formats data from fetchall()."""
        if len(fetchall) == 0:
            return []
        formattedList = []
        for item in fetchall:
            currentItem = []
            # Put everything from tuple in a new list.
            # Processing where required.
            currentItem.append(item[0]) #displayname
            currentItem.append(item[1]) #sapcode
            currentItem.append(item[2]) #sapname
            # Processing displayed. SQlite does not really know booleans
            if item[3] == 0:
                currentItem.append(False) #displayed
            elif item[3] == 1:
                currentItem.append(True) #displayed
            else:
                ValueError("This is not a boolean and should never happen")
            currentItem.append(item[4]) #internalid
            formattedList.append(currentItem)
        return formattedList

    def _formatCodesAndTotals(self, fetchall):
        """Formats data from fetchall()."""
        if len(fetchall) == 0:
            return []
        formattedList = []
        for item in fetchall:
            currentItem = []
            # Put everything from tuple in a new list.
            # Processing where required.
            currentItem.append(item[0]) #displayname
            currentItem.append(item[1]) #sapcode
            currentItem.append(item[2]) #sapname
            # Processing displayed. SQlite does not really know booleans
            if item[3] == 0:
                currentItem.append(False) #displayed
            elif item[3] == 1:
                currentItem.append(True) #displayed
            else:
                ValueError("This is not a boolean and should never happen")
            currentItem.append(item[4]) #Total for code
            currentItem.append(item[5]) #internalid
            formattedList.append(currentItem)
        return formattedList

    def getAllCodes(self):
        """Return a 2D array with all codes."""
        cur = self.connection.cursor()
        cur.execute('''SELECT * FROM codes
                    ORDER BY codes.displayed DESC''')
        return self._formatCodes(cur.fetchall())

    def getAllCodesAndTotals(self):
        """Return a 2D array with all codes with totals."""
        cur = self.connection.cursor()
        cur.execute('''SELECT codes.displayname, codes.sapcode, codes.sapname, codes.displayed, SUM(hours.amount), codes.internalid
                    FROM codes, hours
                    WHERE codes.internalid = hours.code
                    GROUP BY codes.internalid
                    ORDER BY codes.displayed DESC''')
        return self._formatCodesAndTotals(cur.fetchall())

    def getCodes(self):
        """Return a 2D array with only displayed codes."""
        cur = self.connection.cursor()
        cur.execute('''SELECT * FROM codes
                    WHERE displayed = 1
                    ORDER BY displayname''')
        return self._formatCodes(cur.fetchall())

    def addCode(self, displayname, sapname, sapcode, displayed):
        """Add a code to the database. Parameters: (displayname (string),
        sapcode (string), sapname (string), displayed (boolean)."""
        if displayed:
            displayed_int = 1
        else:
            displayed_int = 0
        cur = self.connection.cursor()
        cur.execute('''INSERT INTO codes (displayname, sapcode, sapname, displayed) VALUES
                       (?, ?, ?, ?)''', (displayname, sapcode, sapname, displayed_int))
        self.connection.commit()
        return cur.lastrowid

    def editCode(self, displayname, sapname, sapcode, displayed, internalid):
        """Edit a code in the database."""
        if displayed:
            displayed_int = 1
        else:
            displayed_int = 0
        cur = self.connection.cursor()
        cur.execute('''UPDATE codes SET displayname = ?, sapcode = ?, sapname = ?, displayed = ?
                       WHERE internalid = ?''', (displayname, sapcode, sapname, displayed_int, internalid))
        self.connection.commit()

    def addHours(self, date, code, amount, comment=""):
        """Add an hours entry to the database."""
        date_str = date.isoformat()
        cur = self.connection.cursor()
        cur.execute('''INSERT INTO hours (date, code, amount, comment) VALUES
                       ( DATE( ? ), ?, ?, ?)''', (date_str, int(code), float(amount), comment))
        self.connection.commit()

    def getAllHours(self):
        """Return all hour entries."""
        # TODO Limit this because it might slow down the app when a lot of entries exist.
        cur = self.connection.cursor()
        cur.execute('''SELECT hours.date, codes.displayname, hours.amount, hours.comment, hours.entryid
                    FROM hours, codes WHERE hours.code = codes.internalid 
                    AND hours.date > DATE('1970-01-01') ORDER BY date DESC''')
        items = cur.fetchall()
        return items

    def deleteHours(self, entryid):
        """Delete an entry from Hours"""
        cur = self.connection.cursor()
        cur.execute('''DELETE FROM hours WHERE entryid = ?''', (str(entryid),))
        self.connection.commit()

    def getHoursByDate(self, date):
        """Get hours per category on date."""
        cur = self.connection.cursor()
        cur.execute('''SELECT codes.displayname, SUM(hours.amount) AS total
                       FROM codes, hours WHERE codes.internalid = hours.code AND
                       hours.date = DATE( ? ) GROUP BY hours.code''', (date.isoformat(),))
        return cur.fetchall()

    def getHoursAndSapCodesByDate(self, date):
        """Get hours and code information on date."""
        cur = self.connection.cursor()
        cur.execute('''SELECT SUM(hours.amount) AS total , codes.sapname, codes.sapcode
                       FROM codes, hours WHERE codes.internalid = hours.code AND
                       hours.date = DATE( ? ) GROUP BY codes.sapcode''', (date.isoformat(),))
        return cur.fetchall()

    def getTotalHoursByDate(self, date):
        """Return amount of hours on date."""
        cur = self.connection.cursor()
        cur.execute('''SELECT SUM(amount) AS total FROM hours WHERE date = DATE( ? )''',
                    (date.isoformat(),))
        result =  cur.fetchone()
        if result[0] == None:
            return 0
        else:
            return result[0]

if __name__ == "__main__":
    print("Please do not run this on it's own.")
    db = DatabaseLogic("/home/tom/urenlog.sqlite")
    db.addCode("Vakantie", "V", "Verlof", True)
    db.addCode("Foo", "f00", "foo", True)
    db.addCode("Bar", "b4r", "bar", False)
    db.editCode("EditedVakantie", "123abc", "Dingen", False, 1)
    print("getCodes()", db.getAllCodes())
