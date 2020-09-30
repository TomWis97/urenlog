from datetime import date
from datetime import timedelta
from database import DatabaseLogic

class HoursCLI:
    def __init__(self, database_path):
        self.db = DatabaseLogic(database_path)

    def codeFuzzySearch(self, query):
        """Search for a code with query in displayname."""
        codes = self.db.getCodes()
        result = False
        for code in codes:
            if query.lower() in code[0].lower():
                # If we have a match
                if result is False:
                    result = code
                else:
                    raise ValueError("Multiple results")
        return result 

    def addHoursToday(self, code, amount, comment=""):
        """Add hours for today."""
        entryDate = date.today()
        self.db.addHours(entryDate, code, amount, comment)

    def getHoursToday(self):
        """Return hours written for today."""
        hours = self.db.getTotalHoursByDate(date.today())
        return hours[0]

    def getCategoriesToday(self):
        """Return hours per category for today."""
        hourscat = self.db.getHoursByDate(date.today())
        return hourscat

    def renderTable(self, columns, data, colsep=" ", total=None):
        """Render a table with columns as title with 2D list as data."""
        # Amount of columns.
        num_columns = len(columns)
        # Array for column width
        col_width = []
        for column in columns:
            col_width.append(len(column))

        for index, current_width in enumerate(col_width):
            # Update the width for every column.
            tmp_current_width = current_width # Modifying current_width in the loop causes problems
            for item in data:
                if len(str(item[index])) > tmp_current_width:
                    col_width[index] = len(str(item[index]))
                    tmp_current_width = len(str(item[index]))
        
        # Initialize variable for table
        table = ""

        for index, column in enumerate(columns):
            table = table + str(column).ljust(col_width[index])
            if index == len(columns) - 1:
                # This is the last item
                table = table + "\n"
            else:
                table = table + colsep
        
        # Add line under headers.
        total_width = sum(col_width) + ( (len(col_width) - 1) * len(colsep))
        table = table + "-" * total_width + "\n"

        # Add data
        for row in data:
            for index, width in enumerate(col_width):
                table = table + str(row[index]).ljust(width)
                if index == (len(col_width) - 1):
                    # Last item
                    table = table + "\n"
                else:
                    # We need a seperator
                    table = table + colsep
        if total != None:
            # Add line
            table = table + "=" * total_width + "\n"
            # Add total line
            table = table + "Total".rjust(sum(col_width[:-1])) + colsep + str(total) + "\n"
        return table
