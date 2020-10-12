import npyscreen
import curses
from database import DatabaseLogic

class CodeApplication(npyscreen.NPSAppManaged):
    """This is the main application. Loads other forms."""
    formEditPrefill = {'displayname': '', 'sapname': '', 'sapcode': '', 'displayed': False, 'internalid': None}

    configuration = {
        'database_path': None}

    def configure(self, database_path):
        """Configure the application."""
        self.configuration['database_path'] = database_path

    def onStart(self):
        self.addForm('MAIN', ShowCodesForm, name="Current codes")
        self.addForm('NEW', EnterCodeForm, name="New code entry")
        self.addForm('EDIT', EditCodeForm, name="Edit code entry")
        # Connect to database
        self.db = DatabaseLogic(self.configuration['database_path'])

class EnterCodeForm(npyscreen.Form):
    """This is the form for creating and editing codes."""
    def create(self):
        self.displayname = self.add(npyscreen.TitleText, name="Display Name", value="")
        self.sapcode = self.add(npyscreen.TitleText, name="SAP code", value="")
        self.sapname = self.add(npyscreen.TitleText, name="Name in SAP", value="")
        self.displayed = self.add(npyscreen.Checkbox, name="Displayed", value="")
        self.internalid = self.add(npyscreen.TitleFixedText, value="None.", name="Internal ID")

    def beforeEditing(self):
        self.displayname.value = ""
        self.sapcode.value = ""
        self.sapname.value = ""
        self.displayed.value = True

    def afterEditing(self):
        self.parentApp.db.addCode(
            self.displayname.value,
            self.sapname.value,
            self.sapcode.value,
            self.displayed.value)
        self.parentApp.setNextForm("MAIN")

class EditCodeForm(EnterCodeForm):
    """This is the form for editing codes. Based on the EnterCodeForm, but prefills existing values."""
    def beforeEditing(self):
        data = self.parentApp.formEditPrefill
        self.displayname.value = data['displayname']
        self.sapname.value = data['sapname']
        self.sapcode.value = data['sapcode']
        self.displayed.value = data['displayed']
        self.internalid.value = str(data['internalid'])

    def afterEditing(self):
        self.parentApp.db.editCode(
            self.displayname.value,
            self.sapname.value,
            self.sapcode.value,
            self.displayed.value,
            self.internalid.value)
        self.parentApp.setNextForm("MAIN")

class ShowCodesForm(npyscreen.Form):
    """Form with an overview of all codes."""
    nextForm = None #Setting setNextForm after using switchForm breaks the latter.

    def create(self):
        self.grid = self.add(npyscreen.GridColTitles,
                             columns=6,
                             select_whole_line=True,
                             col_titles=["Display Name", "SAP Code", "SAP Name", "Displayed", "Total hours", "Internal ID"])
        self.grid.add_handlers({curses.ascii.NL: self.selectRow})
        #self.exitButton = self.add(ExitButton, name="Exit")

    def beforeEditing(self):
        newentry = [["Add New Entry", "---", "---", "---", "---", None]]
        data = self.parentApp.db.getAllCodesAndTotals()
        self.grid.values = newentry + data

    def afterEditing(self):
        self.parentApp.setNextForm(self.nextForm)
        self.nextForm = None

    def selectRow(self, input):
        selectedRow = self.grid.selected_row()
        if selectedRow[4] == None:
            # The first entry for creating a new code has been selected
            self.nextForm = 'NEW'
            self.parentApp.switchForm('NEW')
        else:
            self.parentApp.formEditPrefill = {
                'displayname': selectedRow[0],
                'sapcode': selectedRow[1],
                'sapname': selectedRow[2],
                'displayed': selectedRow[3],
                'internalid': selectedRow[4]}
            self.nextForm = 'EDIT'
            self.parentApp.switchForm("EDIT")

class ExitButton(npyscreen.ButtonPress):
    """Button for exiting."""
    def WhenPressed(self):
        self.parent.parentApp.setNextForm(None)

