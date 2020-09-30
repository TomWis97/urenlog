import npyscreen
import curses
import calendar
import datetime
from database import DatabaseLogic

class OverviewApplication(npyscreen.NPSAppManaged):
    """Application which controls."""

    configuration = {
            'database_path': None,
            'labels_amount': None,
            'labels_width': None}

    def configure(self, configuration):
        """Configure the application."""
        self.configuration['database_path'] = configuration['database']['path']
        self.configuration['labels_amount'] = int(configuration['overview']['labels'])
        self.configuration['labels_width'] = int(configuration['overview']['labels_width'])
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
                             relx=self.parentApp.configuration['labels_width']+6,
                             columns=31,
                             select_whole_line=True)
        self.labels = []
        for x in range(self.parentApp.configuration['labels_amount']):
            self.labels.append(self.add(
                CodeLabel,
                name="-"*self.parentApp.configuration['labels_width'],
                width=self.parentApp.configuration['labels_width'],
                rely=4+x,
                relx=1))

    def beforeEditing(self):
        # Reset grid
        for label in self.labels:
            label.name = "-"*self.parentApp.configuration['labels_width']
        self.grid.values = []

        self.currentmonth.value = self.parentApp.logic.currentMonth()
        self.data = self.parentApp.logic.loadData()
        self.grid.col_titles = list(self.data.keys())
        self.month_codes = self.parentApp.logic.getCodesForMonth()
        self.label_list = self.month_codes
        self.grid.values = self.parentApp.logic.buildOverviewList(
            self.data,
            self.month_codes,
            self.parentApp.configuration['labels_amount'])

        not_enough_labels = False
        current_label = 0
        for code in self.label_list:
            try:
                self.labels[current_label].name = code[0]
                self.labels[current_label].setVars(code[1])
                current_label += 1
            except IndexError:
                not_enough_labels = True

        if not_enough_labels:
            npyscreen.notify_confirm("Not enough labels to display all codes.\n"
                                     "Please change the \"labels\" parameter in "
                                     "the configuration file.")

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
    def setVars(self, sapcode):
        if sapcode == None:
            self.more_info = None
        else:
            self.more_info = ("SAP Code: {}\n"
                              "SAP Name: {}").format(sapcode, self.name)
    def whenPressed(self):
        if self.more_info == None:
            return
        npyscreen.notify_confirm(self.more_info, title=self.name)

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
        """Return a list of days in selected month."""
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
            allData[date.day] = self.db.getHoursAndSapCodesByDate(date)
        return allData

    def getCodesForMonth(self):
        """List all codes for month."""
        """Return a list (entry for each code) of
        tuples (SAP code, SAP name)., """
        codes = {}
        for day in self.loadData().values():
            for code in day:
                codes[code[1]] = code[2]
                
        # Convert to list of tuples for keeping order.
        codes_list = []
        for code, name in codes.items():
            codes_list.append((code, name))

        # Sort list by code
        codes_list.sort(key=lambda x:x[0])

        return codes_list

    def buildOverviewList(self, data, codes, max_length):
        """Convert from list per day to list per code.
        Expects paramters from loadData() and getCodesForMonth()"""
        overview_data = []
        for code in codes:
            if len(overview_data) == max_length:
                # Don't display values without label.
                break
            current_code = []
            for day_number in sorted(data.keys()):
                day = data[day_number]
                day_code_combo = ""
                for day_entry in day:
                    if day_entry[1] == code[0]:
                        day_code_combo = day_entry[0]
                if day_code_combo == "":
                    day_code_combo = "-"
                current_code.append(day_code_combo)
            overview_data.append(current_code)
        if len(overview_data) == 0:
            # No data. Display dashes.
            filler_row = []
            for day in data.keys():
                filler_row.append('-')
            overview_data.append(filler_row)
        return overview_data

def test(db_path, year, month):
    db = DatabaseLogic(db_path)
    o = OverviewLogic(db)
    o.changeMonth(year, month)
    print(o.loadData())
    print(o.getCodesForMonth())

