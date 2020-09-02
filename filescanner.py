import folderstats
import matplotlib.pyplot as plt
import PySimpleGUI as sg
from pathlib import Path

sg.theme('Dark Blue 3')
path = sg.popup_get_folder('Please select folder')
df = folderstats.folderstats(path, ignore_hidden=True)
df['Size GB'] = round(df['size'] / (1024 ** 2),2)
df = df[['ctime', 'mtime', 'size', 'Size GB']]
plt.plot_date(df['ctime'], df['mtime'])
plt.ylabel('Modified Date')
plt.xlabel('Created Date')
sg.popup('All done!')
plt.show()