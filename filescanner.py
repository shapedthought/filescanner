import folderstats
import matplotlib.pyplot as plt
import PySimpleGUI as sg
import pandas as pd
import logging

logging.basicConfig(filename='.\\issues.log', level=logging.DEBUG)

logger = logging.getLogger()

# sg.theme('SystemDefaultForReal')


class Gui:
    """Creates the GUI"""

    def __init__(self):
        self.menu_def = [['Help', 'About...']]

        self.layout = [
            [sg.Menu(self.menu_def)],
            [sg.Text('Directory to scan', size=(16, 1)), sg.Input(key='SCANDIR'), sg.FolderBrowse()],
            [sg.Text('Output directory', size=(16, 1)), sg.InputText(key='OUTDIR'), sg.FolderBrowse()],
            [sg.Checkbox('Start', default=False, key='START', enable_events=True),
             sg.Checkbox('End', default=False, key='END', enable_events=True)],
            [sg.Text('Start Date', size=(16, 1)), sg.Input(key='STARTYEAR', disabled=True)],
            [sg.Text('End Date', size=(16, 1)), sg.Input(key='ENDYEAR', disabled=True)],
            [sg.Submit(), sg.Cancel()],
            [sg.Output(size=(70, 10))]
        ]
        self.window = sg.Window('Folder Scanner', self.layout)


class Folderscanner():
    def __init__(self):
        self.df = pd.DataFrame(data=None)

    def scan(self, values, **kwargs):
        print('>> SCANNING')
        df = folderstats.folderstats(values['SCANDIR'], ignore_hidden=False)
        print('>> SCAN DONE - PERFORMING CALCULATIONS')
        # Filter out the folders
        filt = (df['folder'])  # Filter out the folder entries
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

        """
        Filters between specific years.
        """
        if values['STARTYEAR'] and values['ENDYEAR']:
            df = df[(df['mYear'] >= int(values['STARTYEAR'])) & (df['mYear'] <= int(values['ENDYEAR']))]
        elif values['STARTYEAR'] and not values['ENDYEAR']:
            df = df[(df['mYear'] >= int(values['STARTYEAR']))]
        elif not values['STARTYEAR'] and values['ENDYEAR']:
            df = df[(df['mYear'] <= int(values['ENDYEAR']))]

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
        df_perMonth.to_excel(values['OUTDIR'] + '/output.xlsx', sheet_name='Modified Year')
        sg.popup('All done!')
        plt.show()


def main():
    g = Gui()
    f = Folderscanner()
    check_start = False
    check_end = False


    while True:
        event, values = g.window.Read()
        if event is None or event == 'Cancel':
            break
        if event == 'Submit':
            if values['SCANDIR'] and values['OUTDIR']:
                f.scan(values)
            else:
                sg.popup_error('Required info missing')
        if event == 'START':
            if not check_start:
                g.window['STARTYEAR'].update(disabled=False)
                check_start = True
            else:
                g.window['STARTYEAR'].update(disabled=True)
                check_start = False
        if event == 'END':
            if not check_end:
                g.window['ENDYEAR'].update(disabled=False)
                check_end = True
            else:
                g.window['ENDYEAR'].update(disabled=True)
                check_end = False

main()