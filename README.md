# Urenlog
Simple TUI and CLI application for hour registration.

[[https://github.com/TomWis97/urenlog/wiki/Images/help.png]]
*Help function*

# Hour registration
For quick registration of hours, use the `add-hours` option. Enter a part of the display name of the code and the amount of hours. **Make sure first set up codes!** For example: to register one-and-a-half hours on the code "Foo Code", you can use the following command: `urenlog add-hours fo 1.5`. To see the hours you've registered today, use `hours-today`.

[[https://github.com/TomWis97/urenlog/wiki/Images/cli.png]]
*Demo of CLI for quick hour registration.*

## Editing codes
Use the `codes` option to edit codes. When opening, it shows a list of all codes with the total per code. To add a code, select the first row and press enter. Then, fill in the fields (the ID will be generated automatically). The `displayed` option will allow you to select it in the `hours` mode or use it with the `add-hours` command.

[[https://github.com/TomWis97/urenlog/wiki/Images/codes.png]]
*Code overview*

## Listing hour entries
To view all hour entries (with optional comments) or to add entries, use the `hours` option. Navigate with the tab key, select opions with space. To delete an entry, highlight the row and press enter (and use tab and enter to confirm).

[[https://github.com/TomWis97/urenlog/wiki/Images/hours.png]]
*List current entries*

## Overview
At the end of the month, when you need to enter the data in SAP, use the `overview` option. This presents the data in roughly the same way as SAP. This way, you can easily copy the data over. To show data like the hour code, highlight the label and press enter.

[[https://github.com/TomWis97/urenlog/wiki/Images/overview.png]]
*Overview of codes*
