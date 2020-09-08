import folderstats
import matplotlib.pyplot as plt
import PySimpleGUI as sg
from pathlib import Path

sg.theme('Dark Blue 3')
path = sg.popup_get_folder('Please select folder')
df = folderstats.folderstats(path, ignore_hidden=True)
filt = (df['folder'] != True) # Filter out the folder entries
df = df[filt]
df['Size MB'] = round(df['size'] / (1024 ** 2),2)
df = df[['name', 'ctime', 'mtime', 'size', 'Size MB']]
df['Time'] = df['mtime'] - df['ctime']
df['days'] = df['Time'].dt.days
df['Year'] = df['mtime'].dt.year
filt2 = (df['Year'] == 2020)
df = df[filt2]
df.loc[df['days'] > 0, 'Change Data'] = df['Size MB']
df.loc[df['days'] < 1, 'Change Data'] = 0
df = df.sort_values(by="mtime", ascending=False)
df = df.reset_index(drop=True)
print(df.head(10))

fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1)

ax1.plot_date(df['ctime'], df['mtime'])
ax1.set_ylabel('Modified Date')
ax1.set_xlabel('Created Date')

ax2.bar(df['mtime'], df['Change Data'])
ax2.set_ylabel('Change MB')
ax2.set_xlabel('Modifed Date')

# sg.popup('All done!')
plt.show()