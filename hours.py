import npyscreen
import curses
import time
from database import DatabaseLogic
from datetime import date

class HoursApplication(npyscreen.NPSAppManaged):
    """Application which controls."""
    def onStart(self):
        # TODO: Make the path configurable. Not everyone is called Tom.
        self.db = DatabaseLogic("/home/tom/urenlog.sqlite")
        self.addForm('MAIN', MainHoursForm, name="Current hour entries")

class MainHoursForm(npyscreen.Form):
    """Shows a grid with all entries."""
    idList = []

    def create(self):
        self.buildCodesList() # Populate self.idList so we know the height to set.
        self.newdate = self.add(npyscreen.TitleDateCombo, name="Date", value="")
        self.newamount = self.add(npyscreen.TitleText, name="Amount", value="")
        self.newcode = self.add(npyscreen.TitleSelectOne, name="Hour code", max_height=len(self.idList) + 1)
        self.newcomment = self.add(npyscreen.TitleText, name="Comment", value="", max_height=2)
        self.submit = self.add(SubmitButton, name="Submit")
        self.hoursgrid = self.add(npyscreen.GridColTitles,
                                  columns=5,
                                  select_whole_line=True,
                                  col_titles=["Date", "Code", "Amount", "Comment", "ID"])
        self.hoursgrid.add_handlers({curses.ascii.NL: self.selectRow})

    def beforeEditing(self):
        self.newdate.value = date.today()
        #self.newdate.value = ""
        self.newcode.value = ""
        self.newamount.value = ""
        self.newcode.values = self.buildCodesList()
        data = self.parentApp.db.getAllHours()
        if len(data) == 0:
            data = [["No entries found.", "-", "-", "-", "-"]]
        self.hoursgrid.values = data
        self.editw = 3

    def buildCodesList(self):
        """Returns a list of codes.
        Also sets variable within form for linking index to id."""
        codes = self.parentApp.db.getCodes()
        displayList = []
        idList = []
        for code in codes:
            displayList.append(code[0])
            idList.append(code[4])
        self.idList = idList
        return displayList

    def afterEditing(self):
        print(self.newamount.value)

    def selectRow(self, input):
        selectedRow = self.hoursgrid.selected_row()
        if selectedRow[4] == "-":
            # The default No entries-entry has been selected.
            return
        result = npyscreen.notify_ok_cancel(
            "Do you want to delete the entry on {} for {} hour(s)?".format(
                selectedRow[0], selectedRow[2]))
        if result:
            self.parentApp.db.deleteHours(selectedRow[4])
            self.parentApp.switchForm('MAIN')

class SubmitButton(npyscreen.ButtonPress):
    def whenPressed(self):
        entryComment = self.parent.newcomment.value
        entryDate = self.parent.newdate.value
        if not isinstance(entryDate, date):
            npyscreen.notify("Please select a date.",
                             title="No date selected")
            time.sleep(2)
            self.parent.display()
            return
        try:
            entryAmount = float(self.parent.newamount.value.replace(",", "."))
        except:
            npyscreen.notify("Value for amount of hours is not a number.",
                             title="Error in input")
            time.sleep(2)
            self.parent.display()
            return
        try:
            entryCode = self.parent.idList[self.parent.newcode.value[0]]
        except:
            npyscreen.notify("Please select a code.",
                             title="No code selected")
            time.sleep(2)
            self.parent.display()
            return
        # If we reach here, all information should be valid.
        self.parent.parentApp.db.addHours(
            entryDate, entryCode, entryAmount, entryComment)
        self.parent.newamount.value = ""
        self.parent.newcode.value = ""
        self.parent.newcomment.value = ""
        self.parent.parentApp.switchForm('MAIN')
        self.parent.editw = 2
        self.parent.editing = False

if __name__ == "__main__":
    UrenApp = HoursApplication().run()
