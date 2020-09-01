import folderstats
import matplotlib.pyplot as plt
import PySimpleGUI as sg
from pathlib import Path

sg.theme('Dark Blue 3')

path = sg.popup_get_folder('Please select folder')

df = folderstats.folderstats(path, ignore_hidden=True)

df['Size GB'] = round(df['size'] / (1024 ** 2),2)

df = df[['ctime', 'mtime', 'size', 'Size GB']]
df['Time'] = df['mtime'] - df['ctime']
df['days'] = df['Time'].dt.days
df.loc[df['days'] > 0, 'days2'] = df['days']
df.loc[df['days'] < 0, 'days2'] = 0
# results = df.groupby(['ctime', 'mtime']).sum()

plt.plot_date(df['ctime'], df['days2'])

# results.to_excel('file_data_info.xlsx')
sg.popup('All done!')

plt.show()