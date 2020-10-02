import folderstats
import matplotlib.pyplot as plt
import PySimpleGUI as sg
import pandas as pd
from pathlib import Path

sg.theme('Dark Blue 3')


class Gui:
    """Creates the GUI"""

    def __init__(self):
        self.menu_def = [['Help', 'About...']]

        self.layout = [
            [sg.Menu(self.menu_def)],
            [sg.Text('Directory to scan', size=(16, 1)), sg.Input(key='SCANDIR'), sg.FolderBrowse()],
            [sg.Text('Output directory', size=(16, 1)), sg.InputText(key='OUTDIR'), sg.FolderBrowse()],
            [sg.Checkbox('Start Year', default=False, key='START', enable_events=True),
             sg.Checkbox('End Year', default=False, key='END', enable_events=True, disabled=True)],
            [sg.Text('Start Year', size=(16, 1)), sg.Input(key='STARTYEAR')],
            [sg.Text('Start Year', size=(16, 1)), sg.Input(key='ENDYEAR')],
            [sg.Submit(), sg.Cancel()]
        ]
        self.window = sg.Window('Folder Scanner', self.layout)


class Folderscanner(folderstats):
    def scan(self, values):
        super().__init__()


sg.popup('Welcome to Filescanner!')
path = sg.popup_get_folder('Please select folder')

# Grab the file data info
df = folderstats.folderstats(path, ignore_hidden=True)

# Filter out the folders
filt = (df['folder'] != True)  # Filter out the folder entries
df = df[filt]

# Add a column for size in MB
df['Size MB'] = round(df['size'] / (1024 ** 2), 2)

# Caclulate the time delta, in deltaDays, between modified and change dates
df['Time'] = df['mtime'] - df['ctime']
df['deltaDays'] = df['Time'].dt.days

# Add Columns for Modified Day, Month & Year
df['mDay'] = df['mtime'].dt.day
df['mYear'] = df['mtime'].dt.year
df['mMonth'] = df['mtime'].dt.month

# Add Columns for Modified Day, Month & Year
df['cDay'] = df['ctime'].dt.day
df['cYear'] = df['ctime'].dt.year
df['cMonth'] = df['ctime'].dt.month

# Filter for this year only
filt2 = (df['mYear'] == 2020)
df = df[filt2]

# Adds a new column for change data if the deltaDays are higher than 1
df.loc[df['deltaDays'] > 0, 'Change Data'] = df['Size MB']
df.loc[df['deltaDays'] < 1, 'Change Data'] = 0

# Sort the new df by Modified time and reset the index
df = df.sort_values(by="mtime", ascending=False)
df = df.reset_index(drop=True)

# Filter down the df and then group by Year, Month then Day for modified capacity
df_perMonth = df[['mDay', 'mYear', 'mMonth', 'Change Data']]
df_perMonth = df_perMonth.groupby(['mYear', 'mMonth', 'mDay']).sum()

# Split the plot into two
fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1)

# First plot for Modified vs Created Date
ax1.plot_date(df['ctime'], df['mtime'])
ax1.set_ylabel('Modified Date')
ax1.set_xlabel('Created Date')

# Second plot with Modified date vs change data
ax2.bar(df['mtime'], df['Change Data'])
ax2.set_ylabel('Change MB')
ax2.set_xlabel('Modifed Date')

# Output to Excel
df_perMonth.to_excel('Output.xlsx')
df_perMonth.to_excel('output.xlsx', sheet_name='Modified Year')

sg.popup('All done!')
plt.show()
