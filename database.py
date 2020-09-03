import sqlite3

class DatabaseLogic:
    def __init__(self, path):
        self.connection = sqlite3.connect(path)
        self.initializeDatabase()

    def initializeDatabase(self):
        # Idk how to properly indent this.
        # But also I'm not using enough docstrings.
        #self.connection.execute('''DROP TABLE codes''')
        self.connection.execute('''CREATE TABLE IF NOT EXISTS codes
            (displayname TEXT,
            sapcode TEXT,
            sapname TEXT,
            displayed BOOLEAN,
            internalid INTEGER PRIMARY KEY)''')
        self.connection.execute('''CREATE TABLE IF NOT EXISTS hours
            (date INTEGER,
            code INTEGER REFERENCES codes(internalid),
            amount INTEGER,
            comment TEXT)''')
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

    def getAllCodes(self):
        """Return a 2D array with all codes."""
        cur = self.connection.cursor()
        cur.execute('''SELECT * FROM codes
                    ORDER BY displayed DESC''')
        return self._formatCodes(cur.fetchall())

    def getCodes(self):
        """Return a 2D array with only displayed codes."""
        cur = self.connection.cursor()
        cur.execute('''SELECT * FROM codes
                    WHERE displayed = 1
                    ORDER BY displayname''')
        return self._formatCodes(cur.fetchall())

    def addCode(self, displayname, sapcode, sapname, displayed):
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

    def editCode(self, displayname, sapcode, sapname, displayed, internalid):
        """Edit a code in the database."""
        if displayed:
            displayed_int = 1
        else:
            displayed_int = 0
        cur = self.connection.cursor()
        cur.execute('''UPDATE codes SET displayname = ?, sapcode = ?, sapname = ?, displayed = ?
                       WHERE internalid = ?''', (displayname, sapcode, sapname, displayed_int, internalid))
        self.connection.commit()

if __name__ == "__main__":
    print("Please do not run this on it's own.")
    db = DatabaseLogic("/home/tom/urenlog.sqlite")
    db.addCode("Vakantie", "V", "Verlof", True)
    db.addCode("Foo", "f00", "foo", True)
    db.addCode("Bar", "b4r", "bar", False)
    db.editCode("EditedVakantie", "123abc", "Dingen", False, 1)
    print("getCodes()", db.getAllCodes())
