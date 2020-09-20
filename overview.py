import npyscreen
import curses
import calendar
import datetime
from database import DatabaseLogic

class OverviewApplication(npyscreen.NPSAppManaged):
    """Application which controls."""

    configuration = {
            'database_path': None}

    def configure(self, database_path):
        """Configure the application."""
        self.configuration['database_path'] = database_path
        self.db = DatabaseLogic(self.configuration['database_path'])
        self.logic = OverviewLogic(self.db)

    def onStart(self):
        self.addForm('MAIN', OverviewForm, name="Overview entries")

    def changeMonth(self, year, month):
        self.logic.changeMonth(year, month)

class OverviewForm(npyscreen.FormBaseNew):
    def create(self):
        self.exitButton = self.add(ExitButton, rely=1, width=6, name="Exit")
        self.previousmonth = self.add(MonthPreviousButton,
                                      name="<",
                                      rely=1,
                                      relx=9,
                                      width=3)
        self.currentmonth = self.add(npyscreen.FixedText,
                                     value="XX - XXXX",
                                     width=11,
                                     relx=14,
                                     rely=1)
        self.nextmonth = self.add(MonthNextButton,
                                  name=">",
                                  width=3,
                                  relx=24,
                                  rely=1)
        self.grid = self.add(npyscreen.GridColTitles,
                             relx=20,
                             columns=31,
                             select_whole_line=True)
        self.labels = []
        for x in range(10):
            self.labels.append(self.add(
                CodeLabel,
                name="---",
                width=10,
                rely=5+x,
                relx=1))

    def beforeEditing(self):
        self.currentmonth.value = self.parentApp.logic.currentMonth()
        self.data = self.parentApp.logic.loadData()
        self.grid.col_titles = list(self.data.keys())
        #self.grid = self.add(npyscreen.GridColTitles,
        #                     columns=len(self.data),
        #                     col_titles=list(self.data.keys()),
        #                     select_whole_line=True)

class MonthPreviousButton(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.logic.previousMonth()
        self.parent.parentApp.switchForm('MAIN')

class MonthNextButton(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.logic.nextMonth()
        self.parent.parentApp.switchForm('MAIN')

class ExitButton(npyscreen.ButtonPress):
   def whenPressed(self):
        self.parent.parentApp.switchForm(None)
        print(self.parent.parentApp.logic.currentMonth())

class CodeLabel(npyscreen.ButtonPress):
    def whenPressed(self):
        notify_confirm.notify_confirm("Hello, world", title="test")

class OverviewLogic:
    selectedYear = None
    selectedMonth = None
    def __init__(self, db):
        today = datetime.date.today()
        self.selectedYear = today.year
        self.selectedMonth = today.month
        self.db = db

    def currentMonth(self):
        """Return readable current month."""
        text = "{} - {}".format(self.selectedMonth, self.selectedYear)
        return text

    def changeMonth(self, year, month):
        if not 1 <= month <=12:
            raise ValueError("Not a month")
        if not 2000 <= year <= 2050:
            raise ValueError("Not a probable year")
        self.selectedYear = year
        self.selectedMonth = month

    def nextMonth(self):
        currentMonth = self.selectedMonth
        currentYear = self.selectedYear
        if currentMonth == 12:
            # Next month is next year
            self.selectedYear = currentYear + 1
            self.selectedMonth = 1
        else:
            self.selectedMonth = currentMonth + 1

    def previousMonth(self):
        currentMonth = self.selectedMonth
        currentYear = self.selectedYear
        if currentMonth == 1:
            # Previous month is previous year
            self.selectedYear = currentYear - 1
            self.selectedMonth = 12
        else:
            self.selectedMonth = currentMonth - 1

    def _loadMonthData(self):
        monthDays = []
        dates = calendar.Calendar().itermonthdates(
            self.selectedYear, self.selectedMonth)
        for date in dates:
            if date.month == self.selectedMonth:
                monthDays.append(date)
        return monthDays

    def loadData(self):
        """Return a dictionary with per day in month a key.
        Every key contains a dictionary with per code a key."""
        allData = {}
        for date in self._loadMonthData():
            allData[date.day] = self.db.getHoursByDate(date)
        return allData

    def getCodesForMonth(self):
        """List all codes for month."""
        codes = []
        for day in self.loadData().values():
            for code in day:
                if code[0] not in codes:
                    codes.append(code[0])
        return codes

def test(db_path, year, month):
    db = DatabaseLogic(db_path)
    o = OverviewLogic(db)
    o.changeMonth(year, month)
    print(o.loadData())
    print(o.getCodesForMonth())

